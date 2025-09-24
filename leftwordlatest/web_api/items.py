import json
import math
import frappe
from erpnext.e_commerce.shopping_cart.product_info import get_product_info_for_website
from leftwordlatest.web_api.user import get_user_account
@frappe.whitelist(allow_guest=True)
def get_items(**kwargs):
    # Get Banner item
    web_items = {}
    if kwargs.get("is_banner"):
        banner_list = {}
        if kwargs.get("banner"):
            banner = frappe.db.get_list(
                "Website Banners",
                {"banner": ["in", kwargs.get("banner")]},
                ["banner_name"],
                pluck="banner_name",
                ignore_permissions=True
            )
        else:
            banner = frappe.db.get_list(
                "Website Banners",
                ["banner_name"],
                pluck="banner_name",
                ignore_permissions=True
            )
        if banner:
            for ban in banner:
                if frappe.db.get_value("Banner Book", ban, ["disabled"]):
                    break
                banner_items = frappe.db.get_list(
                    "Banner Item",
                    {"parent": ban},
                    ["item_code"],
                    pluck="item_code",
                    ignore_permissions=True
                )
                
                banner_items = [item for item in banner_items if frappe.db.get_value("Item", item, "has_variants") != 1]
                
                banner_list[frappe.db.get_value("Website Banners", {"banner_name": ban}, "banner")] = {
                    "name": ban,
                    "banner_images": frappe.db.get_list("Banner Image", {"parent": ban}, "image", order_by="idx", pluck="image", ignore_permissions=True),
                    "banner_url": frappe.db.get_list("Banner Image", {"parent": ban}, "url", order_by="idx", pluck="url", ignore_permissions=True),
                    "items": []
                }

                if banner_items:
                    banner_list[frappe.db.get_value("Website Banners", {"banner_name": ban}, "banner")]["items"] = item_query(filters={"item_code": banner_items[0] if len(banner_items) == 1 else banner_items})
        if banner_list:
            web_items["banner_list"] = banner_list

    if kwargs.get("is_related"):
        rel_list = {}
        relation = kwargs.get("relation") if kwargs.get("relation") else frappe.db.get_list(
            "Related Items",
            {"disabled": False},
            pluck="name",
            ignore_permissions=True
        )
        for rel in relation:
            rel_itms = frappe.db.get_list(
                "Related Item",
                {"parent": rel},
                ["item_code"],
                pluck="item_code",
                ignore_permissions=True
            )
   
            rel_itms = [item for item in rel_itms if frappe.db.get_value("Item", item, "has_variants") != 1]
            
            # if rel_itms:
            #     rel_list[rel] = {
            #         "website_title": frappe.db.get_value("Related Items", rel, "website_title"),
            #         "items": item_query(filters={"item_code": rel_itms[0] if len(rel_itms) == 1 else rel_itms})
            #     }
            if rel_itms:
                items = item_query(filters={"item_code": rel_itms[0] if len(rel_itms) == 1 else rel_itms})
                rel_list[rel] = {
                    "website_title": frappe.db.get_value("Related Items", rel, "website_title"),
                    "items": deduplicate_items(items)
                }
        if rel_list:
            web_items["related_list"] = rel_list

    if kwargs.get("new_release"):
        new_release = item_query(order_by=["creation", "desc"], limit=6)
        

        new_release = [item for item in new_release if frappe.db.get_value("Item", item.get("item_code"), "has_variants") != 1]
        
        if new_release:
            web_items["new_release"] = new_release

    if kwargs.get("item_code"):
    
        has_variant = frappe.db.get_value("Item", kwargs.get("item_code"), "has_variants")
        if has_variant != 1:
            item_detail = item_query(filters={"item_code": kwargs.get("item_code")})
            if item_detail and isinstance(item_detail, list) and len(item_detail) > 0:
                web_item_details = get_product_info_for_website(kwargs.get("item_code"), False)

                if web_item_details and web_item_details.product_info:
                    if isinstance(web_item_details.product_info.get("stock_qty"), list):
                        web_item_details["product_info"]["stock_qty"] = web_item_details.get("product_info").get("stock_qty")[0][0]

                    item_detail[0].update(web_item_details)
                    if item_detail[0].get("slideshow"):
                        slide_img = frappe.db.get_list(
                            "Website Slideshow Item",
                            {"parent": item_detail[0].get("slideshow")},
                            ["image"],
                            pluck="image",
                            ignore_permissions=True
                        )
                        item_detail[0]["slideshow_image"] = slide_img

                    web_items["product_details"] = item_detail[0]
                    web_items["ap_related_items"] = get_related_items(kwargs.get("item_code"))
            else:
                frappe.throw(f"No item details found for item_code: {kwargs.get('item_code')}")

    return web_items


    
