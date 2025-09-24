no_cache = 1
from leftwordlatest.web_api.cart import get_quotation
from leftwordlatest.web_api.address import get_user_shipping_address,get_user_billing_address
from leftwordlatest.web_api.user import get_user_account
from leftwordlatest.web_api.checkout import get_order


import frappe
def get_context(context):

    context.cart_items_list = ""
    context.checkout_class = ""
    context.net_total = 0
    context.address = ""
    context.user_data = get_user_account()
    user_account = get_user_account()

    if frappe.session.user != "Guest":
        user = frappe.get_doc("User", frappe.session.user)
        if user:
            context.first_name = user.first_name
            context.last_name = user.last_name
            context.email = user.email
    else:
        context.first_name = None
        context.last_name = None
        context.email = None

    context.cart_items = get_quotation()
    context.order = get_order()

    if frappe.session.user != "Guest":
        # Fetch addresses created by the current user
        context.customer_addresses = frappe.get_all(
            "Address",
            filters={"owner": frappe.session.user},
            fields=["name", "address_title", "phone", "address_line1", "city", "pincode", "state", "email_id", "is_shipping_address", "is_primary_address"]
        )

        # Filter addresses based on shipping and billing criteria
        context.shipping_addresses = [
            address for address in context.customer_addresses if address.get("is_shipping_address") == 1
        ]
        
        context.billing_addresses = [
            address for address in context.customer_addresses if address.get("is_primary_address") == 1
        ]

        # If no billing address is found, use the first shipping address as billing address
        if not context.billing_addresses and context.shipping_addresses:
            context.billing_addresses = context.shipping_addresses

    else:
        # For guest users
        context.shipping_addresses = [get_user_shipping_address(guest_address=True)]
        context.billing_addresses = []  # No billing address for guests (adjust as needed)

    if context.cart_items:
        context.cart_class = ""
        context.checkout_class = ""
        context.button_label = "Place Order"
        quotation_details = get_quotation(quotation_details=True)
        context.net_total = quotation_details.get("net_total", 0)
        context.base_net_total = quotation_details.get("base_net_total", 0)
        context.base_grand_total = quotation_details.get("base_grand_total", 0)
        context.grand_total = quotation_details.get("grand_total", 0)

    if not context.cart_items:
        context.button_label = "Place Order"
        context.cart_class = "empty-cart"

    if context.order:
        context.checkout_class = "order-placed"
        context.button_label = "Placing Order...."
        context.cart_class = ""
        context.address = "shipping-address"
        context.cart_items = context.order

    if not context.order:
        context.checkout_class = "checkout"
