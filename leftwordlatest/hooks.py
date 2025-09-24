app_name = "leftwordlatest"
app_title = "leftwordlatest"
app_publisher = "hiba"
app_description = "leftwordlatest"
app_email = "hiba@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------
#required_apps = ["leftword"]
# include js, css files in header of desk.html
# app_include_css = "/assets/leftwordlatest/css/leftwordlatest.css"
# app_include_js = "/assets/leftwordlatest/js/leftwordlatest.js"

# include js, css files in header of web template
# web_include_css = "/assets/leftwordlatest/css/leftwordlatest.css"
# web_include_js = "/assets/leftwordlatest/js/leftwordlatest.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "leftwordlatest/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {"Related Items": "public/js/related_items.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "leftwordlatest.utils.jinja_methods",
# 	"filters": "leftwordlatest.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "leftwordlatest.install.before_install"
# after_install = "leftwordlatest.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "leftwordlatest.uninstall.before_uninstall"
# after_uninstall = "leftwordlatest.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "leftwordlatest.utils.before_app_install"
# after_app_install = "leftwordlatest.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "leftwordlatest.utils.before_app_uninstall"
# after_app_uninstall = "leftwordlatest.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "leftwordlatest.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }
doc_events = {
    "Blog Post": {
        "validate": "leftwordlatest.www.blog_post.validate_blog_post"
    },
    # "User": {
    #     "validate": "leftword.web_api.user.validate_user_phone"
    # }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
    #   "cron": {
    #     "* * * * *": [
    #         "frappe.email.queue.flush"
    #     ]
    # }
# }
# 	"all": [
# 		"leftwordlatest.tasks.all"
# 	],
# 	"daily": [
# 		"leftwordlatest.tasks.daily"
# 	],
# 	"hourly": [
# 		"leftwordlatest.tasks.hourly"
# 	],
# 	"weekly": [
# 		"leftwordlatest.tasks.weekly"
# 	],
# 	"monthly": [
# 		"leftwordlatest.tasks.monthly"
# 	],

# Testing
# -------

# before_tests = "leftwordlatest.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "leftwordlatest.event.get_events"
# }
override_whitelisted_methods = {
    "frappe.www.login.get_context": "leftwordlatest.www.google_signup.get_custom_login_context",
}

#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "leftwordlatest.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
before_request = ["leftwordlatest.utils.set_user_and_full_name"]
# after_request = ["leftwordlatest.utils.after_request"]

jinja = {
    "methods": [
        "leftwordlatest.utils.get_full_name"
    ]
}
# Job Events
# ----------
# before_job = ["leftwordlatest.utils.before_job"]
# after_job = ["leftwordlatest.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"leftwordlatest.auth.validate"
# ]



doc_events = {
    "Payment Entry": {
        "on_submit": "leftwordlatest.create_member_membership_sales_invoice.create_membership_after_payment_entry"
    }
}



# scheduler_events = {
#     "daily": [
#         "leftwordlatest.create_member_membership_sales_invoice.reset_expired_memberships"
#     ]
# }

scheduler_events = {
    "all": [
        "leftwordlatest.www.my_membership.check_membership_expiry"
    ],
}
