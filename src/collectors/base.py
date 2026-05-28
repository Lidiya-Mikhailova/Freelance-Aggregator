from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class RawJob:
    source: str
    external_id: str
    title: str
    description: str
    budget: str
    url: str
    client_rating: float = 0.0
    applicants: int = 0
    submitted_at: Optional[int] = None
    raw_data: Optional[dict] = None
