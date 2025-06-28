
# Environment and OS
import os
import re
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

# stock market
import yfinance as yf

# weather
from langchain_community.utilities import OpenWeatherMapAPIWrapper

# Jira
from jira import JIRA

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

# Update Database
@tool("run_sql_write_query", return_direct=True)
def run_sql_write_query(query: str) -> str:
    """
    Executes a general SQL command for data modification (INSERT, UPDATE, DELETE) on the connected MySQL database.

    ⚠️ WARNING: This tool should be used only for write operations. SELECT queries should use read-only tools.

    Args:
        query (str): A valid SQL command like:
                     - "INSERT INTO stock (slug, nav_price) VALUES ('fund-name', 123.45)"
                     - "UPDATE stock SET nav_price = 130.55 WHERE slug = 'fund-name'"
                     - "DELETE FROM stock WHERE slug = 'fund-name'"

    Returns:
        str: Status message indicating success or error.
    """
    try:
        if not re.match(r"^\s*(INSERT|UPDATE|DELETE)", query, re.IGNORECASE):
            return "❌ Only INSERT, UPDATE, or DELETE statements are allowed."

        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        affected_rows = cursor.rowcount
        cursor.close()
        conn.close()
        return f"✅ Query executed successfully. Rows affected: {affected_rows}"
    except Exception as e:
        return f"❌ Error executing query: {str(e)}"
    
    
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


# Stock Market

@tool("get_stock_price", return_direct=True)
def get_stock_price(ticker: str) -> str:
    """
    Get the latest stock price for a given stock ticker.

    Args:
        ticker (str): The stock symbol (e.g., RELIANCE.BO for BSE, INFY.BO)

    Returns:
        str: Current price and details of the stock.
    """
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period="1d")
        if data.empty:
            return f"⚠️ No data found for ticker: {ticker}"

        latest_price = data['Close'].iloc[-1]
        return f"📈 {ticker} latest closing price: ₹{latest_price:.2f}"
    except Exception as e:
        return f"❌ Failed to fetch price for {ticker}: {str(e)}"


# NAV price of Mutual Funds
@tool("get_mutual_fund_nav_groww", return_direct=True)
def get_mutual_fund_nav_groww(fund_slug: str) -> str:
    """
    Retrieve the latest NAV (Net Asset Value) of a mutual fund from Groww.

    This tool fetches the current NAV of any mutual fund listed on Groww using its URL slug.

    Args:
        fund_slug (str): The Groww mutual fund slug, which is the unique identifier found in the fund's Groww URL.
                        Example:
                        For the fund "Tata Nifty Midcap 150 Momentum 50 Index Fund Direct Growth", 
                        the slug is "tata-nifty-midcap-150-momentum-50-index-fund-direct-growth".

    Returns:
        str: A formatted message containing the latest NAV value.

    Example usage:
        Input: "tata-nifty-midcap-150-momentum-50-index-fund-direct-growth"
        Output: "📈 NAV for Tata Nifty Midcap 150 Momentum 50 Index Fund Direct Growth: ₹123.45
    
    Notes:
        - This tool only supports funds listed on Groww.in.
        - Make sure to provide the correct slug to avoid fetch errors.

    """
    try:
        url = f"https://groww.in/mutual-funds/{fund_slug}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return f"❌ Failed to fetch: {url}"

        # Regex to find the NAV value (₹123.45 style)
        match = re.search(r'₹\s?([\d,]+\.\d+)', response.text)
        if match:
            nav = match.group(1)
            return f"📈 NAV for {fund_slug.replace('-', ' ').title()}: ₹{nav}\n🔗 {url}"
        else:
            return f"⚠️ NAV not found on the page."
    except Exception as e:
        return f"❌ Error: {e}"

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

# Weather

weather_api = OpenWeatherMapAPIWrapper()
# tools = [weather.run]


@tool("weather", return_direct=True)
def get_weather(location: str) -> str:
    """
    Gets the current weather for a given location using OpenWeatherMap.
    
    Args:
        location (str): Name of the city or place (e.g., Delhi, London).
    
    Returns:
        str: Weather description with temperature.
    """
    return weather_api.run(location)

# Jira

@tool("jira_unified_tool", return_direct=True)
def jira_unified_tool(
    action: str,
    issue_key: str = None,
    summary: str = None,
    description: str = None,
    project_key: str = "ECS",
    comment: str = None,
    issue_type: str = "Task",
    jql: str = None,
    max_results: int = 20
) -> str:
    """
    Unified Jira tool to perform create, update, comment, delete, search, and list actions.
    action: "create", "update", "comment", "delete", "search", or "list"
    """
    try:
        jira = JIRA(
            server=os.getenv('JIRA_SERVER'),
            basic_auth=(os.getenv('JIRA_USER'), os.getenv('JIRA_TOKEN'))
        )

        if action == "create":
            if not summary or not description:
                return "Missing required fields for creating an issue: summary, description."
            issue = jira.create_issue(
                project=project_key,
                summary=summary,
                description=description,
                issuetype={'name': issue_type}
            )
            return f"Issue created: {issue.key}"

        elif action == "update":
            if not issue_key or not (summary or description):
                return "Missing required fields for updating an issue: issue_key and at least one of summary or description."
            fields = {}
            if summary:
                fields['summary'] = summary
            if description:
                fields['description'] = description
            issue = jira.issue(issue_key)
            issue.update(fields=fields)
            return f"Issue {issue_key} updated."

        elif action == "comment":
            if not issue_key or not comment:
                return "Missing required fields for adding a comment: issue_key and comment."
            issue = jira.issue(issue_key)
            jira.add_comment(issue, comment)
            return f"Comment added to issue {issue_key}."

        elif action == "delete":
            if not issue_key:
                return "Missing required field for deleting an issue: issue_key."
            issue = jira.issue(issue_key)
            issue.delete()
            return f"Issue {issue_key} deleted."

        elif action == "search":
            if not jql:
                return "Missing required field for searching issues: jql."
            issues = jira.search_issues(jql, maxResults=max_results)
            if not issues:
                return "No issues found matching the query."
            result = [f"{issue.key}: {issue.fields.summary}" for issue in issues]
            return "\n".join(result)

        elif action == "list":
            # List all issues in a project (default: ECS)
            jql_query = f"project = {project_key} ORDER BY created DESC"
            issues = jira.search_issues(jql_query, maxResults=max_results)
            if not issues:
                return f"No issues found in project {project_key}."
            result = [f"{issue.key}: {issue.fields.summary}" for issue in issues]
            return "\n".join(result)

        else:
            return "Unknown action. Supported actions: create, update, comment, delete, search, list."

    except Exception as e:
        return f"Error: {str(e)}"


tools = [
    send_email,
    tavily_search_tool,
    send_whatsapp_message,
    send_telegram_message,
    get_stock_price,
    get_mutual_fund_nav_groww,
    get_weather,
    run_sql_write_query,
    jira_unified_tool
]

agent_executor = create_react_agent(llm, toolkit.get_tools()+ tools)


# # Using the LangChain tool we defined earlier
# response = agent_executor.invoke({
#     "messages": [
#         HumanMessage("Send a telegram message to -4888217603 saying 'Hello GenAI group from the bot!'")
#     ]
# })
