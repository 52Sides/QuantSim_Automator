import asyncio
import json
import logging
from pathlib import Path
from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from core.config import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

TOPICS_PATH = Path(__file__).resolve().parents[3] / "kafka" / "topics_config"


async def create_topics():
    admin = AIOKafkaAdminClient(bootstrap_servers=settings.KAFKA_BROKER)
    await admin.start()
    logger.info("🔍 Checking Kafka topics...")

    try:
        existing = await admin.list_topics()
        new_topics = []

        for json_file in TOPICS_PATH.glob("*.json"):
            with open(json_file, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            name = cfg["name"]
            if name not in existing:
                logger.info(f"📦 Creating topic: {name}")
                new_topics.append(
                    NewTopic(
                        name=name,
                        num_partitions=cfg.get("num_partitions", 1),
                        replication_factor=cfg.get("replication_factor", 1),
                    )
                )

        if new_topics:
            await admin.create_topics(new_topics)
            logger.info(f"✅ Created {len(new_topics)} topics")
        else:
            logger.info("👌 All topics already exist")

    finally:
        await admin.close()
        logger.info("Kafka admin connection closed")


if __name__ == "__main__":
    asyncio.run(create_topics())
