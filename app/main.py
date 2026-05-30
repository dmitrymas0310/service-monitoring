from fastapi import FastAPI


app = FastAPI(
    title="Monitoring Service",
    description="MVP service for monitoring REST endpoint availability.",
    version="0.1.0",
)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


# TODO: Include API routers here when endpoint modules are implemented.
