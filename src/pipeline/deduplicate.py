from src.collectors.base import RawJob


def deduplicate(jobs: list[RawJob]) -> list[RawJob]:
    seen_ids = set()
    unique = []
    for job in jobs:
        key = f"{job.source}:{job.external_id}"
        if key not in seen_ids:
            seen_ids.add(key)
            unique.append(job)
    return unique
