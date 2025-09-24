import frappe
from leftwordlatest.web_api.user import get_user_account
from leftwordlatest.web_api.checkout import get_order

def get_context(context):
    context.no_cache = True
    context.user_account = get_user_account()

    if frappe.session.user != "Guest":
        context.user_data = get_user_account()
        if context.user_data:
            context.custom_display_name = get_user_account(user_details=True).get('custom_display_name')
            context.user_image = get_user_account(user_details=True).get('user_image')
            context.customer_name =  get_user_account(user_details=True).get('customer_name')
        # context.user_image = get_user_account().get('user_image')
            context.orders = get_order(customer=context.customer_name)