@frappe.whitelist(allow_guest=True)
def item_query(filters=None, order_by=None, start=0, limit=0, search_key="", page=None, products_per_page=None):
    """
    filters={"field_name":["value-1", "value-2"], "field_name":"value"}
    """
    if filters:
        filters = makeup_filters(filters)
    if search_key is None:
        search_key = ""
    custom_filters = ""
    order_query = ""
    search_query = ""
    limit_query = ""
    cat_itm = None
    ecom_settings = frappe.get_doc("E Commerce Settings")
    lw_settings = frappe.get_doc("Leftword Settings")
    search_key = search_key.replace("'", "''")
    sql_values = {
        "inr_price_list": ecom_settings.price_list,
        "usd_price_list": lw_settings.usd_price_list
    }
    if filters:
        for i, key in enumerate(filters):
            # param_key = f"filter_val_{i}"
            val = filters[key]
            if isinstance(val, list) and not val:
             continue
            param_key = f"filter_val_{i}"
            if isinstance(val, list) and len(val) > 1:
                custom_filters += f" AND WI.{key} IN %({param_key})s"
            else:
                custom_filters += f" AND WI.{key} = %({param_key})s"
            sql_values[param_key] = val if isinstance(val, list) else str(val)
    if order_by:
        if order_by[0] == "price_list_rate":
            order_query = "ORDER BY INR.{0} {1}".format(order_by[0], order_by[1])
        else:
            order_query = "ORDER BY WI.{0} {1}".format(order_by[0], order_by[1])
    if search_key:
        cat_itm = frappe.db.get_list(
            "Book Category",
            {"category_name": ["LIKE", '%'+search_key+'%']},
            ["parent"],
            pluck="parent",
            ignore_permissions=True
        )
        if len(cat_itm) == 1:
            cat_itm = "OR ITM.item_code = '{0}'".format(cat_itm[0])
        elif len(cat_itm) > 1:
            cat_itm = "OR ITM.item_code IN {0}".format(tuple(cat_itm))
        else:
            cat_itm = ""
        search_query = """
            AND (
                ITM.item_name LIKE '%%{0}%%' OR
                ITM.item_code LIKE '%%{0}%%' OR
                ITM.custom_title LIKE '%%{0}%%' OR
                ITM.custom_subtitle LIKE '%%{0}%%' OR
                ITM.custom_publisher LIKE '%%{0}%%' OR
                ITM.custom_language LIKE '%%{0}%%' OR
                ITM.custom_year LIKE '%%{0}%%' OR
                ITM.custom_year LIKE '%%{0}%%' OR
                ITM.description LIKE '%%{0}%%' OR
                ITM.custom_series LIKE '%%{0}%%' OR
                WI.web_item_name LIKE '%%{0}%%' OR
                AUTH.writer_names LIKE '%%{0}%%'  
                              
                {1}
            )
        """.format(search_key, cat_itm)

    if page:
        # ppp: products_per_page
        if products_per_page:
            ppp = int(products_per_page)
        else:
            ppp = int(ecom_settings.products_per_page)
        start = (int(ppp)*int(page)) -  ppp
        limit = ppp
        limit_query = """
            LIMIT
                {0}, {1}
        """.format(start, limit)

    query = """
        SELECT 
            WI.*, ITM.*,
            COALESCE(INR.price_list_rate, 0) as price_list_rate_inr,
            COALESCE(USD.price_list_rate, 0) as price_list_rate_usd,
            COALESCE(PR_INR.total_discount_percentage, 0) AS discount_amount_inr,
            COALESCE(PR_USD.total_discount_percentage, 0) AS discount_amount_usd,
            (COALESCE(INR.price_list_rate, 0) - (COALESCE(INR.price_list_rate, 0) * COALESCE(PR_INR.total_discount_percentage, 0) / 100)) AS discount_percentage_inr,
            (COALESCE(USD.price_list_rate, 0) - (COALESCE(USD.price_list_rate, 0) * COALESCE(PR_USD.total_discount_percentage, 0) / 100)) AS discount_percentage_usd
        FROM 
            `tabWebsite Item` WI
        INNER JOIN
            `tabItem` ITM ON WI.item_code = ITM.item_code
        LEFT JOIN
            `tabItem Price` INR ON INR.item_code = ITM.item_code
            AND INR.price_list = %(inr_price_list)s
            AND INR.currency = "INR"
        LEFT JOIN
            `tabItem Price` USD ON USD.item_code = ITM.item_code
            AND USD.price_list = %(usd_price_list)s
            AND USD.currency = "USD"
        LEFT JOIN (
            SELECT parent, GROUP_CONCAT(custom_name SEPARATOR ', ') AS writer_names
            FROM `tabAuthor`
            GROUP BY parent
        ) AUTH ON AUTH.parent = ITM.name

        /* INDIAN PRICING RULES: SUM brand + item_code discounts */
        LEFT JOIN (
            SELECT 
                I.item_code,
                SUM(COALESCE(PRI_INR.discount_percentage, 0)) AS item_discount,
                SUM(COALESCE(PRB_INR.discount_percentage, 0)) AS brand_discount,
                SUM(COALESCE(PRI_INR.discount_percentage, 0)) + SUM(COALESCE(PRB_INR.discount_percentage, 0)) AS total_discount_percentage
            FROM `tabItem` I
            LEFT JOIN (
                SELECT PRI_INR.item_code, PR_INR.discount_percentage
                FROM `tabPricing Rule` PR_INR
                INNER JOIN `tabPricing Rule Item Code` PRI_INR ON PR_INR.name = PRI_INR.parent
                WHERE
                    PR_INR.customer_group = 'Book Club Member'
                    AND PR_INR.currency = 'INR'
                    AND PR_INR.valid_upto >= CURDATE()
                    AND PR_INR.disable = 0
            ) PRI_INR ON PRI_INR.item_code = I.item_code
            LEFT JOIN (
                SELECT PRB_INR.brand, PR_INR.discount_percentage
                FROM `tabPricing Rule` PR_INR
                INNER JOIN `tabPricing Rule Brand` PRB_INR ON PR_INR.name = PRB_INR.parent
                WHERE
                    PR_INR.customer_group = 'Book Club Member'
                    AND PR_INR.currency = 'INR'
                    AND PR_INR.valid_upto >= CURDATE()
                    AND PR_INR.disable = 0
            ) PRB_INR ON PRB_INR.brand = I.brand
            GROUP BY I.item_code
        ) PR_INR ON PR_INR.item_code = ITM.item_code

        /* USD PRICING RULES: SUM brand + item_code discounts */
        LEFT JOIN (
            SELECT 
                I.item_code,
                SUM(COALESCE(PRI_USD.discount_percentage, 0)) AS item_discount,
                SUM(COALESCE(PRB_USD.discount_percentage, 0)) AS brand_discount,
                SUM(COALESCE(PRI_USD.discount_percentage, 0)) + SUM(COALESCE(PRB_USD.discount_percentage, 0)) AS total_discount_percentage
            FROM `tabItem` I
            LEFT JOIN (
                SELECT PRI_USD.item_code, PR_USD.discount_percentage
                FROM `tabPricing Rule` PR_USD
                INNER JOIN `tabPricing Rule Item Code` PRI_USD ON PR_USD.name = PRI_USD.parent
                WHERE
                    PR_USD.customer_group = 'Book Club Member'
                    AND PR_USD.currency = 'USD'
                    AND PR_USD.valid_upto >= CURDATE()
                    AND PR_USD.disable = 0
            ) PRI_USD ON PRI_USD.item_code = I.item_code
            LEFT JOIN (
                SELECT PRB_USD.brand, PR_USD.discount_percentage
                FROM `tabPricing Rule` PR_USD
                INNER JOIN `tabPricing Rule Brand` PRB_USD ON PR_USD.name = PRB_USD.parent
                WHERE
                    PR_USD.customer_group = 'Book Club Member'
                    AND PR_USD.currency = 'USD'
                    AND PR_USD.valid_upto >= CURDATE()
                    AND PR_USD.disable = 0
            ) PRB_USD ON PRB_USD.brand = I.brand
            GROUP BY I.item_code
        ) PR_USD ON PR_USD.item_code = ITM.item_code

        WHERE
            WI.published = 1
            AND ITM.disabled = False
            AND (COALESCE(INR.selling, False) = True OR COALESCE(USD.selling, False) = True)
            AND ITM.has_variants = 0
            {custom_filters}
            {search_query}
        {order_query}
        {limit_query}
    """


    items = frappe.db.sql(
        query.format(
            custom_filters=custom_filters,
            search_query=search_query,
            order_query=order_query,
            limit_query=limit_query
        ),
        sql_values,
        as_dict=True
    )

    return items


