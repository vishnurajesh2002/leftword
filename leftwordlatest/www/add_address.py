import frappe
from frappe import _
@frappe.whitelist(allow_guest=True)

def add_address(address_title, phone, pincode, state, country, address_line1, city, address_email, type, is_shipping_address, is_primary_address):
    try:
     
        user = frappe.session.user

        if int(is_primary_address) == 1:
            existing_primary = frappe.db.get_value(
                "Address", {"is_primary_address": 1, "owner": user}, "name"
            )
            if existing_primary:
                return {
                    "status": "error",
                    "message": f"Address '{existing_primary}' is already marked as Primary. Please uncheck it before proceeding."
                }
        if int(is_shipping_address) == 1:
            existing_shipping = frappe.db.get_value(
                "Address", {"is_shipping_address": 1, "owner": user}, "name"
            )
            if existing_shipping:
                return {
                    "status": "error",
                    "message": f"Address '{existing_shipping}' is already marked as Shipping. Please uncheck it before proceeding."
                }

        address = frappe.get_doc({
            "doctype": "Address",
            "address_title": address_title,
            "phone": phone,
            "pincode": pincode,
            "state": state,
            "country": country,
            "address_line1": address_line1,
            "city": city,
            "email_id": address_email,
            "address_type": type,
            "is_shipping_address": int(is_shipping_address),
            "is_primary_address": int(is_primary_address)
        })
        address.insert(ignore_permissions=True)
        frappe.db.commit()

        return {"status": "success", "message": "Address updated successfully."}
    except Exception as e:
        frappe.log_error(message=str(e), title="Address Update Error")
        return {"status": "error", "message": str(e)}
