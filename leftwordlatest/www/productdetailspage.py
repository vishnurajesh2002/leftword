import frappe
from leftwordlatest.web_api.items import get_items, item_query
from leftwordlatest.web_api.cart import get_quotation
from leftwordlatest.create_member_membership_sales_invoice import membership_exist
from leftwordlatest.web_api.user import get_user_account
from leftwordlatest.web_api.offer_price import get_discounted_price




def get_context(context):
    context.no_cache = True  
    load_data(context)
    context.no_cache = True
    context.authors = []
    context.editors = []
    context.translators = []
    context.introductions = []
    context.forewords = []
    context.illustrators = []
    context.contributors = []
    context.prefaces = []
    context.afterwords = []  
    # Ensure an ID is provided
    if frappe.form_dict.get("id") and frappe.db.exists("Item", frappe.form_dict.get("id")):
        load_product(context, frappe.form_dict.get("id"))

        child_categories = frappe.db.get_all("Book Category", {"parent": frappe.form_dict.get("id")}, ["category_name"])
        context.child_categories = [cat["category_name"] for cat in child_categories] 
    
    else:
        frappe.redirect("/")

    # Fetch author-related data
    author_child = frappe.db.get_all("Author", {"parent": frappe.form_dict.get("id")}, ["type", "custom_name"])
    
    # Loop through the data and populate context lists
    for i in author_child:
        if i["type"] == "Author":
            author_desc = get_author_items(i["custom_name"])
            context.authors.append({"name": author_desc[0].author_name, "author_desc": author_desc[0].author_description})
        elif i["type"] == "Translator":
            translator_desc = get_author_items(i["custom_name"])
            context.translators.append({"name": translator_desc[0].author_name, "translator_desc": translator_desc[0].author_description})
        elif i["type"] == "Editor":
            editor_desc = get_author_items(i["custom_name"])
            context.editors.append({"name": editor_desc[0].author_name, "editor_desc": editor_desc[0].author_description})
        elif i["type"] == "Introduction":
            Introduction_desc = get_author_items(i["custom_name"])
            context.introductions.append({"name": Introduction_desc[0].author_name, "Introduction_desc": Introduction_desc[0].author_description})
        elif i["type"] == "Foreword":
            foreword_desc = get_author_items(i["custom_name"])
            context.forewords.append({"name": foreword_desc[0].author_name, "foreword_desc": foreword_desc[0].author_description})
        elif i["type"] == "Illustrator":
            illustrator_desc = get_author_items(i["custom_name"])
            context.illustrators.append({"name": illustrator_desc[0].author_name, "illustrator_desc": illustrator_desc[0].author_description})
        elif i["type"] == "Contributor":
            contributor_desc = get_author_items(i["custom_name"])
            context.contributors.append({"name": contributor_desc[0].author_name, "contributor_desc": contributor_desc[0].author_description})
        elif i["type"] == "Preface":
            preface_desc = get_author_items(i["custom_name"])
            context.prefaces.append({"name": preface_desc[0].author_name, "preface_desc": preface_desc[0].author_description})
        elif i["type"] == "Afterword":
            afterword_desc = get_author_items(i["custom_name"])
            context.afterwords.append({"name": afterword_desc[0].author_name, "afterword_desc": afterword_desc[0].author_description})
    

    return context

def load_data(context):
    if frappe.session.user != "Guest":
        user_data = get_user_account(user_details=True)
        membership_amount = frappe.db.get_value("Membership Type", "Yearly Membership", "amount")
        if user_data:
            context.user_data = user_data
            context.customer = user_data.get('customer_name')
            context.first_name = user_data.get('first_name')
            context.email = user_data.get('email')
            
            context.member = membership_exist(context.customer)
            if context.member:
                context.expiry_date = get_membership_expiry_date(context.customer)
                context.custom_check = frappe.db.get_value('Member', {'customer': context.customer}, 'custom_check')
            else:
                context.amount = membership_amount
                context.member_button_class = ""
                context.button_label = "Get Plan"
                context.expiry_date = None
                context.custom_check = None
def get_membership_expiry_date(customer_name):
    return frappe.db.get_value('Member', {'customer': customer_name}, 'custom_check')

