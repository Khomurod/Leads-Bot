# SMS Auto-Response Feature (RingCentral)

> **Status:** Planned — not yet implemented
> **Effort:** ~1-2 hours
> **Risk to existing code:** Zero

---

## Overview

When a new lead comes in (Lead Ad form OR Messenger), the bot will **automatically send an SMS** to the lead's phone number within seconds:

> *"Hello {name}, this is Tom with Wenze trucking company and thanks for applying to our OTR position. Can I call you right now to explain the details?"*

This happens **after** the Telegram notification, so existing functionality is untouched.

---

## Flow

```
Lead submits form / messages page
    → Facebook webhook fires
    → Bot fetches lead data from Graph API        ← existing
    → Bot sends Telegram notification             ← existing
    → Bot extracts phone number from lead data    ← NEW
    → Bot sends SMS via RingCentral API           ← NEW
```

If the SMS fails for any reason (no phone, invalid number, API error), the Telegram notification still goes through. The SMS is a fire-and-forget bonus.

---

## RingCentral Credentials

| Key | Value |
|-----|-------|
| **From Number** | `+14702374510` |
| **Client ID** | `064d826d04230f624e3af3c70155c4ba` |
| **Client Secret** | `19673522391675e61ff2ddd2d1b013dd` |
| **JWT Token** | `ec9c3412206a1a4e804fabb3d3ef42c5...` (full value stored in .env) |

---

## Files to Change

### 1. `config.py` — Add 4 new env vars

```python
# RingCentral SMS
RC_CLIENT_ID: str = os.environ.get("RC_CLIENT_ID", "")
RC_CLIENT_SECRET: str = os.environ.get("RC_CLIENT_SECRET", "")
RC_JWT_TOKEN: str = os.environ.get("RC_JWT_TOKEN", "")
RC_FROM_NUMBER: str = os.environ.get("RC_FROM_NUMBER", "")
```

### 2. `sms.py` — New file (~40 lines)

```python
"""Send SMS via RingCentral REST API."""

async def get_rc_access_token() -> str:
    """Exchange JWT token for a short-lived access token."""
    # POST https://platform.ringcentral.com/restapi/oauth/token
    # grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer
    # assertion=RC_JWT_TOKEN
    # Returns: {"access_token": "...", "expires_in": 3600}

async def send_sms(to: str, message: str) -> bool:
    """Send an SMS message via RingCentral.
    Returns True on success, False on failure. Never raises.
    """
    # 1. Get access token
    # 2. POST https://platform.ringcentral.com/restapi/v1.0/account/~/extension/~/sms
    #    Body: {"from": {"phoneNumber": RC_FROM_NUMBER},
    #           "to": [{"phoneNumber": to}],
    #           "text": message}
    # 3. Return True/False
```

### 3. `webhook_server.py` — Add ~10 lines inside `_process_lead()`

```python
# After sending Telegram notification:
phone = field_map.get("phone") or field_map.get("phone_number")
first_name = field_map.get("full_name", "Driver").split()[0]

if phone and RC_CLIENT_ID:
    sms_text = (
        f"Hello {first_name}, this is Tom with Wenze trucking company "
        f"and thanks for applying to us. Can I call you right now "
        f"to explain the details?"
    )
    try:
        await send_sms(to=phone, message=sms_text)
        logger.info("SMS sent to %s for lead %s", phone, leadgen_id)
    except Exception as exc:
        logger.warning("SMS failed for lead %s: %s", leadgen_id, exc)
        # SMS failure does NOT affect Telegram — lead is already delivered
```

### 4. `.env` / Render — Add 4 new variables

```env
RC_CLIENT_ID=064d826d04230f624e3af3c70155c4ba
RC_CLIENT_SECRET=19673522391675e61ff2ddd2d1b013dd
RC_JWT_TOKEN=ec9c3412206a1a4e804fabb3d3ef42c5...
RC_FROM_NUMBER=+14702374510
```

---

## Safety Guarantees

| Concern | How it's handled |
|---------|-----------------|
| SMS fails | Wrapped in `try/except` — Telegram still works |
| No phone number | Skipped silently — only sends if phone exists |
| RingCentral credentials missing | `if RC_CLIENT_ID:` guard — does nothing if not set |
| Rate limiting | RingCentral allows ~50 SMS/min on standard plans |
| Lead from Messenger (no phone) | SMS skipped, Telegram still sent |

---

## SMS Message Template

```
Hello {first_name}, this is Tom with Wenze trucking company and thanks
for applying to us. Can I call you right now to explain the details?
```

> The template can be customized later. Could even be stored as an env variable `SMS_TEMPLATE` for easy changes without code deploys.

---

## Testing Plan

1. Set env vars locally in `.env`
2. Run the server locally: `python main.py`
3. Use the `/retry/{lead_id}` endpoint with an existing lead ID to trigger the flow
4. Verify SMS arrives on the lead's phone
5. Verify Telegram notification still works normally
6. Deploy to Render and add 4 env vars
7. Test with a real lead from Lead Ads Testing Tool

---

## Optional Enhancements (Future)

- **Customizable message template** via env var or Telegram command
- **SMS delivery status tracking** (RingCentral webhooks)
- **Delay before sending** (e.g., wait 30 seconds so it feels less bot-like)
- **Skip test leads** (don't SMS Facebook's dummy phone numbers)
- **SMS log** to Telegram (confirm to dispatcher that SMS was sent)
