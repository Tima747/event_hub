# Event Hub - Инструкция по запуску

## Как запустить проект

1. **Установите Docker**  
   Скачайте и установите Docker Desktop с официального сайта:  
   [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)

2. **Запустите сервисы**  
   Откройте терминал в папке проекта и выполните:
   
   docker-compose up -d --build
   

3. **Проверьте работу**  
   Откройте в браузере:  
   [http://localhost:8000/graphql](http://localhost:8000/graphql)  
   (должна открыться GraphQL "песочница")

## Как отправить событие

1. **Через REST API**  
   Выполните в терминале:
   
   curl -X POST "http://localhost:8000/events" \
   -H "Content-Type: application/json" \
   -d '{
     "event_type": "purchase",
     "user_id": "testuser",
     "amount": 100.0,
     "timestamp": "2025-07-16T12:00:00Z"
   }'
   

2. **Правильный формат данных**:
   - `event_type`: строка (пример: "purchase")
   - `user_id`: строка
   - `amount`: число (можно с точкой)
   - `timestamp`: дата в формате `ГГГГ-ММ-ДДTЧЧ:ММ:ССZ`

## Как проверить данные

1. **В MongoDB**:
   
   docker-compose exec mongo mongosh event_hub --eval "db.events.find().pretty()"
   

2. **В Redis**:
   
   docker-compose exec redis redis-cli XRANGE events - +
   

3. **Через GraphQL**:
   graphql
   query {
     lastEvents(limit: 5) {
       id
       userId
       eventType
       amount
       timestamp
     }
   }
   

## Если что-то не работает

1. **Перезапустите сервисы**:
   
   docker-compose down
   docker-compose up -d
   

2. **Проверьте логи**:
   
   docker-compose logs app  # для FastAPI
   docker-compose logs mongo  # для MongoDB
   

3. **Очистите данные** (если нужно начать заново):

   docker-compose down -v
   