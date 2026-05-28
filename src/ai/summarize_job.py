from openai import AsyncOpenAI

from src.utils.config import OPENAI_API_KEY

_client = AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


async def summarize_job(title: str, description: str, budget: str, client_rating: float, applicants: int) -> str | None:
    if not _client:
        return None

    prompt = (
        f"Analyze this freelance job and give a short summary with recommendation.\n\n"
        f"Title: {title}\n"
        f"Description: {description[:800]}\n"
        f"Budget: {budget}\n"
        f"Client rating: {client_rating}\n"
        f"Applicants: {applicants}\n\n"
        "Respond in this format:\n"
        "Client: [assessment]\n"
        "Budget: [assessment]\n"
        "Competition: [assessment]\n\n"
        "Recommendation: [Apply/Skip/Consider]"
    )

    try:
        resp = await _client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return None
