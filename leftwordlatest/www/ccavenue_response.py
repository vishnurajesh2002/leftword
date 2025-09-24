import frappe
import base64
from hashlib import md5
from Crypto.Cipher import AES
from Crypto import Random
from string import Template
import requests
import json
from Crypto.Random import get_random_bytes
import urllib.parse
from erpnext.accounts.doctype.payment_entry.test_payment_entry import create_payment_entry

no_cache = 1
def get_context(context):
    context.no_cache = True
    callback_data = frappe.request.get_data(as_text=True)
    ccavenue_log = None
    if not frappe.db.exists("CCAvenue Log", frappe.form_dict.token_id):
        context.error = True
        context.emessage = "Invalid Token"
    url = frappe.request.url
    parsed_url = urllib.parse.urlparse(url)
    enc_response = callback_data.split("&")[0].split('encResp=')[1]
    if not enc_response:
        context.error = True
        context.emessage = "Unauthorized Transaction"
    token_id = frappe.request.args.get("token")
    if token_id and frappe.db.exists("CCAvenue Log", token_id):
        ccavenue_log = frappe.get_doc("CCAvenue Log", token_id)
        if ccavenue_log.status != "Pending":
            context.error = True
            context.emessage = "Unauthorized Transaction"
        if ccavenue_log.status == "Pending" and ccavenue_log.user:
            frappe.local.login_manager.user = ccavenue_log.user
            frappe.local.login_manager.post_login()
        ccavenue_log.response_data = callback_data
        ccavenue_log.save(ignore_permissions=True)
        ccavenue_setting = frappe.get_doc("CCAvenue Settings")
        data = decrypt(enc_response, ccavenue_setting.working_key)
        context.data = data
        order_id, order_status=process_data(data)
        if not ccavenue_log.order_id == order_id:
            context.error = True
            context.emessage = "Invalid Token"
        if not order_status:
            context.error = True
            context.emessage = "Could not get order status"
        context.order_id = order_id
        context.order_status = order_status
        if order_status == "Success":
            ccavenue_log.status = "Success"
            ccavenue_log.save(ignore_permissions=True)
            payment = confirm_payment(order_id)
            if not payment:
                context.error = True
                context.emessage = "Something went wrong"
                ccavenue_log.note = "Couldn't create payment entry"
            if payment:
                ccavenue_log.payment_reference = payment
                ccavenue_log.save(ignore_permissions=True)
        if order_status == "Failure":
            ccavenue_log.status = "Failure"
            ccavenue_log.save(ignore_permissions=True)
    else:
        context.data = "Authorization failed"

@frappe.whitelist()
def decrypt(cipherText,workingKey):
    iv = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
    decDigest = md5(workingKey.encode())
    encryptedText = bytes.fromhex(cipherText)
    dec_cipher = AES.new(decDigest.digest(), AES.MODE_CBC, iv)
    decryptedText = dec_cipher.decrypt(encryptedText)
    return decryptedText.decode('utf-8')

def process_data(data):
    args = data.split('&')
    if args:
        order_data = args[0]
        status_data = args[3]
        return order_data.split("order_id=")[1], status_data.split("order_status=")[1]

def confirm_payment(order_id):
    if not frappe.db.exists("Payment Request", order_id):
        return False
    pr_doc = frappe.get_doc("Payment Request", order_id)
    if not pr_doc.reference_name:
        return False
    if not frappe.db.exists("Sales Invoice", pr_doc.reference_name):
        return False
    invoice_doc = frappe.get_doc("Sales Invoice", pr_doc.reference_name)
    payment_doc = frappe.new_doc("Payment Entry")
    payment_doc.party_type = "Customer"
    payment_doc.party = invoice_doc.customer
    payment_doc.paid_amount = invoice_doc.rounded_total or invoice_doc.grand_total
    payment_doc.mode_of_payment = "CCAvenue -INR" if invoice_doc.currency == "INR" else "CCAvenue -USD"
    payment_doc.received_amount = invoice_doc.rounded_total or invoice_doc.grand_total
    reference = {
        "reference_doctype": "Sales Invoice",
        "reference_name": invoice_doc.name,
        "total_amount": invoice_doc.rounded_total or invoice_doc.grand_total,
        "allocated_amount": invoice_doc.rounded_total or invoice_doc.grand_total
    }
    payment_doc.reference_no = order_id
    payment_doc.reference_date = invoice_doc.posting_date
    payment_doc.paid_to = "CCAvenue - NRPPL" if invoice_doc.currency == "INR" else "CC Avenue - USD - NRPPL"
    payment_doc.append("references", reference)
    payment_doc.source_exchange_rate = 1
    payment_doc.target_exchange_rate = 1
    payment_doc.flags.ignore_permissions = True
    payment_doc.flags.ignore_validate_update_after_submit = True
    payment_doc.setup_party_account_field()
    payment_doc.set_missing_values()
    payment_doc.docstatus = 1
    payment_doc.save(ignore_permissions=True)

    confirm_membership(invoice_doc.name, invoice_doc.rounded_total or invoice_doc.grand_total)

    return payment_doc.name



@frappe.whitelist()
def confirm_membership(invoice, amount):
    if not frappe.db.exists("Sales Invoice", invoice):
        return False
    customer_name = frappe.db.get_value("Customer", {"customer_name": frappe.session.user}, "name")
    if not customer_name:
        frappe.throw(("No Customer record found for the email {0}").format(frappe.session.user))

    customer = frappe.get_doc("Customer", customer_name)
    if customer.customer_group != "Book Club Member" and customer.member:
        member_filter = {"member": customer.member, "membership_status": "New", "membership_type": "Yearly Membership", "paid": False}
        customer.customer_group = "Book Club Member"
        customer.save(ignore_permissions=True)
        if frappe.db.exists("Membership", member_filter):
            membership = frappe.get_doc("Membership", member_filter)
            membership.paid = True
            membership.invoice = invoice
            membership.amount = amount
            membership.membership_status = "Current"
            membership.customer_name = customer.customer_name 
            
            membership.save(ignore_permissions=True)

            return membership.name
    
    return False


