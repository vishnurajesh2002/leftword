import frappe


#add item to wishlist
@frappe.whitelist(allow_guest=True)
def make_wishlist(item_code, user=None):
    if not user:
        user = frappe.session.user
    if frappe.db.exists("Wishlist Item", {"item_code": item_code, "owner": user}):
        return
    wishlist =  frappe.db.exists("Wishlist", {"user": user})
    wl_doc = None
    if wishlist:
        wl_doc = frappe.get_doc("Wishlist", wishlist)
    else:
        wl_doc = frappe.new_doc("Wishlist")
        wl_doc.user = user
    if wl_doc:
        wl_doc.append("items", {
            "item_code": item_code,
            "website_item": frappe.db.get_value("Website Item", {"item_code": item_code}, "name")
        })
        wl_doc.save(ignore_permissions=True)
    return wl_doc.name

# @frappe.whitelist(allow_guest=True)
# def get_wishlist(user=None, item_code=None):
#     wishlist_items = []
#     if not user:
#         user = frappe.session.user
#     filters = {"owner": user}
#     if item_code:
#         filters["item_code"] = item_code
    
#         wishlist_items = frappe.db.get_list("Wishlist Item", filters, ['*'], ignore_permissions=True)
#     return wishlist_items

#remove item from wishlist
@frappe.whitelist(allow_guest=True)
def remove_wishlist(item_code, user=None):
    if not user:
        user = frappe.session.user
    if not frappe.db.exists("Wishlist Item", {"item_code": item_code, "owner": user}):
        return
    frappe.db.delete("Wishlist Item", {"item_code": item_code, "owner": user})

#get wishlist
# @frappe.whitelist(allow_guest=True)
# def get_wishlist():
#     user = frappe.session.user
#     sql_query = f"""
#         SELECT wi.*, ip.price_list_rate
#         FROM `tabWishlist Item` wi
#         LEFT JOIN `tabItem Price` ip ON wi.item_code = ip.item_code
#         WHERE wi.owner = '{user}' AND ip.currency = 'INR'
#     """
#     wishlist_items = frappe.db.sql(sql_query, as_dict=True)
#     return wishlist_items




@frappe.whitelist(allow_guest=True)
def get_wishlist():
    user = frappe.session.user
    ecom_settings = frappe.get_doc("E Commerce Settings")
    lw_settings = frappe.get_doc("Leftword Settings")
    sql_query = f"""
        SELECT
            wi.*,
            INR.price_list_rate as price_list_rate_inr,
            USD.price_list_rate as price_list_rate_usd,
            ti.custom_website_image as image  
        FROM
            `tabWishlist Item` wi
        LEFT JOIN
            `tabItem Price` INR ON wi.item_code = INR.item_code AND INR.currency = 'INR' AND INR.selling = True AND INR.price_list = '{ecom_settings.price_list}'
        LEFT JOIN
            `tabItem Price` USD ON wi.item_code = USD.item_code AND USD.currency = 'USD' AND USD.selling = True AND USD.price_list = '{lw_settings.usd_price_list}'
        LEFT JOIN
            `tabWebsite Item` ti ON wi.item_code = ti.item_code  
        WHERE
            wi.owner = '{user}'
    """
    wishlist_items = frappe.db.sql(sql_query, as_dict=True)
    return wishlist_items
