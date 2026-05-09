-- Полная новая схема. Запускать на чистой БД.
CREATE DATABASE IF NOT EXISTS crystal_lattice_db;
USE crystal_lattice_db;

-- ─────────────────────────────────────────────────────────────
-- 1. Типы кристаллических решёток (справочник)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS lattice_type (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name_en     VARCHAR(100) NOT NULL,
    name_ru     VARCHAR(100) NOT NULL,
    crystal_system   VARCHAR(50)  COMMENT 'triclinic/monoclinic/orthorhombic/tetragonal/trigonal/hexagonal/cubic',
    bravais_lattice  VARCHAR(10)  COMMENT 'P/I/F/C/R',
    point_group      VARCHAR(20),
    sg_number_min    SMALLINT     COMMENT 'нижняя граница номеров пр. групп ITA',
    sg_number_max    SMALLINT     COMMENT 'верхняя граница номеров пр. групп ITA',
    description      TEXT
);

-- ─────────────────────────────────────────────────────────────
-- 2. Метаданные типа решётки
--    (история открытия, ссылки — обогащается через внешние API)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS lattice_metadata (
    lattice_type_id  INT PRIMARY KEY,
    discoverer       VARCHAR(255) COMMENT 'имя(а) первооткрывателей',
    discovery_year   SMALLINT,
    discovery_context TEXT        COMMENT 'как и при каких условиях открыли',
    wiki_url         VARCHAR(1024),
    review_doi       VARCHAR(255) COMMENT 'DOI обзорной статьи',
    notes            TEXT,
    enriched_at      TIMESTAMP NULL,
    enrichment_source VARCHAR(50) COMMENT 'AI / COD / MP / manual',
    FOREIGN KEY (lattice_type_id) REFERENCES lattice_type(id) ON DELETE CASCADE
);

-- ─────────────────────────────────────────────────────────────
-- 3. Эталонные структуры (вещества)
--    Заменяет старую таблицу substances.
--    Хранит параметры ячейки + ссылки на файлы + внешние ID.
--    Тяжёлые данные (CIF/XYZ/KDE) остаются файлами.
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS reference_structure (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(255) NOT NULL,
    formula      VARCHAR(100),
    lattice_type_id INT NOT NULL,

    -- параметры элементарной ячейки
    cell_length_a  FLOAT,
    cell_length_b  FLOAT,
    cell_length_c  FLOAT,
    cell_volume    FLOAT,
    cell_angle_alpha FLOAT,
    cell_angle_beta  FLOAT,
    cell_angle_gamma FLOAT,

    -- пространственная группа
    sg_number      SMALLINT,
    sg_hall        VARCHAR(100),
    sg_hm          VARCHAR(100),

    -- пути к файлам (относительно корня проекта)
    cif_path       VARCHAR(512) COMMENT 'data/db/cif/...',
    xyz_path       VARCHAR(512) COMMENT 'data/db/xyz/...',
    image_path     VARCHAR(512) COMMENT 'assets/images/...',

    -- внешние идентификаторы
    cod_id         INT          COMMENT 'Crystallography Open Database',
    mp_id          VARCHAR(50)  COMMENT 'Materials Project: mp-XXXXX',
    icsd_id        INT          COMMENT 'ICSD',
    doi            VARCHAR(255),
    source_url     VARCHAR(1024),

    added_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (lattice_type_id) REFERENCES lattice_type(id) ON DELETE CASCADE
);

