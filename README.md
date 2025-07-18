# Event Hub - Промежуточный слой для бизнес-событий

Event Hub - это прототип сервиса для приема, обработки и распространения бизнес-событий через различные протоколы: REST API, gRPC, GraphQL и Redis Streams.

## 🚀 Возможности

- **REST API** - прием событий через HTTP
- **gRPC** - высокопроизводительный прием событий
- **GraphQL** - запросы и подписки в реальном времени
- **Redis Streams** - очередь сообщений для обработки
- **MongoDB** - хранение событий
- **Агрегированные метрики** - ежеминутная статистика

## 🏗️ Архитектура

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   REST API  │    │   gRPC API  │    │  GraphQL    │
│   (FastAPI) │    │   Server    │    │  Playground │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
                    ┌─────▼─────┐
                    │   Event   │
                    │  Hub      │
                    └─────┬─────┘
                          │
       ┌──────────────────┼──────────────────┐
       │                  │                  │
┌──────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐
│   MongoDB   │    │ Redis Stream│    │  Metrics    │
│  (Storage)  │    │   (Queue)   │    │ Consumer    │
└─────────────┘    └─────────────┘    └─────────────┘
```

## 🛠️ Технологический стек

- **Backend**: FastAPI, gRPC, GraphQL (Strawberry)
- **База данных**: MongoDB (Motor)
- **Очередь**: Redis Streams
- **Контейнеризация**: Docker & Docker Compose
- **CI/CD**: GitHub Actions

## 📋 Требования

- Docker & Docker Compose
- Python 3.11+ (для локальной разработки)

## 🚀 Быстрый старт

### 1. Клонирование и запуск

```bash
git clone <repository-url>
cd event_hub
docker-compose up -d --build
```

### 2. Проверка работы

Откройте в браузере:
- **GraphQL Playground**: http://localhost:8000/graphql
- **API Documentation**: http://localhost:8000/docs

## 📡 Использование API

### REST API (порт 8000)

#### Отправка события
```bash
curl -X POST "http://localhost:8000/events" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "event_type": "purchase",
    "amount": 150.75,
    "timestamp": "2024-01-15T10:30:00Z"
  }'
```

#### Формат события
```json
{
  "user_id": "string",      // ID пользователя
  "event_type": "string",   // Тип события (purchase, return, refund)
  "amount": 0.0,           // Сумма
  "timestamp": "string"    // ISO 8601 формат
}
```

### gRPC API (порт 50051)

#### Использование gRPC клиента
```bash
cd client
python grpc_client.py
```

### GraphQL (порт 8000)

#### Запрос последних событий
```graphql
query {
  lastEvents(limit: 5) {
    id
    userId
    eventType
    amount
    timestamp
  }
}
```

#### Агрегированные метрики
```graphql
query {
  aggregatedMetrics(minutes: 1) {
    totalAmount
    eventCount
    timeWindow
  }
}
```

#### Подписка на события в реальном времени
```graphql
subscription {
  eventStream {
    id
    userId
    eventType
    amount
    timestamp
  }
}
```

## 🧪 Тестирование

### Генератор тестовых событий

```bash
cd client
python event_generator.py
```

### Запуск тестов

```bash
# Локально
pip install pytest pytest-asyncio httpx
pytest tests/ -v

# В Docker
docker-compose exec app pytest tests/ -v
```

## 📊 Мониторинг

### Просмотр логов

```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f app
docker-compose logs -f grpc-server
docker-compose logs -f metrics-consumer
```

### Проверка данных

#### MongoDB
```bash
docker-compose exec mongo mongosh event_hub --eval "db.events.find().pretty()"
```

#### Redis Streams
```bash
docker-compose exec redis redis-cli XRANGE events - +
```

## 🔧 Разработка

### Локальная разработка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Генерируйте protobuf файлы:
```bash
python generate_protos.py
```

3. Запустите сервисы:
```bash
docker-compose up mongo redis -d
uvicorn app.main:app --reload
```

### Структура проекта

```
event_hub/
├── app/
│   ├── api/           # REST API endpoints
│   ├── graphql/       # GraphQL schema
│   ├── grpc/          # gRPC server
│   ├── db/            # Database connections
│   └── models/        # Pydantic models
├── consumer/          # Redis Stream consumers
├── client/            # Test clients
├── protos/            # Protocol Buffers
├── tests/             # Unit tests
└── docker-compose.yml # Infrastructure
```

## 🚀 CI/CD

Проект настроен с GitHub Actions для:
- ✅ Линтинг кода (flake8, black)
- ✅ Запуск тестов
- ✅ Сборка Docker образа
- ✅ Публикация в GitHub Container Registry

## 🔍 Порты

| Сервис | Порт | Описание |
|--------|------|----------|
| FastAPI | 8000 | REST API + GraphQL |
| gRPC | 50051 | gRPC Server |
| MongoDB | 27017 | Database |
| Redis | 6379 | Cache & Streams |

## 🐛 Устранение неполадок

### Перезапуск сервисов
```bash
docker-compose down
docker-compose up -d --build
```

### Очистка данных
```bash
docker-compose down -v
docker-compose up -d
```

### Проверка статуса
```bash
docker-compose ps
```

## 📝 TODO

- [ ] Добавить аутентификацию
- [ ] Реализовать Kafka вместо Redis Streams
- [ ] Добавить Prometheus метрики
- [ ] Расширить тестовое покрытие
- [ ] Добавить документацию API

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch
3. Внесите изменения
4. Добавьте тесты
5. Создайте Pull Request

## 📄 Лицензия

MIT License
   