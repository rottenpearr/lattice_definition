-- Создание базы данных
CREATE DATABASE IF NOT EXISTS crystal_lattice_db;

-- Использование базы данных
USE crystal_lattice_db;

-- Создание таблицы для типов кристаллических решёток
CREATE TABLE IF NOT EXISTS lattice_type (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name_en VARCHAR(255) NOT NULL,
    name_ru VARCHAR(255) NOT NULL,
    description TEXT
);

-- Создание таблицы для веществ
CREATE TABLE IF NOT EXISTS substances (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    cell_length_a FLOAT,
    cell_length_b FLOAT,
    cell_length_c FLOAT,
    cell_volume FLOAT,
    cell_angle_alpha FLOAT,
    cell_angle_beta FLOAT,
    cell_angle_gamma FLOAT,
    space_group_IT_number VARCHAR(255),
    symmetry_space_group_name_Hall VARCHAR(255),
    symmetry_space_group_name_H_M VARCHAR(255),
    lattice_type_id INT NOT NULL,
    FOREIGN KEY (lattice_type_id) REFERENCES lattice_type(id) ON DELETE CASCADE
);

-- Создание таблицы для библиотеки начальных ионов
CREATE TABLE IF NOT EXISTS ions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    substance_id INT NOT NULL,
    atom_site_label VARCHAR(255),
    atom_site_type_symbol VARCHAR(255),
    atom_type_oxidation_number FLOAT,
    atom_site_symmetry_multiplicity INT,
    atom_site_Wyckoff_symbol VARCHAR(10),
    atom_site_occupancy FLOAT,
    atom_site_attached_hydrogens INT,
    atom_site_calc_flag VARCHAR(255),
    FOREIGN KEY (substance_id) REFERENCES substances(id) ON DELETE CASCADE
);

-- Создание таблицы для ионов
CREATE TABLE IF NOT EXISTS ions_library (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lattice_type_id INT NOT NULL,
    substance_id INT NOT NULL,
    atom_site_fract_x DECIMAL(10, 6),
    atom_site_fract_y DECIMAL(10, 6),
    atom_site_fract_z DECIMAL(10, 6),
    atom_site_normalized_x DECIMAL(10, 6),
    atom_site_normalized_y DECIMAL(10, 6),
    atom_site_normalized_z DECIMAL(10, 6),
    FOREIGN KEY (lattice_type_id) REFERENCES lattice_type(id) ON DELETE CASCADE,
    FOREIGN KEY (substance_id) REFERENCES substances(id) ON DELETE CASCADE
);
