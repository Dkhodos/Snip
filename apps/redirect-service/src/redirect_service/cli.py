import uvicorn


def dev() -> None:
    uvicorn.run(
        "redirect_service.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
    )


def serve() -> None:
    uvicorn.run(
        "redirect_service.main:app",
        host="0.0.0.0",
        port=8080,
    )
