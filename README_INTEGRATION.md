# GEPA-Pezzo-MMSS Integration Project

Интеграционный проект, объединяющий **GEPA** (оптимизатор промптов), **Pezzo** (управление промптами), **mmss-builder** (структуры MMSS) и миграцию из **prompt-db-local**.

## Архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│                     ИНТЕГРАЦИОННАЯ ПЛАТФОРМА                  │
├─────────────────────────────────────────────────────────────────┤
│  Pezzo Console  │  Pezzo Server  │  Optimizer  │  MMSS        │
│   (UI :4200)    │   (API :3001)  │  (:8000)    │  (:8001)     │
└────────┬────────┴────────┬───────┴─────────────┴───────────────┘
         │                 │              │
         └────────┬────────┴──────┬───────┘
                  │               │
              PostgreSQL      Redis
              ClickHouse
```

## Быстрый старт

### 1. Подготовка окружения

```bash
# Скопировать переменные окружения
cp .env.example .env

# Отредактировать .env под свои нужды
# Особое внимание к паролям баз данных
```

### 2. Запуск инфраструктуры

```bash
# Запуск Pezzo + сервисы
docker-compose up -d

# Проверка статуса
docker-compose ps
```

Сервисы будут доступны:
- **Pezzo Console**: http://localhost:4200
- **Pezzo API**: http://localhost:3001
- **Optimizer Service**: http://localhost:8000
- **MMSS Service**: http://localhost:8001

### 3. Ручной запуск сервисов (для разработки)

```bash
# Optimizer Service
cd services/optimizer
pip install -r requirements.txt
python -m uvicorn src.api:app --reload --port 8000

# MMSS Service (в другом терминале)
cd services/mmss
pip install -r requirements.txt
python -m uvicorn src.api:app --reload --port 8001
```

## Запуск MVP (Minimum Viable Product)

MVP демонстрирует end-to-end сценарий: **MMSS → Pezzo → GEPA → Pezzo**

### Требования

- Docker и Docker Compose
- Python 3.11+
- httpx: `pip install httpx`

### Быстрый запуск MVP

```bash
# 1. Запустить Pezzo (PostgreSQL + Pezzo Server + Console)
docker-compose up -d postgres pezzo-server pezzo-console

# 2. Подождать 30 секунд для инициализации БД
sleep 30

# 3. Установить зависимости сервисов
pip install -r services/optimizer/requirements.txt
pip install -r services/mmss/requirements.txt

# 4. Запустить Optimizer Service (в отдельном терминале)
cd services/optimizer
python -m uvicorn src.api:app --host 0.0.0.0 --port 8000

# 5. Запустить MMSS Service (в отдельном терминале)
cd services/mmss
python -m uvicorn src.api:app --host 0.0.0.0 --port 8001

# 6. Запустить MVP пайплайн (в третьем терминале)
cd examples/pipelines
python mvp_mmss_to_pezzo.py
```

### Ожидаемый вывод

```
============================================================
MVP: MMSS → Pezzo → GEPA → Pezzo
============================================================

=== Проверка сервисов ===
  ✓ Pezzo API доступен
  ✓ Optimizer Service доступен
  ✓ MMSS Service доступен

=== Шаг 1: MMSS → Pezzo ===
Создаем промпт из пакета: MVP_CODE_REVIEW_PROMPT
  ✓ Создан промпт в Pezzo: MVP_CODE_REVIEW_PROMPT
  ✓ ID: <uuid>
  ✓ Операций: 3

=== Шаг 2: Оптимизация через GEPA ===
Запускаем оптимизацию: MVP_CODE_REVIEW_PROMPT
  ✓ Job ID: <uuid>
  ✓ Статус: completed
  ✓ Fitness Score: 0.85
  ✓ Итераций: 20
  ✓ Улучшения (3):
      1. Added clarity markers [OPTIMIZED]
      2. Enhanced structure with section headers
      3. Improved formatting for readability

=== Шаг 3: Проверка в Pezzo ===
Проверяем версии промпта: MVP_CODE_REVIEW_PROMPT
  ✓ Найден промпт: MVP_CODE_REVIEW_PROMPT
  ✓ Версий: 2
      1. a1b2c3d4 - Initial version
      2. e5f6g7h8 - GEPA optimization: fitness=0.850

============================================================
✅ MVP УСПЕШНО ЗАВЕРШЕН
============================================================

📊 Результаты:
   • Промпт в Pezzo: MVP_CODE_REVIEW_PROMPT
   • ID: <uuid>
   • Job ID: <uuid>

🌐 Интерфейсы:
   • Pezzo Console: http://localhost:4200
   • Pezzo API: http://localhost:3001
   • Optimizer API: http://localhost:8000
```

### Важно: GEPA не требуется для MVP!

Optimizer Service имеет **mock-режим** — если GEPA-MCP сервер недоступен, он автоматически использует упрощенную оптимизацию для демонстрации workflow.

Для использования реального GEPA:
1. Установите и запустите `gepa-mcp` сервер на порту 3003
2. Или укажите `GEPA_MCP_SERVER_URL` в `.env`

## API Endpoints

### Optimizer Service (`http://localhost:8000`)