-- ─────────────────────────────────────────────────────────────
-- 4. Позиции ионов в эталонных структурах
--    Заменяет ions + ions_library — всё в одной таблице.
--    fract_* — дробные координаты из CIF
--    norm_*  — нормализованные [0,1] координаты для поиска
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS structure_site (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    structure_id INT NOT NULL,

    -- из CIF (ions)
    atom_label   VARCHAR(50)  COMMENT 'e.g. Na1, Cl2',
    atom_symbol  VARCHAR(10)  COMMENT 'e.g. Na, Cl, U',
    oxidation    FLOAT,
    multiplicity SMALLINT,
    wyckoff      VARCHAR(10),
    occupancy    FLOAT DEFAULT 1.0,

    -- координаты
    fract_x      DECIMAL(12, 8),
    fract_y      DECIMAL(12, 8),
    fract_z      DECIMAL(12, 8),
    norm_x       DECIMAL(12, 8) COMMENT 'нормализованные [0,1]',
    norm_y       DECIMAL(12, 8),
    norm_z       DECIMAL(12, 8),

    FOREIGN KEY (structure_id) REFERENCES reference_structure(id) ON DELETE CASCADE,
    INDEX idx_norm (norm_x, norm_y, norm_z),
    INDEX idx_structure (structure_id)
);

-- ─────────────────────────────────────────────────────────────
-- 5. Сессия распознавания
--    Один запуск = одна сессия, независимо от числа методов.
--    input_hash — SHA-256 нормализованных координат.
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS recognition_session (
    id           CHAR(36) PRIMARY KEY    COMMENT 'UUID',
    ion_count    INT NOT NULL,
    input_hash   CHAR(64) NOT NULL       COMMENT 'SHA-256 отсортированных нормализованных координат',
    xyz_path     VARCHAR(512)            COMMENT 'путь к сохранённому входному файлу (опционально)',
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes        TEXT,
    INDEX idx_hash (input_hash)
);

-- ─────────────────────────────────────────────────────────────
-- 6. Результат распознавания
--    Одна строка = один метод + одна позиция в топе предсказаний.
--    Уникальность: (session_id, method, method_version, rank).
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS recognition_result (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    session_id      CHAR(36) NOT NULL,
    method          VARCHAR(50) NOT NULL   COMMENT 'GEOMETRIC / KDE_RF / KDE_DNN / ...',
    method_version  VARCHAR(20) NOT NULL DEFAULT '1.0',
    rank            TINYINT NOT NULL DEFAULT 1 COMMENT '1 = лучший результат',
    predicted_lattice_type_id INT,
    predicted_structure_id    INT,
    confidence      FLOAT                  COMMENT '0..1',
    vector_path     VARCHAR(512)           COMMENT 'путь к CSV с 1D feature-вектором',
    computed_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_result (session_id, method, method_version, rank),
    FOREIGN KEY (session_id) REFERENCES recognition_session(id) ON DELETE CASCADE,
    FOREIGN KEY (predicted_lattice_type_id) REFERENCES lattice_type(id) ON DELETE SET NULL,
    FOREIGN KEY (predicted_structure_id) REFERENCES reference_structure(id) ON DELETE SET NULL
);

-- ─────────────────────────────────────────────────────────────
-- 7. Кэш feature-векторов
--    PK = (input_hash, params_hash) — один вход + одни параметры → один вектор.
--    Позволяет не пересчитывать KDE для уже виденных координат.
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS feature_vector_cache (
    input_hash   CHAR(64) NOT NULL  COMMENT 'SHA-256 нормализованных координат',
    params_hash  CHAR(64) NOT NULL  COMMENT 'SHA-256 параметров метода (bandwidth, grid_size и др.)',
    method_name  VARCHAR(50) NOT NULL,
    vector_path  VARCHAR(512) NOT NULL,
    ion_count    INT NOT NULL,
    computed_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (input_hash, params_hash)
);

-- ─────────────────────────────────────────────────────────────
-- 8. Лог запросов к внешним источникам
--    Полная история обращений к COD / MP / AI.
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS external_lookup_log (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    source        ENUM('COD','MATERIALS_PROJECT','ICSD','CROSSREF','AI_SEARCH','MANUAL') NOT NULL,
    target_type   ENUM('lattice_type','reference_structure') NOT NULL,
    target_id     INT NOT NULL,
    query_text    TEXT,
    result_summary TEXT,
    enriched_fields JSON COMMENT '{"field": "new_value"} — что занесли в БД',
    http_status   SMALLINT,
    is_successful BOOLEAN DEFAULT FALSE,
    queried_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
