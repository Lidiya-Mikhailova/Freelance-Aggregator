from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def job_keyboard(job_db_id: int, url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Open Job", url=url)],
        [
            InlineKeyboardButton("Proposal", callback_data=f"draft|{job_db_id}"),
            InlineKeyboardButton("Translate", callback_data=f"tr|{job_db_id}")
        ],
        [
            InlineKeyboardButton("Report", callback_data=f"spam|{job_db_id}")
        ],
    ])
