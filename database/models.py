"""
Dataclass-модели, отражающие строки таблиц.
Используются для типизации в репозитории — без ORM-магии.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class LatticeType:
    id: int
    name_en: str
    name_ru: str
    description: str = ""
    crystal_system: str = ""
    bravais_lattice: str = ""
    space_group_number_min: Optional[int] = None
    space_group_number_max: Optional[int] = None
    point_group: str = ""


@dataclass
class LatticeMetadata:
    id: int
    lattice_type_id: int
    discoverer: str = ""
    discovery_year: Optional[int] = None
    discovery_context: str = ""
    wiki_url: str = ""
    review_doi: str = ""
    notes: str = ""
    last_enriched_at: Optional[datetime] = None
    enrichment_source: str = ""


@dataclass
class ReferenceStructure:
    """Эталонное вещество (бывший substances)."""
    id: int
    name: str
    lattice_type_id: int
    formula: str = ""
    cell_length_a: Optional[float] = None
    cell_length_b: Optional[float] = None
    cell_length_c: Optional[float] = None
    cell_volume: Optional[float] = None
    cell_angle_alpha: Optional[float] = None
    cell_angle_beta: Optional[float] = None
    cell_angle_gamma: Optional[float] = None
    space_group_IT_number: str = ""
    symmetry_space_group_name_Hall: str = ""
    symmetry_space_group_name_H_M: str = ""
    cif_path: str = ""
    xyz_path: str = ""
    image_path: str = ""
    cod_id: Optional[int] = None
    mp_id: str = ""
    icsd_id: Optional[int] = None
    source_url: str = ""
    doi: str = ""
    added_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class RecognitionSession:
    id: str                   # UUID
    ion_count: int
    input_hash: str           # SHA-256
    xyz_input_path: str = ""
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
    predicted_substance_id: Optional[int]
    confidence: Optional[float]
    feature_vector_path: str = ""
    computed_at: Optional[datetime] = None


@dataclass
class FeatureVectorCache:
    input_hash: str
    params_hash: str
    method_name: str
    vector_path: str
    ion_count: int
    computed_at: Optional[datetime] = None


@dataclass
class RecognitionTopResult:
    """Агрегированный результат для отображения в UI."""
    lattice_type_id: int
    lattice_name_ru: str
    lattice_name_en: str
    substance_id: Optional[int]
    substance_name: str
    confidence: float
    method: str
    session_id: str
