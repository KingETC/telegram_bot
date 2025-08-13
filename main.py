"""
Ready-to-deploy Telegram onboarding bot (manual UID verification)
Includes your supplied token and admin id by default, but will prefer environment variables if present.
Designed to run on Render / Railway / any Python host supporting long-running processes.
"""

import os
import json
import logging
from datetime import datetime
from functools import wraps
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ---------------------- CONFIG ----------------------
# These default values were provided by the user. You can override them by setting the environment variables
# TELEGRAM_TOKEN and ADMIN_ID on the hosting platform (recommended for security).
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8097594537:AAFlC8KFerUe46JcNQDVRGhQp0JcF4W-g9U")
ADMIN_ID = os.environ.get("ADMIN_ID", "5120079243")
BROKER_LINK = os.environ.get("BROKER_LINK", "https://u3.shortink.io/smart/kcJjtFEblLUmCL")
BONUS_CODE = os.environ.get("BONUS_CODE", "BXH547")

DATA_FILE = "bot_data.json"

# ---------------------- LOGGING ----------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------- STORAGE HELPERS ----------------------
def load_data():
    if not os.path.exists(DATA_FILE):
        default = {"uids": {}, "vip": []}
        with open(DATA_FILE, "w") as f:
            json.dump(default, f, indent=2)
        return default
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ---------------------- DECORATORS ----------------------
def admin_only(func):
    @wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        if user_id == str(ADMIN_ID) or user_id in (str(i) for i in str(ADMIN_ID).split(",")):
            return await func(update, context)
        else:
            await update.message.reply_text("⛔ You are not authorized to use this command.")
    return wrapped

# ---------------------- MESSAGES ----------------------
BEFORE_START_TEXT = (
"💼 Tired of dreaming about financial freedom? Time to make it real!\\n\\n"
"🚀 This is your moment to change everything! Ready? 👇\\n\\n"
"🔥 Click “Get Started” 🫵\\n"
"⚡️ Follow the step-by-step guide!\\n"
"✅ Get access to proven, time-tested signals!\\n"
"💵 Trade with confidence and watch your profits grow!\\n\\n"
"🎯 Success is just one decision away. Will you take it? click /start NOW"
)

WELCOME_TEXT_TEMPLATE = (
"Hi {name} 👋\\n"
"💰Bro, I've collected signals from the most top and proven traders in one place, inclusive of my own signals and pretty soon you'll get them.\\n\\n"
"You can get free from us:\\n\\n"
"💎 5 groups with signals of top traders\\n"
"📚 Best trading training materials\\n\\n"
"✅ Follow the instructions, sign up and copy the signals 👇\\n\\n"
"✔️ Step 1: Sign up on my trading broker:\\n{broker_link}\\n\\n"
"✔️ Step 2: Deposit from $10 upwards\\n(use the code {bonus} to get up to 60% bonus for $50 deposit)"
)

UID_RECEIVED_TEXT = "That's it, your data has been sent for verification. If there is a long delay, please contact support."
AFTER_VERIFY_TEXT = "✅ Verified! You’re ready to receive signals."

# ---------------------- HANDLERS ----------------------
async def before_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Show before-start text (useful if you want a manual preview)
    await update.message.reply_text(BEFORE_START_TEXT)

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name or update.effective_user.username or 'trader'
    text = WELCOME_TEXT_TEMPLATE.format(name=name, broker_link=BROKER_LINK, bonus=BONUS_CODE)
    # send with HTML formatting; ensure Telegram auto-link is allowed
    await update.message.reply_text(text, parse_mode="HTML", disable_web_page_preview=False)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - Begin onboarding\\n"
        "/before - Show pre-start text\\n"
        "/verify <telegram_id> - Admin only: verify a user's UID and mark them VIP\\n"
        "/myid - Get your telegram id (useful for admin check)"
    )

async def myid_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Your Telegram ID is: {update.effective_user.id}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    lower = text.lower()
    # Expecting UID like: UID 1234567 or just the number
    uid = None
    if lower.startswith("uid"):
        uid = text[3:].strip()
    elif text.isdigit():
        uid = text.strip()
    else:
        # If user sends something else, gently prompt for UID
        await update.message.reply_text("Please send your UID in format: UID 1234567 or just send the number.")
        return

    if uid and uid.isdigit():
        data = load_data()
        user_id = str(update.effective_user.id)
        data["uids"][user_id] = {"uid": uid, "time": datetime.utcnow().isoformat() + "Z"}
        save_data(data)
        await update.message.reply_text(UID_RECEIVED_TEXT)
        # notify admin
        try:
            await context.bot.send_message(chat_id=int(ADMIN_ID), text=f"New UID submission:\\nUser: {update.effective_user.first_name} ({user_id})\\nUID: {uid}")
        except Exception as e:
            logger.exception("Failed to notify admin about UID submission")
    else:
        await update.message.reply_text("Invalid UID. Send like: UID 1234567")

@admin_only
async def verify_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Usage: /verify <telegram_id>
    if not context.args:
        await update.message.reply_text("Usage: /verify <telegram_id>")
        return
    tid = context.args[0]
    data = load_data()
    if tid in data.get("uids", {}):
        # mark VIP and notify user
        if tid not in data.get("vip", []):
            data.setdefault("vip", []).append(tid)
            save_data(data)
            try:
                await context.bot.send_message(chat_id=int(tid), text=AFTER_VERIFY_TEXT)
            except Exception:
                logger.exception("Failed to send verification message to user")
            await update.message.reply_text(f"User {tid} verified and notified.")
        else:
            await update.message.reply_text("User already verified.")
    else:
        await update.message.reply_text("No UID found for that user id.")

# ---------------------- MAIN ----------------------
async def main():
    token = TELEGRAM_TOKEN
    if not token:
        print("ERROR: TELEGRAM_TOKEN not set")
        return
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("before", before_cmd))
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("myid", myid_cmd))
    app.add_handler(CommandHandler("verify", verify_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("Bot started...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
