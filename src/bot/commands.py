from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler
from telegram.constants import ParseMode

from src.db import get_or_create_user
from src.utils.config import CHECK_INTERVAL_SEC, FRESH_WINDOW_SEC, API_LIMIT, SPECIALTIES, SPECIALTY_FLAT
from src.utils.languages import LANGUAGES
from src.utils.analytics import get_stats
from src.db import get_feedback_stats
from src.bot.handlers import _category_keyboard, _language_keyboard


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    user = get_or_create_user(uid)

    lines = [f"Hi, {update.effective_user.first_name}! 👋\n"]

    if user.specialty and user.specialty in SPECIALTY_FLAT:
        spec = SPECIALTY_FLAT[user.specialty]
        cat = SPECIALTIES[spec["category_key"]]
        lines.append(f"Specialty: {cat['emoji']} {cat['name']} → {spec['name']}")
    else:
        lines.append("Specialty: not set")

    if user.target_language and user.target_language in LANGUAGES:
        lang = LANGUAGES[user.target_language]
        label = f"{lang['flag']} {lang['name']}" if user.target_language else lang["name"]
        lines.append(f"Language: {label}")
    else:
        lines.append("Language: English (no translation)")

    lines.append("\nUse /settings to change your preferences.")
    await update.message.reply_text("\n".join(lines))


async def cmd_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    user = get_or_create_user(uid)

    lines = ["<b>Settings</b>\n"]

    if user.specialty and user.specialty in SPECIALTY_FLAT:
        spec = SPECIALTY_FLAT[user.specialty]
        cat = SPECIALTIES[spec["category_key"]]
        lines.append(f"Specialty: {cat['emoji']} {cat['name']} → {spec['name']}")
    else:
        lines.append("Specialty: not set")

    if user.target_language and user.target_language in LANGUAGES:
        lang = LANGUAGES[user.target_language]
        label = f"{lang['flag']} {lang['name']}" if user.target_language else lang["name"]
        lines.append(f"Language: {label}")
    else:
        lines.append("Language: English (no translation)")

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Change Specialty", callback_data="cat|")],
        [InlineKeyboardButton("Change Language", callback_data="langlist|")],
    ])

    await update.message.reply_text(
        "\n".join(lines),
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Available commands:\n"
        "/start - Start the bot\n"
        "/settings - Change specialty and language\n"
        "/help - Show this help\n"
        "/status - Monitoring status\n"
        "/stats - Job statistics\n"
        "/feedback - Spam report stats\n",
    )


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    running = context.bot_data.get("running", False)
    last_check = context.bot_data.get("last_check", "Never")
    total_sent = context.bot_data.get("total_sent", 0)

    status_text = "Running" if running else "Stopped"
    await update.message.reply_text(
        f"Status: {status_text}\n"
        f"Last check: {last_check}\n"
        f"Jobs sent: {total_sent}\n",
    )


async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats = get_stats()
    await update.message.reply_text(
        f"<b>Statistics</b>\n\n"
        f"Jobs in DB: {stats['total_jobs']}\n"
        f"Average score: {stats['avg_score']}/100\n"
        f"Proposals generated: {stats['total_proposals']}\n"
        f"Users: {stats['total_users']}\n"
        f"Top source: {stats['top_source']}",
        parse_mode=ParseMode.HTML,
    )


async def cmd_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fstats = get_feedback_stats()
    await update.message.reply_text(
        f"<b>Feedback</b>\n\n"
        f"Total reports: {fstats['total_feedback']}\n"
        f"Marked as spam: {fstats['total_spam']}\n\n"
        "If a job is irrelevant or spam - "
        "click <b>Report</b> on the notification. "
        "This helps improve the filters.",
        parse_mode=ParseMode.HTML,
    )


def get_command_handlers() -> list:
    return [
        CommandHandler("start", cmd_start),
        CommandHandler("settings", cmd_settings),
        CommandHandler("help", cmd_help),
        CommandHandler("status", cmd_status),
        CommandHandler("stats", cmd_stats),
        CommandHandler("feedback", cmd_feedback),
    ]
