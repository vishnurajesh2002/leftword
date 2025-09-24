import frappe
from leftwordlatest.web_api.address import get_user_shipping_address, get_user_billing_address
from leftwordlatest.web_api.user import get_user_account

def get_context(context):
    # if frappe.session.user != "Guest":
    #     context.user_data = get_user_account()
    context.no_cache = True
    context.user_data = get_user_account()
    context.custom_display_name = get_user_account().get('custom_display_name')
    context.user_image = get_user_account().get('user_image')

    # context.shipping_address = get_user_shipping_address(address_details=True)
    # context.address = get_user_shipping_address().get("address_title")
    context.billing_address = get_user_billing_address(billing_address_details=True)

    if frappe.session.user != "Guest":
        context.email = frappe.session.user
        #customer address section
        context.billing_address = get_user_billing_address(billing_address_details=True)
        context.shipping_address = get_user_shipping_address(address_details=True)
        if context.shipping_address:
            context.phone_number = get_user_shipping_address(address_details=True).get('phone')
            context.street_address = get_user_shipping_address(address_details=True).get('address_line1')
            context.city = get_user_shipping_address(address_details=True).get('city')
            context.zip_code = get_user_shipping_address(address_details=True).get('pincode')
            context.state = get_user_shipping_address(address_details=True).get('state')
        if context.billing_address:
            context.billing_phone_number = get_user_billing_address(billing_address_details=True).get('phone')
            context.billing_street_address = get_user_billing_address(billing_address_details=True).get('address_line1')
            context.billing_city = get_user_billing_address(billing_address_details=True).get('city')
            context.billing_zip_code = get_user_billing_address(billing_address_details=True).get('pincode')
            context.billing_state = get_user_billing_address(billing_address_details=True).get('state')

    else:

        context.shipping_address = get_user_shipping_address(guest_address=True)
        if context.shipping_address:
            context.first_name = get_user_shipping_address(guest_address=True).get('custom_first_name')
            context.last_name = get_user_shipping_address(guest_address=True).get('custom_last_name')
            context.email = get_user_shipping_address(guest_address=True).get('custom_email_id')
            context.phone_number = get_user_shipping_address(guest_address=True).get('custom_phone_number')
            context.street_address = get_user_shipping_address(guest_address=True).get('custom_street')
            context.city = get_user_shipping_address(guest_address=True).get('custom_towncity')
            context.zip_code = get_user_shipping_address(guest_address=True).get('custom_zip_code')
            context.state = get_user_shipping_address(guest_address=True).get('custom_state_')
