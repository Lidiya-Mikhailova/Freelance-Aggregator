import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.collectors import collect_all


def main():
    print("Running collectors...")
    jobs = collect_all()
    print(f"Collected {len(jobs)} jobs")

    os.makedirs("data/raw", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"data/raw/jobs_{timestamp}.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump([
            {
                "source": j.source,
                "external_id": j.external_id,
                "title": j.title,
                "description": j.description,
                "budget": j.budget,
                "url": j.url,
                "client_rating": j.client_rating,
                "applicants": j.applicants,
            }
            for j in jobs
        ], f, indent=2, ensure_ascii=False)

    print(f"Saved to {output_path}")


if __name__ == "__main__":
    main()