def makeup_filters(filters):
    if filters and type(filters) == str:
        filters = json.loads(filters)
    if filters.get("product_category"):
        cat_items = frappe.db.get_list(
            "Book Category",
            {"category_name": ["in", filters.get("product_category")]},
            ["parent"],
            pluck="parent",
            ignore_permissions = True
        )
        filters["item_code"] = cat_items
        del filters["product_category"]
    return filters

@frappe.whitelist(allow_guest=True)
def makeup_pagination(filters=None, search_key=None, page=None, sort_by=None, products_per_page=None):
    ecom_settings = frappe.get_doc("E Commerce Settings")        
    if sort_by:
        sort_condition = json.loads(sort_by)
        items = item_query(
            filters=filters,
            order_by=sort_condition,
            search_key=search_key,
            page=page,
            products_per_page=products_per_page
        )
    else:
        items = item_query(
            filters=filters,
            search_key=search_key,
            page=page,
            products_per_page=products_per_page
        )
    items = deduplicate_items(items)
    item_count = len(items)
    if products_per_page:
        ppp = int(products_per_page)
    else:
        ppp = ecom_settings.products_per_page
    # ppp: products_per_page
    if not page:
        page_count = 1
        if items and ppp and item_count >= ppp:
            page_count = math.ceil(item_count/ppp)
            items = items[0:ppp]
        return {"items":items, "item_count":item_count, "ppp":ppp, "page_count":page_count}
    else:
        return {"items":items, "total_count":item_count, "ppp":ppp}

