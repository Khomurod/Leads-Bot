# Full Setup Guide — Facebook Leads → Telegram Bot

> This documents the **exact steps** used to set up the live integration.
> Follow in order if you ever need to rebuild from scratch.

---

## Credentials Reference

| Key | Value |
|-----|-------|
| Render URL | `https://leads-bot-e6x5.onrender.com` |
| Render Service ID | `srv-d6h0q3haae7s73epqf2g` |
| Meta App ID | `1493927455591564` |
| Meta App Secret | `174654afba5dc1a3ccdc3afcdbd4d6ca` |
| Meta App Name | LeadsBot |
| Facebook Page | Wenze Transportation Sevices |
| Page ID | `1012150671970890` |
| Business ID | `1373179280914689` |
| Business Name | Wenze |
| System User | `wenzeleadsbot` (Admin) |
| Webhook Verify Token | `my_super_secret_verify_token_123` |
| Telegram Bot | @WenzeLeadBots |
| Telegram Chat ID | `2117922421` |

---

## PART 1 — Deploy on Render

1. Go to [render.com](https://render.com) → New → **Web Service**
2. Connect GitHub → select `Leads-Bot` repository
3. Render auto-reads `render.yaml`. Confirm settings:
   - **Build:** `pip install -r requirements.txt`
   - **Start:** `python main.py`
4. Add **Environment Variables**:

| Key | Value |
|-----|-------|
| `TELEGRAM_BOT_TOKEN` | *(from @BotFather)* |
| `TELEGRAM_CHAT_ID` | `2117922421` |
| `WEBHOOK_VERIFY_TOKEN` | `my_super_secret_verify_token_123` |
| `META_APP_SECRET` | `174654afba5dc1a3ccdc3afcdbd4d6ca` |
| `META_PAGE_ACCESS_TOKEN` | *(generate in Part 3)* |

5. Click **Create Web Service** — wait ~2 min for deploy
6. Note your URL: `https://leads-bot-xxxx.onrender.com`

---

## PART 2 — Create & Configure Meta App

### A. Create the App

1. Go to [developers.facebook.com](https://developers.facebook.com)
2. Click **My Apps → Create App**
3. Select **Other** → **Business** → Next
4. Name: `LeadsBot`, Business: `Wenze` → Create

### B. Add Webhooks Product

1. Dashboard → **Add Product** → find **Webhooks** → Set Up
2. Dropdown → select **Page** → Subscribe to this object
3. Fill in:
   - **Callback URL:** `https://leads-bot-e6x5.onrender.com/webhook`
   - **Verify Token:** `my_super_secret_verify_token_123`
4. Click **Verify and Save** ✅
5. Find **leadgen** in the field list → click **Subscribe**

### C. Fill Required App Settings

1. Go to **Settings → Basic**
2. Fill in:
   - **Privacy Policy URL:** `https://wenzeinvestments.com/privacy-policy.html`
   - **Category:** Business and Pages
   - Upload an App Icon
3. Click **Save Changes**

### D. Publish App to Live Mode

> ⚠️ **Critical:** In Development mode, Facebook will NOT deliver webhooks for real leads (only for app admins). You MUST publish to Live mode.

1. Left sidebar → **App Review → Publish**
2. Click **Make Live** or **Publish**
3. Confirm: "Your app was successfully published" 🎉

---

## PART 3 — Generate Never-Expiring Page Access Token

> Regular user tokens expire in 1 hour. Use a **System User** for a permanent token.

### A. Create System User

1. Go to [business.facebook.com](https://business.facebook.com)
2. Settings (gear icon) → **System Users** (under Users section)
3. Click **Add** → Name: `wenzeleadsbot`, Role: **Admin** → Create
4. Click **Add Assets** → Pages → select **Wenze Transportation Sevices**
5. Enable **Full Control** → Save

### B. Assign the App

1. System Users → `wenzeleadsbot` → **Assign Assets**
2. Select **Apps** → find **LeadsBot** → toggle to enable → Save

### C. Generate Token

1. System Users → `wenzeleadsbot` → **Generate New Token**
2. Select App: **LeadsBot**
3. Select permissions (add ALL of these):
   - `leads_retrieval`
   - `pages_manage_metadata`
   - `pages_read_engagement`
   - `pages_show_list`
4. Click **Generate Token** → copy it immediately
5. Go to Render → Environment → update `META_PAGE_ACCESS_TOKEN` → Save → Redeploy

---

## PART 4 — Subscribe App to Page Webhook

This tells Facebook to send lead events from the Wenze page to LeadsBot.

1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select App: **LeadsBot**
3. Select token: the System User token (`META_PAGE_ACCESS_TOKEN`)
4. Change method to **POST**, path to: `1012150671970890/subscribed_apps`
5. Add parameter: `subscribed_fields` = `leadgen`
6. Click **Submit** → should return `{"success": true}` ✅

To verify:
- Method: **GET**, path: `1012150671970890/subscribed_apps`
- Should show LeadsBot subscribed to `leadgen`

---

## PART 5 — Lead Access Manager

> Without this step, leads show as "Failure: CRM access has been revoked."

1. Go to **Business Settings** (business.facebook.com → gear icon)
2. Left sidebar → **Integrations → Leads Access**
3. Find **Wenze Transportation Sevices** → click **Details**
4. Click the **CRMs** tab
5. Click **Assign CRM** → select **LeadsBot** → Confirm ✅

---

## PART 6 — Test the Integration

1. Go to [Lead Ads Testing Tool](https://developers.facebook.com/tools/lead-ads-testing)
2. Select page: **Wenze Transportation Sevices**
3. Check **Page Diagnostics** — LeadsBot should show a green ✅ (not ⚠️)
4. Select Product: **Lead Retrieval**, Form: **Company Driver EN**
5. Click **Delete lead** (if existing), then **Create lead**
6. Click **Track status** — LeadsBot should show **Success**
7. Check Telegram — message should arrive within seconds 🎉

---

## PART 7 — Keep-Alive (Anti-Sleep)

Render Free tier sleeps after 15 minutes of inactivity, causing the first lead to be missed.

**Using cron-job.org (fastest to set up):**

1. Sign up at [cron-job.org](https://cron-job.org)
2. Create Cronjob:
   - Title: `LeadsBot Ping`
   - URL: `https://leads-bot-e6x5.onrender.com/health`
   - Schedule: every **10 minutes**
3. Save

**Using Koyeb:**

1. New Service → Docker → Image: `alpine:latest`
2. Command: `sh -c "while true; do wget -qO- https://leads-bot-e6x5.onrender.com/health; sleep 600; done"`
3. Deploy

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Lead "Pending" forever | App was in Development mode → publish to Live mode |
| "CRM access revoked" failure | Add LeadsBot to Lead Access Manager (Part 5) |
| No webhook received on Render | Service was sleeping → ping `/health` to wake up, then retry lead |
| Telegram 401 Unauthorized | Token revoked → regenerate via @BotFather, update Render env var |
| `KeyError: 'values'` | Old bug, fixed in graph.py → fields now use `.get()` safely |
| Wenze page not in System User dropdown | Make sure System User has the page assigned as an asset |
| Webhook verify failed | Check `WEBHOOK_VERIFY_TOKEN` matches exactly in both Render and Meta |

## Retry a Failed Lead

If any lead fails, call the retry endpoint directly:

```
https://leads-bot-e6x5.onrender.com/retry/{LEAD_ID}
```

Example:
```
https://leads-bot-e6x5.onrender.com/retry/909818275177706
```

Expected: `{"status":"ok","lead_id":"...","result":"sent_ok"}`
