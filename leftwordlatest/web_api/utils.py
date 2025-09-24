import json
import frappe
import requests
import base64
import imghdr
from frappe.utils.file_manager import save_file

@frappe.whitelist(allow_guest=True)
def get_currency_info():
    if not frappe.cache().get_value("transaction_currency"):
        ip_address = frappe.local.request_ip
        # ip_address = '157.44.137.21'
        request_url = 'https://geolocation-db.com/jsonp/' + ip_address
        response = requests.get(request_url)
        result = response.content.decode()
        result = result.split("(")[1].strip(")")
        result  = json.loads(result)
        if result.get("country_code") == "IN":
            frappe.cache().set_value("transaction_currency", "INR")
        else:
            frappe.cache().set_value("transaction_currency", "USD")
        return result
    else:
        return frappe.cache().get_value("transaction_currency")

@frappe.whitelist(allow_guest=True)
def update_transaction_currency(currency):
    frappe.cache().set_value("transaction_currency", currency)

@frappe.whitelist()
def upload_cus_img(image, customer):
    """
        image: Base64 encoded data.
        customer: existing customer name(primary key)
        save_file - inbuilt function to upload file.
    """
    if not "data:image/" in image:
        raise Exception("Invalid Image")
    data = image.split(',')[1]
    
    dec_data = base64.b64decode(data)
    exten = imghdr.what(None, h=dec_data)
    file = save_file(customer+"."+exten, dec_data, "", "", is_private=0)
    if file:
        user_doc = frappe.get_doc("User", frappe.session.user)
        user_doc.user_image = file.get("file_url")
        user_doc.save(ignore_permissions=True)
    return file
