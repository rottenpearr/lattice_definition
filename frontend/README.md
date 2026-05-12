# CRIS — Web Frontend

Веб-интерфейс CRIS как SPA на React + Babel inline (без сборщика).

## Запуск локально

```bash
cd assets/web_frontend
python -m http.server 3000
```

Открыть в браузере: **http://localhost:3000**

> Нужен интернет — React, Babel и Three.js подключаются через CDN.

## Структура

```
web_frontend/
  index.html            — точка входа
  colors_and_type.css   — дизайн-токены (цвета, типографика)
  styles.css            — UI-стили компонентов
  README.md
  src/
    icons.jsx           — иконки (Icon*)
    atoms.jsx           — Button, Chip, Card, Field, Seg, Eyebrow, Logo
    chrome.jsx          — Header, Footer
    viewer3d.jsx        — Three.js 3D-вьюер решётки
    home.jsx            — главная страница + LatticeDiagram
    workspace.jsx       — рабочее пространство (input → pipeline → result)
    about_docs.jsx      — О проекте, Документация
    app.jsx             — роутер
  assets/
    logo/               — SVG логотипы
    lattices/           — PNG/SVG иллюстрации типов решёток
  preview/              — HTML-превью дизайн-системы (цвета, компоненты, типографика)
```

## Маршруты

| Роут        | Компонент         | Описание                                      |
|-------------|-------------------|-----------------------------------------------|
| `home`      | `HomeScreen`      | Hero, фичи, описание, команда                 |
| `workspace` | `WorkspaceScreen` | Загрузка файла / ввод координат, 3D-вьюер, AI |
| `about`     | `AboutScreen`     | О методах, команда                            |
| `docs`      | `DocsScreen`      | Документация, quick start                     |

## Состояния Workspace

1. **input** — 3D-вьюер сразу показывает введённые ионы в реальном времени
2. **running** — поверх сцены live-пайплайн (имитация 2.4 с)
3. **result** — вердикт, top-5 ранкинг, AI-чат активирован
