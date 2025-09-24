import frappe
from leftwordlatest.web_api.user import get_user_account
from leftwordlatest.web_api.checkout import get_order

def get_context(context):
    context.no_cache = True
    context.user_data = get_user_account()
    # context.customer_name = context.user_data.get('customer_name')
    context.completed_order = get_order(order_success=True)
    if context.completed_order:
        context.order_name = get_order(order_success=True).get('order_name')
        context.total = get_order(order_success=True).get('grand_total')
        context.date = get_order(order_success=True).get('transaction_date')
        context.payment = get_order(order_success=True).get('payment')


    # context.order_name = context.completed_order.get('order_name')

