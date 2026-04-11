# Архитектура интеграционного проекта GEPA-Pezzo-MMSS

## Обзор

Этот проект объединяет 5 компонентов в единую систему оптимизации и управления промптами:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ИНТЕГРАЦИОННАЯ ПЛАТФОРМА                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌──────────────┐      ┌──────────────┐      ┌──────────────┐            │
│   │  mmss-builder│──────│   Pezzo      │──────│  GEPA/GEPA-  │            │
│   │  (структуры) │      │(управление)  │      │    MCP       │            │
│   │              │      │  + versioning│      │ (оптимизатор)│            │
│   └──────────────┘      └──────┬───────┘      └──────────────┘            │
│          ▲                       │                                        │
│          │                       ▼                                        │
│          │              ┌──────────────┐                                  │
│          │              │  PostgreSQL  │                                  │
│          │              │  ClickHouse  │                                  │
│          │              │    Redis     │                                  │
│          │              └──────────────┘                                  │
│          │                                                                 │
│   ┌──────┴────────┐                                              ┌────────┴────┐
│   │ prompt-db-    │◄─────────────────────────────────────────────│  Миграции   │
│   │ local (legacy)│                                              │   скрипты   │
│   └───────────────┘                                              └─────────────┘
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Компоненты и их роли

### 1. Pezzo (Центральный слой)
- **Роль**: Централизованное управление промптами, версионирование, observability
- **Запуск**: Docker Compose (self-hosted)
- **API**: GraphQL + REST
- **Хранение**: PostgreSQL + ClickHouse (метрики)

### 2. GEPA / GEPA-MCP (Оптимизатор)
- **Роль**: Эволюционная оптимизация промптов
- **Интеграция**: Через gepa-mcp (MCP протокол) или напрямую как библиотека
- **Формат**: Оптимизация параметров/фрагментов MMSS-структур

### 3. mmss-builder (Структуры)
- **Роль**: Источник сложных JSON-промптов в формате MMSS
- **Формат**: Многоуровневые мета-семантические структуры
- **Интеграция**: Файловый интерфейс + API

### 4. prompt-db-local (Legacy)
- **Роль**: Источник данных для миграции
- **Миграция**: Скрипт конвертации в формат Pezzo/MMSS

## Потоки данных

### Поток 1: Оптимизация MMSS-структуры
```
1. mmss-builder создаёт MMSS-структуру (JSON)
2. Структура загружается в Pezzo как Prompt с метаданными MMSS
3. Сервис optimizer забирает промпт из Pezzo
4. GEPA оптимизирует параметры/фрагменты MMSS
5. Результат сохраняется в Pezzo как новая версия
6. mmss-builder может экспортировать оптимизированную версию
```

### Поток 2: Миграция из prompt-db-local
```
1. Скрипт миграции читает БД prompt-db-local
2. Конвертирует в формат MMSS или напрямую в Pezzo API
3. Загружает в Pezzo с тегами "migrated" + оригинальные метаданные
```

## Файловая структура

```
project/
├── infra/                          # Инфраструктура (Docker)
│   ├── pezzo/
│   │   └── docker-compose.yml      # Pezzo + зависимости
│   ├── postgres/                   # Конфиги PostgreSQL
│   ├── clickhouse/                 # Конфиги ClickHouse
│   └── redis/                      # Конфиги Redis
│
├── services/                       # Микросервисы
│   ├── optimizer/                  # Сервис оптимизации (GEPA)
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── gepa_client.py      # Клиент GEPA/MCP
│   │   │   ├── pezzo_client.py     # Клиент Pezzo API
│   │   │   ├── optimizer.py        # Логика оптимизации
│   │   │   └── api.py              # FastAPI эндпоинты
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── .env.example
│   │
│   └── mmss/                       # MMSS интеграция
│       ├── src/
│       │   ├── __init__.py
│       │   ├── mmss_adapter.py     # Адаптер для MMSS-структур
│       │   ├── pezzo_sync.py       # Синхронизация с Pezzo
│       │   └── api.py              # API для mmss-builder
│       ├── tests/
│       ├── Dockerfile
│       └── requirements.txt
│
├── scripts/                        # Утилиты и скрипты
│   └── migrations/
│       ├── migrate_from_prompt_db.py
│       └── utils.py
│
├── shared/                         # Общие модули
│   ├── types/
│   │   ├── mmss_types.py           # Pydantic модели MMSS
│   │   └── pezzo_types.py          # Pydantic модели Pezzo
│   └── utils/
│       ├── logger.py
│       └── config.py
│
├── examples/                       # Примеры использования
│   └── pipelines/
│       ├── basic_optimization.py
│       └── mmss_to_pezzo.py
│
├── docs/                           # Документация
│   └── architecture/
│       ├── components.md
│       └── flows.md
│
├── docker-compose.yml              # Главный compose (все сервисы)
├── .env.example                    # Пример переменных окружения
└── README.md                       # Этот файл
```

## API Endpoints (планируемые)

### Optimizer Service (`/api/optimizer`)
- `POST /optimize` - Запустить оптимизацию промпта
- `GET /status/{job_id}` - Статус оптимизации
- `POST /optimize-mmss` - Оптимизация MMSS-структуры

### MMSS Service (`/api/mmss`)
- `POST /import` - Импорт MMSS-структуры в Pezzo
- `GET /export/{prompt_id}` - Экспорт промпта в MMSS-формат
- `POST /sync` - Синхронизация с mmss-builder

## Технологический стек

- **Pezzo**: TypeScript/Node.js (готовый образ)
- **Optimizer**: Python 3.11 + FastAPI + GEPA
- **MMSS Adapter**: Python 3.11 + FastAPI
- **Базы**: PostgreSQL 15, ClickHouse, Redis
- **Инфра**: Docker Compose
- **Коммуникация**: REST API, MCP Protocol

## Безопасность

- Все сервисы внутри Docker сети
- API ключи через переменные окружения
- Никаких внешних SaaS зависимостей (self-hosted only)
