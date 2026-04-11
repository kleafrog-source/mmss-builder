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
