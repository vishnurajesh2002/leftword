import frappe
import math
import json

@frappe.whitelist(allow_guest=True)
def get_items_with_authors(page=None, author_per_page=None, order_by=None, author_filters=None):
    auth_per_page = int(author_per_page) if author_per_page else 20
    start = (int(page) - 1) * auth_per_page if page else 0
    end = start + auth_per_page

    order_query = ""
    if order_by:
        order_by = json.loads(order_by)
        order_query = f"ORDER BY WR.{order_by[0]} {order_by[1]}"

    author_filters = author_filters.get("authors", []) if author_filters else []
    author_filters = [name.strip() for name in author_filters]

    filters_condition = (
        f"WR.custom_name IN ({', '.join(['%s'] * len(author_filters))})"
        if author_filters
        else "1=1"
    )

    all_authors = frappe.db.sql(
        f"""
        SELECT
            WR.custom_name AS author_name,
            WR.image AS author_image,
            WR.description AS author_description
        FROM
            `tabWriter` WR
        WHERE
            {filters_condition}
        {order_query}
        """,
        tuple(author_filters) if author_filters else (),
        as_dict=True,
    )

    page_count = math.ceil(len(all_authors) / auth_per_page)

    if not all_authors:
        return {
            "authors": [],
            "author_count": 0,
            "auth_per_page": auth_per_page,
            "page_count": 0,
        }

    authors = all_authors[start:end]
    author_names = [author["author_name"] for author in authors]

    items_by_author = frappe.db.sql(
        f"""
        SELECT
            ITM.item_code AS item_code,
            ITM.item_name,
            AUTH.custom_name AS author_name,
            WITM.custom_website_image AS custom_website_image
        FROM
            `tabItem` ITM
        INNER JOIN
            `tabAuthor` AUTH ON AUTH.parent = ITM.item_code
        LEFT JOIN
            `tabWebsite Item` WITM ON WITM.item_code = ITM.item_code
        WHERE
            WITM.published = 1
            AND ITM.disabled = 0
            AND AUTH.custom_name IN ({', '.join(['%s'] * len(author_names))})
        """,
        tuple(author_names),
        as_dict=True,
    )

    item_codes = [item["item_code"] for item in items_by_author]

    prices = frappe.db.sql(
        f"""
        SELECT
            IP.item_code AS item_code,
            IP.price_list AS price_list,
            IP.price_list_rate AS price_list_rate,
            IP.currency AS currency
        FROM
            `tabItem Price` IP
        WHERE
            IP.item_code IN ({', '.join(['%s'] * len(item_codes))})
            AND IP.currency IN ('INR', 'USD')
        """,
        tuple(item_codes),
        as_dict=True,
    ) if item_codes else []

    prices_dict = {}
    for price in prices:
        item_code = price["item_code"]
        currency = price["currency"]
        prices_dict.setdefault(item_code, {})[f"price_list_rate_{currency.lower()}"] = price["price_list_rate"]

    items_dict = {}
    for item in items_by_author:
        inr_price = prices_dict.get(item["item_code"], {}).get("price_list_rate_inr")
        usd_price = prices_dict.get(item["item_code"], {}).get("price_list_rate_usd")
        if inr_price and usd_price:
            items_dict.setdefault(item["author_name"], []).append({
                "item_code": item["item_code"],
                "item_name": item["item_name"],
                "custom_website_image": item["custom_website_image"],
                "price_list_rate_inr": inr_price,
                "price_list_rate_usd": usd_price,
            })

    for author in authors:
        author["items"] = items_dict.get(author["author_name"], [])

    return {
        "authors": authors,
        "author_count": len(all_authors),
        "auth_per_page": auth_per_page,
        "page_count": page_count,
    }