@frappe.whitelist(allow_guest=True)
def get_related_items(item_code):
    #     item_data = frappe.get_doc("Item", item_code)
    # author_list = frappe.db.get_list("Author", {"parent":item_code}, "custom_name", ignore_permissions=True, pluck="custom_name")
    # author_query = ""
    # author_items = []
    # publisher_items = []
    # if author_list:
    #     author_items = frappe.db.get_list(
    #         "Author",
    #         {
    #             "custom_name": ["IN", author_list],
    #             "parent":["!=", item_code]
    #         },
    #         ["parent"],
    #         ignore_permissions=True,
    #         pluck="parent"
    #     )
    # if item_data.custom_publisher:
    #     publisher_items = frappe.db.get_list(
    #         "Item",
    #         {
    #             "custom_publisher":item_data.custom_publisher,
    #             "name": ['!=', item_code]
    #         },
    #         ["name"],
    #         ignore_permissions=True,
    #         pluck="name"
    #     )
    # if not author_items and publisher_items:
    #     return []
    # items = item_query(filters={"item_code":author_items + publisher_items})
    # return items
    # Books of same categories
    category_list = frappe.db.get_list("Book Category", {"parent":item_code}, "category_name", ignore_permissions=True, pluck="category_name")
    author_query = ""
    category_items = []
    if category_list:
        category_items = frappe.db.get_list(
            "Book Category",
            {
                "category_name": ["IN", category_list],
                "parent":["!=", item_code]
            },
            ["parent"],
            ignore_permissions=True,
            pluck="parent"
        )
        category_items = list(set(category_items))

    if not category_items:
        return []

    items = item_query(filters={"item_code": category_items})
    deduped_items = deduplicate_items(items)
    return deduped_items

    
    # if not category_items:
    #     return []
    # items = item_query(filters={"item_code":category_items})
    # return items



