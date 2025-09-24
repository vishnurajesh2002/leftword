import frappe
from leftwordlatest.web_api.user import get_user_account

def get_context(context):
    context.no_cache = True
    load_data(context)

def load_data(context):
    if frappe.session.user != "Guest":
        user_data = get_user_account(user_details=True)
        if user_data:
            context.custom_display_name = user_data.get('custom_display_name')
            context.user_image = user_data.get('user_image')
            context.first_name = user_data.get('first_name')
            context.last_name = user_data.get('last_name')
            context.email = user_data.get('email')
            context.phone = user_data.get('phone')