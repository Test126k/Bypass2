import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from playwright.async_api import async_playwright

# Enable logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Read the bot token from the environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Ensure this matches the environment variable name in Koyeb

# Function to bypass URL shortener using Playwright (async)
async def bypass_url_shortener(short_url):
    try:
        async with async_playwright() as p:
            # Launch a headless browser
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Navigate to the shortened URL
            await page.goto(short_url)
            
            # Wait for the page to fully load (including JavaScript redirects)
            await page.wait_for_timeout(5000)  # Wait for 5 seconds
            
            # Get the final URL after all redirects
            final_url = page.url
            
            # Close the browser
            await browser.close()
            
            return final_url
    except Exception as e:
        return f"An error occurred: {e}"

# Command handler for /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"User {update.message.from_user.id} sent /start")
    await update.message.reply_text("Hello! Send me a shortened URL, and I'll reveal the original URL for you.")

# Message handler for URLs
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    logger.info(f"User {update.message.from_user.id} sent: {text}")
    if text.startswith(("http://", "https://")):
        original_url = await bypass_url_shortener(text)
        await update.message.reply_text(f"Original URL: {original_url}")
    else:
        await update.message.reply_text("Please send a valid shortened URL.")

# Main function to run the bot
if __name__ == "__main__":
    # Check if the bot token is set
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN environment variable is not set!")

    # Build the application
    app = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
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
