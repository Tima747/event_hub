.PHONY: help install dev test clean proto docker-up docker-down docker-logs

# Переменные
PYTHON = python3
PIP = pip3
DOCKER_COMPOSE = docker-compose

help: ## Показать справку
	@echo "Event Hub - Команды для разработки"
	@echo "=================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Установить зависимости
	$(PIP) install -r requirements.txt
	$(PIP) install pytest pytest-asyncio httpx flake8 black

proto: ## Генерировать protobuf файлы
	$(PYTHON) generate_protos.py

dev: ## Запустить в режиме разработки
	$(PYTHON) run_dev.py

test: ## Запустить тесты
	pytest tests/ -v

test-coverage: ## Запустить тесты с покрытием
	pytest tests/ --cov=app --cov-report=html -v

lint: ## Проверить код линтером
	flake8 app/ consumer/ client/ tests/
	black --check app/ consumer/ client/ tests/

format: ## Форматировать код
	black app/ consumer/ client/ tests/

docker-up: ## Запустить Docker сервисы
	$(DOCKER_COMPOSE) up -d --build

docker-down: ## Остановить Docker сервисы
	$(DOCKER_COMPOSE) down

docker-logs: ## Показать логи Docker
	$(DOCKER_COMPOSE) logs -f

docker-clean: ## Очистить Docker данные
	$(DOCKER_COMPOSE) down -v
	docker system prune -f

clean: ## Очистить временные файлы
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf htmlcov/

generate-events: ## Генерировать тестовые события
	cd client && $(PYTHON) event_generator.py

grpc-client: ## Запустить gRPC клиент
	cd client && $(PYTHON) grpc_client.py

check-status: ## Проверить статус сервисов
	@echo "🔍 Проверка статуса сервисов..."
	@echo "FastAPI: $(shell curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs || echo "недоступен")"
	@echo "GraphQL: $(shell curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/graphql || echo "недоступен")"
	@echo "MongoDB: $(shell docker ps | grep mongo || echo "не запущен")"
	@echo "Redis: $(shell docker ps | grep redis || echo "не запущен")"

setup: install proto ## Полная настройка проекта
	@echo "✅ Проект настроен и готов к работе"

all: setup docker-up ## Полный запуск проекта
	@echo "🎉 Event Hub запущен!"
	@echo "📱 Доступные сервисы:"
	@echo "   • FastAPI: http://localhost:8000"
	@echo "   • GraphQL: http://localhost:8000/graphql"
	@echo "   • gRPC: localhost:50051" 