import logging
import sqlite3
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load from environment
BOT_TOKEN = os.environ.get("BOT_TOKEN")
AD_LINK = os.environ.get("AD_LINK", "https://example.com")

# Database setup
conn = sqlite3.connect("clickbot.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)")
cursor.execute("CREATE TABLE IF NOT EXISTS clicks (user_id INTEGER)")
conn.commit()

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cursor.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
    conn.commit()

    keyboard = [[InlineKeyboardButton("Click & Earn", url=AD_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Welcome! Click the button below to earn points.", reply_markup=reply_markup)

# Click Tracker
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    cursor.execute("INSERT INTO clicks (user_id) VALUES (?)", (user_id,))
    conn.commit()
    await query.answer()

# Stat command
async def stat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM clicks")
    total_clicks = cursor.fetchone()[0]
    income = total_clicks * 0.01  # Example: 1 click = $0.01

    msg = f"📊 Stats:\nUsers: {total_users}\nClicks: {total_clicks}\nEstimated Income: ${income:.2f}"
    await update.message.reply_text(msg)

# Main
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stat", stat))
    app.add_handler(CallbackQueryHandler(button_click))
    logger.info("Bot is running...")
    app.run_polling()
