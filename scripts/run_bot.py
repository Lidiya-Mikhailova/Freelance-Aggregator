import asyncio
import html as html_module
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import BotCommand
from telegram.ext import ApplicationBuilder

from src.utils.config import TELEGRAM_TOKEN
from src.utils.logger import setup_logger
from src.bot.commands import get_command_handlers
from src.bot.handlers import get_callback_handler
from src.workers import run_monitoring

logger = setup_logger("bot")

LOCK_FILE = "bot.pid"


def _acquire_lock() -> int | None:
    try:
        if os.path.exists(LOCK_FILE):
            with open(LOCK_FILE) as f:
                old_pid = int(f.read().strip())
            try:
                os.kill(old_pid, 0)
                logger.error(
                    f"Bot already running (PID {old_pid}). "
                    f"Delete {LOCK_FILE} if stuck."
                )
                return None
            except OSError:
                pass
        pid = os.getpid()
        with open(LOCK_FILE, "w") as f:
            f.write(str(pid))
        return pid
    except Exception as e:
        logger.warning(f"Lock file error: {e}")
        return os.getpid()


def _release_lock():
    try:
        if os.path.exists(LOCK_FILE):
            with open(LOCK_FILE) as f:
                if f.read().strip() == str(os.getpid()):
                    os.remove(LOCK_FILE)
    except Exception:
        pass


async def main():
    pid = _acquire_lock()
    if pid is None:
        sys.exit(1)

    if not TELEGRAM_TOKEN:
        _release_lock()
        raise RuntimeError("Set TELEGRAM_TOKEN in .env")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    for handler in get_command_handlers():
        app.add_handler(handler)

    app.add_handler(get_callback_handler())

    try:
        async with app:
            await app.initialize()
            await app.start()

            commands = [
                BotCommand("start", "Start the bot"),
                BotCommand("settings", "Change specialty and language"),
                BotCommand("help", "Show help"),
                BotCommand("status", "Monitoring status"),
                BotCommand("stats", "Job statistics"),
                BotCommand("feedback", "Spam report stats"),
            ]
            await app.bot.set_my_commands(commands)

            await app.updater.start_polling(drop_pending_updates=True)

            app.create_task(run_monitoring(app))

            logger.info("Bot is running...")
            await asyncio.Event().wait()
    finally:
        _release_lock()


if __name__ == "__main__":
    asyncio.run(main())
