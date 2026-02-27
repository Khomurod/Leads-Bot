"""
Fetches full lead details from the Meta Graph API using a leadgen_id.
"""
import httpx
from config import META_PAGE_ACCESS_TOKEN

GRAPH_BASE = "https://graph.facebook.com/v19.0"


async def fetch_lead(leadgen_id: str) -> dict:
    """Return a dict with the lead's field_data list, or empty dict on failure."""
    url = f"{GRAPH_BASE}/{leadgen_id}"
    params = {
        "access_token": META_PAGE_ACCESS_TOKEN,
        "fields": "field_data,created_time,id",
    }
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()


def format_lead_message(lead_data: dict) -> str:
    """Turn raw Graph API lead data into a Telegram message string."""
    lines = ["🔔 *New Facebook Lead!*\n"]

    field_map = {field["name"]: ", ".join(field["values"]) for field in lead_data.get("field_data", [])}

    # Common fields – show them in a friendly order
    pretty_keys = {
        "full_name": "👤 Name",
        "first_name": "👤 First Name",
        "last_name": "Last Name",
        "email": "📧 Email",
        "phone_number": "📞 Phone",
        "phone": "📞 Phone",
        "city": "🏙 City",
        "state": "🗺 State",
        "zip_code": "📮 ZIP",
        "country": "🌍 Country",
        "company_name": "🏢 Company",
        "job_title": "💼 Job Title",
        "message": "💬 Message",
        "comments": "💬 Comments",
    }

    shown = set()
    for key, label in pretty_keys.items():
        if key in field_map:
            lines.append(f"{label}: {field_map[key]}")
            shown.add(key)

    # Any extra fields from the form that aren't in our map
    for key, value in field_map.items():
        if key not in shown:
            lines.append(f"• {key.replace('_', ' ').title()}: {value}")

    lead_id = lead_data.get("id", "N/A")
    created = lead_data.get("created_time", "")
    if created:
        lines.append(f"\n🕐 Submitted: {created}")
    lines.append(f"🆔 Lead ID: `{lead_id}`")

    return "\n".join(lines)
