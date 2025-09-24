import frappe
from leftwordlatest.web_api.items import get_items
from leftwordlatest.web_api.cart import get_quotation


def get_context(context):
    context.no_cache = True
    if(frappe.form_dict.get("id")):
        load_product(context, frappe.form_dict.get("id"))
        
    else:
        frappe.redirect("/")


def load_product(context, id):
    context.allow_guest_cart = ""
    product = get_items(item_code=id)
    item_id = frappe.form_dict.get("id")
    if frappe.session.user == "Guest":
        cart_items = get_quotation(item_code=id, guest_quotation=True)
        context.hide_element = "hide-element"
        context.cart_button_class = "in-cart"
        context.button_label = "View In Cart" 
    cart_items = get_quotation(item_code=id)
    if cart_items:  
        context.hide_element = "hide-element"
        context.cart_button_class = "in-cart"
        context.button_label = "View In Cart"
    if cart_items == []:
        context.button_label = "Add To Cart"
        context.hide_element = ""
        context.cart_button_class = "add-to-cart"
    if frappe.db.get_single_value(
        "Leftword Settings",
        "allow_guest_cart"):
        context.allow_guest_cart = "allow-guest-cart"
    context.product_details = product.get("product_details")
    context.related_items = product.get("ap_related_items")
    context.banners = get_items(
        is_banner=True,
        banner=["Banner-2"],
    )
