import frappe
from datetime import datetime
from leftwordlatest.web_api.user import get_user_account
from leftwordlatest.web_api.cart import get_quotation


@frappe.whitelist(allow_guest=True)
# def create_order():
#     user_details = get_user_account(user_details=True)
#     customer_name = user_details.get("customer_name") if user_details else None
# #     # customer_name = get_user_account().get("customer_name")
#     # cancell_quotation_and_order()
#     cart_id = frappe.request.cookies.get("cart_id")

#     if cart_id:
#         quotation_name = frappe.db.get_value("Quotation", 
#             {"name": cart_id, 
#             "docstatus": 0, 
#             "order_type": "Shopping Cart"},
#             "name")
#         if not quotation_name:
#             frappe.local.response["status_code"] = 500
#             frappe.local.response["message"] = "Quotation not found for the given cart_id"
#             return

#         quotation_doc = frappe.get_doc("Quotation", quotation_name)

#         customer_name = quotation_doc.party_name
#         cart_items = quotation_doc.items

#         if not cart_items:
#             frappe.local.response["status_code"] = 500
#             frappe.local.response["message"] = "No items found in the quotation"
#             return
#     else:
#         frappe.local.response["status_code"] = 500
#         frappe.local.response["message"] = "Cart ID not found in request cookies"
#         return
    
#     # Calculate total quantity
#     total_qty = sum([item.qty for item in cart_items])

#     # Dynamically set shipping rule based on total quantity
#     if total_qty == 1:
#         shipping_rule = "1 books shipping"
#     elif total_qty == 2:
#         shipping_rule = "2 books shipping"
#     elif total_qty >= 3:
#         shipping_rule = "3 books shipping"
#     else:
#         shipping_rule = "Default Shipping" 

#     currency = get_transaction_currency()
#     price_list = get_price_list(currency)
#     so = frappe.new_doc("Sales Order")
#     so.customer = customer_name
#     so.transaction_date = datetime.now().date()
#     so.delivery_date = quotation_doc.transaction_date
#     so.order_type = "Shopping Cart"
#     so.currency = currency
#     so.selling_price_list = price_list

#     so.cost_center = "LWB - NRPPL"
#     so.shipping_rule = shipping_rule 

#     for item in cart_items:
#         so.append("items", {
#             "item_code": item.item_code,
#             "item_name": item.item_name,
#             "qty": item.qty,
#             "rate": item.rate,
#             "delivery_date": quotation_doc.transaction_date,
#             "prevdoc_docname": quotation_name
#         })

#     so.insert(ignore_permissions=True)
#     # cancell_quotation_and_order()
#     frappe.local.response["status_code"] = 200
#     frappe.local.response["order"] = so.name
#     frappe.local.response["message"] = "Placed order successfully."

#     if cart_items and customer_name != "Guest":
#         # date = cart_items[0].get("date")
#         # quotation_name = cart_items[0].get("quotation_name")
#         if quotation_name and customer_name != "Guest":
#             q_doc = frappe.get_doc("Quotation", quotation_name)
#             q_doc.flags.ignore_permissions = True
#             q_doc.submit()

#     return so.name

def get_transaction_currency():
   user_currency = frappe.cache().get_value("transaction_currency") or frappe.db.get_value("User", frappe.session.user, "transaction_currency")
   return user_currency or "INR"



