import frappe   

####ADD Shippping Address

@frappe.whitelist(allow_guest=True)
def add_shipping_address(email=None, street=None, city=None, country=None, phone=None, zip_code=None, state=None, first_name=None, last_name=None):
    user_email = email    
    if frappe.session.user != 'Guest':
        existing_shipping_address = frappe.db.exists(
            "Address",
            {
                "email_id": user_email, 
                "address_type": "Shipping", 
                "disabled": 0
            },
            "name"
        )
        if existing_shipping_address:
            # Update existing address
            existing_address_doc = frappe.get_doc("Address", existing_shipping_address)
            existing_address_doc.address_title = first_name
            existing_address_doc.address_line1 = street
            existing_address_doc.city = city
            existing_address_doc.is_shipping_address = 1
            existing_address_doc.phone = phone
            existing_address_doc.pincode = zip_code
            existing_address_doc.state = state
            existing_address_doc.save(ignore_permissions=True)
            return "Address Updated"
        else:
            new_shipping_address = frappe.new_doc("Address")
            new_shipping_address.email_id = email
            new_shipping_address.address_title = first_name
            new_shipping_address.address_type = "Shipping"
            new_shipping_address.address_line1 = street
            new_shipping_address.city = city
            new_shipping_address.is_shipping_address = 1
            # new_shipping_address.country = country
            new_shipping_address.phone = phone
            new_shipping_address.pincode = zip_code
            new_shipping_address.state = state
            new_shipping_address.insert(ignore_permissions=True)
            new_shipping_address.save(ignore_permissions=True)
            
            return "Address Added"
    
    if frappe.session.user == "Guest":
        cart_id = None
        cart_id = frappe.request.cookies.get("cart_id")
        if cart_id:
            quotation_exists = frappe.db.exists(
                "Quotation", 
                {"customer_name": 'Guest', 
                "docstatus": 0, 
                "name": cart_id})
            if quotation_exists:
                quotation_doc = frappe.get_doc(
                    "Quotation", 
                    {
                    "customer_name": 'Guest', 
                    "docstatus": 0, 
                    "name": cart_id
                    })
                quotation_doc.update({
                    "custom_first_name": first_name,
                    "custom_last_name": last_name,
                    "custom_phone_number": phone,
                    "custom_email_id": email,
                    "custom_street": street,
                    "custom_towncity": city,
                    "custom_state_": state,
                    "custom_country": country, 
                    "custom_zip_code": zip_code
                })
                quotation_doc.save(ignore_permissions=True)
                # frappe.db.commit()
                quotation_doc.submit()



                
######GET user Shipping Address
@frappe.whitelist(allow_guest=True)
def get_user_shipping_address(address_details=False, guest_address=False):
    user = frappe.session.user
    user_shipping_address = None
    if user != 'Guest' and address_details:
        sql_query = """
            SELECT * 
            FROM `tabAddress` 
            WHERE email_id = %s
            AND address_type = 'Shipping' 
            AND disabled = 0 
            AND is_shipping_address = 1
            ORDER BY creation DESC
            LIMIT 1
            """
        user_shipping_address = frappe.db.sql(sql_query, (user,), as_dict=True)
        if user_shipping_address:
            return user_shipping_address[0]
        else:
            return []
    if guest_address:
        cart_id = frappe.request.cookies.get("cart_id")
        quotation_exists = frappe.db.exists(
            "Quotation", 
            {
                "customer_name": 'Guest',
                "name": cart_id
            }
        )
        if quotation_exists:
            sql_query = """
                SELECT 
                    custom_first_name, custom_last_name, custom_state_, custom_towncity,
                    custom_phone_number, custom_email_id, custom_street, custom_zip_code

                FROM 
                    `tabQuotation` 
                WHERE 
                    docstatus = 1
                AND 
                    name = %s
                ORDER BY 
                    creation DESC
                LIMIT 1
                """
            guest_user_shipping_address = frappe.db.sql(sql_query, (cart_id,), as_dict=True)
            if guest_user_shipping_address:
                return guest_user_shipping_address[0]
            else:
                return []



#### Update  Shipping ADDRESS########
@frappe.whitelist(allow_guest=True)
def update_shipping_address(**kwargs):
    user_email = frappe.session.user
    if frappe.session.user != 'Guest':
        existing_shipping_address = frappe.db.exists(
            "Address",
            {"email_id": user_email, 
            "address_type": "Shipping", 
            "disabled": 0, 
            "is_shipping_address": 1},
            "name"
        )
        if existing_shipping_address:
            address_doc = frappe.get_doc("Address", kwargs.get("email"))
            address_doc.update(kwargs)
        if address_doc:
            address_doc.save(ignore_permissions=True)
            return True
        return False


# ####ADD Shippping Address

# @frappe.whitelist(allow_guest=True)
# def add_shipping_address(email=None, street=None, city=None, country=None, phone=None, zip_code=None, state=None, first_name=None):
#     user_email = email
    
