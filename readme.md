# Распознавание кристаллических решёток

Программный комплекс для идентификации типа кристаллической решётки по координатам ионов. Пользователь вводит нормализованные координаты атомов вручную или загружает CSV-файл, система выполняет поиск по базе данных и возвращает наиболее вероятные совпадения по типу решётки и веществу. Алгоритм основан на нормализации координат в куб [0, 1] и точном поиске по предварительно рассчитанным значениям в таблице `ions_library`.

---

## Требования

- Python 3.9+
- MySQL 8.0+ (localhost:3306)
- Зависимости: `pip install -r requirements.txt`

---

## Быстрый старт

```bash
# 1. Установить зависимости
pip install -r requirements.txt

# 2. Создать базу данных
# В MySQL CLI:
#   create database crystal_lattice_db;

# 3. Инициализировать базу данных
python cris/tools/complete_db.py

# 4. Запустить приложение
python main.py
```

---

## Структура проекта

```
cris/                          # Основной пакет
├── app/generated/             # Скомпилированные UI-файлы (не редактировать)
├── core/
│   ├── coordinates.py         # Нормализация координат → [0, 1]
│   ├── vectors.py             # Попарные расстояния между ионами
│   ├── spectrum.py            # KDE-спектры (Gaussian)
│   ├── identification.py      # Точка входа в идентификацию
│   └── clustering.py          # Кластеризация структур (UMAP + HDBSCAN)
├── db/
│   ├── config.py              # Параметры подключения к MySQL
│   ├── queries.py             # Поиск по БД
│   ├── schema/                # SQL-схемы и скрипты инициализации
│   └── importers/             # Импорт CIF/JSON/XYZ → БД
├── tools/                     # Вспомогательные и исследовательские скрипты
│   ├── complete_db.py         # Полная инициализация БД одной командой
│   ├── generate_dataset.py    # Генерация датасета KDE-векторов с шумом
│   ├── testing.py             # Загрузка XYZ с опциональным шумом
│   ├── report.py              # Генерация DOCX-отчёта
│   └── ...
└── ...

assets/
├── ui/                        # Исходные .ui файлы (Qt Designer)
├── icons/                     # SVG-иконки
├── images/                    # Изображения типов решёток (PNG/SVG)
└── resources.qrc

ML/                            # Исследовательские скрипты и эксперименты
├── clustering/                # UMAP + HDBSCAN кластеризация
├── spectre_diff/              # Сравнение спектров (Вассерштейн)
└── ...

data/
├── db/                        # Источники базы данных — в git
│   ├── cif/                   # Исходные CIF-файлы
│   ├── json/                  # Конвертированные JSON
│   └── xyz/                   # XYZ-позиции из CIF
├── structures/                # Эталонные XYZ-структуры — в git
│   ├── accurate/              # Идеальные решётки (Materials Project + чистые супер-ячейки)
│   └── inaccurate/            # Структуры с вакансиями и шумом
├── examples/                  # CSV-примеры для UI — в git
└── generated/                 # Сгенерированные данные — только локально (.gitignore)
    ├── datasets/
    │   ├── accurate/          # KDE-датасеты точных структур
    │   └── inaccurate/        # KDE-датасеты с дефектами
    ├── spectra/               # Графики спектров
    └── spectre_diff/          # Данные сравнения спектров
```

---

## База данных

Подключение: `localhost:3306`, пользователь `root`, база `crystal_lattice_db`. Параметры в `cris/db/config.py`.

| Таблица | Содержимое |
|---|---|
| `lattice_type` | Типы решёток (id, name_en, name_ru) |
| `substances` | Вещества с параметрами ячейки (a, b, c, углы, объём, пространственная группа) |
| `ions` | Атомные позиции из CIF (метка, символ, позиция Вайкоффа) |
| `ions_library` | Нормализованные координаты x/y/z — основная таблица поиска |

Пересоздать базу данных:

```sql
drop database crystal_lattice_db;
create database crystal_lattice_db;
```

Затем: `python cris/tools/complete_db.py`

---

## Пересборка UI

После правок `.ui` файлов в `assets/ui/`:

```bash
pyside6-uic assets/ui/Main_Window.ui -o cris/app/generated/Main_Window_ui.py
pyside6-uic assets/ui/Ion_Dialog.ui -o cris/app/generated/Ion_Dialog_ui.py
pyside6-uic assets/ui/Info_Dialog.ui -o cris/app/generated/Info_Dialog_ui.py
pyside6-rcc assets/resources.qrc -o cris/app/generated/resources_rc.py
```

После пересборки `Main_Window_ui.py` заменить `import resources_rc` на `from cris.app.generated import resources_rc`.

---

## Конвертация CIF в JSON (Ubuntu)

```bash
# Один файл
cif_filter file.cif --json-output > file.json

# Все файлы в директории
for file in *.cif; do cif_filter "$file" --json-output | jq '.' > "${file%.cif}.json"; done
```

---

## Известные проблемы

- CIF-файлы с неопределённостью в значениях (например `0.123(20)`) не обрабатываются
- Инициализация БД завершается ошибкой, если база не создана заранее
- Точное сравнение float-координат чувствительно к точности — возможны пропуски совпадений
- Математика в `cris/core/vectors.py` реализована на чистом Python, стоит переписать на numpy
- `cris/core/spectrum.py` зависит от `cris.db.config` — нежелательная зависимость core-слоя от db-слоя

---

## Задачи и вопросы

### Открытые вопросы

- Как обрабатывать неопределённости float в CIF (`0.123(20)`)?
- Выводить все варианты при большом количестве совпадений или только топ-N?
- Как выбирать предпочтительный элемент при одинаковых вероятностях?
- Достаточно ли 6 знаков после запятой для нормализованных координат?
- Корректно ли ограничение в 1000 атомов?

### Пути развития

- Связать элементы в БД с индексами COD
- 3D-визуализация решёток
- Автоматическая сортировка файлов по категориям
- Валидация уникальности при добавлении в БД
- Добавить аббревиатуру вещества в таблицу `substances`
- Обновить UI
