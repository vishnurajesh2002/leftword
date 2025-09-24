# import frappe
# from dateutil.relativedelta import relativedelta

# @frappe.whitelist()
# def create_member(customer_name, membership_type, year, email_id):
#     # Check if Member already exists
#     if frappe.db.exists('Member', {'member_name': customer_name}):
#         return 'Member already exists'


#     member = frappe.new_doc("Member")
#     member.member_name = customer_name
#     member.customer_name = customer_name
#     member.membership_type = membership_type
#     # email = frappe.db.get_value('Customer', {'customer_name': customer_name}, ['email_id'])
#     member.email_id = email_id
#     customer = frappe.db.get_value('Customer', {'customer_name': customer_name}, ['name'])
#     member.customer = customer
#     gender = frappe.db.get_value('Customer', {'customer_name': customer_name}, ['gender'])
#     member.gender = gender
#     print(gender)

#     start_date = frappe.utils.now_datetime()

#     if membership_type == 'Yearly Membership':
#         expiry_date = start_date + relativedelta(years=int(year))
#         member.custom_check = expiry_date
#         member.insert(ignore_permissions=True)
#         frappe.db.commit()

#         create_membership(member.name, customer_name, membership_type, year)
#         # create_user(member.name, customer_name, email_id)

#     elif membership_type == 'Lifetime Membership':
#         # For Lifetime Membership, set expiry date to 2 years from start date
#         expiry_date = start_date + relativedelta(years=2)
#         member.custom_check = expiry_date
#         member.insert(ignore_permissions=True)
#         frappe.db.commit()

#         create_membership(member.name, customer_name, membership_type, year)
#         # create_user(member.name, customer_name, email_id)
#     else:
#         return 'Invalid membership type'

#     return 'success'

# def create_membership(memberid, customer_name, membership_type, year):
#     # Check if Membership already exists for the member
#     if frappe.db.exists('Membership', {'member': memberid}):
#         return 'Membership already exists for the member'

#     membership = frappe.new_doc("Membership")
#     membership.member = memberid
#     membership.membership_type = membership_type

#     mt = frappe.get_doc("Membership Type", membership_type)

#     start_date = frappe.utils.now_datetime()

#     if membership_type == 'Yearly Membership':
#         membership.from_date = start_date
#         expiry_date = start_date + relativedelta(years=int(year))
#         membership.to_date = expiry_date
#     elif membership_type == 'Lifetime Membership':
#         membership.from_date = start_date
#         expiry_date = start_date + relativedelta(years=2)
#         membership.to_date = expiry_date

#     membership.amount = mt.amount * int(year)
#     membership.insert(ignore_permissions=True)
#     frappe.db.commit()

#     create_sales_invoice(customer_name, membership_type, year, mt.amount, memberid)

#     return 'success'

# def create_sales_invoice(customer_name, membership_type, year, amount, memberid):
#     # Create a new Sales Invoice
#     sales_invoice = frappe.new_doc("Sales Invoice")
#     sales_invoice.customer = customer_name
#     sales_invoice.due_date = frappe.utils.now_datetime()
#     sales_invoice.is_pos = 1
#     sales_invoice.pos_profile = 'LWB'
#     sales_invoice.update_stock = 1

#     # Create a new Sales Invoice Item
#     sales_invoice_item = frappe.new_doc("Sales Invoice Item")
#     sales_invoice_item.item_code = membership_type

#     if membership_type == 'Yearly Membership':
#         sales_invoice_item.qty = int(year)
#         sales_invoice_item.rate = amount
#         sales_invoice_item.amount = amount * int(year)
#         sales_invoice_item.base_rate = amount
#         sales_invoice_item.base_amount = amount * int(year)
#     elif membership_type == 'Lifetime Membership':
#         # Set the logic for Lifetime Membership, assuming amount is a one-time payment
#         sales_invoice_item.qty = 1
#         sales_invoice_item.rate = amount
#         sales_invoice_item.amount = amount
#         sales_invoice_item.base_rate = amount
#         sales_invoice_item.base_amount = amount

#     # Add the Sales Invoice Item to the Sales Invoice
#     sales_invoice.append('items', sales_invoice_item)

