import json
import frappe
import requests
import base64
import imghdr
from frappe.utils.file_manager import save_file

@frappe.whitelist(allow_guest=True)
def detect_country_and_currency():
    response = requests.get(f"https://ipinfo.io/json")
    if response.ok:
        data = response.json()
        country = data.get("country")
        if country == "IN":
            currency = "INR"
        elif country:
            currency ="USD"
        return currency
    return "INR"


def get_client_ip():
    """Get real visitor IP considering Cloudflare and Nginx."""
    if frappe.request.headers.get('X-Forwarded-For'):
        ip_address = frappe.request.headers.get('X-Forwarded-For').split(',')[0]
    else:
        ip_address = frappe.request.remote_addr
    if ip_address:
        return ip_address


def get_currency():
    return getattr(frappe.local, "currency", frappe.session.data.get("currency", "INR"))


def set_user_and_full_name():
    """Set user and full name in frappe session and local context."""

    user = frappe.session.user or "Guest"

    # Ensure session data dictionary exists
    if not hasattr(frappe.session, "data") or frappe.session.data is None:
        frappe.session.data = {}

    # Get full name safely
    full_name = frappe.db.get_value("User", user, "full_name") or user

    # Set session and local context values
    frappe.session.data["user"] = user
    frappe.session.data["full_name"] = full_name
    frappe.local.user = user
    frappe.local.full_name = full_name

def get_full_name():
    """Get the user's full name from frappe.local or session data, with safe fallbacks."""
    try:
        # First priority: frappe.local.full_name (if set)
        if hasattr(frappe.local, "full_name") and frappe.local.full_name:
            return frappe.local.full_name

        # Second priority: session data
        if hasattr(frappe.session, "data") and frappe.session.data:
            return frappe.session.data.get("full_name") or ""

        return ""

    except Exception:
        # In case session or local are not initialized (e.g., during background jobs)
        return ""
    

@frappe.whitelist(allow_guest=True)
def update_transaction_currency(currency):
    frappe.session.data["currency"] = currency
    frappe.local.currency = currency