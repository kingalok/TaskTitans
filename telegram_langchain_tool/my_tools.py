
# Environment and OS
import os
from dotenv import load_dotenv

# Database connectivity
import mysql.connector
from sqlalchemy import create_engine

# LangChain core and community
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage, ToolMessage, HumanMessage, AIMessage

# LangChain chat models and agent toolkits
from langchain.chat_models import init_chat_model
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.tools.tavily_search import TavilySearchResults

# LangGraph for workflow orchestration
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent, ToolNode

# Tavily (search tool)
from langchain_tavily import TavilySearch

# Additional tools
import smtplib
import requests



load_dotenv()

model_id="gemini-2.5-flash-preview-05-20"
llm = init_chat_model(model=model_id,  model_provider="google_vertexai")

config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'port': int(os.getenv('DB_PORT', 3306)),  # optional fallback
}



@tool("get_student_emails", parse_docstring=True, return_direct=True)
def get_all_student_emails() -> list[str]:
    """
    This function returns all the email ids of students from database
    """
    # Connect to the database
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()

    # Query the students table
    query = "SELECT email FROM students"
    cursor.execute(query)

    # Fetch all rows and print them
    rows = cursor.fetchall()
    emails = []
    for row in rows:
        emails.append(row[0])

    # Close the connection
    cursor.close()
    connection.close()
    return emails


# Database
# mysql+<driver>://<username>:<password>@<host>:<port>/<database>

connection_string = f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

#connection_string="mysql+mysqlconnector://ltgenai:rootroot@127.0.0.1:3306/genaideveloper"
#connection_string = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(connection_string, echo=True)
database = SQLDatabase(engine)
toolkit = SQLDatabaseToolkit(db=database, llm=llm)

# Sending Email
@tool("email_sender", parse_docstring=True, return_direct=True)
def send_email(receiver:str, subject:str, message:str) -> None:
    """Sends an email to the receiver with the specified subject and message.

    Args:
        receiver (str): Email address of the recipient.
        subject (str): Subject of the email.
        message (str): Message to be sent.
    """
    sender = "admin@lt.com"

    body = f"""\
Subject: {subject}
To: {receiver}
From: {sender}

{message}"""

    with smtplib.SMTP(os.getenv('SMTP_HOST'), int(os.getenv('SMTP_PORT'))) as server:
        server.starttls()
        server.login(os.getenv('SMTP_USERNAME'), os.getenv('SMTP_PASSWORD'))
        server.sendmail(sender, receiver, body)



# Initialize Tavily Search Tool
tavily_search_tool = TavilySearch(
    max_results=5,
    topic="general"
#    include_domains=["directai.blog"]
    
)


#
#WhatsApp Message


@tool("send_whatsapp_message", return_direct=True)
def send_whatsapp_message(to: str, message: str) -> str:
    """
    Sends a WhatsApp message using the Ultramsg API.

    Args:
        to (str): Recipient's phone number with country code (e.g., +447911123456)
        message (str): Text message to send
    Returns:
        str: API response message
    """
    instance_id = os.getenv("ULTRAMSG_INSTANCE_ID")
    token = os.getenv("ULTRAMSG_TOKEN")

    url = f"https://api.ultramsg.com/{instance_id}/messages/chat"
    payload = {
        "token": token,
        "to": f"whatsapp:{to}",
        "body": message
    }

    response = requests.post(url, data=payload)
    try:
        return response.json().get("message", "Sent")
    except:
        return "Failed to send"
    
    

# Telegram

@tool("send_telegram_message", return_direct=True)
def send_telegram_message(chat_id: str, message: str) -> str:
    """
    Sends a message to a Telegram chat using the Telegram Bot API.

    Args:
        chat_id (str): The chat ID of the Telegram user or group.
        message (str): The message to be sent.

    Returns:
        str: Response status or error message.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        return "Bot token not found in environment."

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }

    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            return "Telegram message sent successfully!"
        else:
            return f"Error: {response.text}"
    except Exception as e:
        return f"Failed to send message: {str(e)}"

tools = [
    send_email,
    tavily_search_tool,
    send_whatsapp_message,
    send_telegram_message
]

agent_executor = create_react_agent(llm, toolkit.get_tools()+ tools)


# # Using the LangChain tool we defined earlier
# response = agent_executor.invoke({
#     "messages": [
#         HumanMessage("Send a telegram message to -4888217603 saying 'Hello GenAI group from the bot!'")
#     ]
# })