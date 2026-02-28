# Архитектура (MVP)

## 1) Компоненты
- FastAPI (routers)
- Service layer:
  - experiment_service (CRUD)
  - import_service (CSV/JSONL парсинг, валидация, статистика)
  - analytics_service (summary, channels stats)
  - export_service (CSV export)
- DB layer (SQLAlchemy)

## 2) Модель данных (минимум)
### Experiment
- id (PK)
- name
- stand (nullable)
- operator (nullable)
- notes (nullable)
- created_at (tz)

### ImportRun
- id (PK)
- experiment_id (FK)
- started_at
- filename
- inserted/skipped/errors

### DataPoint
- id (PK)
- experiment_id (FK)
- import_run_id (FK)
- timestamp (tz, index)
- channel (index)
- value
- unit (nullable)
- quality (nullable, index)
- tag (nullable, index)

## 3) Поток
1) Создали Experiment
2) Загрузили CSV/JSONL -> ImportRun
3) Парсер превращает строки в DataPoint, считает статистику
4) Channels/Series/Summary строятся запросами к DataPoint
5) Export выгружает выборку по фильтрам

## 4) Замечание по масштабу
Для MVP допускается SQLite.
Для реальных объёмов:
- PostgreSQL + (опционально) TimescaleDB
- batch insert и индексы (experiment_id, timestamp, channel)
