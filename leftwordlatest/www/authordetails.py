import frappe

def get_context(context):
    context.no_cache = True
    
    author_name = frappe.form_dict.get("author_name")
    
    authors = get_author_items(author_name)
    
    if author_name:
        author_details = next((author for author in authors if author["author_name"] == author_name), None)
        
        if author_details:
            context.author_name = author_details["author_name"]
            context.author_image = author_details["author_image"]
            context.author_description = author_details["author_description"]
            context.items = author_details.get("items", [])
            
            context.other_authors = [author for author in authors if author["author_name"] != author_name]
        else:
            frappe.local.flags.redirect_location = "/author"
            raise frappe.Redirect
    else:
        frappe.local.flags.redirect_location = "/author"
        raise frappe.Redirect


def get_author_items(selected_author):
    authors = frappe.db.sql("""
        SELECT 
            WR.custom_name AS author_name,
            WR.image AS author_image,
            WR.description AS author_description
        FROM 
            `tabWriter` WR
    """, as_dict=True)

    author_names = [author["author_name"] for author in authors]
    
    items_by_author = frappe.db.sql("""
        SELECT 
            ITM.item_code AS item_code, 
            ITM.item_name,
            ITM.custom_publisher,
            ITM.custom_image1,
            ITM.custom_image2,
            ITM.custom_image3,
            AUTH.custom_name AS author_name,
            WI.custom_website_image AS custom_website_image,
            ITM.image AS item_image,
            WI.website_image 
        FROM 
            `tabItem` ITM
        INNER JOIN 
            `tabAuthor` AUTH ON AUTH.parent = ITM.item_code
        LEFT JOIN
            `tabWebsite Item` WI ON WI.item_code = ITM.item_code
        WHERE 
            ITM.disabled = 0
            AND ITM.has_variants=0
            AND WI.published = 1
            AND AUTH.custom_name IN (%s)
    """ % ', '.join(['%s'] * len(author_names)), tuple(author_names), as_dict=True)

    item_codes = [item["item_code"] for item in items_by_author]
    prices = frappe.db.sql("""
        SELECT
            IP.item_code AS item_code,
            IP.currency AS currency,
            IP.price_list_rate AS price_list_rate
        FROM 
            `tabItem Price` IP
        WHERE 
            IP.item_code IN (%s)
            AND IP.currency IN ('INR', 'USD')
    """ % ', '.join(['%s'] * len(item_codes)), tuple(item_codes), as_dict=True)

    # Create a dictionary with prices
    price_dict = {}
    for price in prices:
        item_code = price["item_code"]
        currency = price["currency"]
        rate = price["price_list_rate"]
        if item_code not in price_dict:
            price_dict[item_code] = {"INR": 0, "USD": 0}  
        price_dict[item_code][currency] = rate

    items_dict = {}
    for item in items_by_author:
        item_code = item["item_code"]
        inr_price = price_dict.get(item_code, {}).get("INR", 0)
        usd_price = price_dict.get(item_code, {}).get("USD", 0)

        items_dict.setdefault(item["author_name"], []).append({
            "item_code": item_code,
            "item_name": item["item_name"],
            "custom_publisher": item["custom_publisher"],
            "custom_website_image": item["custom_website_image"],
            "website_image": item["website_image"],
            "custom_image1": item.get("custom_image1"),  
            "custom_image2": item.get("custom_image2"),
            "custom_image3": item.get("custom_image3"),
            "item_image": item["item_image"],
            "price_list_rate_inr": inr_price,
            "price_list_rate_usd": usd_price
        })

    for author in authors:
        author["items"] = items_dict.get(author["author_name"], [])

    return authors
