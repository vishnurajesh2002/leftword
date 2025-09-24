import random
import string
import frappe
from datetime import datetime, timedelta

@frappe.whitelist(allow_guest=True)
def handle_otp_submission(contact=None, additional_email=None):
    try:
        if not contact:
            return {
                "status_code": 400,
                "success": False,
                "message": "Please provide a valid contact."
            }

        if frappe.db.exists("User", {"email": contact}) or frappe.db.exists("User", {"phone": contact}):
            return {
                "status_code": 400,
                "success": False,
                "message": "This user is already registered."
            }
            
        if additional_email:
            if frappe.db.exists("User", {"email": additional_email}):
                return {
                    "status_code": 400,
                    "success": False,
                    "message": "The provided email is already registered with another user."
                }

        if contact.isdigit() and len(contact) == 10:
            contact_type = "phone"
            message = "OTP sent to mobile number successfully."
        elif "@" in contact and "." in contact:
            contact_type = "email"
            message = "OTP sent to email successfully."
        else:
            return {
                "status_code": 400,
                "success": False,
                "message": "Please enter a valid mobile number or email address."
            }

        otp_code = ''.join(random.choices(string.digits, k=4))
        otp_verification = frappe.new_doc("OTP Verification")
        existing_otp = frappe.get_all("OTP Verification", filters={"login_id": contact}, limit=1)
        if existing_otp:
            # If exists, overwrite the existing OTP record
            otp_verification = frappe.get_doc("OTP Verification", existing_otp[0].name)
        else:
            otp_verification = frappe.new_doc("OTP Verification")
        otp_verification.login_id = contact
        otp_verification.otp = otp_code
        otp_verification.time = datetime.now()
        otp_verification.date = datetime.now().date()
        if contact_type == "phone":
            otp_verification.custom_sms_type ="sign up"
        otp_verification.otp_requests_today = 1
        otp_verification.save(ignore_permissions=True)

        if contact_type == "email":
            email_subject = "Your OTP for Leftword"
            email_message = f"""
                <p>Dear User ,</p> 
                <p>Thank you for choosing Leftword! Use the following OTP to complete your signup and get started:</p>
                <p>Your OTP: {otp_code}</p>
                <p>This OTP is valid for the next 5 minutes. Please enter it on the verification page to proceed.</p>
                <p>If you did not request this OTP, please ignore this email, and no changes will be made to your account.</p>
                <p>Best regards,</p>
                <p>Leftword</p>
            """

            try:
                frappe.sendmail(
                    recipients=contact,
                    subject=email_subject,
                    message=email_message,
                    delayed=False
                )
                return {
                    "status_code": 200,
                    "success": True,
                    "message": message,
                    "otp_code": otp_code
                }
            except Exception as e:
                return {
                    "status_code": 500,
                    "success": False,
                    "message": f"Failed to send OTP to email: {str(e)}"
                }

        elif contact_type == "phone":
            pass  # Implement SMS sending here

        return {
            "status_code": 200,
            "success": True,
            "message": message,
            "otp_code": otp_code
        }

    except Exception as e:
        return {
            "status_code": 500,
            "success": False,
            "message": f"An error occurred: {str(e)}"
        }

def validate_otp(contact, otp, user=None):
    """
    Validates the OTP for the given contact and checks its expiration.
    """
    # Check if the OTP exists and is not verified
    otp_filter = {"login_id": contact, "otp": otp, "verified": False}
    if user:
        otp_filter["user"] = user

    # otp_auth = frappe.get_last_doc("OTP Verification", otp_filter)
    # if not otp_auth:
    #     return {
    #         "status": "error",
    #         "success": False,
    #         "message": "Invalid OTP. Please try again."
    #     }
    # otp_auth = frappe.get_all("OTP Verification", filters=otp_filter, order_by="creation desc", limit=1)
    otp_auth = frappe.get_all("OTP Verification", filters=otp_filter, order_by="creation desc", limit=1)


    if not otp_auth:
        return {
            "status": "error",
            "success": False,
            "message": "Invalid OTP. Please try again."
        }

    otp_auth = frappe.get_doc("OTP Verification", otp_auth[0].name)


    # Check OTP expiration (default: 5 minutes)
    otp_validity_minutes = frappe.db.get_single_value("OTP Login Settings", "otp_expiry") or 5
    otp_expiration_time = otp_auth.time + timedelta(minutes=otp_validity_minutes)
    if datetime.now() > otp_expiration_time:
        return {
            "status": "error",
            "success": False,
            "message": "OTP expired. Please request a new one."
        }

    # Mark the OTP as verified
    otp_auth.verified = True
    otp_auth.save(ignore_permissions=True)
    return {
        "status": "success",
        "success": True,
        "message": "OTP verified successfully."
    }


def create_user(full_name, contact, email=None):
    """
    Create a new user in the system based on the contact (phone or email).
    Returns the created user's name.
    """
    if not email:
        if "@" in contact:
            email = contact
            phone = None
        else:
            email = f"{contact}@gmail.com"
            phone = contact
    else:
        phone = contact if contact.isdigit() and len(contact) == 10 else None

    user = frappe.get_doc({
        "doctype": "User",
        "send_welcome_email": 0,
        "email": email,
        "first_name": full_name,
        "user_type": "Website User",
        "phone": phone
    })
    user.save(ignore_permissions=True)
    user.add_roles("Customer")
    return user.name

def user_login(user):
    frappe.local.login_manager.user = user
    frappe.local.login_manager.post_login()
    clear_active_sessions()  
    return True

def clear_active_sessions():
    if frappe.session.user == "Guest":
        return

    deny_multiple_sessions_conf = frappe.conf.get("deny_multiple_sessions", 0)
    deny_multiple_sessions_setting = frappe.db.get_system_setting("deny_multiple_sessions") or 0

    if not (int(deny_multiple_sessions_conf) or int(deny_multiple_sessions_setting)):
        return
    clear_sessions(frappe.session.user, keep_current=True)


@frappe.whitelist(allow_guest=True)
def verify_signup_otp(otp, full_name, contact, email=None):
    """
    Verify the OTP and create the user if OTP is valid, then log them in.
    Returns a JSON response with status and message.
    """
    validation_result = validate_otp(contact, otp, None)
    if not validation_result["success"]:
        return validation_result  # Return the error message for invalid/expired OTP

    user = create_user(full_name, contact, email)
    if user:
        user_login(user)
        return {
            "status": "success",
            "success": True,
            "message": "OTP verified successfully. Logged In."
        }

    return {
        "status": "error",
        "success": False,
        "message": "Failed to create user."
    }

@frappe.whitelist(allow_guest=True)
def check_user_exists(contact):
    if frappe.db.exists("User",contact):
        return {"exists": True}
    return {"exists": False}