import uvicorn


def dev() -> None:
    uvicorn.run(
        "click_worker.main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
    )


def serve() -> None:
    uvicorn.run(
        "click_worker.main:app",
        host="0.0.0.0",
        port=8080,
    )
