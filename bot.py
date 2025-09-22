import telebot
import pyshorteners
import validators
import os
from pyshorteners.exceptions import ShorteningErrorException, BadAPIResponseException

# Get the API token from Render's environment variables
API_TOKEN = os.environ.get('BOT_TOKEN')

if not API_TOKEN:
    raise ValueError("Bot token not found. Please set the BOT_TOKEN environment variable on Render.")

bot = telebot.TeleBot(API_TOKEN)

# Initialize the URL shortener
s = pyshorteners.Shortener(timeout=10) 

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Handles the /start and /help commands."""
    welcome_message = "Hello! I am a URL Shortener bot. Send me a long URL, and I'll make it short for you."
    welcome_message += "\n\nMade by @SuryaXCristiano 🌝"
    bot.reply_to(message, welcome_message)

@bot.message_handler(func=lambda message: True)
def shorten_url(message):
    """Handles all other messages and attempts to shorten them."""
    long_url = message.text.strip()
    
    if not long_url.startswith(('http://', 'https://')):
        long_url = 'http://' + long_url
    
    if not validators.url(long_url):
        bot.reply_to(message, "Please send a valid URL (e.g., https://example.com).")
        return
        
    short_url = None
    
    # --- Attempt 1: Use Is.gd (Direct redirect) ---
    try:
        short_url = s.isgd.short(long_url)
        bot.reply_to(message, f"Here is your shortened URL:\n{short_url}")
        return
    except (ShorteningErrorException, BadAPIResponseException) as e:
        print(f"Is.gd failed for {long_url}: {e}")
        
    # --- Attempt 2: Use TinyURL (Backup) ---
    try:
        short_url = s.tinyurl.short(long_url)
        bot.reply_to(message, f"Here is your shortened URL from TinyURL:\n{short_url}\n\nNote: TinyURL may show a preview page for safety reasons.")
        return
    except (ShorteningErrorException, BadAPIResponseException) as e:
        print(f"TinyURL failed for {long_url}: {e}")
        
    # --- If both attempts fail ---
    bot.reply_to(message, "Sorry, I couldn't shorten that URL with any of my services. The link may be broken, or the services are temporarily unavailable.")

# Start the bot
bot.polling(non_stop=True)