def load_product(context, id):
    context.allow_guest_cart = ""
    user_data = get_user_account(user_details=True)
    product = get_items(item_code=id)
    item_id = frappe.form_dict.get("id")
    if frappe.session.user == "Guest":
        cart_items = get_quotation(item_code=id, guest_quotation=True)
        context.hide_element = "hide-element"
        context.cart_button_class = "in-cart"
        context.button_label = "View In Cart" 
    cart_items = get_quotation(item_code=id)
    
    if cart_items:  
        context.hide_element = "hide-element"
        context.cart_button_class = "in-cart"
        context.button_label = "View In Cart"
    if cart_items == []:
        context.button_label = "Add To Cart"
        context.hide_element = ""
        context.cart_button_class = "add-to-cart"
    if frappe.db.get_single_value(
        "Leftword Settings",
        "allow_guest_cart"):
        context.allow_guest_cart = "allow-guest-cart"

    # product = get_items(item_code=id)
    product_details = product.get("product_details")

    discount_price = get_discounted_price(item_code=id, customer=user_data.get('customer_name'))
    discount_price_inr = discount_price['dis_inr']['discounted_rate'] if discount_price.get('dis_inr') else None
    discount_price_inr_valid_days = discount_price['dis_inr']['valid_days'] if discount_price.get('dis_inr') else None
    discount_price_usd = discount_price['dis_usd']['discounted_rate'] if discount_price.get('dis_usd') else None
    discount_price_usd_valid_days = discount_price['dis_usd']['valid_days'] if discount_price.get('dis_usd') else None
    discount_price_bc_inr = discount_price['bc_dis_inr']['discounted_rate'] if discount_price.get('bc_dis_inr') else None
    discount_price_bc_inr_valid_days = discount_price['bc_dis_inr']['valid_days'] if discount_price.get('bc_dis_inr') else None
    discount_price_bc_usd = discount_price['bc_dis_usd']['discounted_rate'] if discount_price.get('bc_dis_usd') else None
    discount_price_bc_usd_valid_days = discount_price['bc_dis_usd']['valid_days'] if discount_price.get('bc_dis_usd') else None


    product_details['discount_percentage_inr'] = discount_price_inr
    product_details['discount_percentage_inr_valid_days'] = discount_price_inr_valid_days
    product_details['discount_percentage_usd'] = discount_price_usd
    product_details['discount_percentage_usd_valid_days'] = discount_price_usd_valid_days
    product_details['bc_discount_percentage_inr'] = discount_price_bc_inr
    product_details['bc_discount_percentage_inr_valid_days'] = discount_price_bc_inr_valid_days
    product_details['bc_discount_percentage_usd'] = discount_price_bc_usd
    product_details['bc_discount_percentage_usd_valid_days'] = discount_price_bc_usd_valid_days


    
    

    context["product_details"] = product_details
    context["related_items"] = [
        related_item for related_item in product.get("ap_related_items", [])
        if related_item.get("has_variants") == 0
    ]
    context["banners"] = get_items(is_banner=True, banner=["Banner-2"])

    context["slide_show_images"] = [
        product_details.get("custom_image1"),
        product_details.get("custom_image2"),
        product_details.get("custom_image3"),
    ]
    context["imageone"] = product_details.get("custom_image1")
    context["imagetwo"] = product_details.get("custom_image2")
    context["imagethree"] = product_details.get("custom_image3")

    if product_details.get("has_variants"):
        variant_attribute_list = frappe.db.get_all(
            "Item Variant Attribute",
            {"variant_of": id},
            ["variant_of", "parent", "attribute", "attribute_value"]
        )
        context["variants"] = variant_attribute_list

    elif product_details.get("variant_of"):
        variant_attribute_list = frappe.db.get_all(
            "Item Variant Attribute",
            {"variant_of": product_details.get("variant_of")},
            ["variant_of", "parent", "attribute", "attribute_value"]
        )
        variant_list = [variant["parent"] for variant in variant_attribute_list]
        published_variants = item_query(filters={"item_code": variant_list})
        published_variant_name = [variant.name for variant in published_variants]
        final_variant_attribute_list = [
            item for item in variant_attribute_list
            if item["parent"] in published_variant_name
        ]
        context["variants"] = final_variant_attribute_list

    cart_items = []
    if frappe.session.user == "Guest":
        cart_items = get_quotation(item_code=id, guest_quotation=True)

    if not cart_items:
        cart_items = get_quotation(item_code=id)

    context["button_label"] = "Add To Cart"
    context["hide_element"] = ""
    context["cart_button_class"] = "add-to-cart"

    if cart_items:
        context["button_label"] = "View In Cart"
        context["hide_element"] = "hide-element"
        context["cart_button_class"] = "in-cart"

    if frappe.db.get_single_value("Leftword Settings", "allow_guest_cart"):
        context["allow_guest_cart"] = "allow-guest-cart"
    context["reviews"] = get_public_reviews(id)
    author_name = frappe.form_dict.get("author_name") 

    if author_name:
        authors = get_author_items(author_name)
        author_details = next((author for author in authors if author["author_name"] == author_name), None)
        if author_details:
            context["author_name"] = author_details["author_name"]
            context["author_description"] = author_details["author_description"]
            context["items"] = author_details.get("items", [])
            context["other_authors"] = [a for a in authors if a["author_name"] != author_name]

    return context


def get_author_items(author_name):
    authors = frappe.db.sql("""
        SELECT 
            WR.custom_name AS author_name,
            WR.description AS author_description
        FROM 
            `tabWriter` WR
        WHERE
            WR.name = '{0}'
    """.format(author_name), as_dict=True)
    return authors


@frappe.whitelist(allow_guest=True)
def get_public_reviews(item_id):
    reviews = frappe.get_all(
        "Public Review",
        filters={"enable": 1},  
        fields=["item", "review", "reviewer"]
    )

    data = []
    for review in reviews:
        item_doc = frappe.get_doc("Item", review["item"])
        variants = []
        if item_doc.has_variants:
            variants = frappe.get_all(
                "Item",
                filters={"variant_of": item_doc.name},
                fields=["name", "item_name", "item_code"]
            )
  
        for variant in variants:
            if variant["name"] == item_id: 
                data.append({
                    "item": item_doc.name,
                    "item_name": item_doc.item_name,
                    "review": review["review"],
                    "reviewer": review["reviewer"],
                    "has_variants": item_doc.has_variants,
                    "variants": variants,
                })

    return data 