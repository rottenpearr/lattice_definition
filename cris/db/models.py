"""Dataclass-модели, отражающие строки таблиц БД."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class LatticeType:
    id: int
    name_en: str
    name_ru: str
    crystal_system: str = ""
    bravais_lattice: str = ""
    point_group: str = ""
    sg_number_min: Optional[int] = None
    sg_number_max: Optional[int] = None
    description: str = ""


@dataclass
class LatticeMetadata:
    lattice_type_id: int
    discoverer: str = ""
    discovery_year: Optional[int] = None
    discovery_context: str = ""
    wiki_url: str = ""
    review_doi: str = ""
    notes: str = ""
    enriched_at: Optional[datetime] = None
    enrichment_source: str = ""


@dataclass
class ReferenceStructure:
    id: int
    name: str
    formula: str
    lattice_type_id: int
    cell_length_a: Optional[float] = None
    cell_length_b: Optional[float] = None
    cell_length_c: Optional[float] = None
    cell_volume: Optional[float] = None
    cell_angle_alpha: Optional[float] = None
    cell_angle_beta: Optional[float] = None
    cell_angle_gamma: Optional[float] = None
    sg_number: Optional[int] = None
    sg_hall: str = ""
    sg_hm: str = ""
    cif_path: str = ""
    xyz_path: str = ""
    image_path: str = ""
    cod_id: Optional[int] = None
    mp_id: str = ""
    icsd_id: Optional[int] = None
    doi: str = ""
    source_url: str = ""


@dataclass
class StructureSite:
    id: int
    structure_id: int
    atom_label: str = ""
    atom_symbol: str = ""
    oxidation: Optional[float] = None
    multiplicity: Optional[int] = None
    wyckoff: str = ""
    occupancy: float = 1.0
    fract_x: Optional[float] = None
    fract_y: Optional[float] = None
    fract_z: Optional[float] = None
    norm_x: Optional[float] = None
    norm_y: Optional[float] = None
    norm_z: Optional[float] = None


@dataclass
class RecognitionSession:
    id: str                    # UUID
    ion_count: int
    input_hash: str            # SHA-256
    xyz_path: str = ""
    created_at: Optional[datetime] = None
    notes: str = ""


@dataclass
class RecognitionResult:
    id: int
    session_id: str
    method: str
    method_version: str
    rank: int
    predicted_lattice_type_id: Optional[int]
    predicted_structure_id: Optional[int]
    confidence: Optional[float]
    vector_path: str = ""
    computed_at: Optional[datetime] = None


@dataclass
class FeatureVectorCache:
    input_hash: str
    params_hash: str
    method_name: str
    vector_path: str
    ion_count: int
    computed_at: Optional[datetime] = None
