"""
CRUD для recognition_session, recognition_result и feature_vector_cache.

Основной паттерн использования:
    hash_ = compute_input_hash(coords)
    session = get_or_create_session(hash_, ion_count)
    cached = get_cached_results(session.id, method)
    if cached:
        return cached
    results = run_model(...)
    save_results(session.id, method, results)
"""
import hashlib
import json
import uuid
from typing import Optional
from database.db import get_cursor
from database.models import RecognitionSession, RecognitionResult, FeatureVectorCache


# ─── хэширование ────────────────────────────────────────────────────────────

def compute_input_hash(normalized_coords: list[tuple[float, float, float]]) -> str:
    """SHA-256 нормализованного отсортированного списка координат."""
    sorted_coords = sorted(normalized_coords)
    raw = json.dumps(sorted_coords, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def compute_params_hash(params: dict) -> str:
    """SHA-256 словаря параметров метода (bandwidth, grid_size и др.)."""
    raw = json.dumps(params, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


# ─── session ─────────────────────────────────────────────────────────────────

def get_session_by_hash(input_hash: str) -> Optional[RecognitionSession]:
    with get_cursor() as cur:
        cur.execute("""
            SELECT id, ion_count, input_hash, xyz_input_path, created_at, notes
            FROM recognition_session WHERE input_hash = %s
            ORDER BY created_at DESC LIMIT 1
        """, (input_hash,))
        row = cur.fetchone()
    if not row:
        return None
    return RecognitionSession(id=row[0], ion_count=row[1], input_hash=row[2],
                              xyz_input_path=row[3] or "", created_at=row[4], notes=row[5] or "")


def create_session(ion_count: int, input_hash: str,
                   xyz_input_path: str = "", notes: str = "") -> RecognitionSession:
    session_id = str(uuid.uuid4())
    with get_cursor() as cur:
        cur.execute("""
            INSERT INTO recognition_session (id, ion_count, input_hash, xyz_input_path, notes)
            VALUES (%s, %s, %s, %s, %s)
        """, (session_id, ion_count, input_hash, xyz_input_path or None, notes or None))
    return RecognitionSession(id=session_id, ion_count=ion_count, input_hash=input_hash,
                              xyz_input_path=xyz_input_path, notes=notes)


def get_or_create_session(ion_count: int,
                           normalized_coords: list[tuple[float, float, float]],
                           xyz_input_path: str = "") -> RecognitionSession:
    """Возвращает существующую сессию для этого набора координат или создаёт новую."""
    input_hash = compute_input_hash(normalized_coords)
    session = get_session_by_hash(input_hash)
    if session is None:
        session = create_session(ion_count, input_hash, xyz_input_path)
    return session


# ─── results ─────────────────────────────────────────────────────────────────

def get_cached_results(session_id: str, method: str,
                       method_version: str = "1.0") -> list[RecognitionResult]:
    with get_cursor() as cur:
        cur.execute("""
            SELECT id, session_id, method, method_version, rank,
                   predicted_lattice_type_id, predicted_substance_id,
                   confidence, feature_vector_path, computed_at
            FROM recognition_result
            WHERE session_id = %s AND method = %s AND method_version = %s
            ORDER BY rank
        """, (session_id, method, method_version))
        rows = cur.fetchall()
    return [RecognitionResult(*row) for row in rows]


def save_result(session_id: str, method: str, method_version: str,
                rank: int, lattice_type_id: Optional[int], substance_id: Optional[int],
                confidence: float, feature_vector_path: str = "") -> None:
    with get_cursor() as cur:
        cur.execute("""
            INSERT INTO recognition_result
                (session_id, method, method_version, rank,
                 predicted_lattice_type_id, predicted_substance_id,
                 confidence, feature_vector_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                predicted_lattice_type_id = VALUES(predicted_lattice_type_id),
                predicted_substance_id    = VALUES(predicted_substance_id),
                confidence                = VALUES(confidence),
                feature_vector_path       = VALUES(feature_vector_path),
                computed_at               = CURRENT_TIMESTAMP
        """, (session_id, method, method_version, rank,
               lattice_type_id, substance_id, confidence, feature_vector_path or None))


# ─── feature vector cache ─────────────────────────────────────────────────────

def get_vector_cache(input_hash: str, params: dict) -> Optional[FeatureVectorCache]:
    params_hash = compute_params_hash(params)
    with get_cursor() as cur:
        cur.execute("""
            SELECT input_hash, params_hash, method_name, vector_path, ion_count, computed_at
            FROM feature_vector_cache WHERE input_hash = %s AND params_hash = %s
        """, (input_hash, params_hash))
        row = cur.fetchone()
    if not row:
        return None
    return FeatureVectorCache(*row)


def save_vector_cache(input_hash: str, params: dict,
                      method_name: str, vector_path: str, ion_count: int) -> None:
    params_hash = compute_params_hash(params)
    with get_cursor() as cur:
        cur.execute("""
            INSERT INTO feature_vector_cache
                (input_hash, params_hash, method_name, vector_path, ion_count)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                vector_path = VALUES(vector_path),
                computed_at = CURRENT_TIMESTAMP
        """, (input_hash, params_hash, method_name, vector_path, ion_count))
