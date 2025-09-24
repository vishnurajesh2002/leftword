import frappe
from datetime import datetime
from leftwordlatest.web_api.cart import get_quotation
# from leftwordlatest.leftwordlatest.web_form.become_a_member.become_a_member import check_prev_inv
from leftwordlatest.web_api.user import get_user_account

no_cache = 1
def get_context(context):
    
    
    context.no_cache = True

    if not frappe.session.user:
        context.error = True
        context.emessage = "No User Found"
    if not frappe.db.exists("Customer", frappe.session.user):
        context.error = True
        context.emessage = "No Customer Found"
    order = frappe.form_dict.order
    if not order:
        context.error = True
        context.emessage = "No Invoice Found"
    invoice = frappe.get_doc("Sales Invoice", order)
    if invoice and invoice.status == "Paid":
        context.error = True
        context.emessage = "Already Paid"
    if invoice:
        request_doc = None
        invoice_doc = frappe.get_doc("Sales Invoice", invoice.name)
        address_doc = frappe.get_doc("Address",invoice.shipping_address_name)
        bill_doc = frappe.get_doc("Address",invoice.customer_address)

        invoice_doc.flags.ignore_permissions = True
        invoice_doc.submit()
        if frappe.db.exists("Payment Request", {"reference_name":invoice.name, "docstatus":1}):
            request_doc = frappe.get_last_doc("Payment Request", {"reference_name":invoice.name})
        else:
            request_doc = frappe.new_doc("Payment Request")
            request_doc.party_type = "Customer"
            request_doc.party = invoice_doc.customer_name
            request_doc.reference_doctype = "Sales Invoice"
            request_doc.reference_name = invoice.name
            request_doc.grand_total = invoice_doc.grand_total
            request_doc.currency = invoice_doc.currency
            request_doc.flags.ignore_permissions = True
            request_doc.save(ignore_permissions = True)
            request_doc.submit()
        ccavenue_log = frappe.new_doc("CCAvenue Log")
        ccavenue_log.user = frappe.session.user
        ccavenue_log.status = "Pending"
        ccavenue_log.order_id = request_doc.name
        ccavenue_log.date = datetime.today()
        ccavenue_log.save(ignore_permissions = True)
        shipping_address = invoice_doc.shipping_address 

        item_names = [item.item_name for item in invoice_doc.items]
        
        context.customer_name = invoice_doc.customer_name
        context.street = address_doc.address_line1
        context.town = address_doc.city
        context.state = address_doc.state
        context.zipcode = address_doc.pincode
        context.phone = address_doc.phone
        context.email = address_doc.email_id
        context.street1 = bill_doc.address_line1
        context.town1 = bill_doc.city
        context.state1 = bill_doc.state
        context.zipcode1 = bill_doc.pincode
        context.phone1 = bill_doc.phone


        


        
        context.total = invoice_doc.total
        context.grand_total = invoice_doc.grand_total
        context.shipping = invoice_doc.total_taxes_and_charges
        context.invoice = invoice.name
        context.amount = invoice_doc.grand_total
        context.shipping_address = shipping_address
        context.currency = invoice_doc.currency
        context.language = "EN"
        context.order_id = request_doc.name
        context.token = ccavenue_log.name

        context.item_names = item_names
       

        frappe.db.commit()
    
        
        


# import frappe
# from datetime import datetime
# from leftwordlatest.web_api.cart import get_quotation
# from leftwordlatest.web_api.user import get_user_account

# # no_cache = 1

# def get_context(context):
#     # context.no_cache = True
#     context.error = False
#     context.emessage = None

#     if not frappe.session.user:
#         context.error = True
#         context.emessage = "No User Found"
#         return context

#     if not frappe.db.exists("Customer", frappe.session.user):
#         context.error = True
#         context.emessage = "No Customer Found"
#         return context

#     order = frappe.form_dict.order
#     if not order:
#         context.error = True
#         context.emessage = "No Invoice Found"
#         return context

#     if not frappe.db.exists("Sales Invoice", order):
#         context.error = True
#         context.emessage = "Invoice Not Found"
#         return context

#     invoice = frappe.get_doc("Sales Invoice", order)

#     if invoice.status == "Paid":
#         context.error = True
#         context.emessage = "Already Paid"
#         return context

#     invoice_doc = frappe.get_doc("Sales Invoice", invoice.name)
#     invoice_doc.flags.ignore_permissions = True
#     if invoice_doc.docstatus == 0:
#         invoice_doc.submit()

#     address_doc = None
#     bill_doc = None

#     if invoice.shipping_address_name and frappe.db.exists("Address", invoice.shipping_address_name):
#         address_doc = frappe.get_doc("Address", invoice.shipping_address_name)

#     if invoice.customer_address and frappe.db.exists("Address", invoice.customer_address):
#         bill_doc = frappe.get_doc("Address", invoice.customer_address)

#     if frappe.db.exists("Payment Request", {"reference_name": invoice.name, "docstatus": 1}):
#         request_doc = frappe.get_last_doc("Payment Request", {"reference_name": invoice.name})
#     else:
#         request_doc = frappe.new_doc("Payment Request")
#         request_doc.party_type = "Customer"
#         request_doc.party = invoice_doc.customer_name
#         request_doc.reference_doctype = "Sales Invoice"
#         request_doc.reference_name = invoice.name
#         request_doc.grand_total = invoice_doc.grand_total
#         request_doc.currency = invoice_doc.currency
#         request_doc.flags.ignore_permissions = True
#         request_doc.save(ignore_permissions=True)
#         request_doc.submit()

#     ccavenue_log = frappe.new_doc("CCAvenue Log")
#     ccavenue_log.user = frappe.session.user
#     ccavenue_log.status = "Pending"
#     ccavenue_log.order_id = request_doc.name
#     ccavenue_log.date = datetime.today()
#     ccavenue_log.save(ignore_permissions=True)

#     item_names = [item.item_name for item in invoice_doc.items]

#     context.customer_name = invoice_doc.customer_name

#     context.street = address_doc.address_line1 if address_doc else ""
#     context.town = address_doc.city if address_doc else ""
#     context.state = address_doc.state if address_doc else ""
#     context.zipcode = address_doc.pincode if address_doc else ""
#     context.phone = address_doc.phone if address_doc else ""
#     context.email = address_doc.email_id if address_doc else ""

#     context.street1 = bill_doc.address_line1 if bill_doc else ""
#     context.town1 = bill_doc.city if bill_doc else ""
#     context.state1 = bill_doc.state if bill_doc else ""
#     context.zipcode1 = bill_doc.pincode if bill_doc else ""
#     context.phone1 = bill_doc.phone if bill_doc else ""

#     context.total = invoice_doc.total
#     context.grand_total = invoice_doc.grand_total
#     context.shipping = invoice_doc.total_taxes_and_charges
#     context.invoice = invoice.name
#     context.amount = invoice_doc.grand_total
#     context.shipping_address = invoice_doc.shipping_address or ""
#     context.currency = invoice_doc.currency
#     context.language = "EN"
#     context.order_id = request_doc.name
#     context.token = ccavenue_log.name
#     context.item_names = item_names

#     frappe.db.commit()

#     return context
