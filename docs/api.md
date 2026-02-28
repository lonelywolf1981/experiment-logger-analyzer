# API (MVP)

## Experiments
### POST /experiments
Body:
- name (required)
- stand (optional)
- operator (optional)
- notes (optional)

### GET /experiments
Список экспериментов (created_at desc)

### GET /experiments/{id}
Метаданные эксперимента

### DELETE /experiments/{id}
Удалить эксперимент (в MVP каскадно удаляются точки)

## Import
### POST /experiments/{id}/import
Form-data:
- file (.csv или .jsonl)

Response:
- import_run_id
- inserted
- skipped
- errors

## Channels
### GET /experiments/{id}/channels
Возвращает distinct channels + статистика:
- count/min/max/avg
- first_ts/last_ts

## Series (для графиков)
### GET /experiments/{id}/series
Query:
- channels=TEMP_A&channels=PRESS_1 (repeatable)
- start/end (ISO8601, optional)

Response:
- { channel: [ {timestamp, value}, ... ] }

## Summary
### GET /experiments/{id}/summary
- duration
- total_points
- channels_count
- points_by_quality (если quality есть)

## Export
### GET /experiments/{id}/export.csv
Query:
- channels (optional)
- start/end (optional)
- quality (optional)
Response: text/csv
