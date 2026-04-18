"""Pub/Sub push message ingest endpoint."""

import base64

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from snip_analytics import AnalyticsClient, ClickEventRow
from snip_logger import get_logger
from snip_queue import ClickEventMessage
from snip_telemetry import traced

from click_worker.dependencies import get_analytics_client, verify_pubsub_token

_log = get_logger("click-worker", log_prefix="Ingest")

router = APIRouter(tags=["ingest"])


class PubSubMessage(BaseModel):
    data: str  # base64 encoded
    message_id: str = ""
    attributes: dict[str, str] = {}


class PubSubEnvelope(BaseModel):
    message: PubSubMessage
    subscription: str = ""


@router.post("/ingest", response_model=None)
@traced
async def ingest(
    envelope: PubSubEnvelope,
    analytics: AnalyticsClient = Depends(get_analytics_client),
    _: None = Depends(verify_pubsub_token),
) -> dict[str, str] | JSONResponse:
    """Receive a Pub/Sub push message and write to analytics."""
    try:
        raw = base64.b64decode(envelope.message.data)
        click = ClickEventMessage.from_json(raw)
    except Exception:
        _log.warning(
            "malformed_message_acked",
            message_id=envelope.message.message_id,
            exc_info=True,
        )
        return {"status": "acked_malformed"}

    row = ClickEventRow(
        event_id=click.event_id,
        link_id=click.link_id,
        short_code=click.short_code,
        org_id=click.org_id,
        clicked_at=click.clicked_at,
        user_agent=click.user_agent,
        country=click.country,
    )

    try:
        await analytics.insert_click_event(row)
    except Exception:
        _log.error("analytics_write_failed", event_id=click.event_id, exc_info=True)
        return JSONResponse(status_code=500, content={"status": "error"})

    _log.info("click_event_ingested", event_id=click.event_id, link_id=click.link_id)
    return {"status": "ok"}
