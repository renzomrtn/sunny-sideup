"""
Outbox Relay Worker
───────────────────
Polls `identity_db.Outbox` for undispatched rows, publishes each to RabbitMQ,
then marks the row as dispatched.  Runs as a background asyncio task.

Routing-key convention  →  {aggregate_type}.{event_type}
  e.g.  aggregate_type="account", event_type="created"  →  "account.created"
"""

import asyncio
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.config import settings
from app.core.rabbitmq import rabbitmq
from app.domains.identity.models import Outbox

PHT = ZoneInfo("Asia/Manila")


def pht_now():
    """Return current Philippine Standard Time (UTC+8) as a naive datetime.
    Naive because all DB columns are TIMESTAMP WITHOUT TIME ZONE."""
    return datetime.now(PHT).replace(tzinfo=None)




logger = logging.getLogger(__name__)

POLL_INTERVAL_SECONDS = 2
MAX_BATCH             = 50
MAX_RETRY             = 5


def _make_session_factory():
    engine = create_async_engine(settings.IDENTITY_DB_URL, echo=False, pool_size=5)
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def _process_batch(session: AsyncSession) -> int:
    """Fetch one batch of undispatched rows and publish them. Returns rows processed."""
    result = await session.execute(
        select(Outbox)
        .where(Outbox.dispatched == False, Outbox.failed == False)  # noqa: E712
        .order_by(Outbox.created_at)
        .limit(MAX_BATCH)
        .with_for_update(skip_locked=True)
    )
    rows = result.scalars().all()
    if not rows:
        return 0

    for row in rows:
        routing_key = f"{row.aggregate_type.lower()}.{row.event_type.lower()}"
        envelope = {
            "outbox_id":      row.outbox_id,
            "tenant_id":      row.tenant_id,
            "aggregate_type": row.aggregate_type,
            "aggregate_id":   row.aggregate_id,
            "event_type":     row.event_type,
            "payload":        row.payload,
            "created_at":     row.created_at.isoformat() if row.created_at else None,
        }
        try:
            await rabbitmq.publish(routing_key, envelope)
            row.dispatched    = True
            row.dispatched_at = pht_now()
        except Exception as exc:
            row.retry_count    = (row.retry_count or 0) + 1
            row.last_attempted = pht_now()
            if row.retry_count >= MAX_RETRY:
                row.failed         = True
                row.failure_reason = str(exc)
                logger.error("Outbox row %d permanently failed: %s", row.outbox_id, exc)
            else:
                logger.warning("Outbox row %d publish failed (attempt %d): %s",
                               row.outbox_id, row.retry_count, exc)

    await session.commit()
    return len(rows)


async def run_outbox_relay() -> None:
    """Long-running worker loop. Called once on application startup."""
    logger.info("Outbox relay starting…")
    session_factory = _make_session_factory()

    while True:
        try:
            async with session_factory() as session:
                processed = await _process_batch(session)
                if processed:
                    logger.debug("Outbox relay: dispatched %d messages.", processed)
        except asyncio.CancelledError:
            logger.info("Outbox relay stopped.")
            return
        except Exception as exc:
            logger.error("Outbox relay error: %s", exc, exc_info=True)

        await asyncio.sleep(POLL_INTERVAL_SECONDS)
