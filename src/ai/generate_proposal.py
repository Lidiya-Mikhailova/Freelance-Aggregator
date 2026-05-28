from openai import AsyncOpenAI

from src.utils.config import OPENAI_API_KEY

_client = AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


async def generate_proposal(title: str, description: str) -> str:
    if not _client:
        return "AI API key not configured."
    try:
        prompt = (
            f"Write a professional bid for: '{title}'. Details: {description[:800]}. "
            "Expertise: Specialized data automation systems for cleaning, merging, and formatting. "
            "Focus: Preserving special characters, formatting, and zero duplicates. "
            "STRICTLY FORBIDDEN: Do not mention GitHub or being a developer. "
            "Role: Data Specialist / Automation Expert. "
            "Tone: Business professional. Language: English. Concise."
        )
        resp = await _client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return "Proposal generation unavailable. Check AI API key."
