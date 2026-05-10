# CRIS — Crystal Recognition & Identification System

Программный комплекс для идентификации типа кристаллической решётки по координатам ионов.

---

## Требования

- Python 3.9+
- PostgreSQL 16+ (localhost:5432)
- Зависимости: `pip install -r requirements.txt`

---

## Переменные окружения

Создайте файл `.env` в корне проекта:

```env
# База данных PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=crystal_lattice_db

# Внешние API (опционально — для обогащения данных)
MP_API_KEY=ваш_ключ_от_materials_project
ANTHROPIC_API_KEY=ваш_ключ_claude
```

Ключ Materials Project: [next-gen.materialsproject.org/api](https://next-gen.materialsproject.org/api).  
Ключ Claude AI: [console.anthropic.com](https://console.anthropic.com).

Файл `.env` добавлен в `.gitignore` — ключи не попадут в репозиторий.

---

## Быстрый старт

```bash
# 1. Установить зависимости
pip install -r requirements.txt

# 2. Создать .env файл с параметрами подключения (см. выше)

# 3. Инициализировать схему БД (создаст БД и все таблицы)
python -m cris.db.schema.db_init

# 4. Заполнить справочник типов решёток
python -m cris.db.schema.lattice_types_init

# 5. Запустить приложение
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
│   ├── config.py              # Параметры подключения к PostgreSQL (.env)
│   ├── connection.py          # Пул соединений psycopg2 + get_cursor()
│   ├── queries.py             # Поиск эталонных структур по координатам
│   ├── models.py              # Датаклассы (LatticeType, ReferenceStructure, …)
│   ├── schema/                # SQL-схема и скрипты инициализации
│   ├── repository/            # CRUD: lattice, structure, recognition
│   ├── enrichment/            # Внешние API: COD, Materials Project, Claude AI
│   └── importers/             # Импорт CIF/JSON/XYZ → БД
├── tools/                     # Вспомогательные и исследовательские скрипты
│   ├── enrich_all.py          # Обогащение БД из COD/MP/Claude (CLI)
│   ├── complete_db.py         # Полная инициализация БД одной командой
│   ├── testing.py             # Загрузка XYZ с опциональным шумом
│   ├── report.py              # Генерация DOCX-отчёта
│   └── dataset_generation/    # Генерация обучающих датасетов
│       ├── download_structures.py   # Скачать XYZ из Materials Project API
│       ├── crystal_generator.py     # Генератор структур: 14 типов Браве, мотив, шум, вакансии
│       ├── generate_vacancies.py    # Создать варианты с вакансиями
│       ├── generate_all_datasets.py # Пакетная генерация KDE (с resume)
│       └── generate_dataset.py      # Генерация KDE-датасета для одной структуры
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
├── structures/                # XYZ-структуры
│   ├── micro/                 # Юнит-ячейки (4–80 атомов)
│   │   ├── source/            # Скачанные из MP/CIF — в git
│   │   └── generated/        # С вакансиями/шумом — .gitignore
│   └── macro/                 # Суперячейки NxNxN
│       ├── source/            # Чистые суперячейки — .gitignore (генерируются локально)
│       └── generated/        # С вакансиями/шумом — .gitignore
├── examples/                  # CSV-примеры для UI — в git
└── kde_arrays/                # KDE-массивы (.gitignore — только локально)
    ├── micro/                 # KDE от юнит-ячеек (source + generated)
    └── macro/                 # KDE от суперячеек (source + generated)
```

---

## Генерация датасета

Все скрипты запускаются из корня проекта.

### 1. Скачать структуры из Materials Project

```bash
# 50 урановых соединений (по умолчанию)
python cris/tools/dataset_generation/download_structures.py

# Конкретная формула, другой лимит
python cris/tools/dataset_generation/download_structures.py --formula UN --limit 20
```

Структуры сохраняются в `data/structures/micro/source/`.

### 2. Сгенерировать варианты с вакансиями

```bash
# Все структуры из micro/source/ (5%, 10%, 15%, по 3 варианта)
python cris/tools/dataset_generation/generate_vacancies.py

# Задать уровни вакансий и количество вариантов
python cris/tools/dataset_generation/generate_vacancies.py --rates 0.05 0.10 --variants 5
```

Результат сохраняется в `data/structures/micro/generated/`.

### 3. Сгенерировать синтетические структуры (macro)

```bash
# Список типов решёток и пресетов соединений
python cris/tools/dataset_generation/crystal_generator.py --list

# По готовому пресету (NaCl, UN, UC, UO2, Al, Fe, Cu, CsCl)
python cris/tools/dataset_generation/crystal_generator.py --preset UN --supercell 3
python cris/tools/dataset_generation/crystal_generator.py --preset NaCl --supercell 5

# Одноатомный: FCC алюминий 5x5x5
python cris/tools/dataset_generation/crystal_generator.py --lattice cubic_f --atom Al --a 4.046 --supercell 5

# Многоатомный: произвольный мотив (rock-salt)
python cris/tools/dataset_generation/crystal_generator.py --lattice cubic_f --a 5.64 --motif Na 0 0 0 Cl 0.5 0.5 0.5 --supercell 5

# С шумом и вакансиями, 20 сэмплов, 4 процесса
python cris/tools/dataset_generation/crystal_generator.py --preset UN --supercell 3 --noise 2 --vacancy 0.10 --samples 20 --workers 4

# Примеры разных типов решёток для разнообразного датасета
python cris/tools/dataset_generation/crystal_generator.py --lattice hex_p   --atom Zn --a 2.665 --c 4.947 --supercell 4
python cris/tools/dataset_generation/crystal_generator.py --lattice hex_p   --atom Ti --a 2.951 --c 4.684 --supercell 4
python cris/tools/dataset_generation/crystal_generator.py --lattice tetra_i --atom In --a 3.25  --c 4.95  --supercell 4
python cris/tools/dataset_generation/crystal_generator.py --lattice tetra_p --atom Sn --a 5.83  --c 3.18  --supercell 3
python cris/tools/dataset_generation/crystal_generator.py --lattice ortho_p --atom U  --a 2.85  --b 5.87 --c 4.96  --supercell 3
python cris/tools/dataset_generation/crystal_generator.py --lattice ortho_f --atom S  --a 10.47 --b 12.87 --c 24.49 --supercell 2
python cris/tools/dataset_generation/crystal_generator.py --lattice trig_r  --atom Bi --a 4.75  --alpha 57.3 --supercell 3
python cris/tools/dataset_generation/crystal_generator.py --lattice mono_p  --atom Se --a 9.05  --b 9.07 --c 11.6 --beta 90.8 --supercell 2
```

Результат сохраняется в `data/structures/macro/source/`.

### 4. Сгенерировать KDE-датасеты

```bash
# Все структуры, 400 сэмплов, шум 4% (по умолчанию)
python cris/tools/dataset_generation/generate_all_datasets.py

# Только micro/source, 1000 сэмплов
python cris/tools/dataset_generation/generate_all_datasets.py --source micro/source --samples 1000

# Несколько уровней шума
python cris/tools/dataset_generation/generate_all_datasets.py --noise 2 4 8

# Пересчитать заново
python cris/tools/dataset_generation/generate_all_datasets.py --force
```

KDE-массивы сохраняются в `data/kde_arrays/`. Поддерживается resume — уже сгенерированные итерации пропускаются.

---

## База данных

СУБД: **PostgreSQL 16+**, `localhost:5432`, база `crystal_lattice_db`.  
Параметры подключения — в `.env`, читаются через `cris/db/config.py`.

| Таблица | Содержимое |
|---|---|
| `lattice_type` | Справочник: 8 типов решёток (имя, система, группа Браве, диапазон пр. групп) |
| `lattice_metadata` | История открытия, ссылки — заполняется через внешние API |
| `reference_structure` | Эталонные структуры: параметры ячейки, пути к CIF/XYZ, ID в COD/MP |
| `structure_site` | Позиции ионов: дробные (fract) и нормализованные (norm) координаты |
| `recognition_session` | Сессия распознавания: UUID + SHA-256 хэш входных координат |
| `recognition_result` | Результат по методу: тип решётки, структура, confidence, rank |
| `feature_vector_cache` | Кэш KDE-векторов — не пересчитывать уже виденные входы |
| `external_lookup_log` | Лог запросов к COD / Materials Project / Claude AI |

Пересоздать базу данных:

```bash
# Удалить через psql
psql -U postgres -c "DROP DATABASE IF EXISTS crystal_lattice_db;"

# Заново инициализировать
python -m cris.db.schema.db_init
python -m cris.db.schema.lattice_types_init
```

Обогатить типы решёток из внешних источников:

```bash
python -m cris.tools.enrich_all --lattices          # COD + Claude AI
python -m cris.tools.enrich_all --structures        # Materials Project
python -m cris.tools.enrich_all --lattices --dry-run  # проверить без записи
```

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

## Задачи

### Текущие

- [x] ~~Полностью переработать БД в соответствии с новой концепцией~~
  - [x] ~~Миграция MySQL → PostgreSQL~~
  - [x] ~~Новая схема: 8 таблиц (reference_structure, structure_site, recognition_session/result, feature_vector_cache, external_lookup_log)~~
  - [x] ~~Кэш векторов распознавания (feature_vector_cache)~~
  - [x] ~~Пул соединений psycopg2, репозитории, модели~~
  - [x] ~~Внешнее обогащение: COD API, Materials Project, Claude AI~~
- [ ] Наполнить БД эталонными структурами из `data/db/`
- [ ] Связать ML-пайплайн (RF / CatBoost) с таблицей `recognition_result`
- [ ] Пересобрать структуру проекта, навести порядок в директориях и документациях
  - [x] ~~Определиться с целевой структурой проекта~~
  - [x] ~~Директория RESEARCH — для теории, патентов, документов~~
  - [x] ~~Переработать директорию data: db/, structures/, examples/, generated/~~
  - [x] ~~Придумать куда переместить spectre_diff~~
  - [x] ~~Убрать информацию о VESTA из readme.md~~
  - [x] ~~Перенести всё, что связано с интерфейсом, в assets/~~
  - [x] ~~Гитигнор data/csv_kde и data/generated~~
  - [ ] Улучшить вводное описание проекта в readme.md
  - [ ] Директория ML — пока отдельная папка, revisit позже
- [ ] Сложная часть с закольцовыванием проекта — результаты ML снова в БД
  - [ ] Если вещество уже было распознано — брать вектор из БД, а не пересчитывать
- [ ] Реализовать ещё один метод ML, сравнить с RF
  - [x] ~~CatBoost — добавлен в master~~
  - [ ] Подключить CatBoost к `recognition_result`
- [ ] Навести порядок в точках входа, разделить обучение и распознавание
- [ ] Переработка генерации датасета + унификация пайплайна

### Вопросы

- [ ] В CIF-файлах бывает неопределённость в float-значениях (например `0.123(20)`). Как решить?
- [ ] Если результат выдаёт много вариантов (более 10) — выводить все или только топ-N?
- [ ] Какой элемент выделять предпочтительным при одинаковых вероятностях?
- [ ] Достаточно ли точности 6 знаков после запятой?
- [ ] Корректно ли ограничение в 1000 атомов?

### Баги

- [x] ~~Если база данных не создана, инициализация падает с ошибкой~~ — db_init.py создаёт БД автоматически
- [ ] Переписать математику на numpy: явные типы данных, оптимизированные вычисления, высокая точность
- [ ] Длинные координаты в названиях графиков — обрезать (низкий приоритет)

### Пути развития

- [x] ~~Связать элементы в БД с индексами COD~~ — поле `cod_id` в `reference_structure`
- [ ] 3D-визуализация решёток
- [ ] Автоматическая сортировка файлов по категориям
- [x] ~~Валидация уникальности при добавлении в БД~~ — ON CONFLICT DO NOTHING / RETURNING id
- [ ] Добавить аббревиатуру вещества в `reference_structure`
- [ ] Обновить UI, более современный вид
- [ ] Автодокументация (взамен md-файлов)
- [ ] RAG-система по похожим веществам
- [ ] Организовать проект как самостоятельный Python-модуль/библиотеку
