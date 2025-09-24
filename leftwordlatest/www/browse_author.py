import frappe



def get_context(context):
    context.no_cache = True
    letter = frappe.form_dict.get("letter")
    context.authors = get_authors_by_letter(letter)
@frappe.whitelist(allow_guest=True)

def get_authors_by_letter(letter=None):
    if not letter:
        return []
    authors_list = frappe.get_all(
        "Author",
        filters={"custom_name": ["like", f"{letter}%"]},
        fields=["custom_name"],
        order_by="custom_name"
    )

    authors = []
    seen = set()  

    for author in authors_list:
        custom_name = author["custom_name"]
        if custom_name not in seen:
            seen.add(custom_name)
            authors.append(author)

    return authors
