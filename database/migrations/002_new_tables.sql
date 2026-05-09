-- Migration 002: new tables for metadata, recognition cache, enrichment log
USE crystal_lattice_db;

-- ─────────────────────────────────────────────
-- Расширенные метаданные типов решёток
-- (история открытия, авторы, ссылки)
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS lattice_metadata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lattice_type_id INT NOT NULL UNIQUE,
    discoverer VARCHAR(255) COMMENT 'имя(а) первооткрывателей',
    discovery_year SMALLINT,
    discovery_context TEXT COMMENT 'как и при каких условиях открыли',
    wiki_url VARCHAR(1024),
    review_doi VARCHAR(255) COMMENT 'DOI обзорной статьи',
    notes TEXT,
    last_enriched_at TIMESTAMP NULL COMMENT 'когда последний раз обогащали из внешних источников',
    enrichment_source VARCHAR(100) COMMENT 'COD / MP / AI / manual',
    FOREIGN KEY (lattice_type_id) REFERENCES lattice_type(id) ON DELETE CASCADE
);

-- ─────────────────────────────────────────────
-- Сессия распознавания
-- Один запуск = одна сессия, независимо от числа методов
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS recognition_session (
    id CHAR(36) PRIMARY KEY COMMENT 'UUID',
    ion_count INT NOT NULL,
    input_hash CHAR(64) NOT NULL COMMENT 'SHA-256 отнормированных координат',
    xyz_input_path VARCHAR(512) COMMENT 'путь к сохранённому входному файлу, если сохранили',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    INDEX idx_input_hash (input_hash)
);

-- ─────────────────────────────────────────────
-- Результат распознавания одним методом
-- Несколько строк на сессию — по одной на каждый метод и каждую позицию в топе
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS recognition_result (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id CHAR(36) NOT NULL,
    method VARCHAR(50) NOT NULL COMMENT 'KDE_RF / KDE_DNN / GEOMETRIC / ...',
    method_version VARCHAR(20) NOT NULL DEFAULT '1.0',
    rank INT NOT NULL DEFAULT 1 COMMENT '1=лучший результат, 2=второй и тд',
    predicted_lattice_type_id INT COMMENT 'предсказанный тип решётки',
    predicted_substance_id INT COMMENT 'предсказанное вещество',
    confidence FLOAT COMMENT 'уверенность 0..1',
    feature_vector_path VARCHAR(512) COMMENT 'путь к CSV с 1D-вектором признаков',
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_result (session_id, method, method_version, rank),
    FOREIGN KEY (session_id) REFERENCES recognition_session(id) ON DELETE CASCADE,
    FOREIGN KEY (predicted_lattice_type_id) REFERENCES lattice_type(id) ON DELETE SET NULL,
    FOREIGN KEY (predicted_substance_id) REFERENCES substances(id) ON DELETE SET NULL
);

-- ─────────────────────────────────────────────
-- Кэш feature-векторов
-- Ключ: хэш входных координат + хэш параметров метода (bandwidth, grid_size и др.)
-- Позволяет не пересчитывать KDE для повторных входов
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS feature_vector_cache (
    input_hash CHAR(64) NOT NULL COMMENT 'SHA-256 нормализованных координат',
    params_hash CHAR(64) NOT NULL COMMENT 'SHA-256 параметров метода (bandwidth, grid_size и др.)',
    method_name VARCHAR(50) NOT NULL,
    vector_path VARCHAR(512) NOT NULL COMMENT 'путь к .csv файлу с вектором',
    ion_count INT NOT NULL,
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (input_hash, params_hash)
);

-- ─────────────────────────────────────────────
-- Лог запросов к внешним базам данных и AI-поиску
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS external_lookup_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source ENUM('COD', 'MATERIALS_PROJECT', 'ICSD', 'CROSSREF', 'AI_SEARCH', 'MANUAL') NOT NULL,
    target_type ENUM('lattice_type', 'substance') NOT NULL,
    target_id INT NOT NULL COMMENT 'id из lattice_type или substances',
    query_text TEXT COMMENT 'что запросили',
    result_summary TEXT COMMENT 'краткий извлечённый результат',
    enriched_fields JSON COMMENT '{"field": "value"} — что конкретно занесли в БД',
    http_status INT,
    is_successful BOOLEAN DEFAULT FALSE,
    queried_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
