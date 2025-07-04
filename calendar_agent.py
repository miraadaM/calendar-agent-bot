import json
import os
import dateparser
from datetime import datetime

# Path to calendar file
CALENDAR_FILE = 'calendar.json'

# Load existing calendar or create empty
def load_calendar():
    if not os.path.exists(CALENDAR_FILE):
        return []
    with open(CALENDAR_FILE, 'r') as f:
        return json.load(f)

# Save events to calendar
def save_calendar(calendar):
    with open(CALENDAR_FILE, 'w') as f:
        json.dump(calendar, f, indent=4, default=str)

# Add a new event
def add_event():
    event_name = input("📝 Event title (e.g. Lunch with Kate): ")
    date_input = input("📅 When? (e.g. Friday at 2pm): ")
    
    dt = dateparser.parse(date_input, settings={'PREFER_DATES_FROM': 'future'})
    if not dt:
        return "❌ Couldn't understand the date/time."

    event = {
        "description": event_name,
        "datetime": dt.strftime("%Y-%m-%d %H:%M")
    }
    calendar = load_calendar()
    calendar.append(event)
    save_calendar(calendar)
    return f"✅ Event added: {event_name} at {event['datetime']}"
# Show upcoming events
def show_events():
    calendar = load_calendar()
    if not calendar:
        return "📭 No events in your calendar yet."
    
    # Sort events by time
    sorted_calendar = sorted(calendar, key=lambda e: e['datetime'])
    result = "\n📅 Upcoming Events:\n"
    for event in sorted_calendar:
        result += f"- {event['description']} at {event['datetime']}\n"
    return result

def delete_events():
    confirm = input("⚠️ Are you sure you want to delete ALL events? Type 'yes' to confirm: ")
    if confirm.lower() == "yes":
        with open(CALENDAR_FILE, 'w') as f:
            json.dump([], f)
        return "🗑️ All events deleted."
    else:
        return "❌ Deletion canceled."

while True:
    command = input("\nType 'add', 'show', or 'exit': ").lower()
    if command == "exit":
        break
    elif command == "show":
        print(show_events())
    elif command == "add":
        print(add_event())
    else:
        print(delete_events())