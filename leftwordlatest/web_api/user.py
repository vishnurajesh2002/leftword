import frappe
from frappe.utils.password import check_password
import base64
import string
import random
from datetime import datetime, timedelta
from frappe.core.doctype.sms_settings.sms_settings import send_sms
import hashlib
import frappe
import json
import re
from frappe import _
from frappe.core.doctype.sms_settings.sms_settings import validate_receiver_nos, send_request, create_sms_log, get_headers

# def validate_user_phone(doc, method):
#     if doc.phone:
#         existing_user = frappe.db.exists("User", {
#             "phone": doc.phone,
#             "name": ["!=", doc.name]
#         })

#         if existing_user:
#             frappe.throw(f"Phone number {doc.phone} is already assigned to another user.")


@frappe.whitelist(allow_guest=True)
def get_user_account(email=None, user_details=False):
    lw_setting = frappe.get_doc("Leftword Settings")
    if frappe.session.user == "Guest" and lw_setting.allow_guest_cart == True:
        return frappe.db.get_value(
            "Customer",
            lw_setting.guest_customer_name,
            "*"
        )
    if not email:
        email = frappe.session.user
    user = frappe.get_doc("User", email)
    contact = None
    customer_doc = None
    if frappe.db.exists("Contact", {"email_id": email}):
        contact = frappe.get_last_doc("Contact", {"email_id": email})
    else:
        return
    customer_name = frappe.get_value("Dynamic Link", {"parent": contact.name}, "link_name")
    if customer_name:
        customer_doc = frappe.db.sql("""
            SELECT 
                customer.*, user.*, contact.*, customer.name AS customer_id
            FROM 
                `tabCustomer` customer
            INNER JOIN 
                `tabUser` user
            ON 
                user.name = '{email}'
            INNER JOIN 
                `tabContact` contact
            ON 
                contact.email_id = '{email}'
            WHERE customer.name = '{customer}'
        """.format(email=email, customer=customer_name),
        as_dict=True)
    # else:
    #     return
    # if customer_doc:
        # customer_doc = customer_doc[0]
        # return customer_doc
        # return customer_doc[0]
    if user_details:
        first_name = customer_doc[0].get("first_name") if customer_doc else 0
        last_name = customer_doc[0].get("last_name") if customer_doc else 0
        email = customer_doc[0].get("email") if customer_doc else 0
        customer_name = customer_doc[0].get("customer_name") if customer_doc else 0
        custom_display_name = customer_doc[0].get("custom_display_name") if customer_doc else 0
        user_image = customer_doc[0].get("user_image") if customer_doc else 0
        customer_id = customer_doc[0].get("customer_id") if customer_doc else 0
        phone = user.phone if user else ""
        return {
                "customer_id": customer_id,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "custom_display_name": custom_display_name,
                "customer_name": customer_name,
                "user_image": user_image,
                "phone": phone,
                "customer_doc": customer_doc if customer_doc else []
            }
    return customer_doc if customer_doc else []



# @frappe.whitelist(allow_guest=True)
# def update_user_account(**kwargs):
#     user_doc = frappe.get_doc("User", kwargs.get("email_id"))
#     user_doc.update(kwargs)
    
#     contact_doc = None
#     if frappe.db.exists("Contact", kwargs.get("email_id")):
#         contact_doc = frappe.get_doc("Contact", kwargs.get("email_id"))
#         contact_doc.update(kwargs)
    
#     customer_doc = None
#     if frappe.db.exists("Customer", kwargs.get("first_name")):
#         customer_doc = frappe.get_doc("Customer", kwargs.get("first_name"))
#         customer_doc.update(kwargs) 
    
#     user_doc.save(ignore_permissions=True)
    
#     if customer_doc:
#         customer_doc.save(ignore_permissions=True)
#         return True
    
#     if contact_doc:
#         contact_doc.save(ignore_permissions=True)
#         return True
    
#     return False

