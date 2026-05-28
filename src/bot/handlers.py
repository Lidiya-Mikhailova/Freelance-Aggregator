import html
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode

from src.db import get_job_by_id, save_translation, save_proposal, save_feedback, get_or_create_user, update_user_specialty, update_user_language
from src.ai import translate_to_ru, generate_proposal
from src.utils.config import SPECIALTIES, SPECIALTY_FLAT
from src.utils.languages import LANGUAGES


def _category_keyboard():
    rows = []
    for cat_key, cat in SPECIALTIES.items():
        rows.append([InlineKeyboardButton(f"{cat['emoji']} {cat['name']}", callback_data=f"cat|{cat_key}")])
    return InlineKeyboardMarkup(rows)


def _specialty_keyboard(cat_key: str):
    cat = SPECIALTIES[cat_key]
    rows = []
    for child_key, child in cat["children"].items():
        rows.append([InlineKeyboardButton(child["name"], callback_data=f"spec|{child_key}")])
    rows.append([InlineKeyboardButton("⬅️ Back to categories", callback_data="cat|")])
    return InlineKeyboardMarkup(rows)


def _language_keyboard():
    rows = []
    for code, lang in LANGUAGES.items():
        label = f"{lang['flag']} {lang['name']}" if code else lang["name"]
        rows.append([InlineKeyboardButton(label, callback_data=f"lang|{code}")])
    return InlineKeyboardMarkup(rows)


async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    if not q:
        return
    await q.answer()

    data = q.data or ""
    parts = data.split("|", 1)
    action = parts[0]
    value = parts[1] if len(parts) > 1 else ""

    if action == "cat":
        if value and value in SPECIALTIES:
            await q.message.edit_text(
                f"Choose your specialty in <b>{SPECIALTIES[value]['emoji']} {SPECIALTIES[value]['name']}</b>:",
                reply_markup=_specialty_keyboard(value),
                parse_mode=ParseMode.HTML,
            )
        else:
            await q.message.edit_text(
                "Choose your field:",
                reply_markup=_category_keyboard(),
            )
        return

    if action == "spec":
        if value and value in SPECIALTY_FLAT:
            spec = SPECIALTY_FLAT[value]
            cat = SPECIALTIES[spec["category_key"]]
            uid = str(q.from_user.id)
            update_user_specialty(uid, value)
            await q.message.edit_text(
                f"✅ Specialty saved!\n\n"
                f"{cat['emoji']} {cat['name']} → <b>{spec['name']}</b>\n\n"
                "From now on you'll receive relevant vacancies.\n"
                "Use /settings to change your specialty later.",
                parse_mode=ParseMode.HTML,
            )
        return

    if action == "langlist":
        await q.message.edit_text(
            "Choose your target language for vacancies:",
            reply_markup=_language_keyboard(),
        )
        return

    if action == "lang":
        if value in LANGUAGES:
            lang = LANGUAGES[value]
            uid = str(q.from_user.id)
            update_user_language(uid, value)
            label = f"{lang['flag']} {lang['name']}" if value else lang["name"]
            await q.message.edit_text(
                f"✅ Language set to {label}!\n\n"
                "New vacancies will be translated automatically.",
                parse_mode=ParseMode.HTML,
            )
        return

    try:
        job_id = int(value)
    except ValueError:
        await q.message.reply_text("Invalid job reference.")
        return

    job = get_job_by_id(job_id)
    if not job:
        await q.message.reply_text("Not found in cache. Wait for a new notification and try again.")
        return

    if action == "draft":
        msg = await q.message.reply_text("Generating proposal...")
        try:
            draft = await generate_proposal(job.title, job.description)
        except Exception:
            await msg.edit_text("Proposal generation failed. Check OpenAI API key.")
            return
        safe = html.escape(draft)
        await msg.edit_text(
            f"<b>Proposal</b>\n\n<pre>{safe}</pre>",
            parse_mode=ParseMode.HTML,
        )
        telegram_id = str(q.from_user.id)
        user = get_or_create_user(telegram_id)
        save_proposal(job_id, user.id, draft)

    elif action == "tr":
        if job.translated_ru:
            safe = html.escape(job.translated_ru)
            await q.message.reply_text(
                f"<b>Translation (RU)</b>\n\n<pre>{safe}</pre>",
                parse_mode=ParseMode.HTML,
            )
            return

        msg = await q.message.reply_text("Translating to Russian...")
        try:
            ru = await translate_to_ru(job.description or job.title)
        except Exception:
            await msg.edit_text("Translation failed. Check OpenAI API key.")
            return
        save_translation(job_id, ru)
        safe = html.escape(ru)
        await msg.edit_text(
            f"<b>Translation (RU)</b>\n\n<pre>{safe}</pre>",
            parse_mode=ParseMode.HTML,
        )

    elif action == "spam":
        telegram_id = str(q.from_user.id)
        user = get_or_create_user(telegram_id)
        save_feedback(job_id, user.id, reason="spam")
        await q.message.reply_text(
            "Thanks for the report. This helps improve the filters.",
        )


def get_callback_handler() -> CallbackQueryHandler:
    return CallbackQueryHandler(on_callback)
