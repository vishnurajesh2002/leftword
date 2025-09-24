no_cache = 1
from leftwordlatest.web_api.cart import get_quotation
import frappe

def get_context(context):
    context.cart_class = ""
    context.body_class = "product-page"
    context.net_total = 0 
    context.cart_items = get_quotation()
    if frappe.session.user == 'Guest':
        context.cart_items = get_quotation()
    if context.cart_items:
        context.net_total = get_quotation(quotation_details=True).get('net_total')
        # context.base_net_total = get_quotation(quotation_details=True).get('base_net_total')
        # context.total = get_quotation(quotation_details=True).get('total')
        # context.base_total = get_quotation(quotation_details=True).get('base_total')
    if context.cart_items == [] :
        context.cart_class = "empty-cart"



