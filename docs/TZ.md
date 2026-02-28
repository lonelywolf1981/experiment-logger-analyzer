# ТЗ: Experiment Data Logger & Analyzer (MVP)

## 1. Цель
Создать веб-инструмент для хранения и анализа экспериментальных данных:
- импорт из файлов (CSV/JSONL),
- хранение в БД,
- графики по каналам,
- сводка по эксперименту,
- экспорт результатов.

## 2. Целевая аудитория
- Лаборатория / R&D инженер: анализ каналов измерений, сравнение режимов.
- Техслужба: диагностика отклонений, быстрый просмотр временного ряда.
- Инженер-аналитик: выгрузка в CSV для отчётов.

## 3. Область MVP
### Входит
- CRUD экспериментов (минимально: create/list/get/delete).
- Импорт данных в эксперимент (CSV/JSONL).
- Список каналов по эксперименту.
- График (line chart) по выбранным каналам.
- Summary по эксперименту и по каналам.
- Экспорт CSV с фильтрами.

### Не входит
- real-time ingest (стриминг, сокеты)
- алерты
- авторизация/роли
- сравнение экспериментов (можно в roadmap)

## 4. Сущности (минимум)
- **Experiment**: метаданные эксперимента (название, стенд, оператор, время, комментарии)
- **DataPoint**: точка измерения (timestamp, channel, value, unit, quality, tag)
- **ImportRun**: запуск импорта файла (статистика inserted/skipped/errors)

> Channel как отдельную таблицу в MVP можно не делать — каналы выводим через distinct(channel).

## 5. Форматы данных
Поддержать:
- CSV (строгий header)
- JSONL (1 JSON на строку)

Единая схема полей:
- timestamp (ISO8601)
- channel (например TEMP_A, PRESS_1)
- value (float)
- unit (C, bar, V, Hz, W и т.п.) — опционально
- quality (OK/WARN/BAD) — опционально
- tag (temp/pressure/power/voltage/phase и т.п.) — опционально

Подробно: `data-format.md`.

## 6. Функциональные требования

### 6.1. Эксперименты
- Создать эксперимент: name, stand, operator, notes (все строки, кроме name — optional)
- Список экспериментов с сортировкой по created_at desc
- Получить эксперимент по id
- Удалить эксперимент (в MVP допускается каскадное удаление datapoints)

### 6.2. Импорт
Загрузка файла в конкретный эксперимент.
Единые правила:
- Пустые timestamp/channel/value -> skipped
- timestamp не парсится -> errors
- value не парсится -> errors
- unit/quality/tag могут отсутствовать
- Итог: inserted/skipped/errors + import_run_id

CSV header строго:
`timestamp,channel,value,unit,quality,tag`

### 6.3. Каналы
- Вернуть список каналов эксперимента (distinct channel) + базовая статистика:
  - count, min, max, avg
  - first_ts, last_ts

### 6.4. График
- Получить series для выбранных каналов и диапазона времени:
  - channels[]=TEMP_A&channels[]=PRESS_1
  - start/end optional
  - downsample optional (для MVP можно отключить)

### 6.5. Summary
- Summary эксперимента:
  - duration (last-first)
  - total_points
  - channels_count
  - points_by_quality (если quality есть)
- Summary канала:
  - min/max/avg/count
  - missing/invalid (если считаем)

### 6.6. Экспорт
- Экспорт CSV для эксперимента с фильтрами (channels, start/end, quality).

## 7. Нефункциональные требования
- Быстрый запуск локально.
- Прозрачные ошибки формата файлов.
- Код: router/service/model, без монолита.
- Документация: decision-log + defense обязательны.

## 8. Критерии приёмки (Definition of Done)
Проект готов для портфолио если:
1) Запускается локально по простой инструкции.
2) Можно создать эксперимент и импортировать демо-файл.
3) Видны каналы эксперимента и базовая статистика по ним.
4) Строится график минимум по 2 каналам.
5) Есть summary по эксперименту.
6) Экспорт CSV работает.
7) В репозитории есть документы:
   TZ/architecture/api/data-format/test-plan/decision-log/project-defense/roadmap.
