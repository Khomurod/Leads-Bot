"""
FastAPI webhook server.
- GET  /webhook  → Facebook verification challenge
- POST /webhook  → Receive lead notifications
- GET  /health   → Render health check
"""
import hashlib
import hmac
import json
import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse

from config import META_APP_SECRET, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, WEBHOOK_VERIFY_TOKEN
from graph import fetch_lead, format_lead_message

import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Leads Webhook")


def _verify_signature(payload: bytes, signature_header: str) -> bool:
    """Validate X-Hub-Signature-256 header from Facebook."""
    if not signature_header.startswith("sha256="):
        return False
    expected = hmac.new(
        META_APP_SECRET.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature_header[7:])


async def _send_telegram(text: str) -> None:
    """Send a message to Telegram via Bot API."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
    }
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(url, json=payload)
        if not resp.is_success:
            logger.error("Telegram send failed: %s", resp.text)
        else:
            logger.info("Telegram message sent successfully.")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/webhook")
async def verify_webhook(request: Request):
    """Facebook webhook verification (GET)."""
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == WEBHOOK_VERIFY_TOKEN:
        logger.info("Webhook verified successfully.")
        return PlainTextResponse(challenge)

    logger.warning("Webhook verification failed. token=%s", token)
    raise HTTPException(status_code=403, detail="Verification failed")


@app.post("/webhook")
async def receive_webhook(request: Request):
    """Facebook lead notification (POST)."""
    body = await request.body()

    # Verify signature
    sig = request.headers.get("X-Hub-Signature-256", "")
    if META_APP_SECRET and not _verify_signature(body, sig):
        logger.warning("Invalid signature — rejecting webhook.")
        raise HTTPException(status_code=403, detail="Invalid signature")

    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Bad JSON")

    logger.info("Webhook received: %s", data)

    if data.get("object") != "page":
        return {"status": "ignored"}

    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            if change.get("field") != "leadgen":
                continue
            value = change.get("value", {})
            leadgen_id = value.get("leadgen_id")
            if not leadgen_id:
                continue

            logger.info("New lead ID: %s", leadgen_id)

            try:
                lead_data = await fetch_lead(leadgen_id)
                message = format_lead_message(lead_data)
                await _send_telegram(message)
            except Exception as exc:
                logger.error("Error processing lead %s: %s", leadgen_id, exc)
                # Notify anyway with minimal info
                await _send_telegram(
                    f"🔔 *New Facebook Lead!*\n🆔 Lead ID: `{leadgen_id}`\n⚠️ Could not fetch details: {exc}"
                )

    return {"status": "ok"}
