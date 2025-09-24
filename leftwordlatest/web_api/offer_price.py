import frappe
from frappe.utils import flt, getdate, nowdate

@frappe.whitelist(allow_guest=True)
def get_discounted_price(item_code, customer):
    customer_group_bc = "Book Club Member"
    customer_group_ind = "Individual"

    discounted_rate_inr = get_currency_wise_discounted_price(item_code, customer, currency="INR", customer_group=customer_group_ind)
    discounted_rate_usd = get_currency_wise_discounted_price(item_code, customer, currency="USD", customer_group=customer_group_ind)
    bc_discounted_rate_inr = get_currency_wise_discounted_price(item_code, customer, currency="INR", customer_group=customer_group_bc)
    bc_discounted_rate_usd = get_currency_wise_discounted_price(item_code, customer, currency="USD", customer_group=customer_group_bc)

    return {
        "dis_inr": discounted_rate_inr,
        "dis_usd": discounted_rate_usd,
        "bc_dis_inr": bc_discounted_rate_inr,
        "bc_dis_usd": bc_discounted_rate_usd
    }


def get_currency_wise_discounted_price(item_code, customer, currency, customer_group):
    customer_doc = frappe.get_doc("Customer", customer)
    item_doc = frappe.get_doc("Item", item_code)

    brand = item_doc.brand
    item_group = item_doc.item_group

    default_price_list = {
        "INR": "Standard Selling",
        "USD": "Standard Selling USD"
    }.get(currency)

    price_list_rate = frappe.db.get_value("Item Price", {
        "item_code": item_code,
        "price_list": default_price_list
    }, "price_list_rate")

    if not price_list_rate:
        return None

    base_price = flt(price_list_rate)

    # Item Code based pricing rules
    item_rules = frappe.db.sql("""
        SELECT pr.discount_percentage, pr.valid_upto
        FROM `tabPricing Rule` pr
        JOIN `tabPricing Rule Item Code` pr_item ON pr.name = pr_item.parent
        WHERE pr.selling = 1 AND pr.disable = 0
        AND pr.apply_on = 'Item Code'
        AND pr.customer_group = %s
        AND pr_item.item_code = %s
        AND (pr.currency IS NULL OR pr.currency = %s)
        AND (
            (pr.valid_from IS NULL OR pr.valid_from <= NOW()) AND
            (pr.valid_upto IS NULL OR pr.valid_upto >= NOW())
        )
    """, (customer_group, item_code, currency), as_dict=True)

    # Brand based pricing rules
    brand_rules = []
    if brand:
        brand_rules = frappe.db.sql("""
            SELECT pr.discount_percentage, pr.valid_upto
            FROM `tabPricing Rule` pr
            JOIN `tabPricing Rule Brand` pr_brand ON pr.name = pr_brand.parent
            WHERE pr.selling = 1 AND pr.disable = 0
            AND pr.apply_on = 'Brand'
            AND pr.customer_group = %s
            AND pr_brand.brand = %s
            AND (pr.currency IS NULL OR pr.currency = %s)
            AND (
                (pr.valid_from IS NULL OR pr.valid_from <= NOW()) AND
                (pr.valid_upto IS NULL OR pr.valid_upto >= NOW())
            )
        """, (customer_group, brand, currency), as_dict=True)

    # Item Group based pricing rules
    item_group_rules = []
    if item_group:
        item_group_rules = frappe.db.sql("""
            SELECT pr.discount_percentage, pr.valid_upto
            FROM `tabPricing Rule` pr
            JOIN `tabPricing Rule Item Group` pr_group ON pr.name = pr_group.parent
            WHERE pr.selling = 1 AND pr.disable = 0
            AND pr.apply_on = 'Item Group'
            AND pr.customer_group = %s
            AND pr_group.item_group = %s
            AND (pr.currency IS NULL OR pr.currency = %s)
            AND (
                (pr.valid_from IS NULL OR pr.valid_from <= NOW()) AND
                (pr.valid_upto IS NULL OR pr.valid_upto >= NOW())
            )
        """, (customer_group, item_group, currency), as_dict=True)

    all_rules = item_rules + brand_rules + item_group_rules
    total_discount = sum(rule['discount_percentage'] for rule in all_rules)

    if total_discount == 0:
        return None

    discounted_rate = base_price - (base_price * total_discount / 100)

    # Calculate minimum valid_upto
    valid_upto_dates = [getdate(rule['valid_upto']) for rule in all_rules if rule.get('valid_upto')]
    valid_days = None

    if valid_upto_dates:
        min_valid_upto = min(valid_upto_dates)
        today = getdate(nowdate())
        valid_days = (min_valid_upto - today).days
        if valid_days < 0:
            valid_days = 0

    return {
        "discounted_rate": discounted_rate,
        "valid_days": valid_days
    }
