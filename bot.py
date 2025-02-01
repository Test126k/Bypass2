from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os

BOT_TOKEN = os.getenv("8053602470:AAECsWw8LDZNS7M1xesopgylsozdJcPQwnw")  # Get the token from environment variables

# Function to bypass URL shortener
def bypass_url_shortener(short_url):
    try:
        response = requests.get(short_url, allow_redirects=False)
        if response.status_code in (301, 302, 303, 307, 308):
            return response.headers['Location']
        else:
            return "No redirect found. This might not be a shortened URL."
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

# Command handler for /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Send me a shortened URL, and I'll reveal the original URL for you.")

# Message handler for URLs
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text.startswith(("http://", "https://")):
        original_url = bypass_url_shortener(text)
        await update.message.reply_text(f"Original URL: {original_url}")
    else:
        await update.message.reply_text("Please send a valid shortened URL.")

# Main function to run the bot
if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Set up webhook
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 8080)),
        url_path=BOT_TOKEN,
        webhook_url=f"https://<YOUR_KOYEB_PUBLIC_URL>/{BOT_TOKEN}"
    )
