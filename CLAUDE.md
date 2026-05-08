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
python scripts/db/complete_db.py
```

This runs `cris/db/schema/db_init.py` → `cris/db/schema/lattice_types_init.py` → `cris/db/importers/json_to_db.py` + `cris/db/importers/xyz_to_db.py` for every file in `data/json/`.

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
│   ├── vectors.py             # Pairwise distance vectors between ions
│   ├── spectrum.py            # Gaussian KDE spectra + plots
│   ├── identification.py      # KDE similarity scoring entry point
│   ├── wasserstein_dist.py    # Wasserstein distance metric
│   ├── spectres_wo_err.py     # Spectrum comparison without error handling
│   └── spectres_wo_err_types.py
├── db/
│   ├── config.py              # DB connection config
│   ├── queries.py             # Search logic (get_similar_xyz_from_db, check_coords)
│   ├── schema/
│   │   ├── db_init.py / .sql
│   │   └── lattice_types_init.py / .sql
│   └── importers/
│       ├── json_to_db.py      # CIF metadata → substances + ions
│       └── xyz_to_db.py       # XYZ coordinates → ions_library
└── report.py                  # DOCX report generation

assets/
├── icons/                     # SVG icons
├── ui/                        # Qt Designer .ui source files
└── resources.qrc              # QRC manifest for icons

scripts/                       # Research/utility scripts (not part of main app)
├── db/complete_db.py          # One-shot DB init runner
├── generate_dataset.py        # Batch KDE/CSV dataset generation
└── operations/
    ├── testing.py             # XYZ loading with optional noise
    └── kde_4_all_ions.py      # KDE computation for all ions in a structure
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
