import time

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse


openapi_tags = [
    {
        "name": "Проверочные endpoint'ы",
        "description": "Endpoint'ы для демонстрации сценариев UP, DOWN и TIMEOUT.",
    },
    {
        "name": "Служебные",
        "description": "Служебные endpoint'ы Test Service.",
    },
]


app = FastAPI(
    title="Тестовый сервис",
    description=(
        "Демонстрационный FastAPI-сервис с предсказуемыми endpoint'ами "
        "для проверки работы Monitoring Service."
    ),
    version="0.1.0",
    openapi_tags=openapi_tags,
)


@app.get(
    "/health",
    tags=["Служебные"],
    summary="Проверить состояние Test Service",
    description="Возвращает healthcheck самого Test Service.",
)
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get(
    "/health/up",
    tags=["Проверочные endpoint'ы"],
    summary="Сценарий успешной проверки",
    description="Возвращает HTTP 200 и используется для демонстрации статуса `UP`.",
)
def health_up() -> dict[str, str]:
    return {"status": "ok"}


@app.get(
    "/health/down",
    tags=["Проверочные endpoint'ы"],
    summary="Сценарий сбоя",
    description="Возвращает HTTP 500 и используется для демонстрации статуса `DOWN` с ошибкой `HTTP_5XX`.",
)
def health_down() -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"status": "error"},
    )


@app.get(
    "/health/timeout",
    tags=["Проверочные endpoint'ы"],
    summary="Сценарий timeout",
    description="Ждёт 5 секунд перед ответом и используется для демонстрации статуса `DOWN` с ошибкой `TIMEOUT`.",
)
def health_timeout() -> dict[str, str]:
    time.sleep(5)
    return {"status": "ok"}
