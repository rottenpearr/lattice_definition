"""
CRIS — FastAPI backend
Запуск: uvicorn api:app --reload --port 8000
Документация: http://localhost:8000/docs
"""

import hashlib
import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from cris.core.coordinates import shift_coordinates, normalize_coordinates
from cris.db.connection import get_cursor
from cris.db.queries import check_coords

# ── Приложение ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="CRIS API",
    description="Crystal Recognition & Identification System",
    version="0.1.0",
)

# CORS — разрешаем запросы с фронта (localhost:3000 при локальной разработке)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Схемы запроса / ответа ────────────────────────────────────────────────────

class Ion(BaseModel):
    label: str
    x: float
    y: float
    z: float


class AnalyzeRequest(BaseModel):
    """
    Тело запроса: список ионов в декартовых координатах (Å).
    Фронт конвертирует fractional → cartesian перед отправкой.
    """
    sites: list[Ion]


class LatticeResult(BaseModel):
    id: Optional[int]
    name_en: Optional[str]
    name_ru: Optional[str]
    description: Optional[str]
    confidence: float


class StructureResult(BaseModel):
    id: Optional[int]
    name: Optional[str]
    formula: Optional[str]
    cell_a: Optional[float]
    cell_b: Optional[float]
    cell_c: Optional[float]
    sg_number: Optional[int]
    sg_hm: Optional[str]
    confidence: float


class RankingItem(BaseModel):
    name_en: Optional[str]
    name_ru: Optional[str]
    prob: float


class AnalyzeResponse(BaseModel):
    success: bool
    message: str = ""
    lattice: Optional[LatticeResult] = None
    structure: Optional[StructureResult] = None
    lattice_ranking: list[RankingItem] = []


# ── Эндпоинты ─────────────────────────────────────────────────────────────────

def _input_hash(normalized: list) -> str:
    """SHA-256 нормализованных координат — стабильный идентификатор входа."""
    coords = sorted([[round(r[1], 6), round(r[2], 6), round(r[3], 6)] for r in normalized])
    return hashlib.sha256(json.dumps(coords).encode()).hexdigest()


# ── Эндпоинты ─────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    """Проверка — сервер жив."""
    return {"status": "ok", "version": "0.1.0"}


@app.get("/api/stats")
def stats():
    """
    Живые счётчики для главной страницы.
    Возвращает количество эталонных структур, типов решёток и сессий распознавания.
    """
    try:
        with get_cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM reference_structure")
            struct_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM lattice_type")
            lattice_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM recognition_session")
            session_count = cur.fetchone()[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")

    return {
        "struct_count":   struct_count,
        "lattice_count":  lattice_count,
        "session_count":  session_count,
    }


@app.post("/api/session")
def create_session(body: AnalyzeRequest):
    """
    Логирует сессию распознавания в БД.
    Не запускает ML — только сохраняет факт запроса с хешем координат.
    Возвращает session_id (UUID) для последующей привязки результатов.
    """
    if len(body.sites) < 2:
        raise HTTPException(status_code=400, detail="Нужно минимум 2 иона")

    # Нормализуем координаты для хеша
    raw = [[s.label, s.x, s.y, s.z] for s in body.sites]
    try:
        shifted    = shift_coordinates(raw)
        normalized = normalize_coordinates(shifted)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    input_hash = _input_hash(normalized)

    try:
        with get_cursor() as cur:
            cur.execute(
                """
                INSERT INTO recognition_session (ion_count, input_hash)
                VALUES (%s, %s)
                RETURNING id, created_at
                """,
                (len(body.sites), input_hash),
            )
            row = cur.fetchone()
            session_id  = str(row[0])
            created_at  = row[1].isoformat() if row[1] else None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")

    return {
        "session_id":  session_id,
        "ion_count":   len(body.sites),
        "input_hash":  input_hash[:12] + "…",   # короткий превью
        "created_at":  created_at,
    }


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(body: AnalyzeRequest):
    """
    Принимает декартовые координаты ионов, запускает matching по БД.

    Алгоритм:
    1. Конвертация [[label, x, y, z], ...]
    2. shift_coordinates + normalize_coordinates
    3. check_coords() — сравнение с эталонами из reference_structure
    4. Формирование ответа
    """
    if len(body.sites) < 2:
        raise HTTPException(status_code=400, detail="Нужно минимум 2 иона")

    # 1. Конвертируем в формат [[label, x, y, z], ...]
    raw = [[s.label, s.x, s.y, s.z] for s in body.sites]

    # 2. Нормализуем: сдвиг к началу координат + масштаб в [0, 1]
    try:
        shifted    = shift_coordinates(raw)
        normalized = normalize_coordinates(shifted)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # 3. Собираем словарь {n: [label, nx, ny, nz]} — формат check_coords
    coords_dict = {i: row for i, row in enumerate(normalized)}

    # 4. Запускаем поиск по БД
    result = check_coords(coords_dict, len(body.sites))

    if result is False:
        return AnalyzeResponse(
            success=False,
            message="Совпадающих структур не найдено в эталонной БД",
        )

    # 5. Разбираем результат
    lattice_names, struct_names = result[0]
    lattice_info, lt_prob       = result[1]
    struct_info,  st_prob       = result[2]

    # lattice_type row: (id, name_en, name_ru, description)
    lattice = LatticeResult(
        id          = lattice_info[0] if lattice_info else None,
        name_en     = lattice_info[1] if lattice_info else None,
        name_ru     = lattice_info[2] if lattice_info else None,
        description = lattice_info[3] if lattice_info else None,
        confidence  = round(lt_prob, 2),
    )

    # reference_structure row:
    # (id, name, cell_a, cell_b, cell_c, cell_vol, alpha, beta, gamma,
    #  sg_number, sg_hall, sg_hm, doi, formula)
    structure = StructureResult(
        id         = struct_info[0]  if struct_info else None,
        name       = struct_info[1]  if struct_info else None,
        formula    = struct_info[13] if struct_info else None,
        cell_a     = struct_info[2]  if struct_info else None,
        cell_b     = struct_info[3]  if struct_info else None,
        cell_c     = struct_info[4]  if struct_info else None,
        sg_number  = struct_info[9]  if struct_info else None,
        sg_hm      = struct_info[11] if struct_info else None,
        confidence = round(st_prob, 2),
    )

    # Рейтинг решёток — сортируем по убыванию вероятности
    # lattice_names = [[id, name_ru, name_en, prob], ...]
    ranking = sorted(
        [
            RankingItem(
                name_en = lt[2],
                name_ru = lt[1],
                prob    = round(lt[3], 2),
            )
            for lt in lattice_names
        ],
        key=lambda x: -x.prob,
    )

    return AnalyzeResponse(
        success         = True,
        lattice         = lattice,
        structure       = structure,
        lattice_ranking = ranking,
    )
