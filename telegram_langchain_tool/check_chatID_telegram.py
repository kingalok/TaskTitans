## To find the chat id of the telegram group
## %pip install python-telegram-bot

from telegram.ext import Updater, MessageHandler, Filters
import requests
import os
from dotenv import load_dotenv

# Load .env if you store your token securely there
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or "your_bot_token_here"


def handle_message(update, context):
    chat = update.effective_chat
    print(f"📩 Message received from: {chat.title or chat.username or chat.id}")
    print(f"🆔 Chat ID: {chat.id}")
    print(f"📨 Message Text: {update.message.text}")

updater = Updater(BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(MessageHandler(Filters.all, handle_message))

print("✅ Bot is listening... Send a message in the group now!")
updater.start_polling()
updater.idle()