@frappe.whitelist(allow_guest=True)
def update_user_account(**kwargs):

    phone = kwargs.get("phone")

    if phone:
        phone_cleaned = phone.strip().replace(" ", "").replace("-", "")
        if not re.match(r'^[6-9]\d{9}$', phone_cleaned):
            frappe.throw("Phone number must be 10 digits")


        existing_user = frappe.db.exists("User", {
            "phone": phone_cleaned,
            "name": ["!=", kwargs.get("email_id")]
        })
        if existing_user:
            existing_phone = frappe.db.get_value("User", kwargs.get("email_id"), "phone")
            kwargs["phone"] = existing_phone or ""  

            frappe.msgprint(_("Phone number {0} is already assigned to another user.".format(phone_cleaned)))
            return kwargs

        kwargs["phone"] = phone_cleaned  
    else:
        kwargs["phone"] = None 

    if frappe.session.user == "Administrator":
        name = frappe.session.user
        user_doc = frappe.get_doc("User", name)
        user_doc.reload()
        user_doc.update(kwargs)
    else:
        user_doc = frappe.get_doc("User", kwargs.get("email_id"))
        user_doc.update(kwargs)
    
    contact_doc = None
    if frappe.db.exists("Contact", kwargs.get("email_id")):
        contact_doc = frappe.get_doc("Contact", kwargs.get("email_id"))
        contact_doc.update(kwargs)

    elif frappe.db.exists("Contact", {"email_id": kwargs.get("email_id")}):
        contact_doc_list = frappe.db.get_all("Contact", filters={'email_id':user_doc.get("email")}, fields=['*'])
        contact_doc = frappe.get_doc("Contact", contact_doc_list[0].get('name'))
        contact_doc.update(kwargs)

    customer_doc = None
    if frappe.db.exists("Customer", kwargs.get("email_id")):
        customer_doc = frappe.get_doc("Customer", kwargs.get("email_id"))
        customer_doc.update(kwargs)
    elif  frappe.db.exists("Customer", {"email_id": kwargs.get("email_id")}):
        customer_doc_list = frappe.db.get_all("Customer", filters={'email_id':user_doc.get("email")}, fields=['*'])
        customer_doc = frappe.get_doc("Customer", customer_doc_list[0].get('name'))
        customer_doc.update(kwargs)
    
    if customer_doc:
        customer_doc.save(ignore_permissions=True)

    if contact_doc:
        contact_doc.save(ignore_permissions=True)
 
    user_doc.save(ignore_permissions=True)

    
    return True

@frappe.whitelist()
def send_sms(receiver_list, msg, sender_name="", success_msg=True):
    if isinstance(receiver_list, str):
        receiver_list = json.loads(receiver_list)
        if not isinstance(receiver_list, list):
            receiver_list = [receiver_list]

    receiver_list = validate_receiver_nos(receiver_list)

    arg = {
        "receiver_list": receiver_list,
        "message": frappe.safe_decode(msg).encode("utf-8"),
        "success_msg": success_msg,
    }

    if frappe.db.get_single_value("SMS Settings", "sms_gateway_url"):
        send_via_gateway(arg)
    else:
        frappe.msgprint(_("Please Update SMS Settings"))

def send_via_gateway(arg):
    ss = frappe.get_doc("SMS Settings", "SMS Settings")
    headers = get_headers(ss)
    use_json = headers.get("Content-Type") == "application/json"

    message = frappe.safe_decode(arg.get("message"))
    args = {ss.message_parameter: message}

    for d in ss.get("parameters"):
        if not d.header:
            args[d.parameter] = d.value

    success_list = []
    for d in arg.get("receiver_list"):
        args[ss.receiver_parameter] = d
        status = send_request(ss.sms_gateway_url, args, headers, ss.use_post, use_json)

        if 200 <= status < 300:
            success_list.append(d)

    if len(success_list) > 0:
        args.update(arg)
        create_sms_log(args, success_list)
        # Removed success message popup


