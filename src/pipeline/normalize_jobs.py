import re

from src.collectors.base import RawJob
from src.utils.config import KEYWORDS, STOP_WORDS, SPECIALTY_FLAT, DEBUG_MATCH


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip().casefold()


def explain_match(title: str, snippet: str, keywords: list[str] | None = None, stop_words: list[str] | None = None) -> tuple[bool, str]:
    full = norm(f"{title} {snippet}")

    sw = stop_words if stop_words is not None else STOP_WORDS
    kw = keywords if keywords is not None else KEYWORDS

    hit_stops = [s for s in sw if norm(s) in full]
    if hit_stops:
        return False, f"STOP: {hit_stops[:5]}"

    hit_keys = [k for k in kw if norm(k) in full]
    if not hit_keys:
        return False, "NO_KEYWORDS"

    return True, f"OK: {hit_keys[:6]}"


def filter_jobs(jobs: list[RawJob], specialty: str | None = None) -> list[RawJob]:
    if specialty and specialty in SPECIALTY_FLAT:
        spec = SPECIALTY_FLAT[specialty]
        kw = spec["keywords"]
        sw = spec["stop_words"]
    else:
        kw = None
        sw = None

    filtered = []
    for job in jobs:
        ok, why = explain_match(job.title, job.description, keywords=kw, stop_words=sw)
        if DEBUG_MATCH:
            tag = specialty or "default"
            print(f"[{tag}] {'PASS' if ok else 'SKIP'} {job.title[:80]} | {why}")
        if ok:
            filtered.append(job)
    return filtered


def filter_jobs_for_all_specialties(jobs: list[RawJob]) -> dict[str, list[RawJob]]:
    result = {}
    for spec_key in SPECIALTY_FLAT:
        matched = filter_jobs(jobs, specialty=spec_key)
        if matched:
            result[spec_key] = matched
    return result
