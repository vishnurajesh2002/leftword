import frappe
from leftwordlatest.web_api.items import get_items, makeup_pagination
from leftwordlatest.web_api.author import get_items_with_authors



def get_context(context):
    context.no_cache = True
    context.authors = get_authors_alphabetic()
@frappe.whitelist(allow_guest=True)
def get_authors_alphabetic():

    authors_list = frappe.get_all(
        "Author",
        fields=["custom_name"],
        order_by="custom_name"
    )

    grouped_authors = {}
    seen = set()  

    for author in authors_list:
        custom_name = author["custom_name"]
        if custom_name  not in seen:
            seen.add(custom_name)
            initial = custom_name[0].upper()
            grouped_authors.setdefault(initial, []).append(custom_name)

    for initial in grouped_authors:
        grouped_authors[initial] = grouped_authors[initial][:3]

    return grouped_authors

