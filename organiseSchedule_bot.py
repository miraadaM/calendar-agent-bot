from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import dateparser
import json
import os
from openai import OpenAI
import requests # together ai
from dotenv import load_dotenv
load_dotenv()

import os
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY") # Initialize togetheer ai
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") # Set your bot token here



def ask_gpt(prompt):
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "messages": [
           {"role": "system", "content": """You are a calendar assistant.

Return only JSON like this:
{
  "action": "add",
  "title": "Dinner with Ali",
  "time": "Friday at 6pm"
}

If user wants to see events:
{ "action": "show" }

If user wants to delete events:
{ "action": "delete" }

NEVER explain. Only return JSON."""},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"]



CALENDAR_FILE = "calendar.json"

# Load/save
def load_calendar():
    if not os.path.exists(CALENDAR_FILE):
        return []
    with open(CALENDAR_FILE, 'r') as f:
        return json.load(f)

def save_calendar(calendar):
    with open(CALENDAR_FILE, 'w') as f:
        json.dump(calendar, f, indent=4, default=str)


# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hi! I'm your calendar bot. Type event and its date for me, i will add it to your virtual calendar! You can also delete or see the whole calendar!!")

# Show Events
async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    calendar = load_calendar()
    if not calendar:
        await update.message.reply_text("📭 No events.")
        return
    
    sorted_calendar = sorted(calendar, key=lambda e: e["datetime"])
    text = "📅 Upcoming Events:\n"
    for event in sorted_calendar:
        text += f"- {event['description']} at {event['datetime']}\n"
    await update.message.reply_text(text)

# Delete Events
async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_calendar([])
    await update.message.reply_text("🗑️ All events deleted.")


# Cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Cancelled.")
    return ConversationHandler.END

import json

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    gpt_response = ask_gpt(user_input)

    try:
        data = json.loads(gpt_response)
    except json.JSONDecodeError:
        await update.message.reply_text("❌ I didn’t understand. Please try again.")
        return

    action = data.get("action")
    
    if action == "add":
        title = data.get("title")
        time = data.get("time")
        
        if not title or not time:
            await update.message.reply_text("❌ Missing title or time.")
            return

        dt = dateparser.parse(time, settings={'PREFER_DATES_FROM': 'future'})
        if not dt:
            await update.message.reply_text("❌ Couldn’t understand the time.")
            return

        event = {
            "description": title,
            "datetime": dt.strftime("%Y-%m-%d %H:%M")
        }
        calendar = load_calendar()
        calendar.append(event)
        save_calendar(calendar)
        await update.message.reply_text(f"✅ Event added: {title} at {event['datetime']}")

    elif action == "show":
        await show(update, context)

    elif action == "delete":
        await delete(update, context)

    else:
        await update.message.reply_text("❌ Unknown action.")



# Main
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
