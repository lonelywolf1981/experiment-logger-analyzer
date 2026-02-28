# План тестирования (ручной) — MVP

## 1. Запуск
- [ ] Приложение стартует по README.
- [ ] OpenAPI /docs доступен.

## 2. Experiments
- [ ] POST /experiments создаёт эксперимент.
- [ ] GET /experiments показывает созданный.
- [ ] GET /experiments/{id} возвращает метаданные.
- [ ] DELETE /experiments/{id} удаляет эксперимент.

## 3. Import
### CSV
- [ ] импорт sample_experiment.csv: inserted > 0, errors = 0/минимум
- [ ] неверный header -> 400
- [ ] битый timestamp -> errors++
- [ ] битый value -> errors++

### JSONL
- [ ] импорт sample_experiment.jsonl: inserted > 0
- [ ] битая строка JSON -> errors++

## 4. Channels
- [ ] /channels возвращает список каналов
- [ ] статистика min/max/avg/count корректна

## 5. Series
- [ ] /series?channels=TEMP_A&channels=PRESS_1 возвращает массивы точек
- [ ] start/end ограничивают диапазон

## 6. Summary
- [ ] duration и total_points корректны
- [ ] channels_count корректен

## 7. Export
- [ ] export.csv отдаёт CSV с header
- [ ] фильтрация по channel работает
