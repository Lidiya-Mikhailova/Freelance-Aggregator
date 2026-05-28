import asyncio
import html
import time
from datetime import datetime

from telegram.constants import ParseMode

from src.collectors import collect_all
from src.pipeline import filter_jobs_for_all_specialties, deduplicate, score_jobs
from src.db import job_exists, save_job, save_ai_summary, Job, get_users_by_specialty
from src.bot.keyboards import job_keyboard
from src.ai.summarize_job import summarize_job
from src.pipeline.scoring import parse_budget
from src.ai.translate import get_translation
from src.utils.config import CHECK_INTERVAL_SEC, FRESH_WINDOW_SEC, TG_CHAT_ID, API_LIMIT, SPECIALTY_FLAT
from src.utils.languages import LANGUAGES
from src.utils.logger import setup_logger

logger = setup_logger("worker")

FETCH_TIMEOUT_SEC = 120


async def run_monitoring(app):
    app.bot_data["running"] = True

    await app.bot.send_message(
        chat_id=TG_CHAT_ID,
        text=(
            f"Monitoring started.\n"
            f"Check every {CHECK_INTERVAL_SEC}s. "
            f"Freshness window: {FRESH_WINDOW_SEC // 3600}h. "
            f"Fetch limit: {API_LIMIT}."
        ),
    )

    while True:
        try:
            await _monitor_cycle(app)
        except Exception as e:
            logger.error(f"Monitor cycle error: {e}")

        await asyncio.sleep(CHECK_INTERVAL_SEC)


async def _monitor_cycle(app):
    logger.info("Fetching jobs...")
    try:
        raw_jobs = await asyncio.wait_for(
            asyncio.to_thread(collect_all),
            timeout=FETCH_TIMEOUT_SEC,
        )
    except asyncio.TimeoutError:
        logger.error(f"collect_all() timed out after {FETCH_TIMEOUT_SEC}s")
        return
    logger.info(f"Raw jobs: {len(raw_jobs)}")

    unique = deduplicate(raw_jobs)
    logger.info(f"Unique jobs: {len(unique)}")

    by_spec = filter_jobs_for_all_specialties(unique)
    specs_with_matches = {k: v for k, v in by_spec.items() if v}
    if not specs_with_matches:
        logger.info("No jobs matched any specialty")
        app.bot_data["last_check"] = datetime.now().strftime("%H:%M:%S")
        app.bot_data["running"] = True
        return

    now = int(time.time())
    fresh_cutoff = now - FRESH_WINDOW_SEC
    total_sent = 0

    has_any_subscriber = False

    for spec_key, spec_jobs in specs_with_matches.items():
        spec = SPECIALTY_FLAT.get(spec_key)
        if not spec:
            continue

        subscribers = get_users_by_specialty(spec_key)
        if not subscribers:
            continue

        has_any_subscriber = True

        scored = score_jobs(spec_jobs)
        scored.sort(key=lambda x: x[1], reverse=True)

        for job, score in scored:
            if job.submitted_at is not None and job.submitted_at < fresh_cutoff:
                continue

            if job_exists(job.source, job.external_id):
                continue

            db_job = Job(
                source=job.source,
                external_id=job.external_id,
                title=job.title,
                description=job.description,
                budget=job.budget,
                url=job.url,
                score=float(score),
                client_rating=job.client_rating,
                applicants=job.applicants,
                submitted_at=job.submitted_at,
            )
            saved_id = save_job(db_job)

            analysis = await _get_analysis(job)

            age = _format_age(now, job.submitted_at)
            desc_block = f"\n\n<b>Description:</b>\n{html.escape(job.description)}" if job.description else ""
            budget_display = html.escape(job.budget) if job.budget else "Not specified"
            analysis_block = f"\n\n<b>Analysis:</b>\n{html.escape(analysis)}" if analysis else ""

            text = (
                f"<b>New Job</b>\n\n"
                f"<b>{html.escape(job.title)}</b>\n"
                f"{html.escape(age)}\n\n"
                f"Budget: {budget_display}\n"
                f"Client rating: {job.client_rating}\n"
                f"Applicants: {job.applicants}\n"
                f"Score: {score}/100"
                f"{analysis_block}\n\n"
                f"{html.escape(job.url)}"
                f"{desc_block}"
            )

            kb = job_keyboard(saved_id, job.url)

            lang_cache: dict[str, str] = {}
            for user in subscribers:
                try:
                    if user.target_language and user.target_language in LANGUAGES:
                        tl = user.target_language
                        if tl not in lang_cache:
                            lang_cache[tl] = tl
                            title_t = await get_translation(saved_id, job.title, tl)
                            desc_t = await get_translation(saved_id, job.description or "", tl)
                            budget_t = await get_translation(saved_id, budget_display, tl)
                            age_t = await get_translation(saved_id, age, tl)
                            if analysis:
                                analysis_t = await get_translation(saved_id, analysis, tl)
                            else:
                                analysis_t = ""
                        else:
                            title_t = desc_t = budget_t = age_t = analysis_t = None

                        if title_t is not None:
                            user_text = (
                                f"<b>New Job</b>\n\n"
                                f"<b>{html.escape(title_t)}</b>\n"
                                f"{html.escape(age_t)}\n\n"
                                f"Budget: {html.escape(budget_t)}\n"
                                f"Client rating: {job.client_rating}\n"
                                f"Applicants: {job.applicants}\n"
                                f"Score: {score}/100"
                                + (f"\n\n<b>Analysis:</b>\n{html.escape(analysis_t)}" if analysis_t else "")
                                + f"\n\n{html.escape(job.url)}"
                                + (f"\n\n<b>Description:</b>\n{html.escape(desc_t)}" if desc_t else "")
                            )
                            await app.bot.send_message(
                                chat_id=int(user.telegram_id),
                                text=user_text,
                                reply_markup=kb,
                                parse_mode=ParseMode.HTML,
                                disable_web_page_preview=True,
                            )
                        else:
                            await app.bot.send_message(
                                chat_id=int(user.telegram_id),
                                text=text,
                                reply_markup=kb,
                                parse_mode=ParseMode.HTML,
                                disable_web_page_preview=True,
                            )
                    else:
                        await app.bot.send_message(
                            chat_id=int(user.telegram_id),
                            text=text,
                            reply_markup=kb,
                            parse_mode=ParseMode.HTML,
                            disable_web_page_preview=True,
                        )
                except Exception as e:
                    logger.warning(f"Failed to send to {user.telegram_id}: {e}")

            total_sent += 1

    if not has_any_subscriber:
        specs_found = ", ".join(
            SPECIALTY_FLAT[k]["name"] for k in specs_with_matches
        )
        try:
            await app.bot.send_message(
                chat_id=int(TG_CHAT_ID),
                text=(
                    f"Found jobs matching: {specs_found}\n"
                    "But no subscribers yet.\n"
                    "Use /start in the bot to pick your specialty."
                ),
            )
        except Exception as e:
            logger.warning(f"Failed to notify admin: {e}")

    app.bot_data["last_check"] = datetime.now().strftime("%H:%M:%S")
    app.bot_data["total_sent"] = app.bot_data.get("total_sent", 0) + total_sent
    app.bot_data["running"] = True

    logger.info(f"Cycle complete: fetched={len(raw_jobs)} sent={total_sent}")


