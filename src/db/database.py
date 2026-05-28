import json
from contextlib import contextmanager
from typing import Optional

from sqlalchemy import func

from src.db.models import get_session_factory, Job, User, Proposal, Feedback

SessionFactory = get_session_factory()


@contextmanager
def get_db():
    session = SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def job_exists(source: str, external_id: str) -> bool:
    with get_db() as session:
        return session.query(Job).filter_by(source=source, external_id=external_id).first() is not None


def save_job(job: Job) -> int:
    with get_db() as session:
        session.add(job)
        session.flush()
        session.refresh(job)
        job_id = job.id
    return job_id


def get_job_by_id(job_id: int) -> Optional[Job]:
    with get_db() as session:
        return session.query(Job).filter_by(id=job_id).first()


def update_job_score(job_id: int, score: float):
    with get_db() as session:
        session.query(Job).filter_by(id=job_id).update({"score": score})


def save_ai_summary(job_id: int, summary: str):
    with get_db() as session:
        session.query(Job).filter_by(id=job_id).update({"ai_summary": summary})


def save_translation(job_id: int, translated: str):
    with get_db() as session:
        session.query(Job).filter_by(id=job_id).update({"translated_ru": translated})


def save_proposal(job_id: int, user_id: int, content: str) -> Proposal:
    with get_db() as session:
        proposal = Proposal(job_id=job_id, user_id=user_id, content=content)
        session.add(proposal)
        session.flush()
        session.refresh(proposal)
        return proposal


def get_or_create_user(telegram_id: str, plan: str = "free") -> User:
    with get_db() as session:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if not user:
            user = User(telegram_id=telegram_id, plan=plan)
            session.add(user)
            session.flush()
            session.refresh(user)
        return user


def update_user_specialty(telegram_id: str, specialty: str) -> User:
    with get_db() as session:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if user:
            user.specialty = specialty
            session.flush()
            session.refresh(user)
        return user


def update_user_language(telegram_id: str, language: str) -> User:
    with get_db() as session:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if user:
            user.target_language = language
            session.flush()
            session.refresh(user)
        return user


def get_users_by_specialty(specialty: str) -> list[User]:
    with get_db() as session:
        return session.query(User).filter_by(specialty=specialty).all()


def get_cached_translation(job_id: int, lang: str, text_hash: str = "") -> str | None:
    with get_db() as session:
        job = session.query(Job.translations).filter_by(id=job_id).scalar()
    if not job:
        return None
    try:
        cache = json.loads(job) if isinstance(job, str) else {}
        key = f"{lang}:{text_hash}" if text_hash else lang
        return cache.get(key)
    except (json.JSONDecodeError, TypeError):
        return None


def save_translation_cache(job_id: int, lang: str, text_hash: str, text: str):
    with get_db() as session:
        job = session.query(Job).filter_by(id=job_id).first()
        if not job:
            return
        current = {}
        if job.translations:
            try:
                current = json.loads(job.translations)
            except (json.JSONDecodeError, TypeError):
                current = {}
        key = f"{lang}:{text_hash}" if text_hash else lang
        current[key] = text
        job.translations = json.dumps(current, ensure_ascii=False)
        session.flush()


def get_all_users() -> list[User]:
    with get_db() as session:
        return session.query(User).all()


def save_feedback(job_id: int, user_id: int, reason: str = "spam") -> Feedback:
    with get_db() as session:
        fb = Feedback(job_id=job_id, user_id=user_id, reason=reason)
        session.add(fb)
        session.flush()
        session.refresh(fb)
        return fb


def get_feedback_stats() -> dict:
    with get_db() as session:
        total = session.query(Feedback).count()
        spam_count = session.query(Feedback).filter_by(reason="spam").count()
        top_spam_sources = (
            session.query(Job.source, func.count(Feedback.id))
            .join(Feedback, Feedback.job_id == Job.id)
            .filter(Feedback.reason == "spam")
            .group_by(Job.source)
            .order_by(func.count(Feedback.id).desc())
            .all()
        )
        return {
            "total_feedback": total,
            "total_spam": spam_count,
            "top_spam_sources": [{"source": s, "count": c} for s, c in top_spam_sources],
        }
