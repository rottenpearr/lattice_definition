-- Migration 001: enhance existing tables
USE crystal_lattice_db;

-- Добавляем поля в lattice_type
ALTER TABLE lattice_type
    ADD COLUMN IF NOT EXISTS crystal_system VARCHAR(50) COMMENT 'triclinic/monoclinic/orthorhombic/tetragonal/trigonal/hexagonal/cubic',
    ADD COLUMN IF NOT EXISTS bravais_lattice VARCHAR(10) COMMENT 'P/I/F/C/R',
    ADD COLUMN IF NOT EXISTS space_group_number_min INT COMMENT 'нижняя граница номеров пр. групп',
    ADD COLUMN IF NOT EXISTS space_group_number_max INT COMMENT 'верхняя граница номеров пр. групп',
    ADD COLUMN IF NOT EXISTS point_group VARCHAR(20),
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

-- Добавляем поля в substances (переименованы в reference_structure позже, пока патчим)
ALTER TABLE substances
    ADD COLUMN IF NOT EXISTS formula VARCHAR(100),
    ADD COLUMN IF NOT EXISTS cif_path VARCHAR(512) COMMENT 'относительный путь к .cif файлу',
    ADD COLUMN IF NOT EXISTS xyz_path VARCHAR(512) COMMENT 'относительный путь к .xyz файлу',
    ADD COLUMN IF NOT EXISTS image_path VARCHAR(512) COMMENT 'относительный путь к изображению решётки',
    ADD COLUMN IF NOT EXISTS cod_id INT COMMENT 'ID в Crystallography Open Database',
    ADD COLUMN IF NOT EXISTS mp_id VARCHAR(50) COMMENT 'ID в Materials Project (mp-XXXXX)',
    ADD COLUMN IF NOT EXISTS icsd_id INT COMMENT 'ID в ICSD',
    ADD COLUMN IF NOT EXISTS source_url VARCHAR(1024) COMMENT 'ссылка на источник структуры',
    ADD COLUMN IF NOT EXISTS doi VARCHAR(255) COMMENT 'DOI статьи-источника',
    ADD COLUMN IF NOT EXISTS added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;
