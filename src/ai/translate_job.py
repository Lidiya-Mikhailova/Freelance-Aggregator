from openai import AsyncOpenAI

from src.utils.config import OPENAI_API_KEY

_client = AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


async def translate_to_ru(text_en: str) -> str:
    if not _client:
        return "AI API key not configured."
    try:
        prompt = (
            "Translate to Russian. Keep it concise, natural, and professional. "
            "Do not add anything that isn't in the original.\n\n"
            f"TEXT:\n{text_en}"
        )
        resp = await _client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return "Translation unavailable. Check AI API key."
