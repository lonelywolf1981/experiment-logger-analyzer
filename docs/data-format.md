# Формат данных эксперимента

## Единые поля события DataPoint
- timestamp: ISO8601 (например `2026-02-28T21:06:00+05:00`)
- channel: строка (например `TEMP_A`, `PRESS_1`)
- value: float
- unit: строка (optional), например `C`, `bar`, `V`, `Hz`, `W`
- quality: `OK|WARN|BAD` (optional)
- tag: строка (optional), например `temp`, `pressure`, `power`

## CSV
- UTF-8
- Разделитель `,`
- Header строго:
  `timestamp,channel,value,unit,quality,tag`

Пример:
```csv
timestamp,channel,value,unit,quality,tag
2026-02-28T21:06:00+05:00,TEMP_A,3.125,C,OK,temp
2026-02-28T21:06:00+05:00,PRESS_1,1.023,bar,OK,pressure
```

## JSONL
- UTF-8
- 1 JSON-объект на строку
- пустые строки игнорируются

Пример:
```jsonl
{"timestamp":"2026-02-28T21:06:00+05:00","channel":"TEMP_A","value":3.125,"unit":"C","quality":"OK","tag":"temp"}
{"timestamp":"2026-02-28T21:06:00+05:00","channel":"PRESS_1","value":1.023,"unit":"bar","quality":"OK","tag":"pressure"}
```

## Правила валидации (MVP)
- timestamp/channel/value обязательны
- channel не пустой
- value должен быть числом
- quality если задан — привести к upper и принять только OK/WARN/BAD, иначе:
  - для MVP: считать skipped (или нормализовать в OK). Рекомендуется skipped.
