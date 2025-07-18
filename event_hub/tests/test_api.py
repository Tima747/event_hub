import pytest
import asyncio
from httpx import AsyncClient
from datetime import datetime
from app.main import app

@pytest.mark.asyncio
async def test_create_event():
    """Тест создания события через REST API"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        event_data = {
            "user_id": "test_user",
            "event_type": "purchase",
            "amount": 100.50,
            "timestamp": datetime.now().isoformat()
        }
        
        response = await ac.post("/events", json=event_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["status"] == "success"

@pytest.mark.asyncio
async def test_create_event_invalid_data():
    """Тест создания события с некорректными данными"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        event_data = {
            "user_id": "test_user",
            # Отсутствует обязательное поле event_type
            "amount": 100.50
        }
        
        response = await ac.post("/events", json=event_data)
        
        assert response.status_code == 422  # Validation error

@pytest.mark.asyncio
async def test_graphql_query():
    """Тест GraphQL запроса"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        query = """
        query {
            lastEvents(limit: 5) {
                id
                userId
                eventType
                amount
                timestamp
            }
        }
        """
        
        response = await ac.post("/graphql", json={"query": query})
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "lastEvents" in data["data"]

@pytest.mark.asyncio
async def test_aggregated_metrics():
    """Тест агрегированных метрик"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        query = """
        query {
            aggregatedMetrics(minutes: 1) {
                totalAmount
                eventCount
                timeWindow
            }
        }
        """
        
        response = await ac.post("/graphql", json={"query": query})
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "aggregatedMetrics" in data["data"] 