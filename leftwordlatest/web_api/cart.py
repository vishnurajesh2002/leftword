import frappe
from datetime import datetime
from leftwordlatest.web_api.user import get_user_account
from erpnext.e_commerce.shopping_cart.product_info import get_product_info_for_website




######################### make cart including guest user #################
@frappe.whitelist(allow_guest=True)
def make_cart(item_code, qty, currency=None):
    cart_id = None
    user_details = get_user_account(user_details=True)
    customer = user_details.get("customer_name") if user_details else None
    # customer = get_user_account().get("customer_name")
    if customer == 'Guest':
        quotation_doc = get_quotation_for_guest(customer)
    else:
        quotation_doc = get_quotation_for_customer(customer)

    if quotation_doc:
        update_quotation(quotation_doc, item_code, qty)
    else:
        quotation_doc = create_new_quotation(customer, item_code, qty, currency)

    return quotation_doc.name, quotation_doc.total_qty, quotation_doc.net_total, quotation_doc.base_net_total

def get_quotation_for_guest(customer):
    cart_id = frappe.request.cookies.get("cart_id")
    if cart_id and frappe.db.exists("Quotation", {"party_name": customer, "docstatus": 0, "order_type": "Shopping Cart", "name": cart_id}):
        return frappe.get_doc("Quotation", cart_id)
    else:
        return None
    
def get_quotation_for_customer(customer):
    if frappe.db.exists("Quotation", {"party_name": customer, "docstatus": 0, "order_type": "Shopping Cart"}):
        return frappe.get_last_doc("Quotation", 
            filters={"party_name": customer, 
            "docstatus": 0, "order_type": "Shopping Cart"})
    else:
        return None

def update_quotation(quotation_doc, item_code, qty):
    currency = quotation_doc.currency
    price_list = quotation_doc.selling_price_list

    
    item_price_exists = frappe.db.exists("Item Price", {
        "item_code": item_code,
        "price_list": price_list
    })

    if not item_price_exists:
        frappe.throw(f"Item Not Available In '{currency}'")

    stock_qty = get_stock_quantity(item_code)
    if stock_qty <= 0:
        frappe.throw(f"Item is out of stock")    

       
    for item in quotation_doc.items:
        if item.item_code == item_code:
            item.qty = int(qty)
            quotation_doc.save(ignore_permissions=True)
            break
    else:
        quotation_doc.append("items", {
            "item_code": item_code,
            "qty": int(qty)
        })
        quotation_doc.save(ignore_permissions=True)
    
    
    total_qty = sum([item.qty for item in quotation_doc.items])
    
    
    quotation_doc.shipping_rule = get_shipping_rule(total_qty,currency)
    quotation_doc.save(ignore_permissions=True)
    update_cart_count()
    
def get_price_list(currency):
    price_list_mapping = {
        "INR": "Standard Selling",  # Price list for INR
        "USD": "Standard Selling USD"  # Price list for USD
    }
    price_list = price_list_mapping.get(currency)
    
    if not frappe.db.exists("Price List", price_list):
        frappe.throw(f"Price list for currency {currency} is not configured.")
    
    return price_list


def get_transaction_currency():
    # Debugging print
    user_currency = frappe.cache().get_value("transaction_currency") or frappe.db.get_value("User", frappe.session.user, "transaction_currency")
    return user_currency or "INR"


def create_new_quotation(customer, item_code, qty, currency=None):
    quotation_doc = frappe.new_doc("Quotation")
    quotation_doc.party_name = customer
    quotation_doc.order_type = "Shopping Cart"

    if currency:
        quotation_doc.currency = currency
    else:
        currency = get_transaction_currency()
    
    price_list = get_price_list(currency)

    quotation_doc.currency = currency
    quotation_doc.selling_price_list = price_list  


    item_price_exists = frappe.db.exists("Item Price", {
        "item_code": item_code,
        "price_list": price_list
    })
    stock_qty = get_stock_quantity(item_code)
    if stock_qty <= 0:
        frappe.throw(f"Item is out of stock")

    if not item_price_exists:
        frappe.throw(f"Item Not Available In '{currency}'")

    quotation_doc.append("items", {
        "item_code": item_code,
        "qty": int(qty)
    })

    total_qty = int(qty)
    quotation_doc.shipping_rule = get_shipping_rule(total_qty,currency)
    quotation_doc.insert(ignore_permissions=True)
    update_cart_count()
    return quotation_doc



