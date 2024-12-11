-- Создание базы данных
CREATE DATABASE IF NOT EXISTS crystal_lattice_db;

-- Использование базы данных
USE crystal_lattice_db;

-- Создание таблицы для типов кристаллических решёток
CREATE TABLE IF NOT EXISTS lattice_type (
    id INT AUTO_INCREMENT PRIMARY KEY,
    crystalline_system VARCHAR(255) NOT NULL,
    lattice_system VARCHAR(255) NOT NULL,
    description TEXT
);

-- Создание таблицы для ионов
CREATE TABLE IF NOT EXISTS ions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lattice_type_id INT NOT NULL,
    x FLOAT NOT NULL,
    y FLOAT NOT NULL,
    z FLOAT NOT NULL,
    FOREIGN KEY (lattice_type_id) REFERENCES lattice_type(id) ON DELETE CASCADE
);

-- Создание таблицы для библиотеки ионов
CREATE TABLE IF NOT EXISTS ion_library (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ion_id INT NOT NULL,
    charge FLOAT NOT NULL,
    FOREIGN KEY (ion_id) REFERENCES ions(id) ON DELETE CASCADE
);

-- Создание таблицы для веществ
CREATE TABLE IF NOT EXISTS substances (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    lattice_type_id INT NOT NULL,
    similarity_coefficient FLOAT,
    FOREIGN KEY (lattice_type_id) REFERENCES lattice_type(id) ON DELETE CASCADE
);
