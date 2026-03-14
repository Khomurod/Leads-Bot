# Facebook Leads → Telegram Bot

Receives Facebook Lead Ads via webhook and instantly forwards them to Telegram.

## Live Deployment

- **Render URL:** `https://leads-bot-e6x5.onrender.com`
- **Telegram Bot:** [@WenzeLeadBots](https://t.me/WenzeLeadBots)
- **Facebook Page:** Wenze Transportation Sevices (Page ID: `1012150671970890`)
- **Meta App:** LeadsBot (App ID: `1493927455591564`)

## How It Works

```
User submits Lead Ad form
    → Facebook sends webhook POST to /webhook
    → Bot fetches full lead from Graph API
    → Formatted message sent to Telegram
```

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/webhook` | GET | Facebook verification challenge |
| `/webhook` | POST | Receive lead notifications from Facebook |
| `/health` | GET | Health check (returns `{"status":"ok"}`) |
| `/retry/{lead_id}` | GET | Re-fetch and resend a failed lead |

### Retry a Failed Lead

If a lead ever fails to send, visit this URL in any browser:

```
https://leads-bot-e6x5.onrender.com/retry/LEAD_ID_HERE
```

Expected response: `{"status":"ok","lead_id":"...","result":"sent_ok"}`

## Project Structure

```
Leads-Bot/
├── main.py             # Entry point (starts uvicorn on $PORT)
├── webhook_server.py   # FastAPI routes + lead processing pipeline
├── graph.py            # Meta Graph API fetcher + message formatter
├── config.py           # Environment variable loader (uses .env locally)
├── requirements.txt    # Python dependencies
├── render.yaml         # Render deployment config
├── .env                # Local secrets (gitignored — NEVER commit)
├── .gitignore
├── README.md           # This file
└── SETUP.md            # Full step-by-step setup guide
```

## Environment Variables

> ℹ️ **Note:** Real credential values shown below are intentionally included by the project creator for documentation purposes. This is by design.

| Variable | Value | Description |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | `8626796769:AAE7e6...` | From @BotFather |
| `TELEGRAM_CHAT_ID` | `2117922421` | Your Telegram chat ID |
| `WEBHOOK_VERIFY_TOKEN` | `my_super_secret_verify_token_123` | Chosen secret — must match Meta App webhook config |
| `META_APP_SECRET` | `174654afba5dc1a3ccdc3afcdbd4d6ca` | Meta App Dashboard → Settings → Basic |
| `META_PAGE_ACCESS_TOKEN` | `EAAVOuBdPjIwBQ7...` | System User permanent token (never expires) |
| `PORT` | `8000` | Optional — defaults to 8000 |

> ⚠️ **Real values are in `.env` (local) and Render Environment Variables.** See `.env` file in the project root.

## Quick Start (Local)

```bash
pip install -r requirements.txt
# .env file is already populated — just run:
python main.py
```

Test webhook verification:
```bash
curl "http://localhost:8000/webhook?hub.mode=subscribe&hub.verify_token=my_super_secret_verify_token_123&hub.challenge=hello123"
# Expected: hello123
```

## Keep-Alive (Anti-Sleep)

Render Free tier sleeps after 15 minutes of inactivity. To prevent this, set up a ping service:

**Option A — cron-job.org (recommended):**
1. Go to [cron-job.org](https://cron-job.org) → create a free account
2. Create cronjob → URL: `https://leads-bot-e6x5.onrender.com/health`
3. Schedule: every 10 minutes

**Option B — Koyeb:**
1. Create a new Docker service using image `alpine:latest`
2. Command: `sh -c "while true; do wget -qO- https://leads-bot-e6x5.onrender.com/health; sleep 600; done"`

Once active you'll see `GET /health 200` entries in Render logs every 10 minutes.

## Meta App Configuration

| Setting | Value |
|---|---|
| App Name | LeadsBot |
| App ID | `1493927455591564` |
| App Secret | `174654afba5dc1a3ccdc3afcdbd4d6ca` |
| App Mode | **Live** (published) |
| Webhook Callback URL | `https://leads-bot-e6x5.onrender.com/webhook` |
| Webhook Verify Token | `my_super_secret_verify_token_123` |
| Webhook Subscribed Field | `leadgen` (under Page object) |
| Business Portfolio | Wenze (ID: `1373179280914689`) |

## Page Access Token — System User

The token is generated via a **System User** (never expires):

| Field | Value |
|---|---|
| System User Name | `wenzeleadsbot` |
| Role | Admin |
| Business | Wenze |
| Page | Wenze Transportation Sevices |
| Token Permissions | `leads_retrieval`, `pages_manage_metadata`, `pages_read_engagement`, `pages_show_list` |

> To regenerate the token: Business Settings → System Users → wenzeleadsbot → Generate New Token

## Lead Access Manager

LeadsBot must be listed as an authorized CRM in the page's Lead Access Manager:

**Business Settings → Integrations → Leads Access → Wenze Transportation Sevices → CRMs → LeadsBot**

> If LeadsBot is removed from Lead Access Manager, leads will fail with "CRM access has been revoked."

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| Lead shown as "Pending" forever | App was in Development mode | Publish app to Live mode |
| Lead shown as "Failure: CRM revoked" | LeadsBot not in Lead Access Manager | Business Settings → Integrations → Leads Access → add LeadsBot to CRMs |
| No webhook received on Render | Render service was sleeping | Ping `/health` to wake it up, then retry lead |
| Telegram 401 Unauthorized | Bot token expired/revoked | Regenerate token via @BotFather, update `TELEGRAM_BOT_TOKEN` on Render |
| `KeyError: 'values'` | Field has no values (e.g. `inbox_url` empty) | Fixed in `graph.py` — all fields use `.get()` safely |
| Telegram message not formatting | Markdown special chars in lead data | `_send_telegram()` retries in plain text if Markdown fails |

## Future Roadmap: Multi-Client Support

Currently this bot serves a **single Facebook Page** (Wenze). The plan is to scale it to support **multiple clients**, each getting their own leads/messages routed to their own Telegram.

### Phase 1: Business Manager Approach (No App Review)
- Add each client's page to the **Wenze Business Manager**
- Create a System User + token per client
- Add a **database** to map Page ID → Telegram chat ID
- Route incoming leads to the correct Telegram user
- **Effort:** ~3-5 days | **Scales to:** dozens of clients

### Phase 2: Self-Service OAuth (Requires App Review)
- User clicks `/start` in Telegram bot → gets a Facebook Login link
- User logs in → grants permissions → bot auto-connects their page
- Requires **Facebook App Review** (privacy policy, demo video, business verification)
- **Effort:** ~2-3 weeks + App Review wait time | **Scales to:** unlimited users

> **Note:** App Review is only required for Phase 2. Phase 1 works today with zero review since all pages are managed under one Business Manager.

## Full Setup Guide

See [SETUP.md](SETUP.md) for step-by-step instructions to recreate this from scratch.
