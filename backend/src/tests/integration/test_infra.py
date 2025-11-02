import os
import psycopg2
import redis
from kafka import KafkaAdminClient
from contextlib import closing
import pytest
from kafka.errors import NoBrokersAvailable
from redis.exceptions import ConnectionError as RedisConnectionError
from psycopg2 import OperationalError

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

KAFKA_HOST = os.getenv("KAFKA_HOST", "kafka")
KAFKA_PORT = int(os.getenv("KAFKA_PORT", 9092))


@pytest.mark.integration
def test_postgres_connection():
    dsn = f"host={POSTGRES_HOST} port={POSTGRES_PORT} user=postgres password=postgres dbname=quantsim_db"
    with closing(psycopg2.connect(dsn)) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            assert cur.fetchone()[0] == 1


@pytest.mark.integration
def test_redis_ping():
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
    assert r.ping() is True


@pytest.mark.integration
def test_kafka_health():
    client = KafkaAdminClient(bootstrap_servers=f"{KAFKA_HOST}:{KAFKA_PORT}")
    topics = client.list_topics()
    assert isinstance(topics, set)
