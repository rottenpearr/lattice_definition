-- PostgreSQL-схема crystal_lattice_db
-- Запускать от имени пользователя с правами на БД crystal_lattice_db
-- Создание БД выполняется отдельно (db_init.py)

-- ─────────────────────────────────────────────────────────────
-- ENUM-типы
-- ─────────────────────────────────────────────────────────────
DO $$ BEGIN
    CREATE TYPE existence_status_t AS ENUM (
        'experimental', 'theoretical', 'hypothetical', 'disputed'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE lookup_source_t AS ENUM (
        'COD', 'MATERIALS_PROJECT', 'ICSD', 'CROSSREF',
        'PUBCHEM', 'SEMANTIC_SCHOLAR', 'OSTI', 'AI_SEARCH', 'MANUAL'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE lookup_target_t AS ENUM (
        'lattice_type', 'reference_structure', 'substance'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- ─────────────────────────────────────────────────────────────
-- Триггерная функция для updated_at
-- ─────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ─────────────────────────────────────────────────────────────
-- 1. Типы кристаллических решёток (справочник)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS lattice_type (
    id               SERIAL PRIMARY KEY,
    name_en          VARCHAR(100) NOT NULL UNIQUE,
    name_ru          VARCHAR(100) NOT NULL,
    crystal_system   VARCHAR(50),   -- triclinic/monoclinic/orthorhombic/tetragonal/trigonal/hexagonal/cubic
    bravais_lattice  VARCHAR(10),   -- P/I/F/C/R
    point_group      VARCHAR(20),
    sg_number_min    SMALLINT,      -- нижняя граница номеров пр. групп ITA
    sg_number_max    SMALLINT,      -- верхняя граница номеров пр. групп ITA
    description      TEXT
);

-- ─────────────────────────────────────────────────────────────
-- 2. Метаданные типа решётки (обогащается через GigaChat)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS lattice_metadata (
    lattice_type_id      INT PRIMARY KEY,
    coordination_number  SMALLINT,          -- координационное число (12 для FCC, 8 для BCC)
    packing_efficiency   REAL,              -- плотность упаковки, 0..1 (0.74 для FCC)
    typical_materials    TEXT,              -- "Al, Cu, Au, Ni, γ-Fe"
    applications         TEXT,              -- области применения
    wiki_url             VARCHAR(1024),
    notes                TEXT,              -- интересные факты
    enriched_at          TIMESTAMP NULL,
    enrichment_source    VARCHAR(50),
    FOREIGN KEY (lattice_type_id) REFERENCES lattice_type(id) ON DELETE CASCADE
);

-- ─────────────────────────────────────────────────────────────
-- 3. Эталонные структуры (вещества)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS reference_structure (
    id               SERIAL PRIMARY KEY,
    name             VARCHAR(255) NOT NULL,
    formula          VARCHAR(100),
    lattice_type_id  INT NOT NULL,

    -- параметры элементарной ячейки
    cell_length_a    REAL,
    cell_length_b    REAL,
    cell_length_c    REAL,
    cell_volume      REAL,
    cell_angle_alpha REAL,
    cell_angle_beta  REAL,
    cell_angle_gamma REAL,

    -- пространственная группа
    sg_number        SMALLINT,
    sg_hall          VARCHAR(100),
    sg_hm            VARCHAR(100),

    -- пути к файлам (относительно корня проекта)
    cif_path         VARCHAR(512),  -- data/db/cif/...
    xyz_path         VARCHAR(512),  -- data/db/xyz/...
    image_path       VARCHAR(512),  -- assets/images/...

    -- внешние идентификаторы
    cod_id           INT,           -- Crystallography Open Database
    mp_id            VARCHAR(50),   -- Materials Project: mp-XXXXX
    icsd_id          INT,           -- ICSD
    doi              VARCHAR(255),
    source_url       VARCHAR(1024),

    -- статус существования
    existence_status existence_status_t NOT NULL DEFAULT 'experimental',
    existence_source VARCHAR(512),

    -- описание (robocrystallographer или MP)
    structure_description TEXT,

    added_at         TIMESTAMP DEFAULT NOW(),
    updated_at       TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (lattice_type_id) REFERENCES lattice_type(id) ON DELETE CASCADE
);

DROP TRIGGER IF EXISTS trg_rs_updated_at ON reference_structure;
CREATE TRIGGER trg_rs_updated_at
    BEFORE UPDATE ON reference_structure
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ─────────────────────────────────────────────────────────────
-- 4. Описание вещества (обогащается после распознавания)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS substance_info (
    id               SERIAL PRIMARY KEY,
    structure_id     INT NOT NULL UNIQUE,   -- один к одному с reference_structure
    description      TEXT,                  -- связный текст от GigaChat
    applications     TEXT,                  -- применение в промышленности/науке
    hazards          TEXT,                  -- токсичность, радиоактивность и пр.
    properties       JSONB,                 -- {melting_point, density, color, ...}
    scientific_sources JSONB,               -- [{doi, title, journal, year, url, snippet}]
    enriched_at      TIMESTAMP DEFAULT NOW(),
    enrichment_source VARCHAR(100),         -- "PUBCHEM+CROSSREF+AI"
    FOREIGN KEY (structure_id) REFERENCES reference_structure(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_substance_structure ON substance_info (structure_id);

-- ─────────────────────────────────────────────────────────────
-- 6. Сессия распознавания
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS recognition_session (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ion_count    INT NOT NULL,
    input_hash   CHAR(64) NOT NULL,   -- SHA-256 нормализованных координат
    xyz_path     VARCHAR(512),
    created_at   TIMESTAMP DEFAULT NOW(),
    notes        TEXT
);

CREATE INDEX IF NOT EXISTS idx_session_hash ON recognition_session (input_hash);

-- ─────────────────────────────────────────────────────────────
-- 8. Результат распознавания
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS recognition_result (
    id              SERIAL PRIMARY KEY,
    session_id      UUID NOT NULL,
    method          VARCHAR(50) NOT NULL,   -- GEOMETRIC / KDE_RF / KDE_DNN / ...
    method_version  VARCHAR(20) NOT NULL DEFAULT '1.0',
    rank            SMALLINT NOT NULL DEFAULT 1,   -- 1 = лучший результат
    predicted_lattice_type_id INT,
    predicted_structure_id    INT,
    confidence      REAL,
    vector_path     VARCHAR(512),
    computed_at     TIMESTAMP DEFAULT NOW(),
    CONSTRAINT uq_result UNIQUE (session_id, method, method_version, rank),
    FOREIGN KEY (session_id) REFERENCES recognition_session(id) ON DELETE CASCADE,
    FOREIGN KEY (predicted_lattice_type_id) REFERENCES lattice_type(id) ON DELETE SET NULL,
    FOREIGN KEY (predicted_structure_id) REFERENCES reference_structure(id) ON DELETE SET NULL
);

-- ─────────────────────────────────────────────────────────────
-- 9. Кэш feature-векторов (KDE и др.)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS feature_vector_cache (
    input_hash   CHAR(64) NOT NULL,   -- SHA-256 нормализованных координат
    params_hash  CHAR(64) NOT NULL,   -- SHA-256 параметров метода (bw, grid_size и др.)
    method_name  VARCHAR(50) NOT NULL,
    vector_path  VARCHAR(512) NOT NULL,
    ion_count    INT NOT NULL,
    computed_at  TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (input_hash, params_hash)
);

-- ─────────────────────────────────────────────────────────────
-- 10. Лог запросов к внешним источникам
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS external_lookup_log (
    id             SERIAL PRIMARY KEY,
    source         lookup_source_t NOT NULL,
    target_type    lookup_target_t NOT NULL,
    target_id      INT NOT NULL,
    query_text     TEXT,
    result_summary TEXT,
    enriched_fields JSONB,   -- {"field": "new_value"}
    http_status    SMALLINT,
    is_successful  BOOLEAN DEFAULT FALSE,
    queried_at     TIMESTAMP DEFAULT NOW()
);
