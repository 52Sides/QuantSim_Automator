import os
import psycopg2
import redis
from kafka import KafkaAdminClient
from contextlib import closing
import pytest
from kafka.errors import NoBrokersAvailable
from redis.exceptions import ConnectionError as RedisConnectionError
from psycopg2 import OperationalError


# ---- Автоматическая подмена хостов при запуске локально ----
def is_running_in_docker() -> bool:
    """Определяет, запущен ли код внутри контейнера."""
    try:
        with open("/proc/1/cgroup", "rt") as f:
            return "docker" in f.read()
    except FileNotFoundError:
        return False


def resolve_host(env_var, default_container_name, default_local="localhost"):
    if is_running_in_docker():
        return os.getenv(env_var, default_container_name)

    return os.getenv(env_var, default_local)


# ---- Настройки ----
POSTGRES_HOST = resolve_host("POSTGRES_HOST", "postgres")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))

REDIS_HOST = resolve_host("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

KAFKA_HOST = resolve_host("KAFKA_HOST", "kafka")
KAFKA_PORT = int(os.getenv("KAFKA_PORT", 9092))


@pytest.mark.integration
def test_postgres_connection():
    dsn = f"host={POSTGRES_HOST} port={POSTGRES_PORT} user=postgres password=postgres dbname=postgres"
    try:
        with closing(psycopg2.connect(dsn)) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                assert cur.fetchone()[0] == 1
    except OperationalError as e:
        pytest.skip(f"Postgres not reachable: {e}")


@pytest.mark.integration
def test_redis_ping():
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
        assert r.ping() is True
    except RedisConnectionError as e:
        pytest.skip(f"Redis not reachable: {e}")


@pytest.mark.integration
def test_kafka_health():
    try:
        client = KafkaAdminClient(bootstrap_servers=f"{KAFKA_HOST}:{KAFKA_PORT}")
        topics = client.list_topics()
        assert isinstance(topics, set)

    except NoBrokersAvailable as e:
        pytest.skip(f"Kafka broker not reachable: {e}")
