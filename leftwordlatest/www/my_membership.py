import frappe
from leftwordlatest.web_api.user import get_user_account
from leftwordlatest.create_member_membership_sales_invoice import membership_exist

def get_context(context):
    context.no_cache = True  
    load_data(context)

def load_data(context):
    if frappe.session.user != "Guest":
        user_data = get_user_account(user_details=True)
        membership_amount = frappe.db.get_value("Membership Type", "Yearly Membership", "amount")
        membership_amount_usd = frappe.db.get_value("Membership Type", "Yearly Membership", "custom_usd_amount")
        if user_data:
            context.user_data = user_data
            context.customer = user_data.get('customer')
            context.customer_id = user_data.get('customer_name')
            context.first_name = user_data.get('first_name')
            context.email = user_data.get('email')
            context.customer_id = user_data.get('customer_id')
            
            context.member = membership_exist(context.customer_id)
            if context.member:
                context.member_button_class = "already-member"
                context.button_label = "Already Member"
                context.expiry_date = get_membership_expiry_date(context.customer)
                context.custom_check = frappe.db.get_value('Member', {'customer': context.customer}, 'custom_check')
            else:
                context.amount = membership_amount
                context.amount_usd = membership_amount_usd
                context.member_button_class = ""
                context.button_label = "Get Plan"
                context.expiry_date = None
                context.custom_check = None

def get_membership_expiry_date(customer_name):
    return frappe.db.get_value('Member', {'customer': customer_name}, 'custom_check')



# import frappe
# from datetime import datetime

# def check_membership_expiry():
#     today = datetime.now().date()

#     try:
#         # Get Memberships where custome_check (expiry date) is <= today
#         memberships = frappe.get_all(
#             "Member",
#             filters={"custome_check": ["<=", today]},
#             fields=["name", "member"]
#         )

#         for membership in memberships:
#             member_id = membership.member

#             try:
#                 # Check if the Customer exists
#                 if frappe.db.exists("Customer", member_id):
#                     customer = frappe.get_doc("Customer", member_id)

#                     # If customer_group is currently "Book Club Member", update to "Individual"
#                     if customer.customer_group == "Book Club Member":
#                         customer.customer_group = "Individual"
#                         customer.save()
#                         frappe.db.commit()

#                         frappe.logger().info(f"[SUCCESS] Customer {member_id}: customer_group changed to 'Individual' because Membership {membership.name} expired on {today}.")

#             except Exception as e:
#                 frappe.logger().error(f"[ERROR] Failed to update customer {member_id} for membership {membership.name}: {str(e)}")

#     except Exception as main_e:
#         frappe.logger().error(f"[ERROR] Failed to fetch memberships or process expiry check: {str(main_e)}")


import frappe
from datetime import datetime

def check_membership_expiry():
    today = datetime.now().date()
    frappe.logger().info(f"Running check_membership_expiry at {datetime.now()}")

    try:
        memberships = frappe.get_all(
            "Member",
            filters={"custome_check": ["<=", today]},
            fields=["name", "member"]
        )

        for membership in memberships:
            member_id = membership.member

            try:
                if frappe.db.exists("Customer", member_id):
                    customer = frappe.get_doc("Customer", member_id)

                    if customer.customer_group == "Book Club Member":
                        customer.customer_group = "Individual"
                        customer.save()
                        frappe.db.commit()

                        frappe.logger().info(f"Customer {member_id} changed to Individual due to Membership {membership.name} expired on {today}.")

            except Exception as e:
                frappe.logger().error(f"Error processing membership {membership.name} for customer {member_id}: {str(e)}")

    except Exception as e:
        frappe.logger().error(f"Error fetching memberships in check_membership_expiry: {str(e)}")

