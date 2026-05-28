from sqlalchemy import func

from src.db.database import get_db
from src.db.models import Job, Proposal, User, Feedback


def get_stats() -> dict:
    with get_db() as session:
        total_jobs = session.query(Job).count()
        total_proposals = session.query(Proposal).count()
        total_users = session.query(User).count()

        avg_score = session.query(func.avg(Job.score)).scalar() or 0.0

        top_source = session.query(Job.source, func.count(Job.id)).group_by(
            Job.source
        ).order_by(func.count(Job.id).desc()).first()

        total_spam = session.query(Feedback).filter_by(reason="spam").count()

        return {
            "total_jobs": total_jobs,
            "total_proposals": total_proposals,
            "total_users": total_users,
            "avg_score": round(avg_score, 1),
            "top_source": top_source[0] if top_source else "N/A",
            "total_spam": total_spam,
        }
