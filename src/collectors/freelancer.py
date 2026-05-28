import time
from typing import List, Optional

from freelancersdk.session import Session
from freelancersdk.resources.projects.projects import search_projects
from freelancersdk.resources.projects.helpers import create_search_projects_filter

from src.collectors.base import RawJob
from src.utils.config import FLN_OAUTH_TOKEN, FLN_URL, FRESH_WINDOW_SEC, API_LIMIT, SNIPPET_LIMIT_MODEL, SEARCH_QUERY, SEARCH_JOBS


def clamp_text(s: str, n: int) -> str:
    import re
    s = re.sub(r"\s+", " ", (s or "")).strip()
    return s[:n]


def safe_project_url(project_id: int, seo_url: Optional[str]) -> str:
    import re
    base = FLN_URL.rstrip("/")

    if seo_url:
        if seo_url.startswith(("http://", "https://")):
            if str(project_id) in seo_url or re.search(r"\d{6,}", seo_url):
                return seo_url
        else:
            candidate = base + "/" + seo_url.lstrip("/")
            if str(project_id) in candidate or re.search(r"\d{6,}", candidate):
                return candidate

    return f"{base}/projects/{project_id}"


def fetch_freelancer_jobs(since_time: int | None = None) -> List[RawJob]:
    session = Session(oauth_token=FLN_OAUTH_TOKEN, url=FLN_URL)

    now = int(time.time())

    job_ids = [int(x.strip()) for x in SEARCH_JOBS.split(",") if x.strip().isdigit()] if SEARCH_JOBS else None

    search_filter = create_search_projects_filter(
        from_time=now - FRESH_WINDOW_SEC,
        sort_field="time_updated",
        reverse_sort=True,
        jobs=job_ids,
    )

    res = search_projects(
        session=session,
        query=SEARCH_QUERY,
        search_filter=search_filter,
        limit=API_LIMIT,
        offset=0,
        active_only=True,
    )

    projects_data = []
    if isinstance(res, dict):
        projects_data = res.get("projects") or res.get("result", {}).get("projects") or []
    elif hasattr(res, "projects"):
        projects_data = res.projects

    out: List[RawJob] = []
    for pr in projects_data:
        pid = pr.get("id") or pr.get("project_id")
        if not pid:
            continue
        pid = int(pid)

        title = (pr.get("title") or "").strip()
        descr = (pr.get("preview_description") or pr.get("description") or "").strip()
        snippet = clamp_text(descr, SNIPPET_LIMIT_MODEL)

        submit_ts = pr.get("submitdate") or pr.get("time_submitted") or pr.get("time_created")
        try:
            submit_ts = int(submit_ts) if submit_ts is not None else None
        except Exception:
            submit_ts = None

        budget = pr.get("budget") or pr.get("budget_details") or ""
        if isinstance(budget, dict):
            budget = str(budget.get("minimum", "") or "")
            if budget and pr.get("budget", {}).get("maximum"):
                budget += f" - {pr['budget']['maximum']}"

        url = safe_project_url(pid, pr.get("seo_url"))

        client_info = pr.get("owner") or {}
        client_rating = 0.0
        if isinstance(client_info, dict):
            client_rating = float(client_info.get("rating") or client_info.get("reputation") or 0.0)

        upgrades = pr.get("upgrades") or {}
        applicants = 0
        if isinstance(upgrades, dict):
            active = upgrades.get("active_entries")
            if active is not None:
                applicants = int(active)
            contestants = upgrades.get("contest_entries")
            if contestants is not None:
                applicants = int(contestants)

        out.append(RawJob(
            source="freelancer",
            external_id=str(pid),
            title=title,
            description=snippet,
            budget=str(budget),
            url=url,
            client_rating=client_rating,
            applicants=applicants,
            submitted_at=submit_ts,
            raw_data=pr,
        ))

    return out
