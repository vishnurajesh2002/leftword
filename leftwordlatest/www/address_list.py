import frappe
from leftwordlatest.web_api.user import get_user_account

def get_context(context):
    context.no_cache = True
    load_data(context)



def load_data(context):
    if frappe.session.user != "Guest":
        user_account = get_user_account(user_details=True)
        if user_account:
            context.user_data = user_account
            context.custom_display_name = user_account.get('custom_display_name')
            context.user_image = user_account.get('user_image')
            context.first_name = user_account.get('first_name')
            context.last_name = user_account.get('last_name')
            context.email = user_account.get('email')

            customer_data = frappe.get_all(
                "Customer",
                filters={"customer_name": user_account.get("first_name")},
                fields=["*"]
            )
            context.customer_data = customer_data[0] if customer_data else None

            # Fetch all addresses linked to the customer, including shipping and billing flags
            all_addresses = frappe.get_all(
                "Address",
                filters={"link_name": context.customer_data.get("name")},
                fields=[
                    "name", "address_title", "address_line1", "address_line2", 
                    "city", "state", "pincode", "country", "phone", "email_id", 
                    "is_shipping_address", "is_primary_address"  # Include these fields
                ]
            )

            context.all_addresses = all_addresses  # Pass all addresses directly
        else:
            context.all_addresses = []  # No addresses if user_account doesn't exist


@frappe.whitelist(allow_guest=True)
def remove_address(address_name):
    if not frappe.session.user or frappe.session.user == "Guest":
        frappe.throw("You need to be logged in to delete an address.")
    
    try:
        if frappe.db.exists("Address", address_name):
            frappe.delete_doc("Address", address_name, force=1,ignore_permissions=True)
            return {"status": "success"}
        else:
            return {"status": "error"}
    except Exception as e:
        frappe.log_error(f"Error deleting address: {str(e)}")
        return {"status": "error"}




@frappe.whitelist(allow_guest=True)
def delete_address(address_name):
    if not frappe.session.user or frappe.session.user == "Guest":
        frappe.throw("You need to be logged in to delete an address.")
    
    try:
        if frappe.db.exists("Address", address_name):
            frappe.delete_doc("Address", address_name, force=1,ignore_permissions=True)
            return {"status": "success"}
        else:
            return {"status": "error", "message": "Address not found"}
    except Exception as e:
        frappe.log_error(f"Error deleting address: {str(e)}")
        return {"status": "error"}


@frappe.whitelist()
def set_primary_address(address_name):
    user = frappe.session.user
    if user == "Guest":
        return {"status": "error"}

    frappe.db.sql("""
        UPDATE `tabAddress`
        SET is_primary_address = 0
        WHERE owner = %s AND is_primary_address = 1
    """, user)

    
    frappe.db.set_value("Address", address_name, "is_primary_address", 1)
    frappe.db.commit()

    return {"status": "success", "message": "primary address updated successfully."}
@frappe.whitelist()
def reset_primary_address(address_name):
    user = frappe.session.user
    if user == "Guest":
        return {"status": "error", "message": "You must be logged in to perform this action."}

    frappe.db.set_value("Address", address_name, "is_primary_address", 0)
    frappe.db.commit()

    return {"status": "success", "message": "Primary address unset successfully."}

@frappe.whitelist()
def check_existing_primary_address():
    user = frappe.session.user

    existing_primary_address = frappe.db.get_value(
        "Address", {"is_primary_address": 1, "owner": user}, "name"
    )
    if existing_primary_address:
        return {"has_primary_address": True, "address_name": existing_primary_address}
    return {"has_primary_address": False}



@frappe.whitelist()
def set_shipping_address(address_name):
    user = frappe.session.user
    if user == "Guest":
        return {"status": "error", "message": "You must be logged in to perform this action."}

    frappe.db.sql("""
        UPDATE `tabAddress`
        SET is_shipping_address = 0
        WHERE owner = %s AND is_shipping_address = 1
    """, user)

    frappe.db.set_value("Address", address_name, "is_shipping_address", 1)
    frappe.db.commit()

    return {"status": "success", "message": "Shipping address updated successfully."}
@frappe.whitelist()
def reset_shipping_address(address_name):
    user = frappe.session.user
    if user == "Guest":
        return {"status": "error", "message": "You must be logged in to perform this action."}

    frappe.db.set_value("Address", address_name, "is_shipping_address", 0)
    frappe.db.commit()

    return {"status": "success", "message": "Shipping address unset successfully."}


@frappe.whitelist()
def check_existing_shipping_address():
    user = frappe.session.user

    existing_shipping_address = frappe.db.get_value(
        "Address", {"is_shipping_address": 1, "owner": user}, "name"
    )
    if existing_shipping_address:
        return {"has_shipping_address": True, "address_name": existing_shipping_address}
    return {"has_shipping_address": False}
