import frappe
from leftwordlatest.web_api.items import get_items
from leftwordlatest.web_api.cart import make_cart
from frappe import _
from bs4 import BeautifulSoup
from datetime import datetime


from frappe.model.document import Document

def get_context(context):
    
    context.no_cache = True
    load_home(context)

def load_home(context):
    
    events = frappe.db.get_list(
    "Leftword Events",
    fields=["event_date", "link", "description", "custom_title"],
    filters={"custom_show_in_dashboard": 1},
    order_by="event_date asc",
    limit_page_length=2,
    ignore_permissions=True
)

    for event in events:
        if event.get("event_date"):
           
            event["event_date"] = event["event_date"].strftime("%d-%b-%Y")

    context.event = events

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
    blog = frappe.db.get_list(
        "Blog Post",
        fields=["name", "title", "blogger", "published_on", "blog_intro", "content", "meta_image"],
        order_by="idx asc",
        filters={"published": 1,"custom_show_in_dashboard": 1},
        limit_page_length=2,
        ignore_permissions=True  
    )

 
    for post in blog:
       
        if isinstance(post.get('published_on'), str):
            post['published_on'] = datetime.strptime(post['published_on'], '%Y-%m-%d')  # Adjust format as needed
        
        soup = BeautifulSoup(post.get('content', ''), 'html.parser')
        img_tag = soup.find('img')
        
        if img_tag and img_tag.get('src'):
            post['content_image'] = img_tag['src']  
        else:
            post['content_image'] = None  
    if home_data:
        context.sliders = home_data.get("related_list")
        context.banners = home_data.get("banner_list")
        context.new_release = home_data.get("new_release")
    
    context.blog = blog 
    context.disabled = frappe.db.get_single_value("Leftword Settings", "disabled")




@frappe.whitelist(allow_guest=True)
def get_blog_details(blog_id):
    try:
      
        blog = frappe.get_doc('Blog Post', blog_id)
        return {
            
            'title': blog.title,
            'bio_intro':blog.blog_intro,
            'content': blog.content,
            'blogger':blog.blogger,
            'published_on': blog.published_on.strftime('%d %B %Y'),
            
        }
    except frappe.DoesNotExistError:
        frappe.throw(_("Blog with ID {} does not exist").format(blog_id))
    except ImportError as e:
        frappe.throw(_("Module import failed: {}").format(str(e)))
    except Exception as e:
        frappe.throw(_("An unexpected error occurred: {}").format(str(e)))



@frappe.whitelist()
def get_dashboard_events():
   
    events = frappe.get_all(
        'Leftword Events',
        filters={
            'custom_show_in_dashboard': 1
        },
        fields=['link', 'event_date', 'description'],
        order_by='event_date desc' 
    )
    return events
