from fastapi import FastAPI

from app.api import checks_router, endpoints_router, services_router, stats_router
from app.database import Base, engine
from app import models
from app.services.scheduler_service import scheduler_service


openapi_tags = [
    {
        "name": "Сервисы",
        "description": "Регистрация мониторируемых сервисов и получение их конфигурации.",
    },
    {
        "name": "Endpoint'ы",
        "description": "Регистрация и управление REST endpoint'ами мониторируемых сервисов.",
    },
    {
        "name": "История проверок",
        "description": "Получение сохранённых результатов проверок доступности.",
    },
    {
        "name": "Статистика и SLA",
        "description": "Расчёт uptime, SLA и сводной информации по сервисам.",
    },
    {
        "name": "Служебные",
        "description": "Служебные endpoint'ы Monitoring Service.",
    },
]


app = FastAPI(
    title="Сервис мониторинга",
    description=(
        "MVP backend-сервис для мониторинга доступности REST endpoint'ов. "
        "Позволяет регистрировать сервисы и endpoint'ы, выполнять периодические "
        "проверки, хранить историю, рассчитывать uptime/SLA и отправлять "
        "email-уведомления ответственным сотрудникам."
    ),
    version="0.1.0",
    openapi_tags=openapi_tags,
)


@app.get(
    "/health",
    tags=["Служебные"],
    summary="Проверить состояние Monitoring Service",
    description="Возвращает простой healthcheck основного сервиса мониторинга.",
)
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
    scheduler_service.start()


@app.on_event("shutdown")
def shutdown() -> None:
    scheduler_service.stop()


app.include_router(stats_router)
app.include_router(services_router)
app.include_router(endpoints_router)
app.include_router(checks_router)
