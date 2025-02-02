import os
import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Read the bot token from the environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Ensure this matches the environment variable name in Koyeb

# Function to bypass URL shortener
def bypass_url_shortener(short_url):
    try:
        import requests
        from bs4 import BeautifulSoup
        import re

        # Direct Redirect Handling
        response = requests.get(short_url, allow_redirects=True)
        if response.status_code in (301, 302, 303, 307, 308):
            return response.url  # Direct Redirect

        # Agar direct redirect nahi mila to HTML parse karo
        soup = BeautifulSoup(response.text, "lxml")

        # Meta Refresh Handling
        meta_refresh = soup.find("meta", attrs={"http-equiv": "refresh"})
        if meta_refresh:
            content = meta_refresh.get("content", "")
            url_part = content.split("url=")[-1] if "url=" in content else None
            if url_part:
                return url_part.strip()

        # JavaScript Redirect Handling
        script = soup.find("script", text=lambda x: x and "window.location" in x)
        if script:
            match = re.search(r'window\.location\s*=\s*["\'](.*?)["\']', script.text)
            if match:
                return match.group(1)

        # Agar kuch bhi na mile to original URL return karo
        return short_url

    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

        
        # If it's a direct redirect, return the final URL
        if response.status_code in (301, 302, 303, 307, 308):
            return response.headers['Location']
        
        # If it's an intermediate page, parse the HTML to find the final URL
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Look for a meta refresh tag
        meta_refresh = soup.find('meta', attrs={'http-equiv': 'refresh'})
        if meta_refresh:
            # Extract the URL from the content attribute
            content = meta_refresh.get('content', '')
            if 'url=' in content:
                return content.split('url=')[1]
        
        # Look for a JavaScript redirect
        script = soup.find('script', text=lambda x: x and 'window.location' in x)
        if script:
            # Extract the URL from the JavaScript code
            script_text = script.string
            if 'window.location' in script_text:
                return script_text.split('window.location=')[1].split(';')[0].strip("'\"")
        
        # If no redirect is found, return the intermediate URL
        return short_url
    except requests.exceptions.RequestException as e:
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
        # Check if the URL is from inshorturl.com
        if "inshorturl.com" in text:
            original_url = bypass_url_shortener(text)
            await update.message.reply_text(f"Original URL: {original_url}")
        else:
            await update.message.reply_text("Sorry, I only support inshorturl.com links for now.")
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
