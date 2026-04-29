"""
RabbitMQ connection manager.

Exchange layout
───────────────
  Exchange : youth.events   (topic, durable)
  Routing keys:
    account.created
    account.updated
    account.deactivated
    account.activated
    account.imported
    login.login
    login.logout

Queues (durable, bound to youth.events)
────────────────────────────────────────
  youth.audit     – receives  #            (every event)
  youth.eventing  – receives  account.*   (domain events only)
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any

import aio_pika
from aio_pika import ExchangeType, Message, DeliveryMode
from aio_pika.abc import AbstractRobustConnection, AbstractChannel

from app.core.config import settings

logger = logging.getLogger(__name__)

EXCHANGE_NAME = "youth.events"
AUDIT_QUEUE   = "youth.audit"
EVENTING_QUEUE = "youth.eventing"


class RabbitMQManager:
    """Singleton-style async manager. Call startup() on app start, shutdown() on stop."""

    def __init__(self) -> None:
        self._connection: AbstractRobustConnection | None = None
        self._channel:    AbstractChannel | None = None
        self._exchange:   aio_pika.Exchange | None = None

    # ── Lifecycle ─────────────────────────────────────────────────────────

    async def startup(self) -> None:
        retries = 0
        max_retries = 10
        while retries < max_retries:
            try:
                self._connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
                self._channel    = await self._connection.channel()
                await self._channel.set_qos(prefetch_count=10)

                self._exchange = await self._channel.declare_exchange(
                    EXCHANGE_NAME,
                    ExchangeType.TOPIC,
                    durable=True,
                )

                # Declare queues and bind them
                audit_q = await self._channel.declare_queue(AUDIT_QUEUE, durable=True)
                await audit_q.bind(self._exchange, routing_key="#")

                eventing_q = await self._channel.declare_queue(EVENTING_QUEUE, durable=True)
                await eventing_q.bind(self._exchange, routing_key="account.*")

                logger.info("RabbitMQ connected — exchange '%s' ready.", EXCHANGE_NAME)
                return
            except Exception as exc:
                retries += 1
                wait = min(2 ** retries, 30)
                logger.warning(
                    "RabbitMQ not ready (%s). Retrying in %ds… (%d/%d)",
                    exc, wait, retries, max_retries,
                )
                await asyncio.sleep(wait)

        logger.error("Could not connect to RabbitMQ after %d retries.", max_retries)

    async def shutdown(self) -> None:
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
            logger.info("RabbitMQ connection closed.")

    # ── Publishing ────────────────────────────────────────────────────────

    async def publish(self, routing_key: str, payload: dict[str, Any]) -> None:
        """Publish a single event. Safe to call even if connection is not yet ready."""
        if self._exchange is None:
            logger.warning("RabbitMQ not ready; dropping event '%s'.", routing_key)
            return

        # Stamp every outbound message
        payload.setdefault("published_at", datetime.now(timezone.utc).isoformat())

        body = json.dumps(payload, default=str).encode()
        msg  = Message(
            body=body,
            delivery_mode=DeliveryMode.PERSISTENT,
            content_type="application/json",
        )
        await self._exchange.publish(msg, routing_key=routing_key)
        logger.debug("Published '%s': %s", routing_key, payload)

    # ── Helpers ───────────────────────────────────────────────────────────

    @property
    def channel(self) -> AbstractChannel | None:
        return self._channel

    @property
    def is_ready(self) -> bool:
        return self._exchange is not None


# Module-level singleton
rabbitmq = RabbitMQManager()
