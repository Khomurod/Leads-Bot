# Full Setup Guide — Facebook Leads → Telegram Bot

Follow every step in order. No tech experience needed.

---

## PART 1 — Get Your Telegram Chat ID

You need your personal Telegram ID so the bot knows where to send leads.

1. Open Telegram and search for **@userinfobot**
2. Press **Start**
3. It will reply with your user ID, e.g. `Id: 123456789`
4. Copy that number — this is your `TELEGRAM_CHAT_ID`

---

## PART 2 — Push Code to GitHub

You need the code on GitHub so Render can deploy it.

1. Go to [github.com](https://github.com) → click **New repository**
2. Name it `leads-bot`, leave it **Private**, click **Create**
3. Open a terminal in your `d:\SH\Leads-Bot` folder and run:

```bash
git add .
git commit -m "Initial leads bot"
git remote add origin https://github.com/YOUR_USERNAME/leads-bot.git
git push -u origin main
```

---

## PART 3 — Deploy on Render

1. Go to [render.com](https://render.com) → **Sign up / Log in** (free account is fine)
2. Click **New +** → **Web Service**
3. Connect your GitHub account → select your `leads-bot` repository
4. Render will auto-detect the settings from `render.yaml`. Confirm:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`
5. Scroll down to **Environment Variables** — add these one by one:

| Key | Value |
|-----|-------|
| `TELEGRAM_BOT_TOKEN` | `8626796769:AAE7e6PHADIlMnA0QNpnan196NYW007LyGc` |
| `TELEGRAM_CHAT_ID` | *(your ID from Part 1)* |
| `WEBHOOK_VERIFY_TOKEN` | `my_super_secret_verify_token_123` *(or any secret phrase you choose)* |
| `META_APP_SECRET` | *(from Part 4, Step 6)* |
| `META_PAGE_ACCESS_TOKEN` | *(from Part 4, Step 12)* |

6. Click **Create Web Service** — wait ~2 minutes for it to deploy
7. Copy your URL — it looks like: `https://leads-bot-xxxx.onrender.com`

---

## PART 4 — Set Up Facebook (Meta) App

This is the bridge that sends leads from Facebook to your bot.

### A. Create a Meta Developer Account

1. Go to [developers.facebook.com](https://developers.facebook.com)
2. Log in with your Facebook account
3. Click **Get Started** if you haven't used it before
4. Accept the terms

### B. Create a New App

1. Click **My Apps** → **Create App**
2. Choose **Business** as the app type → click **Next**
3. Give it a name (e.g. `Leads Webhook`) → click **Create App**

### C. Get Your App Secret

1. In your app dashboard, go to **Settings → Basic** (left sidebar)
2. Find **App Secret** → click **Show** → copy it
3. This is your `META_APP_SECRET` — add it to Render now

### D. Add the Leads Retrieval Product

1. In your app dashboard, click **Add Product** (left sidebar)
2. Find **Webhooks** → click **Set Up**
3. In the dropdown, choose **Page**
4. Click **Subscribe to this object**
5. Fill in:
   - **Callback URL:** `https://leads-bot-xxxx.onrender.com/webhook`  
     *(replace with your actual Render URL)*
   - **Verify Token:** `my_super_secret_verify_token_123`  
     *(must match `WEBHOOK_VERIFY_TOKEN` in Render)*
6. Click **Verify and Save** — Facebook will call your server and verify it ✅
7. Find **leadgen** in the list of fields → check its box → click **Subscribe**

### E. Get Your Page Access Token

1. In the left sidebar, click **Tools → Graph API Explorer**
2. In the top-right dropdown, select your **Facebook Page** (not your personal account)
3. Click **Generate Access Token** → grant all permissions
4. Copy the long token — this is your `META_PAGE_ACCESS_TOKEN`
5. Go to Render → your service → **Environment** → update `META_PAGE_ACCESS_TOKEN` → **Save** (Render will redeploy)

> ⚠️ **Important:** The default token expires in ~1 hour. To get a permanent (never-expiring) token:
> 1. Use Graph API Explorer — click **i** next to the token → click **Open in Access Token Tool**
> 2. Click **Extend Access Token** → copy the new long-lived token
> 3. Exchange it for a Page token that never expires using:  
>    `GET /YOUR_PAGE_ID?fields=access_token&access_token=LONG_LIVED_USER_TOKEN`  
>    (run this in Graph API Explorer)

---

## PART 5 — Test It

### Quick Verification Test

In your browser, open:
```
https://leads-bot-xxxx.onrender.com/webhook?hub.mode=subscribe&hub.verify_token=my_super_secret_verify_token_123&hub.challenge=hello
```
You should see: `hello`  
This means the server is running and the token matches ✅

### Test a Real Lead

1. In Meta for Developers → your App → **Leads Ads Testing Tool**  
   *(or search "Lead Ads Testing Tool" in the left sidebar)*
2. Select your **Page** and **Lead Form**
3. Click **Preview Form** → fill it out → submit
4. Within a few seconds you should receive a Telegram message from @wenzeleadbot 🎉

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Render not starting | Check the **Logs** tab in Render for errors |
| Verification failed | Make sure `WEBHOOK_VERIFY_TOKEN` in Render matches what you typed in Meta |
| No Telegram message | Check `META_PAGE_ACCESS_TOKEN` is valid and not expired |
| Bot sends but wrong chat | Double-check `TELEGRAM_CHAT_ID` using @userinfobot |