#     sales_invoice_payment = frappe.new_doc("Sales Invoice Payment")
#     sales_invoice_payment.mode_of_payment = "Cash"
#     sales_invoice_payment.amount = amount if membership_type == 'Lifetime Membership' else amount * int(year)
#     sales_invoice_payment.base_paid_amount = sales_invoice_payment.amount

#     # Add the Sales Invoice Payments to the Sales Invoice
#     sales_invoice.append('payments', sales_invoice_payment)

#     # Save the Sales Invoice
#     sales_invoice.insert(ignore_permissions=True)
#     frappe.db.commit()
#     sales_invoice.submit()    
#     update_membership(memberid, sales_invoice.name)
#     update_customer(customer_name, memberid)

#     return 'success'

# def update_customer(customer_name, memberid):   
#     cus = frappe.get_doc("Customer", {'customer_name':customer_name})    
#     cus.customer_group = "Book Club Member"
#     cus.member = memberid
#     cus.save(ignore_permissions=True)
#     frappe.db.commit()
#     return 'success'

# def update_membership(memberid, invoice_name):
#     # Get the Membership document by member ID
#     membership = frappe.get_doc("Membership", {'member': memberid})
#     membership.invoice = invoice_name
#     membership.paid = 1
#     membership.save(ignore_permissions=True)
#     frappe.db.commit()

#     return 'success'

# def create_user(memberid, customer_name, email_id):
#     user = frappe.get_doc({
#         "doctype": "User",
#         "email": email_id,
#         "first_name": customer_name
#     })
#     user.append("roles", {"role": "Customer"})
#     user.insert(ignore_permissions=True)
#     create_customer_and_contact(memberid, customer_name, email_id)

#     return 'success'

# def create_customer_and_contact(memberid, customer_name, email_id):
#     if not frappe.db.exists('Contact', {"email_id": email_id}):
#         contact = frappe.get_doc({
#             "doctype": "Contact",
#             "first_name": customer_name,
#             "email_id": email_id,
#         })
#         contact.update({
#             "email_ids": [{
#                 "email_id": email_id,
#                 "is_primary": 1
#             }]
#         })
#         contact.append("links", {
#             "link_doctype": "Customer",
#             "link_name": customer_name,
#         })
#         contact.flags.ignore_permissions = True
#         contact.flags.ignore_password_policy = True
#         contact.save(ignore_permissions=True)

# def membership_exist(customer_name):
#     query = """
#         SELECT 
#             m.member_name,
#             m.customer          
#         FROM 
#             `tabMember` m                      
#         """

#     members = frappe.db.sql(query, as_dict=True)
#     for member in members: 
#         if member['customer'] == customer_name:       
#             return 'Membership exists'

# import frappe
# from dateutil.relativedelta import relativedelta

# @frappe.whitelist()
# def create_member(customer_name,customer_id,membership_type, year, email_id, currency=None):
#     if frappe.db.exists('Member', {'member_name': customer_name}):
#         return 'Member already exists'
#     if frappe.db.exists('Dynamic Link', {
#     'link_doctype': 'Customer',
#     'link_name': customer_id,
#     'parenttype': 'Address'}):
#         member = frappe.new_doc("Member")
#         member.member_name = customer_name
#         member.customer_name = customer_name
#         member.membership_type = membership_type
#         member.email_id = email_id
#         customer = frappe.db.get_value('Customer', {'name': customer_id}, ['name'])
#         member.customer = customer
#         gender = frappe.db.get_value('Customer', {'name': customer_id}, ['gender'])
#         member.gender = gender

#         start_date = frappe.utils.now_datetime()

        
#         if membership_type == 'Yearly Membership':
#             expiry_date = start_date + relativedelta(years=int(year))
#             member.custom_check = expiry_date
#             member.insert(ignore_permissions=True)
#             frappe.db.commit()

#             sales_invoice_name = create_membership(member.name, customer_name, customer_id, membership_type, year, currency=currency)
#             # create_user(member.name, customer_name, email_id)

#         elif membership_type == 'Lifetime Membership':
#             expiry_date = start_date + relativedelta(years=2)
#             member.custom_check = expiry_date
#             member.insert(ignore_permissions=True)
#             frappe.db.commit()

#             sales_invoice_name = create_membership(member.name, customer_name, customer_id, membership_type, year, currency=currency)
#             # create_user(member.name, customer_name, email_id)
#         else:
#             return 'Invalid membership type'

