
import frappe



def get_context(context):
    context.no_cache = True
    context.events_data = get_leftword_events()
    return context

@frappe.whitelist(allow_guest=True)
def get_leftword_events():
    from frappe.utils import today, getdate, formatdate
    
    current_date = getdate(today())

    # Fetch all events
    events = frappe.get_all(
        "Leftword Events",
        fields=["name", "event_date", "image", "link", "status", "venue_details", "event_details", "description", "custom_title"],
        order_by="event_date desc"
    )

    # Categorize events into upcoming and past
    upcoming_events = []
    past_events = []

    for event in events:
        event_date = getdate(event.get("event_date"))
        
        # Format the event_date
        formatted_date = formatdate(event_date, "dd-MM-yyyy")  # Example: 17-01-2025
        event["event_date"] = formatted_date
        
        if event_date < current_date and event.get("status") != "pastevent":
            frappe.db.set_value("Leftword Events", event.get("name"), "status", "pastevent")
            event["status"] = "pastevent"
        if event.get("status") == "pastevent":
            past_events.append(event)
        else:
            upcoming_events.append(event)

    return {
        "upcoming_events": upcoming_events,
        "past_events": past_events
    }