#     if frappe.session.user != 'Guest':
#         existing_shipping_address = frappe.db.exists(
#             "Address",
#             {"email_id": user_email, "address_type": "Shipping", "disabled": 0},
#             "name"
#         )
#         if existing_shipping_address:
#             address_doc = frappe.get_doc("Address", existing_shipping_address)
#             address_doc.address_title = first_name
#             address_doc.city = city
#             address_doc.address_line1 = street
#             # address_doc.country = country
#             address_doc.phone = phone
#             address_doc.pincode = zip_code
#             address_doc.state = state
#             address_doc.save(ignore_permissions=True)
#             return "Shipping address updated successfully."
#         else:
#             create_address(email, street, city, country, phone, zip_code, state, first_name)
#             # add_billing_address(email, street, city, country, phone, zip_code, state, first_name)

#             return new_shipping_address.name
    
#     if frappe.session.user == "Guest":
#         cart_id = frappe.request.cookies.get("cart_id")
#         if cart_id:
#             quotation_exists = frappe.db.exists("Quotation", {"customer_name": 'Guest', "docstatus": 0, "name": cart_id})
#             if quotation_exists:
#                 quotation_doc = frappe.get_doc("Quotation", {"customer_name": 'Guest', "docstatus": 0, "name": cart_id})
#                 quotation_doc.update({
#                     "custom_first_name": first_name,
#                     "custom_phone_number": phone,
#                     "custom_email_id": email,
#                     "custom_street": street,
#                     "custom_towncity": city,
#                     "custom_state_": state,
#                     "custom_zip_code": zip_code
#                 })
#                 quotation_doc.save(ignore_permissions=True)
#                 quotation_doc.submit()
#                 create_address(email, street, city, country, phone, zip_code, state, first_name)
#                 # add_billing_address(email, street, city, country, phone, zip_code, state, first_name)

# def create_address(email, street, city, country, phone, zip_code, state, first_name):
#     new_shipping_address = frappe.new_doc("Address")
#     new_shipping_address.email_id = email
#     new_shipping_address.address_title = first_name
#     new_shipping_address.address_type = "Shipping"
#     new_shipping_address.address_line1 = street
#     new_shipping_address.city = city
#     # new_shipping_address.country = country
#     new_shipping_address.phone = phone
#     new_shipping_address.pincode = zip_code
#     new_shipping_address.state = state
#     new_shipping_address.insert(ignore_permissions=True)
#     new_shipping_address.save(ignore_permissions=True)
#     # return new_shipping_address.name


###### ADD billing Address#######################

@frappe.whitelist(allow_guest=True)
def add_billing_address(email=None, street=None, city=None, country=None, phone=None, zip_code=None, state=None, first_name=None):
    user_email = email
    
    if frappe.session.user != 'Guest':
        existing_billing_address = frappe.db.exists(
            "Address",
            {"email_id": user_email, "address_type": "Billing", "disabled": 0},
            "name"
        )
        if existing_billing_address:
            return 0
        else:
            new_billing_address = frappe.new_doc("Address")
            new_billing_address.email_id = email
            new_billing_address.address_title = first_name
            new_billing_address.address_type = "Billing"
            new_billing_address.address_line1 = street
            new_billing_address.city = city
            # new_shipping_address.country = country
            new_billing_address.phone = phone
            new_billing_address.pincode = zip_code
            new_billing_address.state = state
            new_billing_address.is_primary_address = 1
            new_billing_address.insert(ignore_permissions=True)
            new_billing_address.save(ignore_permissions=True)

    
    if frappe.session.user == "Guest":
        cart_id = None
        cart_id = frappe.request.cookies.get("cart_id")
        if cart_id:
            quotation_exists = frappe.db.exists(
                "Quotation", 
                {"customer_name": 'Guest', 
                "docstatus": 0, "name": cart_id})
            if quotation_exists:
                quotation_doc = frappe.get_doc(
                    "Quotation", 
                    {"customer_name": 'Guest', 
                    "docstatus": 0, 
                    "name": cart_id})
                quotation_doc.update({
                    "custom_first_name": first_name,
                    "custom_phone_number": phone,
                    "custom_email_id": email,
                    "custom_bill_street": street,
                    "custom_guest_towncity": city,
                    "custom_guest_state": state,
                    "custom_guest_pin_code": zip_code
                })
                quotation_doc.save(ignore_permissions=True)
                # quotation_doc.submit()


#### get billing Addresss ##############

@frappe.whitelist(allow_guest=True)
def get_user_billing_address(billing_address_details=False):
    user = frappe.session.user
    user_billing_address = None
    if billing_address_details:
        sql_query = """
            SELECT * 
            FROM `tabAddress` 
            WHERE email_id = %s
            AND address_type = 'Billing' 
            AND disabled = 0
            AND is_primary_address = 1
            ORDER BY creation DESC
            LIMIT 1
            """
        user_billing_address = frappe.db.sql(sql_query, (user,), as_dict=True)
        if user_billing_address:
            return user_billing_address[0]

        if not user_billing_address:
            return []
    else:
        return []