@frappe.whitelist(allow_guest=True)
def get_login_image():
    """Fetch the login image URL from Leftword Settings."""
    image_url = frappe.db.get_value('Leftword Settings', None, 'image')
    return {
        "image_url": image_url or "/src/img/login-left-img.jpg"  # Provide default if no image is set
    }


# @frappe.whitelist(allow_guest=True)
# def get_shipping_amount_for_rule():
#     """Fetch the shipping_amount from the Shipping Rule named '2-8 working days'."""
#     rule_name = "2-8 working days" 
#     shipping_amount = frappe.db.get_value('Shipping Rule', rule_name, 'shipping_amount')
#     return {
#         "shipping_amount": shipping_amount if shipping_amount is not None else 0
#     }


@frappe.whitelist(allow_guest=True)
def get_shipping_charge():
    """Fetch the shipping_charge from the Leftword Shipping Rule."""
    shipping_charge = frappe.db.get_value('Leftword Shipping Rule', None, 'shipping_charge')
    return {
        "shipping_charge": shipping_charge if shipping_charge is not None else ""
    }


@frappe.whitelist(allow_guest=True)
def get_leftword_catalogue():
    
    catalogues = frappe.get_all(
        "Leftword Catalogue",  
        fields=["catalogue_title", "year", "publisher_details","description", "pdf_file", "image"],
        order_by="modified desc"  
    )
    if not catalogues:
        return {"message": ("No catalogues found.")}

    return catalogues

    

@frappe.whitelist(allow_guest=True)
def get_shipping_charge():
    # Get the user account details
    user_details = get_user_account(user_details=True)
    customer = user_details.get("customer_name") if user_details else None

    if not customer:
        frappe.throw("Customer not found")

    # Fetch the latest quotation for the customer
    quotation_doc = frappe.get_last_doc(
        "Quotation", filters={"party_name": customer, "docstatus": 0, "order_type": "Shopping Cart"}
    )

    if not quotation_doc:
        frappe.throw("No active quotation found for the customer")

    # Fetch base_total_taxes_and_charges and total_taxes_and_charges
    currency = quotation_doc.currency
    base_shipping_charge = quotation_doc.base_total_taxes_and_charges or 0.00
    shipping_charge = quotation_doc.total_taxes_and_charges or 0.00

    # Return both values in the response
    return {
        "currency": currency,
        "base_total_taxes_and_charges": base_shipping_charge,
        "total_taxes_and_charges": shipping_charge
    }

# duplicate items new code api
def deduplicate_items(items):
    seen = set()
    unique = []
    for item in items:
        code = item.get("item_code")
        if code and code not in seen:
            seen.add(code)
            unique.append(item)
    return unique
