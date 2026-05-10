# CRIS — Crystal Recognition & Identification System

Программный комплекс для идентификации типа кристаллической решётки по координатам ионов.

---

## Требования

- Python 3.9+
- MySQL 8.0+ (localhost:3306)
- Зависимости: `pip install -r requirements.txt`

---

## Переменные окружения

Создайте файл `.env` в корне проекта:

```
MP_API_KEY=ваш_ключ_от_materials_project
```

Получить ключ: [next-gen.materialsproject.org/api](https://next-gen.materialsproject.org/api).

Файл `.env` уже добавлен в `.gitignore` — ключ не попадёт в репозиторий.

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
│   ├── testing.py             # Загрузка XYZ с опциональным шумом
│   ├── report.py              # Генерация DOCX-отчёта
│   └── dataset_generation/    # Генерация обучающих датасетов
│       ├── download_structures.py   # Скачать XYZ из Materials Project API
│       ├── crystal_generator.py     # Генератор структур: 14 типов Браве, мотив, шум, вакансии
│       ├── generate_vacancies.py    # Создать варианты с вакансиями
│       ├── generate_all_datasets.py # Пакетная генерация KDE (с resume)
│       ├── generate_dataset.py      # Генерация KDE-датасета для одной структуры
│       └── macrocubic_NaCl.py       # Устаревший генератор NaCl/UN/UC (заменён crystal_generator)
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
│       ├── source/            # Чистые суперячейки — в git
│       └── generated/        # С вакансиями/шумом — .gitignore
├── examples/                  # CSV-примеры для UI — в git
└── kde_arrays/                # KDE-массивы (.gitignore — только локально)
    ├── micro/source/          # KDE от чистых юнит-ячеек
    ├── micro/generated/       # KDE от юнит-ячеек с вакансиями
    ├── macro/source/          # KDE от чистых суперячеек
    └── macro/generated/       # KDE от суперячеек с вакансиями
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

# Интерактивное меню
python cris/tools/dataset_generation/crystal_generator.py --interactive
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

## Задачи

### Текущие

- [ ] Полностью переработать БД в соответствии с новой концепцией
  - [ ] Отдельная таблица с кэшированными результатами распознавания нейросети — вектор ML, а не все KDE
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
- [ ] Сложная часть с закольцовыванием проекта. Переделать пайплайн распознавания так, чтобы результаты нейронки снова попадали в БД
  - [ ] Если вещество уже было распознано — брать вектор из БД, а не пересчитывать. Определить ключ
- [ ] Реализовать ещё один метод ML. Сравнить результаты с текущим RF
  - [ ] Отдельная таблица или поле для каждого метода
- [ ] Сейчас много точек входа — навести порядок, разделить скрипты обучения и распознавания
- [ ] Отдельный скрипт для обучения (Jupyter), отдельный для распознавания по PKL-файлам (для RF) либо отдельно блоками разделить просто
- [ ] Переработка генерации датасета + CatBoost

### Вопросы

- [ ] В CIF-файлах бывает неопределённость в float-значениях (например `0.123(20)`). Как решить?
- [ ] Если результат выдаёт много вариантов (более 10) — выводить все или только топ-N?
- [ ] Какой элемент выделять предпочтительным при одинаковых вероятностях?
- [ ] Достаточно ли точности 6 знаков после запятой?
- [ ] Корректно ли ограничение в 1000 атомов?

### Баги

- [ ] Если база данных не создана, инициализация падает с ошибкой — нужно добавить автосоздание БД
- [ ] Переписать математику на numpy: явные типы данных, оптимизированные вычисления, высокая точность
- [ ] Длинные координаты в названиях графиков — обрезать (низкий приоритет)

### Пути развития

- [ ] Связать элементы в БД с индексами COD
- [ ] 3D-визуализация решёток
- [ ] Автоматическая сортировка файлов по категориям
- [ ] Валидация уникальности при добавлении в БД
- [ ] Добавить аббревиатуру вещества в таблицу `substances`
- [ ] Ионы в `ions_library` не привязаны к типу иона из таблицы `ions` (Na или Cl — неизвестно)
- [ ] Обновить UI, более современный вид
- [ ] Автодокументация (взамен md-файлов)
- [ ] RAG-система по похожим веществам
- [ ] Организовать проект как самостоятельный Python-модуль/библиотеку
