"""
Cms domain router
─────────────────
Add endpoints here as the domain is built out.

Publishing events to RabbitMQ (when ready):
────────────────────────────────────────────
from app.core.rabbitmq import rabbitmq

await rabbitmq.publish("cms.created", {
    "tenant_id":      ...,
    "aggregate_type": "cms",
    "aggregate_id":   ...,
    "event_type":     "created",
    "payload":        {"actor": ..., ...},
})

Then add "cms.*" to eventing-service/app/consumer.py ROUTING_KEYS.
"""
from fastapi import APIRouter

router = APIRouter()

# @router.get("")
# async def list_cms_items():
#     ...