| Endpoint | Method | Описание |
|----------|--------|----------|
| `/health` | GET | Проверка здоровья сервиса |
| `/optimize` | POST | Запустить оптимизацию промпта |
| `/optimize-mmss` | POST | Оптимизировать MMSS-структуру |
| `/jobs/{id}` | GET | Статус задачи оптимизации |
| `/jobs` | GET | Список задач |

### MMSS Service (`http://localhost:8001`)

| Endpoint | Method | Описание |
|----------|--------|----------|
| `/health` | GET | Проверка здоровья сервиса |
| `/import` | POST | Импорт MMSS в Pezzo |
| `/export/{id}` | POST | Экспорт из Pezzo в MMSS |
| `/load-file` | POST | Загрузить MMSS из файла |
| `/sync` | POST | Синхронизировать директорию |
| `/optimize` | POST | Оптимизация MMSS через GEPA |

## Примеры использования

### Базовая оптимизация промпта

```bash
# Запуск примера
cd examples/pipelines
python basic_optimization.py
```

### MMSS → Pezzo → Оптимизация → MMSS

```bash
# Запуск полного пайплайна
python mmss_to_pezzo.py
```

### Миграция из prompt-db-local

```bash
# Сухой прогон (без записи)
python scripts/migrations/migrate_from_prompt_db.py \
    ./prompt-db-local \
    --dry-run

# Реальная миграция
python scripts/migrations/migrate_from_prompt_db.py \
    ./prompt-db-local \
    --convert-to-mmss
```

## Структура проекта

```
project/
├── infra/
│   └── pezzo/
│       └── docker-compose.yml      # Pezzo + PostgreSQL + ClickHouse + Redis
│
├── services/
│   ├── optimizer/                    # GEPA Optimizer Service
│   │   ├── src/
│   │   │   ├── api.py                # FastAPI endpoints
│   │   │   ├── gepa_client.py        # Клиент GEPA/MCP
│   │   │   ├── pezzo_client.py       # Клиент Pezzo API
│   │   │   └── optimizer.py          # Логика оптимизации
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   └── mmss/                         # MMSS Integration Service
│       ├── src/
│       │   ├── api.py                # FastAPI endpoints
│       │   ├── mmss_adapter.py       # Адаптер MMSS-структур
│       │   └── pezzo_sync.py         # Синхронизация с Pezzo
│       ├── Dockerfile
│       └── requirements.txt
│
├── scripts/
│   └── migrations/
│       └── migrate_from_prompt_db.py # Скрипт миграции
│
├── examples/
│   └── pipelines/
│       ├── basic_optimization.py     # Базовая оптимизация
│       └── mmss_to_pezzo.py          # Полный пайплайн
│
├── docker-compose.yml                # Главный compose-файл
├── .env.example                      # Пример переменных окружения
├── ARCHITECTURE.md                   # Документация архитектуры
└── README_INTEGRATION.md             # Этот файл
```

## Конфигурация

### Переменные окружения

| Переменная | Описание | Значение по умолчанию |
|------------|----------|----------------------|
| `POSTGRES_PASSWORD` | Пароль PostgreSQL | `pezzo_password` |
| `CLICKHOUSE_PASSWORD` | Пароль ClickHouse | `pezzo_password` |
| `REDIS_PASSWORD` | Пароль Redis | `pezzo_password` |
| `PEZZO_API_KEY` | API ключ Pezzo | - |
| `GEPA_MCP_SERVER_URL` | URL GEPA-MCP сервера | `http://localhost:3003` |
| `GEPA_OPTIMIZATION_ITERATIONS` | Итерации оптимизации | `50` |
| `GEPA_POPULATION_SIZE` | Размер популяции GEPA | `20` |

## Разработка

### Локальный запуск для разработки

```bash
# 1. Запустить только инфраструктуру
docker-compose up -d postgres clickhouse redis pezzo-server pezzo-console

# 2. Запустить сервисы вручную (с hot-reload)
cd services/optimizer && python -m uvicorn src.api:app --reload
cd services/mmss && python -m uvicorn src.api:app --reload --port 8001
```

### Тестирование

```bash
# Optimizer Service
cd services/optimizer
pytest tests/

# MMSS Service
cd services/mmss
pytest tests/
```

## Интеграция с GEPA-MCP

Для работы оптимизатора требуется запущенный GEPA-MCP сервер:

```bash
# Установка gepa-mcp (если доступен как пакет)
pip install gepa-mcp

# Запуск MCP сервера
gepa-mcp-server --port 3003
```

Или через Docker (при наличии образа):

```yaml
# docker-compose.yml - раскомментировать секцию gepa-mcp
  gepa-mcp:
    build:
      context: ./vendor/gepa-mcp
      dockerfile: Dockerfile
    ports:
      - "3003:3003"
```

## Roadmap

- [x] Базовая инфраструктура Pezzo
- [x] Optimizer Service с клиентами GEPA и Pezzo
- [x] MMSS Service с адаптером и синхронизацией
- [x] Скрипт миграции из prompt-db-local
- [x] Примеры пайплайнов
- [ ] Интеграционные тесты
- [ ] Web UI для управления пайплайнами
- [ ] Поддержка батчевой оптимизации
- [ ] Метрики и мониторинг

## Лицензия

MIT (соответствует лицензиям компонентов)

## Контакты

- **Pezzo**: https://docs.pezzo.ai
- **GEPA**: https://github.com/gepa-ai/gepa
- **GEPA-MCP**: https://github.com/developzir/gepa-mcp
