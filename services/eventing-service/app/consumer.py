"""
Eventing Service — Standalone Consumer
───────────────────────────────────────
Listens on the `youth.eventing` queue (routing key `account.*`)
and writes a Domain_Event row to `eventing_db` for every account
event published by identity-service.

As more services come online (budget, project, etc.) they will
publish their own events. Add new queue bindings here, or create
separate consumer tasks, to capture those domain events too.

This is a plain Python process — no FastAPI, no HTTP server.
"""

import asyncio
import json
import logging
import signal
from datetime import datetime
from zoneinfo import ZoneInfo

import aio_pika
from sqlalchemy import Table, Column, BigInteger, Integer, String, Boolean, DateTime, Text, MetaData
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings

PHT = ZoneInfo("Asia/Manila")


def pht_now():
    """Return current Philippine Standard Time (UTC+8) as a naive datetime.
    Naive because all DB columns are TIMESTAMP WITHOUT TIME ZONE."""
    return datetime.now(PHT).replace(tzinfo=None)




logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [eventing-service] %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────

EXCHANGE_NAME = "youth.events"
QUEUE_NAME    = "youth.eventing"

# Routing keys this service subscribes to.
# Extend this list as new services start publishing events.
ROUTING_KEYS = [
    "account.*",   # from identity-service
    # "budget.*",  # uncomment when budget-service publishes
    # "project.*",
    # "expenditure.*",
]


# ── SQLAlchemy Core table ──────────────────────────────────────────────────

_meta = MetaData()

domain_event = Table(
    "domain_event", _meta,
    Column("dom_event_id",          BigInteger, primary_key=True, autoincrement=True),
    Column("tenant_id",             Integer,    nullable=False),
    Column("event_type",            String(100),nullable=False),
    Column("aggregate_type",        String(100),nullable=False),
    Column("aggregate_id",          Integer,    nullable=False),
    Column("triggered_by_role_id",  Integer),
    Column("triggered_by_snapshot", JSONB),
    Column("payload",               JSONB),
    Column("occurred_at",           DateTime),
    Column("processed",             Boolean,    default=False),
    Column("processed_at",          DateTime),
    Column("failed",                Boolean,    default=False),
    Column("failure_reason",        Text),
)


# ── Message handler ────────────────────────────────────────────────────────

async def _handle(message: aio_pika.IncomingMessage, engine) -> None:
    async with message.process(requeue=True):
        try:
            body    = json.loads(message.body.decode())
            payload = body.get("payload") or {}
            actor   = payload.get("actor") or {}

            async with engine.begin() as conn:
                await conn.execute(
                    domain_event.insert().values(
                        tenant_id            = body.get("tenant_id") or 0,
                        event_type           = body.get("event_type", ""),
                        aggregate_type       = body.get("aggregate_type", ""),
                        aggregate_id         = body.get("aggregate_id") or 0,
                        triggered_by_role_id = actor.get("role_id"),
                        triggered_by_snapshot= actor or None,
                        payload              = payload,
                        occurred_at          = pht_now(),
                    )
                )
            logger.info(
                "domain_event stored: %s.%s  aggregate_id=%s",
                body.get("aggregate_type"), body.get("event_type"), body.get("aggregate_id"),
            )
        except Exception as exc:
            logger.error("Failed to process message: %s", exc, exc_info=True)
            raise  # triggers requeue


# ── Main loop ──────────────────────────────────────────────────────────────

async def main() -> None:
    engine = create_async_engine(settings.EVENTING_DB_URL, echo=False, pool_size=5)
    logger.info("eventing-service starting — connecting to RabbitMQ…")

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    while not stop_event.is_set():
        try:
            connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
            async with connection:
                channel  = await connection.channel()
                await channel.set_qos(prefetch_count=10)

                exchange = await channel.declare_exchange(
                    EXCHANGE_NAME, aio_pika.ExchangeType.TOPIC, durable=True
                )
                queue = await channel.declare_queue(QUEUE_NAME, durable=True)

                # Bind all routing keys this service cares about
                for rk in ROUTING_KEYS:
                    await queue.bind(exchange, routing_key=rk)
                    logger.info("Bound '%s' → '%s'", QUEUE_NAME, rk)

                logger.info("eventing-service listening on '%s'", QUEUE_NAME)

                async with queue.iterator() as q:
                    async for message in q:
                        if stop_event.is_set():
                            break
                        await _handle(message, engine)

        except asyncio.CancelledError:
            break
        except Exception as exc:
            if stop_event.is_set():
                break
            logger.error("Connection error: %s — reconnecting in 5s…", exc)
            await asyncio.sleep(5)

    logger.info("eventing-service stopped.")


if __name__ == "__main__":
    asyncio.run(main())