#         return sales_invoice_name
#     else:
#         return "Address not found"

# def create_membership(memberid, customer_name, customer_id, membership_type, year, currency=None):
#     if frappe.db.exists('Membership', {'member': memberid}):
#         return 'Membership already exists for the member'

#     membership = frappe.new_doc("Membership")
#     membership.member = memberid
#     membership.membership_type = membership_type

#     mt = frappe.get_doc("Membership Type", membership_type)
#     start_date = frappe.utils.now_datetime()

#     if membership_type == 'Yearly Membership':
#         membership.from_date = start_date
#         expiry_date = start_date + relativedelta(years=int(year))
#         membership.to_date = expiry_date
#     elif membership_type == 'Lifetime Membership':
#         membership.from_date = start_date
#         expiry_date = start_date + relativedelta(years=2)
#         membership.to_date = expiry_date

#     membership.amount = mt.amount * int(year)
#     membership.insert(ignore_permissions=True)
#     frappe.db.commit()

#     sales_invoice_name = create_sales_invoice(customer_name, customer_id, membership_type, year, mt.amount, memberid, currency=currency)

#     return sales_invoice_name

# def create_sales_invoice(customer_name, customer_id, membership_type, year, amount, memberid, currency=None):
#     sales_invoice = frappe.new_doc("Sales Invoice")
#     sales_invoice.customer = customer_id
#     sales_invoice.due_date = frappe.utils.now_datetime()
#     sales_invoice.is_pos = 0
#     sales_invoice.pos_profile = 'May Day Bookstore'
#     sales_invoice.update_stock = 1

#     sales_invoice_item = frappe.new_doc("Sales Invoice Item")
#     sales_invoice_item.item_code = membership_type
    

#     if currency == 'USD':
#         sales_invoice.currency = currency  
#         sales_invoice.selling_price_list = "Standard Selling USD"  
#     elif currency == 'INR':
#         sales_invoice.currency = currency
#         sales_invoice.selling_price_list = "Standard Selling"

#     if membership_type == 'Yearly Membership':
#         sales_invoice_item.qty = int(year)
#         # sales_invoice_item.rate = amount
#         # sales_invoice_item.amount = amount * int(year)
#         # sales_invoice_item.base_rate = amount
#         # sales_invoice_item.base_amount = amount * int(year)
#     elif membership_type == 'Lifetime Membership':
#         sales_invoice_item.qty = 1
#         # sales_invoice_item.rate = amount
#         # sales_invoice_item.amount = amount
#         # sales_invoice_item.base_rate = amount
#         # sales_invoice_item.base_amount = amount

#     sales_invoice.append('items', sales_invoice_item)

#     # sales_invoice_payment = frappe.new_doc("Sales Invoice Payment")
#     # sales_invoice_payment.mode_of_payment = "Cash"
#     # sales_invoice_payment.amount = amount if membership_type == 'Lifetime Membership' else amount * int(year)
#     # sales_invoice_payment.base_paid_amount = sales_invoice_payment.amount

#     # sales_invoice.append('payments', sales_invoice_payment)

#     sales_invoice.insert(ignore_permissions=True)
#     frappe.db.commit()
#     sales_invoice.submit()

#     update_membership(memberid, sales_invoice.name)
#     update_customer(customer_name, customer_id, memberid)

#     return sales_invoice.name

# def update_customer(customer_name, customer_id, memberid):   
#     cus = frappe.get_doc("Customer", customer_id)
#     # cus.customer_group = "Book Club Member"
#     cus.member = memberid
#     cus.save(ignore_permissions=True)
#     frappe.db.commit()
#     return 'success'

# def update_membership(memberid, invoice_name):
#     membership = frappe.get_doc("Membership", {'member': memberid})
#     membership.invoice = invoice_name
#     membership.paid = 0
#     membership.save(ignore_permissions=True)
#     frappe.db.commit()

#     return 'success'

# def create_user(memberid, customer_name, email_id):
#     user = frappe.get_doc({
#         "doctype": "User",
#         "email": email_id,
#         "first_name": customer_name
#     })
#     user.append("roles", {"role": "Customer"})
#     user.insert(ignore_permissions=True)
#     create_customer_and_contact(memberid, customer_name, email_id)

#     return 'success'

