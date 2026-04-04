# snip-queue

Async message publishing with pluggable providers.

## Protocol

```python
class QueuePublisher(Protocol):
    async def publish(self, topic: str, data: bytes, attributes: dict[str, str] | None = None) -> str: ...
```

Returns the published message ID.

## Providers

| Provider | Usage |
|----------|-------|
| `GCP_PUBSUB` | Production — publishes to Google Cloud Pub/Sub |
| `DEV` | Local dev — in-memory store, logs messages |

## Messages

`ClickEventMessage` is the primary message type — serializable via `to_json()` / `from_json()`.

## Usage

```python
from snip_queue import create_queue_publisher, QueueProvider, ClickEventMessage

publisher = create_queue_publisher(QueueProvider.GCP_PUBSUB, gcp_project_id="my-project")
msg = ClickEventMessage(link_id="abc", short_code="xyz", org_id="org1", ...)
await publisher.publish("click-events", msg.to_json())
```