@frappe.whitelist(allow_guest=True)
def send_otp_sms(phone, user=None, allow_sms=True, validate_phone=False, check_existing_user=False):
    try:
        if check_existing_user:
            if not frappe.db.exists("User", {"phone": phone}):
                raise Exception("User not found. Please use the correct mobile number.")

        user = None
        if frappe.session.user == "Guest":
            if not frappe.db.exists("User", {"phone":phone}):
                raise Exception("User not found")
            user = frappe.db.get_value("User", {"phone":phone}, "name")
        else:
            user = frappe.session.user
        last_otp_docs = frappe.get_all('OTP Verification', filters={"login_id": phone}, order_by='creation desc', limit=1)
        today = datetime.now().date()
        if last_otp_docs:
            last_otp_doc = frappe.get_doc("OTP Verification", last_otp_docs[0].name)
            if last_otp_doc and last_otp_doc.date == today:
                otp_requests_today = last_otp_doc.otp_requests_today + 1
                if otp_requests_today > 5:
                    raise Exception("OTP limit for today has been reached. Please continue login with email.")
            else:
                otp_requests_today = 1
        else:
            otp_requests_today = 1

        if validate_phone:
            if frappe.db.exists("User", {"phone": phone}):
                raise Exception("Mobile number already exists.")
        password = ''.join(random.choices(string.digits, k=4))
        hashed_otp = hashlib.sha256(password.encode()).hexdigest()
    
        message = """
            {0} is the one time password for your Leftword account.
        """.format(password)
        otp = frappe.new_doc("OTP Verification")
        otp.otp = password
        otp.time = datetime.now()
        otp.login_id = phone
        otp.date = today
        otp.custom_sms_type ="Sign in"
        otp.otp_requests_today = otp_requests_today
        if user:
            otp.user = user
        otp.save(ignore_permissions=True)
        frappe.db.commit()
        if allow_sms:
            send_sms([phone], message)
        
        otp_doc = otp.as_dict()
        for field in ["otp","email_otp","attempt", "otp_requests_today", "date"]:
            otp_doc.pop(field, None)
        frappe.local.response["status_code"] = 200
        frappe.local.response["message"] = otp_doc

    except Exception as e:
        if "Mobile number already exists." in str(e):
            frappe.local.response["status_code"] = 500
            frappe.local.response["message"] = str(e)
        elif "OTP limit for today has been reached. Please continue login with email." in str(e):
            frappe.local.response["status_code"] = 500
            frappe.local.response["message"] = str(e)
        elif "User not found" in str(e):
            frappe.local.response["status_code"] = 500
            frappe.local.response["message"] = str(e)
        else:
            frappe.local.response["status_code"] = 500
            frappe.local.response["message"] = "Could not generate OTP! Please contact admin."
        frappe.local.response["error"] = e



@frappe.whitelist(allow_guest=True)
def send_otp_email(email, user=None, allow_email=True, validate_email=False, check_existing_user=False):
    try:
        if check_existing_user:
            if not frappe.db.exists("User", {"email": email}):
                raise Exception("User not found. Please use the correct Email address.")

        user = None
        if frappe.session.user == "Guest":
            if not frappe.db.exists("User", {"email":email}):
                raise Exception("User not found")
            user = frappe.db.get_value("User", {"email":email}, "name")
            phone = frappe.db.get_value("User", {"email":email}, "phone")
        else:
            user = frappe.session.user
        
        last_otp_docs = frappe.get_all('OTP Verification', filters={"login_id": email}, order_by='creation desc', limit=1)
        today = datetime.now().date()  
        if last_otp_docs:
            last_otp_doc = frappe.get_doc("OTP Verification", last_otp_docs[0].name)  
            if last_otp_doc and last_otp_doc.date == today:
                otp_requests_today = last_otp_doc.otp_requests_today + 1
                
            else:
                otp_requests_today = 1
        else:
            otp_requests_today = 1
        if validate_email:
            if frappe.db.exists("User", {"email": email}):
                raise Exception("Email ID already exists.")
        
        e_password = ''.join(random.choices(string.digits, k=4))
        hashed_email_otp = hashlib.sha256(e_password.encode()).hexdigest()

        otp = frappe.new_doc("OTP Verification")
        otp.otp = e_password
        otp.time = datetime.now()
        otp.login_id = email
        otp.date = today
        otp.email_otp = e_password
        otp.otp_requests_today = otp_requests_today
        if user:
            otp.user = user
        otp.save(ignore_permissions=True)
        frappe.db.commit()
        
        if allow_email:
            user_email = email
            user_full_name = frappe.db.get_value("User", user, "full_name")
            if user_email:
                email_subject = "Your OTP for Leftword"
                email_message = """
                    <p>Dear {0},</p>
                    <p>To ensure the security of your account, please use the following One-Time Password (OTP) to complete your verification process:</p>
                    <p>Your OTP: {1}</p>
                    <p>This OTP is valid for the next 5 minutes. Please enter it on the verification page to proceed.</p>
                    <p>If you did not request this OTP, please ignore this email, and no changes will be made to your account.</p>
                    <p>Thank you for choosing Leftword.</p>
                    <p>Best regards,</p>
                    <p>Leftword</p>
                """.format(user_full_name,e_password)
                frappe.sendmail(recipients=user_email, subject=email_subject, message=email_message, delayed=False)
        otp_doc = otp.as_dict()
        for field in ["otp","email_otp","attempt", "otp_requests_today", "date"]:
            otp_doc.pop(field, None)
        frappe.local.response["status_code"] = 200
        frappe.local.response["message"] = otp_doc

    except Exception as e:
        if "Email ID already exists." in str(e):
            frappe.local.response["status_code"] = 500
            frappe.local.response["message"] = str(e)
        elif "OTP limit for today has been reached. Please continue login with email." in str(e):
            frappe.local.response["status_code"] = 500
            frappe.local.response["message"] = str(e)
        elif "User not found" in str(e):
            frappe.local.response["status_code"] = 500
            frappe.local.response["message"] = str(e)
        else:
            frappe.local.response["status_code"] = 500
            frappe.local.response["message"] = "Could not generate OTP! Please contact admin."
        frappe.local.response["error"] = e

