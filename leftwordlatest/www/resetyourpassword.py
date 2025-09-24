import frappe
from frappe.utils.password import encrypt


@frappe.whitelist(allow_guest=True, methods=["POST"])
def reset_password(email=None, new_password=None):
    """
    Securely resets the password by encrypting it and saving it in the User document.
    """
    try:
        user = email or frappe.session.user
        if email:
            user = frappe.get_value("User", {"email": email}, "name")
            if not user:
                frappe.throw("User not found")

        if len(new_password) < 8:
            return "Password should be at least 8 characters long"
        if not any(char.islower() for char in new_password):
            return "Password must contain at least one lowercase letter"
        if not any(char.isupper() for char in new_password):
            return "Password must contain at least one uppercase letter"
        if not any(char.isdigit() for char in new_password):
            return "Password must contain at least one number"
        if not any(char in '!@#$%^&*(),.?":{}|<>' for char in new_password):
            return "Password must contain at least one special character"

        user_doc = frappe.get_doc("User", user)
        user_doc.new_password = new_password
        user_doc.save(ignore_permissions=True) 
        
        frappe.db.commit()  
        
        return "Password updated successfully"
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Password Reset Error")
        return f"An error occurred: {str(e)}"
