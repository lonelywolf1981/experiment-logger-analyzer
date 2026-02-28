# Experiment Logger & Analyzer

![CI](https://github.com/lonelywolf1981/experiment-logger-analyzer/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)
![Ruff](https://img.shields.io/badge/linter-ruff-orange)

Веб-инструмент для инженеров и лабораторий: загружаешь файл с данными эксперимента — получаешь графики по каналам, статистику, сводку и экспорт.

---

## Что решает

Когда оборудование пишет данные в CSV или JSONL, сложно быстро ответить на вопросы:
- Что происходило с температурой и давлением в конкретный момент?
- Какой канал выбивается за норму?
- Как выглядит динамика за весь эксперимент?

Experiment Logger решает это без Excel и скриптов: загрузил файл — сразу видишь график, статистику по каналам и сводку.

---

## Для кого

- **Лаборант / R&D инженер** — анализирует каналы измерений, сравнивает режимы работы.
- **Техслужба** — быстро смотрит динамику параметров, ищет момент отклонения.
- **Инженер-аналитик** — выгружает нужные каналы в CSV для отчётов.

---

## Возможности

### MVP (v0.1 — v0.2)
- Создание экспериментов с метаданными: стенд, оператор, заметки
- Импорт данных CSV и JSONL с валидацией и статистикой (`inserted / skipped / errors`)
- Список каналов с базовой статистикой: `count / min / max / avg / first_ts / last_ts`
- Line chart по выбранным каналам через Chart.js — строится прямо в браузере
- Сводка эксперимента: длительность, число точек, каналов, разбивка по качеству
- Экспорт отфильтрованной выборки в CSV (до 5 000 строк)
- История импортов по каждому эксперименту
- Светлая / тёмная тема с сохранением в браузере

---

## Скриншоты

### Список экспериментов — светлая и тёмная тема

<table>
  <tr>
    <td><img src="screenshots/list-light.png" alt="Experiments list — light" width="100%"></td>
    <td><img src="screenshots/list-dark.png" alt="Experiments list — dark" width="100%"></td>
  </tr>
  <tr>
    <td align="center">Светлая тема</td>
    <td align="center">Тёмная тема</td>
  </tr>
</table>

### График по каналам — светлая и тёмная тема

<table>
  <tr>
    <td><img src="screenshots/chart-light.png" alt="Chart — light" width="100%"></td>
    <td><img src="screenshots/chart-dark.png" alt="Chart — dark" width="100%"></td>
  </tr>
  <tr>
    <td align="center">Светлая тема</td>
    <td align="center">Тёмная тема</td>
  </tr>
</table>

### Импорт данных и таблица каналов

<table>
  <tr>
    <td><img src="screenshots/import.png" alt="Import section" width="100%"></td>
    <td><img src="screenshots/channels.png" alt="Channels table" width="100%"></td>
  </tr>
  <tr>
    <td align="center">Импорт CSV / JSONL</td>
    <td align="center">Каналы со статистикой</td>
  </tr>
</table>

---

## Стек

| Слой | Технология |
|---|---|
| Backend | Python 3.11+, FastAPI |
| База данных | SQLite + SQLAlchemy 2.0 |
| Шаблоны | Jinja2 + HTMX |
| Графики | Chart.js 4 + chartjs-adapter-date-fns |
| Тесты | pytest + httpx |
| Линтер | ruff |

---

## Быстрый старт

### 1. Создать виртуальное окружение

```bash
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```

macOS / Linux:
```bash
source .venv/bin/activate
```

### 2. Установить зависимости

```bash
pip install -r requirements.txt
```

### 3. Запустить сервер

```bash
uvicorn app.main:app --reload
```

После запуска открыть: `http://127.0.0.1:8000`

| Адрес | Что открывается |
|---|---|
| `http://127.0.0.1:8000` | Список экспериментов |
| `http://127.0.0.1:8000/ui/experiments/{id}` | Страница эксперимента |
| `http://127.0.0.1:8000/docs` | Swagger / OpenAPI |

---

## Загрузка демо-данных

В репозитории есть готовые файлы:
- `data/sample_experiment.csv` — 10 точек по 5 каналам (TEMP_A, TEMP_B, PRESS_1, POWER_1, STATE)
- `data/sample_experiment.jsonl` — 6 точек в формате JSONL

**Через веб-интерфейс:**
1. Открыть `http://127.0.0.1:8000`
2. Нажать «Создать» — ввести название эксперимента
3. Кликнуть «Открыть» → в разделе «Импорт данных» выбрать `data/sample_experiment.csv`
4. Нажать «Загрузить» — данные появятся в таблице каналов
5. Отметить нужные каналы и нажать «Построить график»

**Через API (curl):**
```bash
# 1. Создать эксперимент
curl -X POST http://127.0.0.1:8000/experiments \
     -H "Content-Type: application/json" \
     -d '{"name": "Demo", "stand": "bench-1", "operator": "tester"}'

# 2. Импортировать CSV (experiment_id из предыдущего ответа)
curl -X POST http://127.0.0.1:8000/experiments/1/import \
     -F "file=@data/sample_experiment.csv"

# 3. Импортировать JSONL
curl -X POST http://127.0.0.1:8000/experiments/1/import \
     -F "file=@data/sample_experiment.jsonl"
```

Формат файлов описан в [`docs/data-format.md`](docs/data-format.md).

---

## Документация

| Документ | Описание |
|---|---|
| [`docs/TZ.md`](docs/TZ.md) | Техническое задание |
| [`docs/architecture.md`](docs/architecture.md) | Архитектура и модель данных |
| [`docs/api.md`](docs/api.md) | Описание всех эндпоинтов |
| [`docs/data-format.md`](docs/data-format.md) | Форматы CSV и JSONL |
| [`docs/decision-log.md`](docs/decision-log.md) | Лог архитектурных решений |
| [`docs/test-plan.md`](docs/test-plan.md) | Чеклист ручного тестирования |
| [`docs/project-defense.md`](docs/project-defense.md) | Защита проекта |
| [`docs/roadmap.md`](docs/roadmap.md) | Планы развития |

---

## Что планируется дальше

### v0.3
- Переход на PostgreSQL / TimescaleDB для больших объёмов
- Downsampling (агрегация по минутам для длинных рядов)
- Сравнение двух экспериментов на одном графике

### v1.0
- Live ingest через API без файлов
- Детект аномалий по порогу / правилу
- Пользователи и роли

---

## Не входит в MVP

- Real-time стриминг (WebSocket)
- Алерты и уведомления
- Сложная аналитика (ML)
- Мультитенантность
