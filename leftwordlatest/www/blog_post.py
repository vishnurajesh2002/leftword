import frappe

def validate_blog_post(doc, method):
    if doc.custom_show_in_dashboard:  
        
        count = frappe.db.count(
            "Blog Post",
            filters={
                "custom_show_in_dashboard": 1,
                "name": ["!=", doc.name]  
            }
        )
    
        if count >= 2:
            frappe.throw("Only 2 blogs can be shown in the dashboard. Please uncheck this option for other blogs.")
