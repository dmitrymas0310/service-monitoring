import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.database import SessionLocal
from app.repositories.endpoint_repository import get_active_endpoints
from app.services.health_check_service import check_endpoint
from app.services.result_sla_service import save_check_result
from app.utils.config import settings


logger = logging.getLogger(__name__)


class SchedulerService:
    def __init__(self) -> None:
        self.scheduler = BackgroundScheduler()

    def start(self) -> None:
        if self.scheduler.running:
            return

        self.scheduler.add_job(
            self.run_checks,
            trigger=IntervalTrigger(seconds=settings.check_interval_seconds),
            id="endpoint-health-checks",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
        )
        self.scheduler.start()
        logger.info(
            "Scheduler started with interval %s seconds",
            settings.check_interval_seconds,
        )

    def stop(self) -> None:
        if not self.scheduler.running:
            return

        self.scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")

    def run_checks(self) -> None:
        db = SessionLocal()
        try:
            endpoints = get_active_endpoints(db)
            logger.info("Running health checks for %s active endpoints", len(endpoints))

            for endpoint in endpoints:
                try:
                    check_result = check_endpoint(endpoint)
                    save_check_result(db, check_result)
                except Exception:
                    db.rollback()
                    logger.exception(
                        "Failed to check endpoint %s (%s)",
                        getattr(endpoint, "id", "unknown"),
                        getattr(endpoint, "url", "unknown"),
                    )
        except Exception:
            db.rollback()
            logger.exception("Failed to run scheduler health check cycle")
        finally:
            db.close()


scheduler_service = SchedulerService()
