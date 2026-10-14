import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.blocking import BlockingScheduler

from app.core.config import settings
from app.jobs import daily

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger(__name__)


def main() -> None:
    scheduler = BlockingScheduler(timezone=settings.timezone)
    scheduler.add_job(
        daily.run,
        "cron",
        hour=settings.ingestion_hour,
        minute=settings.ingestion_minute,
        id="daily_ingestion",
        misfire_grace_time=3600,
        coalesce=True,
    )
    job = scheduler.get_job("daily_ingestion")
    # до start() у job ещё нет next_run_time
    next_run = job.trigger.get_next_fire_time(None, datetime.now(ZoneInfo(settings.timezone)))
    log.info(
        "Планировщик запущен: сбор в %02d:%02d %s, следующий запуск %s",
        settings.ingestion_hour,
        settings.ingestion_minute,
        settings.timezone,
        next_run,
    )
    scheduler.start()


if __name__ == "__main__":
    main()
