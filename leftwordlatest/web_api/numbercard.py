
import frappe

@frappe.whitelist()
def get_inr_without_usd_count():
    result = frappe.db.sql("""
        SELECT COUNT(DISTINCT ip1.item_code) AS count
        FROM `tabItem Price` ip1
        INNER JOIN `tabItem` item ON ip1.item_code = item.name
        WHERE ip1.price_list = 'Standard Selling'
        AND item.has_variants = 0
        AND item.disabled = 0
        AND ip1.item_code NOT IN (
            SELECT ip2.item_code
            FROM `tabItem Price` ip2
            WHERE ip2.price_list = 'Standard Selling USD'
        )
    """, as_dict=True)
    count = result[0]['count'] if result else 0

    excluded_items = frappe.db.sql_list("""
        SELECT DISTINCT ip1.item_code
        FROM `tabItem Price` ip1
        LEFT JOIN `tabItem Price` ip2 ON ip1.item_code = ip2.item_code AND ip2.price_list = 'Standard Selling USD'
        INNER JOIN `tabItem` item ON ip1.item_code = item.name
        WHERE ip1.price_list = 'Standard Selling'
        AND item.has_variants = 0
        AND item.disabled = 0
        AND ip2.item_code IS NULL
    """)

    route_options = {
        "price_list": "Standard Selling",
        "has_variants": 0,
        "disabled": 0,
    }
    if excluded_items:
        route_options["item_code"] = ["in", excluded_items]

    return {
        "value": count,
        "fieldtype": "Int",
        "label": "INR without USD Count",
        "route": "List/Item Price",
        "route_options": route_options
    }