# def create_customer_and_contact(memberid, customer_name, email_id):
#     if not frappe.db.exists('Contact', {"email_id": email_id}):
#         contact = frappe.get_doc({
#             "doctype": "Contact",
#             "first_name": customer_name,
#             "email_id": email_id,
#         })
#         contact.update({
#             "email_ids": [{
#                 "email_id": email_id,
#                 "is_primary": 1
#             }]
#         })
#         contact.append("links", {
#             "link_doctype": "Customer",
#             "link_name": customer_name,
#         })
#         contact.flags.ignore_permissions = True
#         contact.flags.ignore_password_policy = True
#         contact.save(ignore_permissions=True)

# def membership_exist(customer_name):
#     query = """
#         SELECT 
#             m.member_name,
#             m.customer,
#             c.customer_group      
#         FROM 
#             `tabMember` m
#         JOIN
#             `tabCustomer` c
#         ON
#             c.name = m.customer
#         WHERE
#             c.customer_group = 'Book Club Member'                      
#         """
#     members = frappe.db.sql(query, as_dict=True)
#     for member in members: 
#         if member['customer'] == customer_name:       
#             return 'Membership exists'

import frappe
from frappe.utils import nowdate, now_datetime



@frappe.whitelist()
def create_sales_invoice_first(customer_name, customer_id, membership_type, year, email_id, amount=0, memberid=None, currency=None):
    try:
        # --- Validate Address ---
        has_address = frappe.db.exists("Dynamic Link", {
            "link_doctype": "Customer",
            "link_name": customer_id,
            "parenttype": "Address"
        })
        if not has_address:
            return {"status": "invalid", "reason": "Address not found"}

        # --- Validate Membership Type ---
        if membership_type not in ["Yearly Membership", "Lifetime Membership"]:
            return {"status": "invalid", "reason": "Invalid membership type"}

        # --- Check Existing Unpaid Invoice ---
        existing_invoice = frappe.db.sql("""
            SELECT name, status, grand_total, currency
            FROM `tabSales Invoice`
            WHERE customer=%s 
              AND status IN ('Unpaid','Overdue')
              AND docstatus=1
            ORDER BY creation DESC
            LIMIT 1
        """, (customer_id,), as_dict=True)

        if existing_invoice:
            inv = existing_invoice[0]
            return {
                "status": "exists",
                "invoice_name": inv.name,
                "customer": customer_id,
                "currency": inv.currency,
                "amount": inv.grand_total,
                "invoice_status": inv.status
            }

        # --- Create Sales Invoice ---
        sales_invoice = frappe.new_doc("Sales Invoice")
        sales_invoice.customer = customer_id
        sales_invoice.due_date = now_datetime()
        sales_invoice.is_pos = 0
        sales_invoice.pos_profile = "May Day Bookstore"
        sales_invoice.update_stock = 1   # refreshed as per your style

        # --- Create Sales Invoice Item ---
        sales_invoice_item = frappe.new_doc("Sales Invoice Item")
        sales_invoice_item.item_code = membership_type

        # Quantity & Rate logic
        if membership_type == "Yearly Membership":
            sales_invoice_item.qty = int(year)
            sales_invoice_item.rate = float(amount)
            sales_invoice_item.amount = float(amount) * int(year)

        elif membership_type == "Lifetime Membership":
            sales_invoice_item.qty = 1
            sales_invoice_item.rate = float(amount)
            sales_invoice_item.amount = float(amount)

        # --- Append item to Sales Invoice ---
        sales_invoice.append("items", sales_invoice_item)

        # --- Currency Setup ---
        if currency == "USD":
            sales_invoice.currency = "USD"
            sales_invoice.selling_price_list = "Standard Selling USD"
        else:
            sales_invoice.currency = "INR"
            sales_invoice.selling_price_list = "Standard Selling"

        # --- Insert & Submit ---
        sales_invoice.insert(ignore_permissions=True)
        frappe.db.commit()
        sales_invoice.submit()

        return {
            "status": "created",
            "invoice_name": sales_invoice.name,
            "customer": sales_invoice.customer,
            "currency": sales_invoice.currency,
            "amount": sales_invoice.grand_total,
            "invoice_status": sales_invoice.status
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Membership Invoice Failed")
        return {"status": "error", "message": str(e)}



import frappe
from dateutil.relativedelta import relativedelta

def create_membership_after_payment_entry(doc, method):
    """
    Create Member & Membership when a Payment Entry is submitted
    and linked to a Sales Invoice that is Paid.
    """
    
    if doc.docstatus != 1:
        return

    for reference in doc.references:
        if reference.reference_doctype == "Sales Invoice":
            si = frappe.get_doc("Sales Invoice", reference.reference_name)

            # Only proceed if Sales Invoice is Paid
            if si.docstatus == 1 and si.status == "Paid":
                customer_id = si.customer
                customer_name = frappe.db.get_value("Customer", customer_id, "customer_name")

                # --- Get email from linked Contact ---
                contact_name = frappe.db.get_value(
                    "Dynamic Link",
                    {"link_doctype": "Customer", "link_name": customer_id, "parenttype": "Contact"},
                    "parent"
                )
                email_id = None
                if contact_name:
                    email_id = frappe.db.get_value("Contact Email", {"parent": contact_name}, "email_id")

                # --- Membership type from Invoice item ---
                if not si.items:
                    frappe.throw(f"Sales Invoice {si.name} has no items. Cannot create Member/Membership.")
                membership_type = si.items[0].item_name

                # --- Get membership years (from qty if yearly/monthly) ---
                year = si.items[0].qty if membership_type in ["Yearly Membership", "Monthly Membership"] else 1
                amount = si.items[0].rate
                currency = si.currency

                # ---------------- Create Member ----------------
                if not frappe.db.exists("Member", {"member_name": customer_name}):
                    member = frappe.new_doc("Member")
                    member.member_name = customer_name
                    member.customer_name = customer_name
                    member.membership_type = membership_type
                    member.email_id = email_id
                    member.customer = customer_id
                    member.gender = frappe.db.get_value("Customer", customer_id, "gender")

                    start_date = frappe.utils.now_datetime()

                    # Expiry handling
                    if membership_type == 'Yearly Membership':
                        expiry_date = start_date + relativedelta(years=int(year))
                        member.custom_check = expiry_date

                    elif membership_type == 'Lifetime Membership':
                        expiry_date = start_date + relativedelta(years=2)  # change if truly lifetime
                        member.custom_check = expiry_date

                    member.insert(ignore_permissions=True)
                    frappe.db.commit()

                # --- Get Member ID ---
                member_id = frappe.db.get_value("Member", {"member_name": customer_name}, "name")


                # ---------------- Create Membership ----------------
                if member_id and not frappe.db.exists("Membership", {"member": member_id, "invoice": si.name}):
                    mt = frappe.get_doc("Membership Type", membership_type)
                    start_date = frappe.utils.now_datetime()

                    membership = frappe.new_doc("Membership")
                    membership.member = member_id
                    membership.membership_type = membership_type
                    membership.invoice = si.name   # make sure fieldname in Membership Doctype is 'invoice'
                    membership.from_date = start_date

                    if membership_type == 'Yearly Membership':
                        expiry_date = start_date + relativedelta(years=int(year))
                        membership.to_date = expiry_date
                    elif membership_type == 'Lifetime Membership':
                        expiry_date = start_date + relativedelta(years=2)
                        membership.to_date = expiry_date
                    else:
                        # fallback: at least set to_date = from_date
                        membership.to_date = start_date

                    membership.amount = mt.amount * int(year)
                    membership.insert(ignore_permissions=True)
                    frappe.db.commit()

                    update_customer(customer_name, customer_id, member_id)


                frappe.log_error(f"Member & Membership created/validated for Invoice {si.name}", "Membership Hook")
                

def update_customer(customer_name, customer_id, memberid):   
    cus = frappe.get_doc("Customer", customer_id)
    cus.customer_group = "Book Club Member"
    cus.member = memberid
    cus.save(ignore_permissions=True)
    frappe.db.commit()
    return 'success'

def membership_exist(customer_name):
    query = """
        SELECT 
            m.member_name,
            m.customer,
            c.customer_group      
        FROM 
            `tabMember` m
        JOIN
            `tabCustomer` c
        ON
            c.name = m.customer
        WHERE
            c.customer_group = 'Book Club Member'                      
        """
    members = frappe.db.sql(query, as_dict=True)
    for member in members: 
        if member['customer'] == customer_name:       
            return 'Membership exists'
