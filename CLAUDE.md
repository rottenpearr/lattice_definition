# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the application

```bash
python main.py
```

Requires MySQL 8.0+ running on `localhost:3306`. Credentials are in `cris/db/config.py` (`root`/`root`, database `crystal_lattice_db`).

## Database setup

```bash
# Full initialization from scratch (runnable from any directory)
python cris/tools/complete_db.py
```

This runs `cris/db/schema/db_init.py` → `cris/db/schema/lattice_types_init.py` → `cris/db/importers/json_to_db.py` + `cris/db/importers/xyz_to_db.py` for every file in `data/db/json/`.

To recreate from scratch in MySQL CLI:
```sql
drop database crystal_lattice_db;
create database crystal_lattice_db;
```

## Regenerating UI Python files

After editing `.ui` files in `assets/ui/`:
```bash
pyside6-uic assets/ui/Main_Window.ui -o cris/app/generated/Main_Window_ui.py
pyside6-uic assets/ui/Ion_Dialog.ui -o cris/app/generated/Ion_Dialog_ui.py
pyside6-uic assets/ui/Info_Dialog.ui -o cris/app/generated/Info_Dialog_ui.py
pyside6-rcc assets/resources.qrc -o cris/app/generated/resources_rc.py
```

After regenerating `Main_Window_ui.py`, replace `import resources_rc` with `from cris.app.generated import resources_rc`.

## Architecture

### Project layout

```
cris/                          # Main installable package
├── app/
│   └── generated/             # Compiled UI artifacts (do not edit directly)
│       ├── Main_Window_ui.py
│       ├── Ion_Dialog_ui.py
│       ├── Info_Dialog_ui.py
│       └── resources_rc.py
├── core/
│   ├── coordinates.py         # Normalization: shift + scale to [0, 1]
│   ├── vectors.py             # Pairwise distance vectors + normalize_vectors()
│   ├── spectrum.py            # Gaussian KDE spectra + plots
│   ├── identification.py      # KDE similarity scoring entry point
│   └── clustering.py          # UMAP + HDBSCAN clustering of CIF structures
├── db/
│   ├── config.py              # DB connection config
│   ├── queries.py             # Search logic (get_similar_xyz_from_db, check_coords)
│   ├── schema/
│   │   ├── db_init.py / .sql
│   │   └── lattice_types_init.py / .sql
│   └── importers/
│       ├── json_to_db.py      # CIF metadata → substances + ions
│       └── xyz_to_db.py       # XYZ coordinates → ions_library
├── tools/                     # Utility and research runner scripts
│   ├── testing.py             # XYZ loading with optional Gaussian noise
│   ├── kde_4_all_ions.py      # KDE computation for all ions in a structure
│   ├── kde_to_csv.py          # Save per-ion KDE arrays to CSV
│   ├── complete_db.py         # One-shot DB init runner
│   ├── get_vectors_from_xyz.py
│   ├── normalize_vectors.py
│   ├── mp_api_test.py         # Materials Project API query (see known issues)
│   └── dataset_generation/    # Scripts for building training datasets
│       ├── download_structures.py  # Download XYZ from Materials Project API
│       ├── generate_vacancies.py   # Create vacancy variants of structures
│       ├── generate_dataset.py     # Single-structure KDE dataset generation
│       ├── generate_all_datasets.py # Batch KDE dataset generation with resume
│       └── macrocubic_NaCl.py      # Generate NaCl/UN/UC supercell XYZ files
└── report.py                  # DOCX report generation

assets/
├── icons/                     # SVG icons
├── images/                    # Lattice type images (PNG/SVG)
├── ui/                        # Qt Designer .ui source files
└── resources.qrc              # QRC manifest for icons

ML/                            # Research notebooks and ML scripts
├── clustering/
│   ├── ase.py
│   └── init_cluster_umap.py   # Runs cluster_structures + plot_umap from cris.core.clustering
├── spectre_diff/
│   ├── spectres_wo_err.py     # Spectrum comparison without error handling
│   ├── spectres_wo_err_types.py
│   └── wasserstein_dist.py    # Wasserstein distance metric
├── percentage_ident.py        # KDE identification experiment (hardcoded NaCl data)
└── visualize_kde.py           # Quick KDE plot from CSV

data/
├── db/                        # DB source files — tracked in git
│   ├── cif/                   # Raw CIF files
│   ├── json/                  # JSON converted from CIF
│   └── xyz/                   # XYZ atom positions from CIF
├── structures/                # XYZ structures
│   ├── micro/                 # Unit cells (4–80 atoms)
│   │   ├── source/            # Downloaded from MP/CIF — tracked in git
│   │   └── generated/        # With vacancies/noise — .gitignore
│   └── macro/                 # Supercells NxNxN
│       ├── source/            # Clean supercells — tracked in git
│       └── generated/        # With vacancies/noise — .gitignore
├── examples/                  # CSV input examples for UI — tracked in git
└── kde_arrays/                # KDE vectors per structure — .gitignore (local only)
    ├── micro/source/          # KDE from clean unit cells
    ├── micro/generated/       # KDE from unit cells with vacancies
    ├── macro/source/          # KDE from clean supercells
    └── macro/generated/       # KDE from supercells with vacancies
```

### Core identification pipeline

User input → `cris/core/coordinates.py` → `cris/db/queries.py` → results

1. **Normalization** (`cris/core/coordinates.py`): `shift_coordinates` moves the minimum to origin, `normalize_coordinates` divides by global max → [0.0, 1.0] cube. Makes matching scale-independent.

2. **DB search** (`cris/db/queries.py`):
   - `get_similar_xyz_from_db(coordinates)` — exact match on normalized x/y/z in `ions_library`
   - `check_coords(ions, ion_amount)` — filters by ion count, builds `Counter` probability distributions
   - Returns `[[lattice_names, substance_names], [top_lattice_info, probability], [top_substance_info, probability]]`

### Database schema (`crystal_lattice_db`)

- `lattice_type` — lattice type definitions (id, name_en, name_ru)
- `substances` — compounds with cell parameters (a, b, c, angles, volume, space group)
- `ions` — original CIF atom sites (label, symbol, Wyckoff position, occupancy)
- `ions_library` — matching table: normalized x/y/z per substance/lattice pair

Matching is exact float comparison on normalized coordinates — precision sensitivity is a known open issue.

### GUI (`main.py`)

`MainWindow` owns `ions_data: dict` mapping ion index → `[label, x, y, z]`. Flow:
- Combo box sets ion count → `populate_list` fills `QListWidget`
- Clicking an ion opens `InputDialog` (coordinate entry with float validation)
- CSV upload fills `ions_data` directly
- "Start" calls `check_all_values`: validates → normalizes → queries DB → renders results

Generated UI files in `cris/app/generated/` are compiled artifacts — edit the `.ui` sources in `assets/ui/`, not the generated Python.

## Known issues

- CIF files with uncertainty notation like `0.123(20)` are not handled
- DB initialization fails if `crystal_lattice_db` doesn't exist yet (needs a pre-create step)
- Float precision in normalized coordinates can cause missed matches
- Ion count hard limit of 1000 in the UI
- Math operations in `cris/core/vectors.py` use pure Python — should be rewritten with numpy
- `cris/core/spectrum.py` imports `cris.db.config` — core module has an unwanted dependency on the db layer; should be refactored so DB config is injected or spectrum plotting is decoupled
- `cris/tools/mp_api_test.py` contains a hardcoded Materials Project API key — must be moved to an environment variable or `.env` file before sharing/deploying
