import frappe
from leftwordlatest.web_api.items import get_items, makeup_pagination
from leftwordlatest.web_api.author import get_items_with_authors

def get_context(context):
    context.no_cache = True
    context.authors = []
    context.page_count = 0
    context.item_count = 0

    context.categories = frappe.db.get_list(
        "Item Category",
        order_by="name",
        pluck="name",
        ignore_permissions=True
    )

    
    if frappe.form_dict.get("filter_args"):
        authors= frappe.form_dict.get("filter_args").split(',')
        author_filters = {
            "authors": authors,
        }
    else:
        author_filters = {}

    
    data = get_items_with_authors(author_filters = author_filters )
    if data:
        context.authors = data.get("authors")
        context.page_count = data.get("page_count")
        context.author_count = data.get("author_count")
        context.auth_per_page = data.get("auth_per_page")
    
   
    oth_data = get_items(
        is_banner=True,
        banner=["Banner-3"],
        new_release=True
    )
    if oth_data:
        context.banners = oth_data.get("banner_list")
        context.new_release = oth_data.get("new_release")
