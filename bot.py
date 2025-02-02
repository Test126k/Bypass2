import os
import logging
import sqlite3
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from bypass import bypass_url  # Import the bypass function

# Enable logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Read the bot token from the environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Ensure this matches the environment variable name in Koyeb
CHANNEL_ID = "@master_bypass"  # Replace with your Telegram channel username

# Database setup
conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, is_banned BOOLEAN, is_premium BOOLEAN)")
cursor.execute("CREATE TABLE IF NOT EXISTS links (short_url TEXT PRIMARY KEY, original_url TEXT)")
conn.commit()

# Function to check if a link is already bypassed
async def get_cached_link(short_url):
    bot = Bot(token=BOT_TOKEN)
    async for message in bot.get_chat_history(CHANNEL_ID):
        if short_url in message.text:
            return message.text.split("Original URL: ")[1]
    return None

# Function to cache a bypassed link in the Telegram channel
async def cache_link(short_url, original_url):
    bot = Bot(token=BOT_TOKEN)
    await bot.send_message(CHANNEL_ID, f"Short URL: {short_url}\nOriginal URL: {original_url}")

# Command handler for /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    cursor.execute("INSERT OR IGNORE INTO users (user_id, is_banned, is_premium) VALUES (?, ?, ?)", (user_id, False, False))
    conn.commit()
    await update.message.reply_text("Hello! Send me a shortened URL, and I'll reveal the original URL for you.")

# Message handler for URLs
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    # Check if the user is banned
    cursor.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    if result and result[0]:
        await update.message.reply_text("You are banned from using this bot.")
        return

    if text.startswith(("http://", "https://")):
        # Check if the link is already cached
        cached_link = await get_cached_link(text)
        if cached_link:
            await update.message.reply_text(f"Original URL (cached): {cached_link}")
            return

        # Bypass the URL
        original_url = bypass_url(text)
        await update.message.reply_text(f"Original URL: {original_url}")
        await cache_link(text, original_url)
    else:
        await update.message.reply_text("Please send a valid shortened URL.")

# Command handler for /ban (admin only)
async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id != YOUR_ADMIN_USER_ID:  # Replace with your admin user ID
        await update.message.reply_text("You are not authorized to use this command.")
        return

    target_user_id = int(context.args[0])
    cursor.execute("UPDATE users SET is_banned = ? WHERE user_id = ?", (True, target_user_id))
    conn.commit()
    await update.message.reply_text(f"User {target_user_id} has been banned.")

# Command handler for /unban (admin only)
async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id != YOUR_ADMIN_USER_ID:  # Replace with your admin user ID
        await update.message.reply_text("You are not authorized to use this command.")
        return

    target_user_id = int(context.args[0])
    cursor.execute("UPDATE users SET is_banned = ? WHERE user_id = ?", (False, target_user_id))
    conn.commit()
    await update.message.reply_text(f"User {target_user_id} has been unbanned.")

# Main function to run the bot
if __name__ == "__main__":
    # Check if the bot token is set
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN environment variable is not set!")

    # Build the application
    app = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("unban", unban_user))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Log the webhook URL
    webhook_url = f"https://willowy-cindy-arman1269-4ca980f1.koyeb.app/{BOT_TOKEN}"  # Replace with your Koyeb public URL
    logger.info(f"Setting webhook URL: {webhook_url}")

    # Set up webhook
    app.run_webhook(
        listen="0.0.0.0",  # Listen on all available interfaces
        port=int(os.getenv("PORT", 8080)),  # Use the PORT environment variable or default to 8080
        url_path=BOT_TOKEN,  # URL path for the webhook
        webhook_url=webhook_url  # Replace with your Koyeb public URL
    )
