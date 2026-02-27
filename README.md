# Facebook Leads → Telegram Bot (@wenzeleadbot)

Receives Facebook Lead Ads via a webhook and instantly forwards them to your Telegram.

## How It Works

1. Someone fills out your Facebook Lead Ad form
2. Facebook sends the lead data to this bot's webhook URL
3. The bot fetches the full lead details from the Meta Graph API
4. A formatted message is sent to your Telegram

## Project Structure

```
leads-bot/
├── main.py             # Entry point (starts uvicorn)
├── webhook_server.py   # FastAPI routes (GET + POST /webhook)
├── graph.py            # Meta Graph API fetcher + message formatter
├── config.py           # Environment variable loader
├── requirements.txt
├── render.yaml         # Render deployment config
└── .env.example        # Template for all required secrets
```

## Quick Start (Local)

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in your real values
python main.py
```

Test webhook verification:
```bash
curl "http://localhost:8000/webhook?hub.mode=subscribe&hub.verify_token=my_super_secret_verify_token_123&hub.challenge=hello123"
# Expected: hello123
```

## Environment Variables

| Variable | Description |
|---|---|
| `TELEGRAM_BOT_TOKEN` | From @BotFather |
| `TELEGRAM_CHAT_ID` | Your Telegram user/group ID |
| `WEBHOOK_VERIFY_TOKEN` | Any secret string you choose |
| `META_APP_SECRET` | From Meta App → Settings → Basic |
| `META_PAGE_ACCESS_TOKEN` | Your Facebook Page access token |

## Deployment → Render

See the full step-by-step guide in [SETUP.md](SETUP.md).

## Getting Your Telegram Chat ID

1. Message [@userinfobot](https://t.me/userinfobot) on Telegram
2. It will reply with your user ID — that's your `TELEGRAM_CHAT_ID`
