# Freelance Aggregator

Telegram bot that scrapes freelance projects from Freelancer.com, filters them by specialty, and sends personalized notifications with AI-powered analysis, translation, and proposal generation.

## Features

- **Specialty-based Subscriptions** — pick your IT/Design/Marketing/Writing/Admin specialty at `/start`, receive only relevant jobs
- **Real-time Alerts** — notified about new projects within minutes
- **Multi-user** — each user chooses their own specialty and language
- **Auto-Translation** — jobs auto-translated to RU, KK, ES, DE, FR, PT, ZH, AR, TR, PL, IT via deep-translator with DB cache
- **AI Proposal Generator** — generate professional bids via OpenAI GPT
- **AI Job Summary** — quick analysis and recommendations for each job
- **Spam Reporting** — mark irrelevant jobs to improve filters


## Architecture

```
Freelancer.com → Collectors → Pipeline (filter per specialty) → DB → AI → Telegram per-user
```

## Project Structure

```
src/
  collectors/     — Freelancer.com API integration
  pipeline/       — per-specialty filter, deduplicate, scoring
  bot/            — handlers, commands, keyboards
  ai/             — translate, summarize, proposal (OpenAI GPT)
  db/             — SQLAlchemy models (User, Job, Proposal, Feedback)
  workers/        — background monitoring loop
  utils/          — config, logger, analytics
scripts/          — CLI entry points
data/             — SQLite DB, raw/processed/analytics output
```

## Setup

1. Clone and configure `.env`:
   ```bash
   cp .env.example .env
   ```

2. Create virtual environment and install dependencies:
   ```bash
   python3 -m venv .venv
   .venv/bin/python -m pip install -r requirements.txt
   ```

3. Run the bot (from project root — always use `.venv/bin/python` directly):
   ```bash
   .venv/bin/python scripts/run_bot.py
   ```

## Docker

```bash
docker compose -p jobbot up -d --build
```

## Environment Variables

| Variable | Description |
|---|---|
| `TELEGRAM_TOKEN` | Telegram bot token |
| `TG_CHAT_ID` | Admin chat ID for startup notifications |
| `OPENAI_API_KEY` | OpenAI API key |
| `FLN_OAUTH_TOKEN` | Freelancer.com API OAuth token |
| `DATABASE_URL` | Database connection string |
| `CHECK_INTERVAL_SEC` | Monitoring interval (default: 300) |
| `FRESH_WINDOW_SEC` | Job freshness window (default: 86400) |

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and choose specialty |
| `/settings` | Change specialty and language |
| `/help` | Show command list |
| `/status` | Show monitoring status |
| `/stats` | Show database statistics |
| `/feedback` | Show spam/feedback statistics |
