# 🚀 Event Hub

**Полнофункциональная система обработки событий** с поддержкой REST API, gRPC, GraphQL, JWT авторизацией, мониторингом и надежной доставкой сообщений.

## 📋 Содержание

- [Возможности](#-возможности)
- [Архитектура](#-архитектура)
- [Быстрый старт](#-быстрый-старт)
- [Авторизация](#-авторизация)
- [API Endpoints](#-api-endpoints)
- [Метрики и трейсинг](#-метрики-и-трейсинг)
- [Надежная доставка](#-надежная-доставка)
- [Тестирование](#-тестирование)
- [Развертывание](#-развертывание)
- [Разработка](#-разработка)

## ✨ Возможности

- 🔐 **JWT авторизация** с ролями reader/writer
- 🌐 **REST API** на FastAPI
- 🔌 **gRPC сервер** для микросервисов
- 📊 **GraphQL** для гибких запросов
- 📈 **Prometheus метрики** и мониторинг
- 🔍 **OpenTelemetry трейсинг** с Jaeger
- 💾 **MongoDB** для хранения событий
- 🚀 **Redis** для очередей сообщений
- 🔄 **Надежная доставка** с retry и DLQ
- 🧪 **Интеграционные тесты**
- 📊 **Нагрузочное тестирование** с Locust
- ☸️ **Helm чарт** для Kubernetes
- 🔄 **CI/CD** с GitHub Actions

## 🏗️ Архитектура

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │  gRPC Server    │    │ Metrics Consumer│
│   (Port 8000)   │    │  (Port 50051)   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     MongoDB     │    │      Redis      │    │    Prometheus   │
│   (Port 27017)  │    │   (Port 6379)   │    │   (Port 9090)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                              ┌─────────────────┐
                                              │     Jaeger      │
                                              │   (Port 16686)  │
                                              └─────────────────┘
```

## 🚀 Быстрый старт

### Предварительные требования

- Docker Desktop
- Python 3.11+
- Git

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd event_hub
```

### 2. Запуск через Docker

```bash
# Запуск всех сервисов
docker-compose up -d --build

# Проверка статуса
docker ps
```

### 3. Проверка доступности

```bash
# FastAPI документация
curl http://localhost:8000/docs

# Prometheus
curl http://localhost:9090

# Jaeger UI
curl http://localhost:16686
```

## 🔐 Авторизация

### Генерация JWT токенов

```bash
# Валидный токен для writer
python issue_token.py --role writer

# Валидный токен для reader
python issue_token.py --role reader

# Просроченный токен
python issue_token.py --role writer --expired
```

### Пример использования

```bash
# Получение токена
TOKEN=$(python issue_token.py --role writer | grep "Bearer" | cut -d' ' -f2)

# Отправка события с авторизацией
curl -X POST http://localhost:8000/events \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "user_action",
    "user_id": "user123",
    "amount": 100,
    "timestamp": "2025-07-25T12:00:00Z",
    "data": {"action": "login", "ip": "192.168.1.1"}
  }'
```

## 📡 API Endpoints

### REST API (FastAPI)

| Метод | Endpoint | Описание | Авторизация |
|-------|----------|----------|-------------|
| POST | `/events` | Создание события | Writer |
| GET | `/events` | Получение событий | Reader |
| GET | `/metrics` | Prometheus метрики | - |
| GET | `/docs` | Swagger документация | - |

### gRPC

```protobuf
service EventService {
  rpc CreateEvent(CreateEventRequest) returns (CreateEventResponse);
  rpc GetEvents(GetEventsRequest) returns (GetEventsResponse);
}
```

### GraphQL

```graphql
type Event {
  id: ID!
  event_type: String!
  user_id: String!
  amount: Float!
  timestamp: String!
  data: JSON!
}

type Query {
  events(limit: Int, offset: Int): [Event!]!
  event(id: ID!): Event
}
```

## 📊 Метрики и трейсинг

### Prometheus метрики

- `http_requests_total` - общее количество HTTP запросов
- `events_ingested_total` - количество обработанных событий
- `queue_lag` - задержка в очереди
- `mongo_ops_total` - операции с MongoDB

### Доступ к метрикам

```bash
# Prometheus UI
http://localhost:9090

# Grafana Dashboard
# Импортируйте docs/grafana_dashboard.json
```

### OpenTelemetry трейсинг

- Трейс `persist_event` для операций сохранения
- Интеграция с Jaeger
- Автоматическая инструментация FastAPI, gRPC, MongoDB, Redis

### Доступ к трейсам

```bash
# Jaeger UI
http://localhost:16686
```

## 🔄 Надежная доставка

### Retry механизм

- Тройной retry с экспоненциальным back-off
- Dead Letter Queue (DLQ) для неудачных сообщений
- CLI команда для восстановления из DLQ

### Управление DLQ

```bash
# Восстановление сообщений из DLQ за последние 2 часа
python manage.py replay-dlq --since 2h

# Просмотр сообщений в DLQ
python manage.py list-dlq
```

## 🧪 Тестирование

### Интеграционные тесты

```bash
# Запуск тестов
pytest tests/ -v

# Тесты с покрытием
pytest tests/ --cov=app --cov-report=html -v
```

### Нагрузочное тестирование

```bash
# Запуск Locust
locust -f locustfile.py --host=http://localhost:8000

# Headless режим (500 RPS, 2 минуты)
locust -f locustfile.py --headless -u 500 -r 50 --run-time 2m --html docs/locust_report.html
```

### Результаты тестирования

- ✅ Процент ошибок ≤ 1%
- ✅ p95 время ответа < 200ms
- ✅ 1000 событий успешно обработаны
- 📊 Отчет в `docs/locust_report.html`

## ☸️ Развертывание

### Helm чарт

```bash
# Установка в Kubernetes
helm install event-hub ./chart

# Обновление
helm upgrade event-hub ./chart

# Удаление
helm uninstall event-hub
```

### Компоненты Helm чарта

- **Deployment** - основное приложение
- **Service** - сетевой доступ
- **ConfigMap** - конфигурация и JWT ключи
- **HPA** - горизонтальное масштабирование по CPU
- **ServiceAccount** - права доступа

### Переменные окружения

```yaml
# values.yaml
replicaCount: 3
image:
  repository: event-hub
  tag: latest
resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 500m
    memory: 512Mi
```

## 🔄 CI/CD

### GitHub Actions

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - lint → tests → build → push → helm-lint
```

### Этапы CI/CD

1. **Lint** - проверка кода (flake8, black)
2. **Tests** - запуск тестов с покрытием
3. **Build** - сборка Docker образа
4. **Push** - публикация образа в registry
5. **Helm Lint** - проверка Helm чарта

## 🛠️ Разработка

### Установка зависимостей

```bash
pip install -r requirements.txt
```

### Локальная разработка

```bash
# Запуск в режиме разработки
python run_dev.py

# Генерация protobuf файлов
python generate_protos.py
```

### Структура проекта

```
event_hub/
├── app/                    # Основное приложение
│   ├── auth/              # JWT авторизация
│   ├── api/               # REST API
│   ├── grpc/              # gRPC сервер
│   ├── graphql/           # GraphQL схема
│   ├── metrics/           # Prometheus + OpenTelemetry
│   ├── queue/             # Надежная доставка
│   └── models/            # Модели данных
├── consumer/              # Потребители сообщений
├── client/                # Клиентские утилиты
├── tests/                 # Тесты
├── chart/                 # Helm чарт
├── docs/                  # Документация
├── docker-compose.yml     # Docker Compose
├── Dockerfile            # Docker образ
├── requirements.txt      # Python зависимости
├── issue_token.py        # JWT токены
├── locustfile.py         # Нагрузочное тестирование
└── manage.py             # CLI утилиты
```

### Команды Make

```bash
# Установка зависимостей
make install

# Запуск тестов
make test

# Линтинг кода
make lint

# Форматирование кода
make format

# Запуск Docker сервисов
make docker-up

# Остановка Docker сервисов
make docker-down
```

## 📈 Мониторинг и алерты

### Grafana Dashboard

Импортируйте `docs/grafana_dashboard.json` в Grafana для получения:

- Графики HTTP запросов
- Метрики событий
- Задержки очередей
- Операции MongoDB

### Алерты

Настройте алерты в Prometheus для:

- Высокого процента ошибок (> 1%)
- Больших задержек очереди
- Недоступности сервисов

## 🔧 Конфигурация

### Переменные окружения

```bash
# База данных
MONGO_URI=mongodb://mongo:27017
REDIS_HOST=redis

# Мониторинг
JAEGER_HOST=jaeger
JAEGER_PORT=6831

# JWT
JWT_SECRET_KEY=your-secret-key
```

### Конфигурация Prometheus

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'event-hub'
    static_configs:
      - targets: ['app:8000']
```

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch
3. Внесите изменения
4. Добавьте тесты
5. Создайте Pull Request

## 📄 Лицензия

MIT License

## 🆘 Поддержка

- 📧 Email: support@eventhub.com
- 📖 Документация: `/docs`
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions

---

**Event Hub** - надежная и масштабируемая система обработки событий для современных приложений! 🚀 