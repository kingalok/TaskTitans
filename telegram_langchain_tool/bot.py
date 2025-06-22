import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from langchain_core.messages import HumanMessage
from my_tools import agent_executor

load_dotenv()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    response = agent_executor.invoke({
        "messages": [HumanMessage(user_input)]
    })
    await update.message.reply_text(response['messages'][-1].content)

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()