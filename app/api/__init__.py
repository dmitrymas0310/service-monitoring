from app.api.checks_api import router as checks_router
from app.api.endpoints_api import router as endpoints_router
from app.api.services_api import router as services_router
from app.api.stats_api import router as stats_router


__all__ = [
    "checks_router",
    "endpoints_router",
    "services_router",
    "stats_router",
]
