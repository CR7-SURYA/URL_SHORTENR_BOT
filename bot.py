import telebot
import pyshorteners
import validators
import os
import threading
from flask import Flask, request
from pyshorteners.exceptions import ShorteningErrorException, BadAPIResponseException

# Get the API token from Render's environment variables
API_TOKEN = os.environ.get('BOT_TOKEN')

if not API_TOKEN:
    raise ValueError("Bot token not found. Please set the BOT_TOKEN environment variable on Render.")

bot = telebot.TeleBot(API_TOKEN)

# --- CORRECTED LINE BELOW ---
s = pyshorteners.Shortener(timeout=10)

# --- The "fake" Flask web server part ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!", 200

# Function to run the bot in a separate thread
def run_bot():
    print("Starting bot polling...")
    bot.polling(non_stop=True)

# Function to start the web server
def run_web_server():
    print("Starting web server...")
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))

# --- Bot Handlers (your original code) ---
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_message = "Hello! I am a URL Shortener bot. Send me a long URL, and I'll make it short for you."
    welcome_message += "\n\nMade by @SuryaXCristiano 🌝"
    bot.reply_to(message, welcome_message)

@bot.message_handler(func=lambda message: True)
def shorten_url(message):
    long_url = message.text.strip()
    
    if not long_url.startswith(('http://', 'https://')):
        long_url = 'http://' + long_url
    
    if not validators.url(long_url):
        bot.reply_to(message, "Please send a valid URL (e.g., https://example.com).")
        return
        
    short_url = None
    
    try:
        short_url = s.isgd.short(long_url)
        bot.reply_to(message, f"Here is your shortened URL:\n{short_url}")
        return
    except (ShorteningErrorException, BadAPIResponseException) as e:
        print(f"Is.gd failed for {long_url}: {e}")
        
    try:
        short_url = s.tinyurl.short(long_url)
        bot.reply_to(message, f"Here is your shortened URL from TinyURL:\n{short_url}\n\nNote: TinyURL may show a preview page for safety reasons.")
        return
    except (ShorteningErrorException, BadAPIResponseException) as e:
        print(f"TinyURL failed for {long_url}: {e}")
        
    bot.reply_to(message, "Sorry, I couldn't shorten that URL with any of my services. The link may be broken, or the services are temporarily unavailable.")

# --- Main execution block ---
if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot)
    web_server_thread = threading.Thread(target=run_web_server)
    
    bot_thread.start()
    web_server_thread.start()
