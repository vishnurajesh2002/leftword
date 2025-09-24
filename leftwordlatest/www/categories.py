import frappe
from leftwordlatest.web_api.items import get_items, makeup_pagination

def get_context(context):
    context.no_cache = True
    context.items = []
    context.page_count = 0
    context.item_count = 0

    # Load categories
    context.categories = frappe.db.get_list(
        "Item Category",
        filters={"custom_enable": 1},
        order_by="name",
        pluck="name",
        ignore_permissions=True
    )

    filters = {}

    if frappe.form_dict.get("filter_args"):   
        item_codes = frappe.form_dict.get("filter_args").split(',')
        filters["product_category"] = item_codes

    if 'product_category' in filters and len(filters['product_category']) > 0:
        if len(filters['product_category']) == 1:
            result = filters['product_category'][0]
            if result and frappe.db.exists("Book Category", {"category_name": result}):
                data = makeup_pagination(filters=filters, search_key=frappe.form_dict.get("search_key"))
                if data:
                    context.items = [item for item in data.get("items") if item.get("has_variants") == 0]
                    context.page_count = data.get("page_count")
                    context.item_count = data.get("item_count")
                    context.ppp = data.get("ppp")
            else:
                context.items = []
        else:
            data = makeup_pagination(filters=filters, search_key=frappe.form_dict.get("search_key"))
            if data:
                context.items = [item for item in data.get("items") if item.get("has_variants") == 0]
                context.page_count = data.get("page_count")
                context.item_count = data.get("item_count")
                context.ppp = data.get("ppp")
    oth_data = get_items(
        is_banner=True,
        banner=["Banner-3"],
        new_release=True
    )
    if oth_data:
        context.banners = oth_data.get("banner_list")
        context.new_release = oth_data.get("new_release")
