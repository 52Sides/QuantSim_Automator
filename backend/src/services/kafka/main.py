import asyncio
from services.kafka.consumer import consume_simulation_requests, consume_metrics_events, consume_simulation_events


async def main():
    await asyncio.gather(
        consume_simulation_requests(),
        consume_metrics_events(),
        consume_simulation_events(),
    )


if __name__ == "__main__":
    asyncio.run(main())
