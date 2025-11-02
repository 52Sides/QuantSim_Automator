#!/bin/sh
set -e

# --- Ждём Postgres ---
echo "Waiting for Postgres..."
until pg_isready -h postgres -p 5432 -U postgres; do
  sleep 2
done

# --- Ждём Redis ---
echo "Waiting for Redis..."
until redis-cli -h redis ping | grep PONG; do
  sleep 2
done

# --- Ждём Kafka ---
echo "Waiting for Kafka..."
until nc -z kafka 9092; do
  sleep 3
done

# --- Применяем миграции ---
echo "Running Alembic migrations..."
alembic -c src/db/migrations/alembic.ini upgrade head

# --- Запускаем backend ---
echo "Starting backend..."
exec uvicorn api.main:app --host 0.0.0.0 --port 8000
