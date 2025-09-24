import frappe
from leftwordlatest.web_api.itemquery import makeup_pagination
def get_context(context):
    context.no_cache = True
    context.items = []
    context.page_count = 0
    context.item_count = 0

    series = frappe.db.sql("""
        SELECT custom_series
        FROM tabItem
        WHERE custom_series LIKE '_%'
          AND has_variants = 0
    """, as_dict=True)
    
    series_list = []
    for s in series:
        if s["custom_series"] not in series_list:
            series_list.append(s["custom_series"])
    context.series = series_list

    data = makeup_pagination(search_key=frappe.form_dict.get("series"))
    if data:
   
        context.items = [item for item in data.get("items") if item.get("has_variants") == 0]
        context.page_count = data.get("page_count")
        context.item_count = data.get("item_count")
        context.ppp = data.get("ppp")
