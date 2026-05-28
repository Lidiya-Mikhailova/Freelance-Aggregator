import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.collectors import collect_all
from src.pipeline import deduplicate, filter_jobs, score_jobs


def main():
    print("Running pipeline...")

    raw_jobs = collect_all()
    print(f"Raw: {len(raw_jobs)}")

    unique = deduplicate(raw_jobs)
    print(f"Unique: {len(unique)}")

    filtered = filter_jobs(unique)
    print(f"Filtered: {len(filtered)}")

    scored = score_jobs(filtered)
    scored.sort(key=lambda x: x[1], reverse=True)

    os.makedirs("data/processed", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"data/processed/jobs_{timestamp}.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump([
            {
                "title": j.title,
                "budget": j.budget,
                "url": j.url,
                "score": s,
                "client_rating": j.client_rating,
                "applicants": j.applicants,
            }
            for j, s in scored
        ], f, indent=2, ensure_ascii=False)

    print(f"\nTop jobs:")
    for job, score in scored[:10]:
        print(f"  Score: {score}/100 | {job.title[:60]} | Budget: {job.budget}")

    print(f"\nSaved to {output_path}")


if __name__ == "__main__":
    main()
