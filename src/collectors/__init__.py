import sqlite3
import time

from src.collectors.base import RawJob
from src.collectors.freelancer import fetch_freelancer_jobs
from src.utils.logger import setup_logger
from src.utils.config import FRESH_WINDOW_SEC

logger = setup_logger("collectors")

SEEN_DB = "seen_projects.sqlite3"


def _get_last_fetch_time() -> int:
    try:
        db = sqlite3.connect(SEEN_DB)
        row = db.execute("SELECT last_sent_at FROM seen WHERE uid='meta:last_fetch'").fetchone()
        db.close()
        if row:
            return row[0]
    except Exception:
        pass
    now = int(time.time())
    return now - FRESH_WINDOW_SEC


def _set_last_fetch_time(ts: int):
    try:
        db = sqlite3.connect(SEEN_DB)
        db.execute(
            "INSERT OR REPLACE INTO seen (uid, last_sent_at) VALUES ('meta:last_fetch', ?)",
            (ts,),
        )
        db.commit()
        db.close()
    except Exception as e:
        logger.warning(f"Failed to save last_fetch_time: {e}")


def collect_all() -> list[RawJob]:
    jobs: list[RawJob] = []
    last_fetch = _get_last_fetch_time()
    fetch_start = int(time.time())

    try:
        freelancer_jobs = fetch_freelancer_jobs(since_time=last_fetch)
        jobs.extend(freelancer_jobs)
        logger.info(f"Freelancer: {len(freelancer_jobs)} jobs fetched (since {last_fetch})")
    except Exception as e:
        logger.error(f"Freelancer error: {e}")
        return jobs

    _set_last_fetch_time(fetch_start)

    return jobs
