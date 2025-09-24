import frappe
from leftwordlatest.web_api.user import get_user_account

def get_context(context):
    context.no_cache = True
    load_data(context)

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
                filters={"email_id": user_account.get("email")},
                fields=["*"]
            )

            if customer_data:
                context.customer_data = customer_data[0]  
                customer_name = context.customer_data.get("name")
               

          
                all_addresses = frappe.get_all(
                    "Address",
                    filters={"link_name": customer_name},
                    fields=["name", "address_title", "address_line1", "address_line2", 
                            "city", "state", "pincode", "country", "phone", "email_id"]
                )

                context.all_addresses = all_addresses 
            else:
                context.customer_data = None  
                context.all_addresses = [] 

        else:
            context.user_data = None 
            context.all_addresses = []  
    else:
        context.all_addresses = [] 

   

@frappe.whitelist(allow_guest=True)
def remove_address(address_name):
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
        return {"status": "error", "message": "An error occurred while deleting the address."}

