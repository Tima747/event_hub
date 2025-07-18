# 🚀 Event Hub - Быстрый старт

## Вариант 1: Docker Compose (рекомендуется)

```bash
# Клонируйте репозиторий
git clone <repository-url>
cd event_hub

# Запустите все сервисы
docker-compose up -d --build

# Проверьте статус
docker-compose ps
```

## Вариант 2: Локальная разработка (упрощенный)

```bash
# Установите упрощенные зависимости (без gRPC)
pip install -r requirements-simple.txt

# Запустите инфраструктуру
docker-compose up mongo redis -d

# Запустите FastAPI сервер
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Вариант 3: Полная разработка (с gRPC)

```bash
# Установите все зависимости
pip install -r requirements.txt

# Генерируйте protobuf файлы
python generate_protos.py

# Запустите инфраструктуру
docker-compose up mongo redis -d

# Запустите приложения
python run_dev.py
```

## Вариант 3: Makefile

```bash
# Полная настройка и запуск
make all

# Только разработка
make dev

# Только тесты
make test
```

## 🧪 Тестирование

### Генерация событий
```bash
# REST API события (рекомендуется)
cd client && python event_generator.py

# Упрощенный клиент (без gRPC)
cd client && python simple_client.py

# gRPC события (требует установки grpcio)
cd client && python grpc_client.py
```

### GraphQL запросы
Откройте http://localhost:8000/graphql и выполните:

```graphql
# Последние события
query {
  lastEvents(limit: 5) {
    id
    userId
    eventType
    amount
    timestamp
  }
}

# Агрегированные метрики
query {
  aggregatedMetrics(minutes: 1) {
    totalAmount
    eventCount
    timeWindow
  }
}

# Подписка на события
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

## 📊 Мониторинг

```bash
# Логи всех сервисов
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f app
docker-compose logs -f grpc-server
docker-compose logs -f metrics-consumer

# Проверка данных
docker-compose exec mongo mongosh event_hub --eval "db.events.find().pretty()"
docker-compose exec redis redis-cli XRANGE events - +
```

## 🔧 Полезные команды

```bash
# Остановка
docker-compose down

# Очистка данных
docker-compose down -v

# Перезапуск
docker-compose restart

# Проверка статуса
make check-status
```

## 🎯 Что работает

✅ **REST API** - прием событий на порту 8000  
✅ **gRPC** - высокопроизводительный API на порту 50051  
✅ **GraphQL** - запросы и подписки на порту 8000/graphql  
✅ **Redis Streams** - очередь сообщений  
✅ **MongoDB** - хранение событий  
✅ **Агрегированные метрики** - ежеминутная статистика  
✅ **Consumer** - обработка событий  
✅ **CI/CD** - GitHub Actions  
✅ **Тесты** - unit тесты  
✅ **Документация** - подробная документация  

## 🚨 Устранение неполадок

### Сервисы не запускаются
```bash
# Проверьте Docker
docker --version
docker-compose --version

# Очистите и перезапустите
docker-compose down -v
docker-compose up -d --build
```

### Ошибки подключения к БД
```bash
# Проверьте статус контейнеров
docker-compose ps

# Проверьте логи
docker-compose logs mongo
docker-compose logs redis
```

### GraphQL не работает
```bash
# Проверьте FastAPI
curl http://localhost:8000/docs

# Проверьте GraphQL
curl http://localhost:8000/graphql
```

## 📞 Поддержка

Если что-то не работает:
1. Проверьте логи: `docker-compose logs -f`
2. Убедитесь, что порты свободны
3. Проверьте версии Docker и Python
4. Создайте issue в репозитории 