@frappe.whitelist(allow_guest=True)
def create_order(billing_address=None, shipping_address=None):
    import datetime
    user_details = get_user_account(user_details=True)
    customer_name = user_details.get("customer_name") if user_details else None
    cart_id = frappe.request.cookies.get("cart_id")

    if not cart_id:
        frappe.local.response["status_code"] = 500
        frappe.local.response["message"] = "Cart ID not found in request cookies"
        return

    quotation_name = frappe.db.get_value("Quotation", 
        {"name": cart_id, "docstatus": 0, "order_type": "Shopping Cart"},
        "name")
    if not quotation_name:
        frappe.local.response["status_code"] = 500
        frappe.local.response["message"] = "Quotation not found for the given cart_id"
        return

    quotation_doc = frappe.get_doc("Quotation", quotation_name)
    cart_items = quotation_doc.items

    if not cart_items:
        frappe.local.response["status_code"] = 500
        frappe.local.response["message"] = "No items found in the quotation"
        return

    total_qty = sum([item.qty for item in cart_items])
    currency = quotation_doc.currency or get_transaction_currency()
    price_list = get_price_list(currency)

    shipping_rule = (
        "1 books shipping" if total_qty == 1 and currency == "INR" else
        "2 books shipping" if total_qty == 2 and currency == "INR" else
        "3 books shipping" if total_qty >= 3 and currency == "INR" else
        "1 books shipping usd" if total_qty == 1 and currency == "USD" else
        "2 books shipping usd" if total_qty == 2 and currency == "USD" else
        "3 books shipping usd" if total_qty >= 3 and currency == "USD" else
        None  
    )

    
    so = frappe.new_doc("Sales Order")
    so.customer = customer_name
    so.transaction_date = datetime.date.today()
    so.delivery_date = quotation_doc.transaction_date
    so.order_type = "Shopping Cart"
    so.currency = currency
    so.selling_price_list = price_list
    so.cost_center = "LWB - NRPPL"
    so.shipping_rule = shipping_rule

    if billing_address:
        billing_address_doc = frappe.get_doc("Address", billing_address)
        if billing_address_doc:
            so.shipping_address_name = billing_address_doc.name
            so.shipping_address_display = f"{billing_address_doc.address_line1} {billing_address_doc.address_line2}, {billing_address_doc.city}, {billing_address_doc.state}, {billing_address_doc.pincode}"

    if shipping_address:
        shipping_address_doc = frappe.get_doc("Address", shipping_address)
        if shipping_address_doc:
            so.customer_address = shipping_address_doc.name
            so.address_display = f"{shipping_address_doc.address_line1} {shipping_address_doc.address_line2}, {shipping_address_doc.city}, {shipping_address_doc.state}, {shipping_address_doc.pincode}"

    for item in cart_items:
        so.append("items", {
            "item_code": item.item_code,
            "item_name": item.item_name,
            "qty": item.qty,
            "rate": item.rate,
            "delivery_date": quotation_doc.transaction_date,
            "prevdoc_docname": quotation_name
        })

    so.insert(ignore_permissions=True)
    so.submit()

    if quotation_name and customer_name != "Guest":
        q_doc = frappe.get_doc("Quotation", quotation_name)
        q_doc.flags.ignore_permissions = True
        q_doc.submit()

    frappe.local.response["status_code"] = 200
    frappe.local.response["order"] = so.name
    
    frappe.local.response["message"] = "Order placed successfully."
    return {"order": so.name}



def get_price_list(currency):
   price_list_mapping = {
       "INR": "Standard Selling",  # Price list for INR
       "USD": "Standard Selling USD"  # Price list for USD
   }
   price_list = price_list_mapping.get(currency)
  
   if not frappe.db.exists("Price List", price_list):
       frappe.throw(f"Price list for currency {currency} is not configured.")
  
   return price_list





#delete order and  cancell Quotation
@frappe.whitelist(allow_guest=True)
def open_quotations():
    cart_id = frappe.request.cookies.get("cart_id")
    query = """
        SELECT
            q.name AS quotation_id,
            so.parent AS sales_order_id
        FROM
            `tabQuotation` q
        INNER JOIN
            `tabSales Order Item` so ON q.name = so.prevdoc_docname
        INNER JOIN
            `tabSales Order` s ON so.parent = s.name
        WHERE
            q.status = 'Open'
        AND 
            s.status = 'Draft'
        AND
            q.name != '{cart_id}'
        """

    results = frappe.db.sql(query, as_dict=True)
    return results if results else []
def cancell_quotation_and_order():
    open_quotation = open_quotations()

    for record in open_quotation:
        sales_order_id = record.get('sales_order_id')
        quotation_id = record.get('quotation_id')

        if sales_order_id:
            frappe.delete_doc('Sales Order', sales_order_id)
        
        quotation = frappe.get_doc('Quotation', quotation_id)
        if quotation.docstatus != 2:  
            quotation.cancel()



### GET Order ####################

