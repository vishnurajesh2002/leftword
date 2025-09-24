import frappe

from leftwordlatest.web_api.items import makeup_pagination
def get_context(context):
    context.no_cache=True
    context.items = []
    context.page_count = 0
    context.item_count = 0

    if frappe.form_dict.get("filter_args"):
        item_codes = frappe.form_dict.get("filter_args").split(',')
        filters = {
            "item_code": item_codes,
            "item_group": "Ebooks"
        }
    else:
        filters = {
            "item_group": "Ebooks"
        }

    data = makeup_pagination(filters=filters )
    if data:
        context.items = [item for item in data.get("items") if item.get("has_variants") == 0]
        context.page_count = data.get("page_count")
        context.item_count = data.get("item_count")
        context.ppp = data.get("ppp")