def get_shipping_rule(total_qty,currency):
    """
    Determine the shipping rule based on total quantity.
    """
    if total_qty == 1 and currency == "INR":
        return "1 books shipping"
    elif total_qty == 2 and currency == "INR":
        return "2 books shipping"
    elif total_qty >= 3 and currency == "INR":
        return "3 books shipping"
    if total_qty == 1 and currency == "USD":
        return "1 books shipping usd"
    elif total_qty == 2 and currency == "USD":
        return "2 books shipping usd"
    elif total_qty >= 3 and currency == "USD":
        return "3 books shipping usd"
    else:
        return "Default Shipping"


##### get guest and other customer quotation################

@frappe.whitelist(allow_guest=True)
def get_quotation(customer=None, item_code=None, quotation_details=False, guest_quotation=False):
    cart_id = None
    cart_id = frappe.request.cookies.get("cart_id")
    filters = ""
    if item_code:
        filters = f"AND qi.item_code = '{item_code}'"

    query = """
        SELECT
            qi.*, qi.item_code, qi.qty, qi.amount, qi.item_name, qi.rate, ti.custom_website_image,ti.website_image,
            q.name as quotation_name, q.transaction_date as date, q.net_total, q.customer_name, q.*
        FROM
            `tabQuotation` q
        JOIN
            `tabQuotation Item` qi ON q.name = qi.parent
        INNER JOIN
            `tabWebsite Item` ti ON qi.item_code = ti.item_code
        WHERE
            q.quotation_to = 'Customer' AND
            q.docstatus = 0 {filters} AND
            {condition} AND
            q.docstatus != 2  
    """

    condition = ""
    if frappe.session.user == 'Guest':
        condition = f"q.name = '{cart_id}'"
    else:
        user_details = get_user_account(user_details=True)
        customer_name = user_details.get("customer_name") if user_details else None
        # user_account = get_user_account()
        # customer_name = user_account.get("customer_name")
        condition = f"q.customer_name = '{customer_name}'"

    query = query.format(condition=condition, filters=filters)  

    cart_items = frappe.db.sql(query, as_dict=True)

    if quotation_details:
        conversion_rate = cart_items[0].get("conversion_rate") if cart_items else 0
        base_total = cart_items[0].get("base_total") if cart_items else 0
        net_total = cart_items[0].get("net_total") if cart_items else 0
        base_net_total = cart_items[0].get("base_net_total") if cart_items else 0
        base_grand_total = cart_items[0].get("base_grand_total") if cart_items else 0
        grand_total = cart_items[0].get("grand_total") if cart_items else 0
        amount = cart_items[0].get("amount") if cart_items else 0

        return {
            "net_total": net_total,
            "base_net_total": base_net_total,
            "amount": amount,
            "base_grand_total": base_grand_total,
            "grand_total": grand_total,
            "total": net_total,
            "base_total": base_total,
            "conversion_rate": conversion_rate,
            "cart_items": cart_items if cart_items else []
        }

    return cart_items if cart_items else []

