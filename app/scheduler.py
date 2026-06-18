from collections.abc import Callable
import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.config import get_settings
from app.services import monitor_service


logger = logging.getLogger(__name__)
MonitorRunner = Callable[[int], object]


def run_active_monitors(
    monitor_runner: MonitorRunner = monitor_service.run_monitor_now,
) -> int:
    processed = 0

    for monitor in monitor_service.list_active_monitors():
        if monitor.id is None:
            continue

        try:
            monitor_runner(monitor.id)
            processed += 1
        except Exception:
            logger.exception("Monitor execution failed for monitor_id=%s", monitor.id)

    return processed


def create_scheduler(
    monitor_runner: MonitorRunner = monitor_service.run_monitor_now,
) -> BackgroundScheduler:
    settings = get_settings()
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        lambda: run_active_monitors(monitor_runner),
        trigger="interval",
        hours=settings.check_interval_hours,
        id="flight_monitor_periodic_check",
        replace_existing=True,
    )
    return scheduler
