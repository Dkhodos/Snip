# snip-logger

Structured logging with structlog. Provides consistent log formatting across all services.

## API

```python
from snip_logger import configure_logging, get_logger, logging_middleware
```

- `configure_logging(is_local)` — call once at app startup. Colorized console output when local, JSON in production.
- `get_logger(app_name)` — returns a bound structlog logger with app context.
- `logging_middleware` — FastAPI middleware that logs every HTTP request with method, path, status, and duration.

## Usage

```python
from snip_logger import configure_logging, get_logger, logging_middleware

configure_logging(is_local=True)
log = get_logger("dashboard-backend")

app.middleware("http")(logging_middleware)

log.info("link_created", short_code="abc", org_id="org_1")
```
