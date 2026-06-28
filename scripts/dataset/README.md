# MMSS Fine-tuning Dataset Pipeline

Подготовка JSONL-датасета для Gemma 4 E2B (Kaggle + Unsloth).

## Быстрый запуск

```bash
cd d:\project
pip install pyyaml
python scripts/dataset/run_pipeline.py
```

## Этапы пайплайна

| Шаг | Скрипт | Результат |
|-----|--------|-----------|
| 1 | `scan_inventory.py` | Инвентарь 3050+ файлов, дедупликация, таблица готовности |
| 2 | `extractors.py` + `extractors_stage4.py` | JSONL из ядра MMSS + raw-dataset + архив |
| 3 | `build_jsonl.py` | train/val split по 3 категориям |
| 4 | `validate_jsonl.py` | Проверка схемы Gemma `messages` |

### Источники Этапа 4

| Источник | Экстрактор |
|----------|------------|
| `raw-dataset/` (extract) | `extract_from_raw_dataset` |
| `packages/mmss_meta_core_v6.yaml` | `extract_from_meta_yaml` (512 ops) |
| `architectures/*.json` | `extract_from_architectures` |
| `mmss_core/ai/source_files_done/` | `extract_from_source_archive` |
| `helper_mmss_builder.json` | `extract_from_helper_json` |
| `ready-for-dataset/` | `extract_from_ready_for_dataset` |

## Выходные каталоги

**Staging (mmss-builder):**
```
data/fine-tuning/staging/
├── mmss-universal/
├── mmss-sound-craft/
├── categories/
└── mmss_combined_all.jsonl
```

**Целевой (extract):**
```
D:\WORK\CLIENTS\extract\prepare-for-fine-tuning-dataset-kaggle-gemma\ready-for-dataset\almost_ready\
├── mmss-universal/
├── mmss-sound-craft/
└── categories/
```

## Формат JSONL

```json
{"messages": [
  {"role": "system", "content": "..."},
  {"role": "user", "content": "..."},
  {"role": "model", "content": "..."}
]}
```

## Конфигурация

`scripts/dataset/config.yaml` — пути источников, категории, лимиты.

## Отчёты

```
data/fine-tuning/reports/
├── inventory_latest.json
├── readiness_latest.csv
├── summary_latest.json
└── pipeline_latest.json
```