@frappe.whitelist()
def delete_last_draft_quotation():
    user = frappe.session.user
    last_quotation = frappe.db.get_list(
        "Quotation",
        filters={"owner": user, "docstatus": 0},
        fields=["name"],
        order_by="creation DESC",
        limit=1
    )

    if not last_quotation:
        frappe.throw("No draft quotations found for the user", frappe.PermissionError)

    quotation_doc = frappe.get_doc("Quotation", last_quotation[0]["name"])
    if frappe.db.exists("Sales Order Item", {"prevdoc_docname": quotation_doc.name}):
        sales_order = frappe.get_value("Sales Order Item", {"prevdoc_docname": quotation_doc.name}, "parent")
        sales_order_doc = frappe.get_doc("Sales Order", sales_order)
        if sales_order_doc.docstatus == 1:
            sales_order_doc.cancel()
        sales_order_doc.delete()
    quotation_doc.delete(ignore_permissions=True) 

    return {"status": "success", "message": "Last draft quotation deleted successfully"}


#remove Quotation
@frappe.whitelist(allow_guest=True)
def delete_quotation(quotation_name=None, item_code=None):
    if not quotation_name:
        frappe.local.response["status_code"] = 400
        frappe.local.response["message"] = "Quotation name is required"
        return

    quotation_doc = frappe.get_doc("Quotation", quotation_name)
    
    if len(quotation_doc.items) > 1:  
        for item in quotation_doc.items:
            if item.item_code == item_code:
                
                quotation_doc.items.remove(item)
                quotation_doc.save(ignore_permissions=True)

                
                total_qty = sum(item.qty for item in quotation_doc.items)
                currency = quotation_doc.currency

                
                new_shipping_rule = get_shipping_rule(total_qty,currency)
                quotation_doc.shipping_rule = new_shipping_rule
                quotation_doc.save(ignore_permissions=True)

                
                update_cart_count()

                frappe.local.response["status_code"] = 200
                frappe.local.response["message"] = f"Item removed. Updated shipping rule: {new_shipping_rule}"
                return

        frappe.local.response["status_code"] = 404
        frappe.local.response["message"] = "Quotation item not found"
    else:  
        quotation_doc.delete(ignore_permissions=True)

        
        frappe.cache().set_value("cart_count", 0)

        frappe.local.response["status_code"] = 200
        frappe.local.response["message"] = "Quotation deleted successfully"


# cart update including Guest user

@frappe.whitelist(allow_guest=True)
def update_cart_count(customer=None):
    cart_id = None
    cart_id = frappe.request.cookies.get("cart_id")
    if frappe.session.user == 'Guest':
        if not cart_id or not frappe.db.exists("Quotation", {"customer_name": 'Guest', "docstatus": 0, "name": cart_id}):
            frappe.cache().set_value("cart_count", 0)
            return frappe.cache().get_value("cart_count")
        else:
            quotation_doc = frappe.get_last_doc("Quotation", {"customer_name": 'Guest', "docstatus": 0, "name": cart_id})
            frappe.cache().set_value("cart_count", quotation_doc.total_qty)
            return frappe.cache().get_value("cart_count")
    else:
        user_details = get_user_account(user_details=True)
        customer_name = user_details.get("customer_name") if user_details else None
        # customer_name = customer_data.get("customer_name")
        customer = frappe.get_value("Customer", {"customer_name": customer_name}, "name")
        
        if not frappe.db.exists("Quotation", {"customer_name": customer_name, "docstatus": 0}):
            frappe.cache().set_value("cart_count", 0)
            return frappe.cache().get_value("cart_count")
        else:
            quotation_doc = frappe.get_last_doc("Quotation", {"customer_name": customer_name, "docstatus": 0})
            frappe.cache().set_value("cart_count", quotation_doc.total_qty)
            return frappe.cache().get_value("cart_count")




# @frappe.whitelist(allow_guest=True)
# def update_cart_count(customer=None):
#     customer_data = get_user_account()
#     if customer_data:
#         print(customer_data.customer_name)
#         customer = frappe.get_value("Customer", {"customer_name":customer_data.get("customer_name")}, "name")
#     # if not frappe.db.exists("Quotation", {"customer_name":customer, "docstatus":0}):
#     #     return 
#     if not frappe.db.exists("Quotation", {"customer_name":customer, "docstatus":0}):
#         frappe.cache().set_value("cart_count", 0)
#         return frappe.cache().get_value("cart_count")
    
