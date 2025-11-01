.PHONY: up down rebuild logs test integration-test backend-shell ps clean

# --- Basic lifecycle commands ---
# Запуск всех сервисов
up:
	docker compose up -d

# Остановка и очистка
down:
	docker compose down -v

# Полная пересборка всех сервисов
rebuild:
	docker compose down -v
	docker compose build --no-cache
	docker compose up -d

# Просмотр логов (backend и worker)
logs:
	docker compose logs -f backend worker

# Список контейнеров и их статусы
ps:
	docker compose ps

# Очистка dangling-образов и volume'ов
clean:
	docker system prune -f
	docker volume prune -f


# --- Testing ---
# Запуск unit-тестов (локально внутри backend)
test:
	docker compose exec backend pytest -v --disable-warnings -m "not integration"

# Запуск интеграционных тестов (в Docker)
integration-test:
	@echo "Starting infrastructure: Postgres, Redis, Kafka, Zookeeper..."
	docker compose up -d postgres redis zookeeper kafka
	@echo "Waiting for services to become healthy..."
	@for i in {1..10}; do \
		unhealthy=$$(docker compose ps --format json | jq '.[] | select(.Health != null and .Health != "healthy")'); \
		if [ -z "$$unhealthy" ]; then \
			echo "All containers are healthy"; \
			break; \
		fi; \
		echo "Waiting... ($$i/10)"; \
		sleep 5; \
	done
	@echo "Starting backend..."
	docker compose up -d backend
	sleep 10
	docker compose ps
	@echo "Running integration tests..."
	docker compose exec backend pytest -v -m integration --disable-warnings --maxfail=1
	@echo "Cleaning up..."
	docker compose down -v

# --- Utilities ---
# Войти внутрь backend-контейнера
backend-shell:
	docker compose exec backend bash
