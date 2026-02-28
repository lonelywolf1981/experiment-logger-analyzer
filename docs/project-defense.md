# Защита проекта (коротко)

## Elevator pitch (30 секунд)
Experiment Logger & Analyzer — инструмент для импорта экспериментальных данных (CSV/JSONL) и быстрого анализа: каналы, графики, сводка, экспорт.

## Демонстрация (3 минуты)
1) Создать эксперимент (POST /experiments)
2) Импортировать sample_experiment.csv (POST /experiments/{id}/import)
3) Открыть /channels и показать список + статистику
4) Открыть /series по 2 каналам и построить график (UI/Plotly)
5) Открыть /summary
6) Экспорт /export.csv по выбранному каналу

## Почему так
- long-format точки (timestamp/channel/value) — универсально для любых экспериментов и каналов
- CSV/JSONL — быстрый и понятный ввод данных
- ImportRun — прозрачность качества данных (inserted/skipped/errors)

## Ограничения MVP
- нет real-time
- нет алертов
- нет авторизации
- SQLite

## Что улучшить первым
- PostgreSQL/Timescale
- downsampling для больших рядов
- сравнение экспериментов
- правила аномалий (threshold)
