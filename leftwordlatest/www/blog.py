



import re
import frappe

from bs4 import BeautifulSoup

def get_context(context):
    context.no_cache = True
    context.blogs = get_blog()


def get_blog():
    blogs = frappe.db.get_list(
        "Blog Post",
        fields=["name", "title", "blogger", "published_on", "blog_intro", "content", "meta_image"],
        order_by="idx asc",
        filters={"published": 1, "custom_show_in_dashboard": 1},
        ignore_permissions=True
    )

    for blog in blogs:
        if blog["content"]:
           
            blog["content"] = remove_rel_noreferrer(blog["content"])
           
            blog["content"] = embed_youtube_links(blog["content"])

    return blogs

def remove_rel_noreferrer(content):
    soup = BeautifulSoup(content, 'html.parser')
    
    for a_tag in soup.find_all('a', attrs={'rel': 'noopener noreferrer'}):
        del a_tag['rel'] 
    
    content = str(soup)
    
    
    return content

def embed_youtube_links(content):
   
    youtube_regex = r'(https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([\w\-]+))'
    
    def replace_with_iframe(match):
        video_id = match.group(2)
       
        iframe = f'<iframe width="560" height="315" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'
        return iframe

    content = re.sub(youtube_regex, replace_with_iframe, content)
    

    return content


