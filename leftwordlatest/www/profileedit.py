import frappe
from frappe import _
from frappe.model.document import Document
def get_context(context):
    context.no_cache = True
    user_id = frappe.session.user

 
    address_id = frappe.form_dict.get('address_id')

    if address_id:

        address_data = get_address_data(address_id)
        context.address = address_data
    else:
        context.address= {}

  
    user_data = get_user_data(user_id) 
    context.user_data = user_data


def get_user_data(user_id):
 
    user = frappe.get_doc("User", user_id)
    return {
        "first_name": user.first_name,
        "last_name": user.last_name,
  
    }

@frappe.whitelist()
def get_address_data(address_id):
    address = frappe.get_doc("Address", address_id)

    return {
        "name": address.name,  # Change from "address-id" to "name"
        "address_line1": address.address_line1,
        "address_line2": address.address_line2,
        "city": address.city,
        "state": address.state,
        "country": address.country,
        "pincode": address.pincode,
        "phone": address.phone,
        "email_id": address.email_id,
        "address_title": address.address_title,
        "is_shipping_address": address.is_shipping_address,
        "is_primary_address": address.is_primary_address
    }



@frappe.whitelist(allow_guest=True)
def update_profile(first_name, middle_name, last_name):
    try:
 
        user = frappe.get_doc("User", frappe.session.user)
        user.first_name = first_name
        user.middle_name = middle_name
        user.last_name = last_name
        user.save()

        frappe.db.commit() 
        return {"status": "success"}

    except Exception as e:
        frappe.log_error(message=str(e), title="Profile Update Error")
        return {}



@frappe.whitelist()
def update_address(address_id, address_title, phone, email_id, pincode, city, state, country, address_line1):
    try:
        # Get the existing address document
        address = frappe.get_doc("Address", address_id)
        address.flags.ignore_permissions = True
        
        # Update the address fields
        address.address_title = address_title
        address.phone = phone
        address.email_id = email_id
        address.pincode = pincode
        address.city = city
        address.state = state
        address.country = country
        address.address_line1 = address_line1

       
        # Save the updated address
        address.save()
        frappe.db.commit()

        return {"message": "success"}
    
    except Exception as e:
        frappe.log_error(message=str(e), title="Address Update Error")
        return {"message": "failure"}
