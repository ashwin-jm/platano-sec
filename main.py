import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
from agents.task_agent import add_task, list_tasks, complete_task, delete_task

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction="""
You are PlatanoSec, the personal AI assistant for the founder of Platano (platano.in) —
a work experience platform for Indian students based in Kottayam, Kerala.

Your job is to understand the founder's messages and return a JSON response
with the action to take. Always respond ONLY with valid JSON, no markdown, no backticks.

Possible actions:
- add_task: when the user wants to remember or do something
- list_tasks: when the user wants to see pending tasks
- complete_task: when the user marks a task as done (extract task_id)
- delete_task: when the user wants to remove a task (extract task_id)
- chat: for anything else, just have a normal conversation

Response format:
{
  "action": "add_task" | "list_tasks" | "complete_task" | "delete_task" | "chat",
  "task_text": "extracted task text if action is add_task",
  "task_id": 1,
  "chat_reply": "your reply if action is chat"
}
"""
)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    try:
        response = model.generate_content(user_message)
        raw = response.text.strip()

        # Clean up in case Gemini adds backticks
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        result = json.loads(raw)
        action = result.get("action")

        if action == "add_task":
            reply = add_task(result.get("task_text", user_message))
        elif action == "list_tasks":
            reply = list_tasks()
        elif action == "complete_task":
            reply = complete_task(result.get("task_id"))
        elif action == "delete_task":
            reply = delete_task(result.get("task_id"))
        else:
            reply = result.get("chat_reply", "I didn't understand that.")

    except Exception as e:
        reply = f"Something went wrong: {str(e)}"

    await update.message.reply_text(reply)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hey! I'm PlatanoSec, your personal assistant.\n\n"
        "You can:\n"
        "• Tell me tasks: 'Remind me to post on Instagram'\n"
        "• See your list: 'Show my tasks'\n"
        "• Mark done: 'Done task 1'\n"
        "• Delete: 'Delete task 2'\n\n"
        "Let's get to work! 🚀"
    )

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("PlatanoSec is running...")
app.run_polling()