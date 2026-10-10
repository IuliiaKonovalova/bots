import json
import logging
import os
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from pathlib import Path

# Define the directory path
FOLDER = Path("datajsontg_folder")

# Load tg-api.json
with open(FOLDER / "tg-api.json", "r", encoding="utf-8") as f:
    datajsontg = json.load(f)

# Load statsjsontg.json
with open(FOLDER / "statsjsontg.json", "r", encoding="utf-8") as f:
    statsjsontg = json.load(f)

logging.basicConfig(level=logging.INFO)
TOKEN = datajsontg.get("YOUR_TELEGRAM_BOT_TOKEN_HERE")
STATS_FILE = statsjsontg.get("STATS_FILE_PATH", "bot_stats.json")  # Default to 'bot_stats.json' if not specified

def log_event(user_id: int, event_name: str, step: int):
    """Helper to log bot triggers and step completions into a JSON file."""
    data = {}
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = {}

    str_user = str(user_id)
    if str_user not in data:
        data[str_user] = {"first_seen": str(datetime.now()), "events": []}

    data[str_user]["events"].append({
        "event": event_name,
        "step": step,
        "timestamp": str(datetime.now())
    })

    with open(STATS_FILE, "w") as f:
        json.dump(data, f, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /start command (Trigger / Step 1)."""
    user_id = update.effective_user.id
    log_event(user_id, event_name="bot_triggered", step=1)

    keyboard = [
        [
            InlineKeyboardButton("Option A (Step 2)", callback_data="opt_a"),
            InlineKeyboardButton("Option B (Step 2)", callback_data="opt_b"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Hello {update.effective_user.first_name}! Welcome to the bot.\n"
        "Select an option to proceed to Step 2:",
        reply_markup=reply_markup,
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles inline keyboard button responses (Step 2)."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    selected_option = query.data

    log_event(user_id, event_name=f"selected_{selected_option}", step=2)

    await query.edit_message_text(
        text=f" You selected {selected_option.upper()}! Step 2 complete."
    )

def main():
    """Starts the bot using long polling."""
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()