@frappe.whitelist(allow_guest=True)     
def verify_otp_email(email,otp_code):
    otp_docs=frappe.get_all("OTP Verification",filters={"login_id":email},order_by='creation desc',limit=1)
    otp_doc=frappe.get_doc("OTP Verification",otp_docs[0].name)
    stored_otp_hash=otp_doc.otp
    
    #entered_otp_hash = hashlib.sha256(otp_code.encode()).hexdigest()
    entered_otp_hash=otp_code
    
    if stored_otp_hash == entered_otp_hash:
        frappe.local.response['error'] = False
        frappe.local.response['message'] = 'OTP verified successfully'
    else:
        # OTP does not match
        frappe.local.response['error'] = True
        frappe.local.response['message'] = 'Invalid OTP. Please try again.'

@frappe.whitelist(allow_guest=True)
def verify_otp_sms(phone,otp_code):
    otp_docs=frappe.get_all("OTP Verification",filters={'login_id':phone},order_by='creation desc',limit=1)
    otp_doc=frappe.get_doc("OTP Verification",otp_docs[0].name)
    stored_otp_hash=otp_doc.otp
   # entered_otp_hash=hashlib.sha256(otp_code.encode()).hexdigest()
    entered_otp_hash=otp_code
    if stored_otp_hash==entered_otp_hash:
        frappe.local.response['error']= False
        frappe.local.response['message']= 'OTP verified successfully'
    else:
        frappe.local.response['error'] = True
        frappe.local.response['message'] = 'Invalid OTP. Please try again.'

        


        


@frappe.whitelist(allow_guest=True)
def otp_login(otp, phone=None, email=None):
    try:
        if phone:
            if not frappe.db.exists("User", {"phone": phone, "enabled":True}):
                raise Exception("User not found!")
            user = frappe.get_doc("User", {"phone": phone, "enabled":True})
        if email:
            if not frappe.db.exists("User", {"email": email, "enabled":True}):
                raise Exception("User not found!")
            user = frappe.get_doc("User", {"email": email, "enabled":True})
        hashed_otp = hashlib.sha256(otp.encode()).hexdigest()
        if phone:
            otp_doc = frappe.get_last_doc("OTP Verification", { "verified":False, "login_id": phone})
        elif email:
            otp_doc = frappe.get_last_doc("OTP Verification", { "verified":False, "login_id": email})
        
        if datetime.now() - otp_doc.time > timedelta(minutes=5):
            raise Exception("OTP Expired")
        if otp_doc.attempt >= 3:
            raise Exception("Maximum OTP attempts exceeded. Please request a new OTP.")
        if otp_doc.otp != otp or otp_doc.verified:          
            try:
                otp_doc.attempt += 1
                otp_doc.save(ignore_permissions=True)
                frappe.db.commit()  
            except Exception as save_error:
                raise Exception(f"Failed to save OTP document: {str(save_error)}")
            raise Exception("Invalid OTP")
        otp_doc.verified = True
        otp_doc.save(ignore_permissions=True)
        frappe.db.commit()

        frappe.local.login_manager.user = user.name
        frappe.local.login_manager.post_login()
        api_generate = generate_keys(frappe.session.user)
        user = frappe.get_doc('User', frappe.session.user)
        token = base64.b64encode(('{}:{}'.format(user.api_key, api_generate)).encode('utf-8')).decode('utf-8')
        frappe.local.response["status_code"] =200
        frappe.local.response["message"] ="Authentication success"
        frappe.local.response["username"] =user.username
        frappe.local.response["email"] =user.email
        frappe.local.response["phone"] =user.phone
        frappe.local.response["auth_key"] =token
        frappe.local.response["first_name"] =user.first_name
        frappe.local.response["last_name"] =user.last_name
        frappe.local.response["session"] =frappe.session.user
    except Exception as e:
        frappe.local.response["status_code"] = 500
        frappe.local.response["message"] = str(e)


def generate_keys(user):
    user_details = frappe.get_doc('User', user)
    api_secret = frappe.generate_hash(length=15)

    if not user_details.api_key:
        api_key = frappe.generate_hash(length=15)
        user_details.api_key = api_key

    user_details.api_secret = api_secret
    user_details.flags.ignore_permissions = True
    user_details.flags.ignore_password_policy = True
    user_details.save()
    return api_secret
