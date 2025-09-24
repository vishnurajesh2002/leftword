import frappe
from leftwordlatest.web_api.wishlist import get_wishlist
from leftwordlatest.web_api.user import get_user_account



def get_context(context):
    context.no_cache = True
    # if frappe.session.user != "Guest":
    context.user_data = get_user_account()
    context.custom_display_name = get_user_account().get('custom_display_name')
    context.user_image = get_user_account().get('user_image')
    context.wishlist_items = get_wishlist()
