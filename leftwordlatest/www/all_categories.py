import frappe
frappe.db.sql("UPDATE `tabItem Category` SET custom_enable = 1 WHERE custom_enable IS NULL OR custom_enable = 0")
frappe.db.commit()

def get_context(context):
    context.no_cache = True
    # Fetch all categories (no filter applied initially)
    context.categories = get_categories_by_alphabet(letter=None)

@frappe.whitelist(allow_guest=True)
def get_categories_by_alphabet(letter=None):
    filters = {"custom_enable": 1}  # Ensure only categories with custom_enable checked are fetched
    if letter:  # Apply filter only if a letter is provided
        filters["category_name"] = ["like", f"{letter}%"]

    categories = frappe.db.get_all(
        "Item Category",
        fields=["category_name"],
        filters=filters,
        order_by="category_name"
    )
    return categories  # Corrected from 'categoriess'
