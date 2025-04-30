import logging
import os
import sqlite3
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
AD_LINK = os.getenv("AD_LINK")

# Initialize SQLite
conn = sqlite3.connect("clickbot.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
c.execute("CREATE TABLE IF NOT EXISTS clicks (user_id INTEGER, count INTEGER)")
conn.commit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    c.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user.id,))
    conn.commit()
    keyboard = [[InlineKeyboardButton("Click to Earn", url=AD_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome! Click the button below to earn:", reply_markup=reply_markup)

async def stat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    c.execute("SELECT SUM(count) FROM clicks")
    total_clicks = c.fetchone()[0] or 0
    income = total_clicks * 0.01  # Example income per click
    await update.message.reply_text(f"Total Users: {total_users}
Total Clicks: {total_clicks}
Estimated Income: ${income:.2f}")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    c.execute("INSERT OR IGNORE INTO clicks (user_id, count) VALUES (?, 0)", (user.id,))
    c.execute("UPDATE clicks SET count = count + 1 WHERE user_id = ?", (user.id,))
    conn.commit()
    await query.answer("Click registered!")

def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stat", stat))
    app.add_handler(CallbackQueryHandler(button))

    app.run_polling()

if __name__ == '__main__':
    main()
