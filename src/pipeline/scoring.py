import re

from src.collectors.base import RawJob


def parse_budget(budget_str: str) -> float:
    if not budget_str:
        return 0.0
    numbers = re.findall(r"[\d,]+\.?\d*", budget_str)
    if not numbers:
        return 0.0
    vals = [float(n.replace(",", "")) for n in numbers]
    if len(vals) >= 2:
        return (vals[0] + vals[1]) / 2
    return vals[0]


def score_job(job: RawJob) -> int:
    score = 50

    budget_val = parse_budget(job.budget)
    if budget_val > 0:
        if budget_val >= 500:
            score += 15
        elif budget_val >= 200:
            score += 10
        elif budget_val >= 50:
            score += 5
        elif budget_val < 10:
            score -= 15

    if job.client_rating > 0:
        if job.client_rating >= 4.5:
            score += 15
        elif job.client_rating >= 4.0:
            score += 10
        elif job.client_rating >= 3.0:
            score += 5
        else:
            score -= 5

    if job.applicants == 0:
        score += 15
    elif job.applicants <= 5:
        score += 10
    elif job.applicants <= 15:
        score += 5
    elif job.applicants > 50:
        score -= 10

    desc_len = len(job.description or "")
    if desc_len > 200:
        score += 5
    elif desc_len < 30:
        score -= 5

    title_lower = (job.title or "").lower()
    if any(word in title_lower for word in ["urgent", "asap", "immediately", "need today"]):
        score += 5

    return max(0, min(100, score))


def score_jobs(jobs: list[RawJob]) -> list[tuple[RawJob, int]]:
    return [(job, score_job(job)) for job in jobs]
