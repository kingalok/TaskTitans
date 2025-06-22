import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from langchain_core.messages import HumanMessage
from my_tools import agent_executor

# Load environment variables
load_dotenv()

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Configure rotating log handler
log_file = "logs/bot.log"
log_handler = RotatingFileHandler(
    log_file, maxBytes=1_000_000, backupCount=3  # Rotate after 1MB, keep 3 backups
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        log_handler,               # Rotating file log
        logging.StreamHandler()   # Console log
    ]
)

logger = logging.getLogger(__name__)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    logger.info(f"📩 Received message: {user_input} from user: {update.effective_user.username}")
    
    response = agent_executor.invoke({
        "messages": [HumanMessage(user_input)]
    })
    reply = response['messages'][-1].content
    await update.message.reply_text(reply)
    
    logger.info(f"📤 Sent reply: {reply}")

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("❌ TELEGRAM_BOT_TOKEN not set in environment.")
        return

    logger.info("✅ Bot is starting...")
    app = ApplicationBuilder().token(token).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