async def _get_analysis(job) -> str | None:
    try:
        analysis = await summarize_job(
            job.title, job.description, job.budget, job.client_rating, job.applicants
        )
        if analysis and "API key" not in analysis:
            return analysis
    except Exception:
        pass
    return _basic_analysis(job)


def _basic_analysis(job):
    budget_val = parse_budget(job.budget)
    lines = []

    if budget_val > 0:
        if budget_val >= 500:
            lines.append("Budget: High")
        elif budget_val >= 200:
            lines.append("Budget: Medium")
        elif budget_val >= 50:
            lines.append("Budget: Low")
        else:
            lines.append("Budget: Very low")
    else:
        lines.append("Budget: Not specified")

    if job.client_rating > 0:
        if job.client_rating >= 4.5:
            lines.append("Client: Excellent rating")
        elif job.client_rating >= 4.0:
            lines.append("Client: Good rating")
        elif job.client_rating >= 3.0:
            lines.append("Client: Average rating")
        else:
            lines.append("Client: Poor rating")
    else:
        lines.append("Client: No rating")

    if job.applicants == 0:
        lines.append("Competition: None (apply now)")
    elif job.applicants <= 5:
        lines.append("Competition: Low")
    elif job.applicants <= 15:
        lines.append("Competition: Medium")
    elif job.applicants <= 50:
        lines.append("Competition: High")
    else:
        lines.append("Competition: Very high")

    desc_len = len(job.description or "")
    if desc_len < 30:
        lines.append("Description: Too short")
    elif desc_len < 200:
        lines.append("Description: Brief")
    else:
        lines.append("Description: Detailed")

    return "\n".join(lines)


def _format_age(now: int, submit_ts) -> str:
    if not submit_ts:
        return ""
    delta = max(0, now - int(submit_ts))
    mins = delta // 60
    if mins < 60:
        return f"{mins} min ago"
    hrs = mins // 60
    return f"{hrs} h ago"