@frappe.whitelist(allow_guest=True)
def get_order(customer=None, item_code=None, order_details=False, order_success=False):
  
    # customer_name = get_user_account().get("customer_name")
    user_details = get_user_account(user_details=True)
    customer_name = user_details.get("customer_name") if user_details else None
    # get all completed  order of customer
    if customer:
        cust_orders = frappe.db.get_all('Sales Order',
        filters={
            'customer_name': customer, 
            # 'status': 'Completed'
            'status': ['in', ['To Deliver', 'Completed']]
        },
        fields=['name', 'transaction_date', 'status', 'net_total' , 'base_net_total','grand_total','currency'],
        order_by='delivery_date desc'
        
        
        )
        for order in cust_orders:
            delivery_date_obj = order.get('transaction_date')  
            if delivery_date_obj:
                formatted_date = delivery_date_obj.strftime("%B %d, %Y")
                order['transaction_date'] = formatted_date
        return cust_orders 

    # customer order success details with payment

    if order_success:
        completed_order = frappe.db.sql(
        """
            SELECT 
                so.*,
                pe.mode_of_payment
            FROM 
                `tabSales Order` so
            LEFT JOIN 
                `tabPayment Entry Reference` per ON per.reference_name = so.name
            LEFT JOIN 
                `tabPayment Entry` pe ON pe.name = per.parent
            WHERE 
                so.status = 'Completed' AND
                so.customer_name = %(customer)s AND
                pe.docstatus = 1 AND
                pe.status = 'Submitted' AND
                pe.party_name = %(party_name)s
            ORDER BY 
                so.creation DESC
            LIMIT 1
        """, {"customer": customer_name, "party_name": customer_name}, as_dict=True)


        if completed_order:
            order_name = completed_order[0].get('name')
            grand_total = completed_order[0].get('grand_total')
            transaction_date_new = completed_order[0].get('transaction_date')
            if transaction_date_new:
                transaction_date = transaction_date_new.strftime("%B %d, %Y")
            mode_of_payment = completed_order[0].get('mode_of_payment')


            return {
                "order_name": order_name,
                "grand_total": grand_total,
                "transaction_date": transaction_date,
                "payment": mode_of_payment



            }
        else:
            return 0  


    #cart orders
    cart_id = frappe.request.cookies.get("cart_id")

    filters = ""
    if item_code:
        filters = f"AND si.item_code = '{item_code}'"
    order_items = frappe.db.sql(
        f"""
        SELECT
            si.item_code, si.qty, si.amount, si.item_name, 
            si.rate, ti.custom_website_image, s.name as order_name, 
            s.delivery_date as date, s.net_total, s.customer_name, s.status
        FROM
            `tabSales Order` s
        JOIN
            `tabSales Order Item` si ON s.name = si.parent
        INNER JOIN
            `tabWebsite Item` ti ON si.item_code = ti.item_code

        WHERE
            # s.customer = 'Customer' AND
            s.customer_name = '{customer_name}' AND
            s.docstatus = 0 {filters} AND
            si.prevdoc_docname = '{cart_id}'
        LIMIT 1
        """, as_dict=1)
    if order_details:
        net_total = order_items[0].get("net_total") if order_items else 0
        customer = order_items[0].get("customer_name") if order_items else 0


        return {
            "net_total": net_total,
            "customer_name": customer,
            "order_items":order_items if order_items else []
        }

    
    return order_items if order_items else []  


# #create sales invoice
@frappe.whitelist(allow_guest=True)
def create_invoice(order_id):
    order = frappe.get_doc("Sales Order", order_id)

    if not order:
        frappe.local.response["status_code"] = 500
        frappe.local.response["message"] = "Sales Order not found"
        return
    si = frappe.new_doc("Sales Invoice")
    si.flags.ignore_permissions = True
    si.customer = order.customer
    si.customer_address = order.customer_address  
    si.shipping_address_name = order.shipping_address_name  
    si.transaction_date = datetime.now().date()
    si.delivery_date = order.delivery_date
    si.order_type = "Shopping Cart"
    si.currency = order.currency
    si.selling_price_list = order.selling_price_list
    si.cost_center = "LWB - NRPPL"  
    si.shipping_rule = order.shipping_rule

    for item in order.items:
        si.append("items", {
            "item_code": item.item_code,
            "item_name": item.item_name,
            "qty": item.qty,
            "rate": item.rate,
            "delivery_date": item.delivery_date,
            "sales_order": order.name
        })

    si.save(ignore_permissions=True)

    si.submit()

    frappe.local.response["status_code"] = 200
    frappe.local.response["order"] = si.name
    frappe.local.response["message"] = "Sales Invoice created successfully."
    
    return {
        "status_code": 200,
        "order": si.name,
        "message": "Sales Invoice created successfully."
    }



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
   user_currency = frappe.cache().get_value("transaction_currency") or frappe.db.get_value("User", frappe.session.user, "transaction_currency")
   return user_currency or "INR"






