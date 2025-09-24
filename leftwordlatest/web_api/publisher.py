import frappe
from leftwordlatest.web_api.items import item_query

@frappe.whitelist(allow_guest=True)
def get_brand_variants_only(brand_name, start=0, limit=21):
    if not brand_name:
        return {"items": [], "total_count": 0}

    item_names = frappe.db.get_list(
        "Item",
        filters={
            "brand": brand_name,
            "has_variants": 0,  
            "disabled": 0
        },
        fields=["name"],
        ignore_permissions=True,
        pluck="name"
    )

    if not item_names:
        return {"items": [], "total_count": 0}

    total_count = len(item_names)
    paginated_item_names = item_names[int(start):int(start)+int(limit)]

    items = item_query(filters={"item_code": paginated_item_names})
    return {"items": items, "total_count": total_count}


@frappe.whitelist(allow_guest=True)
def get_brands(start_letter=None):
    if start_letter:
        filters = {"brand": ["like", start_letter + "%"]}
        brands = frappe.db.get_list(
            "Brand",
            fields=["name", "brand"],
            filters=filters,
            order_by="brand asc",
            ignore_permissions=True
        )
        return brands
    else:
        all_brands = frappe.db.get_list(
            "Brand",
            fields=["name", "brand"],
            order_by="brand asc",
            ignore_permissions=True
        )

        result = {}
        for brand in all_brands:
            first_char = brand["brand"][0].upper() if brand["brand"] else ""
            if first_char not in result:
                result[first_char] = []
            if len(result[first_char]) < 3:
                result[first_char].append(brand)

        flattened = []
        for letter in sorted(result.keys()):
            flattened.extend(result[letter])

        return flattened





