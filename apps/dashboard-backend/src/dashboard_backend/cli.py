import uvicorn


def dev() -> None:
    uvicorn.run(
        "dashboard_backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


def serve() -> None:
    uvicorn.run(
        "dashboard_backend.main:app",
        host="0.0.0.0",
        port=8080,
    )
