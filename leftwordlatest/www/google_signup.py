import frappe
from frappe import _
from frappe.utils import cint, escape_html
from frappe.core.doctype.navbar_settings.navbar_settings import get_app_logo
from frappe.utils.oauth import get_oauth2_authorize_url, get_oauth_keys
from frappe.utils.password import get_decrypted_password
import base64
import json

@frappe.whitelist(allow_guest=True)
def get_custom_login_context():
    context = {}

    # Redirect URL after successful login
    redirect_to = frappe.utils.get_url("/leftword_home")  # Customize this path as needed

    context["no_header"] = True
    context["for_test"] = "login.html"
    context["title"] = "Login"
    context["provider_logins"] = []
    context["disable_signup"] = cint(frappe.get_website_settings("disable_signup"))
    context["disable_user_pass_login"] = cint(frappe.get_system_settings("disable_user_pass_login"))
    context["logo"] = get_app_logo()
    context["app_name"] = (
        frappe.get_website_settings("app_name") or frappe.get_system_settings("app_name") or _("Frappe")
    )

    # Fetch social login providers
    providers = frappe.get_all(
        "Social Login Key",
        filters={"enable_social_login": 1},
        fields=["name", "client_id", "base_url", "provider_name", "icon"],
        order_by="name",
    )

    for provider in providers:
        client_secret = get_decrypted_password("Social Login Key", provider.name, "client_secret")
        if not client_secret:
            continue
        # Set provider icon for display
        icon = f"<img src={escape_html(provider.icon)!r} alt={escape_html(provider.provider_name)!r}>" if provider.icon else None

        # Generate auth URL for the provider
        if provider.client_id and provider.base_url and get_oauth_keys(provider.name):
            auth_url = get_oauth2_authorize_url(provider.name, redirect_to)
            context["provider_logins"].append({
                "name": provider.name,
                "provider_name": provider.provider_name,
                "auth_url": auth_url,
                "icon": icon,
            })
            context["social_login"] = True

    return context