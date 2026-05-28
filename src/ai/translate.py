import asyncio
import hashlib

from deep_translator import GoogleTranslator

from src.db import get_cached_translation, save_translation_cache

_memory_cache: dict[str, str] = {}


async def get_translation(job_id: int, text: str, target_lang: str) -> str:
    if not text or not target_lang:
        return text

    text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
    cache_key = f"{job_id}:{target_lang}:{text_hash}"
    cached = _memory_cache.get(cache_key)
    if cached:
        return cached

    db_cached = get_cached_translation(job_id, target_lang, text_hash)
    if db_cached:
        _memory_cache[cache_key] = db_cached
        return db_cached

    translated = await asyncio.to_thread(
        GoogleTranslator(source="auto", target=target_lang).translate, text
    )
    if translated:
        translated = translated.strip()
        _memory_cache[cache_key] = translated
        save_translation_cache(job_id, target_lang, text_hash, translated)
        return translated

    return text