#     quotation_doc = frappe.get_last_doc("Quotation", {"customer_name":customer, "docstatus":0})
#     frappe.cache().set_value("cart_count", quotation_doc.total_qty)    
#     return frappe.cache().get_value("cart_count")





# wishlist apis
@frappe.whitelist(allow_guest=True)
def add_to_wishlist(item_code=None):
    if not item_code:
        frappe.local.response["status_code"] = 400
        frappe.local.response["message"] = "Item code is required."
        return

    if frappe.db.exists("Wishlist Item", {"item_code": item_code, "parent": frappe.session.user}):
        frappe.local.response["status_code"] = 409
        frappe.local.response["message"] = "Item already exists in wishlist."
        return

    web_item_data = frappe.db.get_value(
        "Website Item",
        {"item_code": item_code},
        [
            "website_image",
            "website_warehouse",
            "name",
            "web_item_name",
            "item_name",
            "item_group",
            "route",
        ],
        as_dict=1,
    )

    if not web_item_data:
        frappe.local.response["status_code"] = 404
        frappe.local.response["message"] = "Item not found."
        return

    wished_item_dict = {
        "item_code": item_code,
        "item_name": web_item_data.get("item_name"),
        "item_group": web_item_data.get("item_group"),
        "website_item": web_item_data.get("name"),
        "web_item_name": web_item_data.get("web_item_name"),
        "image": web_item_data.get("website_image"),
        "warehouse": web_item_data.get("website_warehouse"),
        "route": web_item_data.get("route"),
    }

    if not frappe.db.exists("Wishlist", frappe.session.user):
        wishlist = frappe.get_doc({"doctype": "Wishlist"})
        wishlist.user = frappe.session.user
        wishlist.append("items", wished_item_dict)
        wishlist.save(ignore_permissions=True)
    else:
        wishlist = frappe.get_doc("Wishlist", frappe.session.user)
        item = wishlist.append("items", wished_item_dict)
        item.db_insert()

    frappe.local.response["status_code"] = 201
    frappe.local.response["message"] = "Item added to wishlist successfully."



#remove item from wish list
@frappe.whitelist(allow_guest=True)
def remove_from_wishlist(item_code=None):
    if frappe.db.exists("Wishlist Item", {"item_code": item_code, "parent": frappe.session.user}):
        frappe.db.delete("Wishlist Item", {"item_code": item_code, "parent": frappe.session.user})
        frappe.db.commit()

        wishlist_items = frappe.db.get_values("Wishlist Item", filters={"parent": frappe.session.user})

        if hasattr(frappe.local, "cookie_manager"):
            frappe.local.cookie_manager.set_cookie("wish_count", str(len(wishlist_items)))

        frappe.local.response["status_code"] = 200
        frappe.local.response["message"] = "Item removed from wishlist successfully."
    else:
        frappe.local.response["status_code"] = 404
        frappe.local.response["message"] = "Item not found in wishlist."
### add coupon code

def get_stock_quantity(item_code):
    web_item_details = get_product_info_for_website(item_code, False)

    if web_item_details and web_item_details.get("product_info"):
        stock_qty = web_item_details["product_info"].get("stock_qty", 0)
        
        if isinstance(stock_qty, list):
            stock_qty = stock_qty[0][0] if stock_qty and stock_qty[0] else 0
        return float(stock_qty)
    return 0.0

@frappe.whitelist(allow_guest=True)
def get_cart_currency_info():
    user = frappe.session.user

    
    quotation = frappe.get_all(
        "Quotation",
        filters={
            "docstatus": 0,
            "order_type": "Shopping Cart",
            "owner": user
        },
        fields=["name", "currency"],
        limit=1
    )

    if quotation:
        quotation_doc = frappe.get_doc("Quotation", quotation[0].name)
        return {
            "currency": quotation_doc.currency,
            "item_count": len(quotation_doc.items)
        }

    return {
        "currency": None,
        "item_count": 0
    }




