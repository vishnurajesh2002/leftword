import frappe
from leftwordlatest.web_api.items import get_items, makeup_pagination
def get_context(context):
    context.no_cache = True
    context.items = []
    context.page_count = 0
    context.item_count = 0

    sliders = frappe.db.get_list(
        "Home Page Slider",
        ["slider_name"],
        order_by="idx asc",
        pluck="slider_name",
        ignore_permissions=True
    )
    home_data = get_items(
        is_banner=True,
        is_related=True,
        banner=["Banner-1", "Banner-2", "Banner-3"],
        relation=sliders,
        new_release=True
    )

    if home_data:
        context.new_release = list({item.get("item_code"): item for item in home_data.get("new_release", []) 
                                    if frappe.db.get_value("Item", item.get("item_code"), "has_variants") != 1}.values())

    context.categories = list(set(frappe.db.get_list(
        "Item Category",
        filters={"custom_enable": 1},
        order_by="name",
        pluck="name",
        ignore_permissions=True
    )))

    data = makeup_pagination(search_key=frappe.form_dict.get("search_key"))
    if data:
        context.items = list({item.get("item_code"): item for item in data.get("items", []) 
                              if frappe.db.get_value("Item", item.get("item_code"), "has_variants") != 1}.values())
        context.page_count = data.get("page_count")
        context.item_count = data.get("item_count")

    oth_data = get_items(
        is_banner=True,
        banner=["Banner-3"],
        new_release=True
    )
    if oth_data:
        context.banners = oth_data.get("banner_list")
        context.new_release += list({item.get("item_code"): item for item in oth_data.get("new_release", []) 
                                     if frappe.db.get_value("Item", item.get("item_code"), "has_variants") != 1}.values())
        
        context.new_release = list({item.get("item_code"): item for item in context.new_release}.values())
