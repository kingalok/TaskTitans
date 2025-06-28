# 🛠️ TaskTitans - Command Your Tasks Like a Titan!

**TaskTitans** is an intelligent, modular command interface built on top of Telegram + LangChain agents. It enables natural language task execution through Telegram by integrating with multiple tools like WhatsApp, email, MySQL, weather, stock market alerts, travel guides, fuel price lookups, Jira, and more — all wrapped in a Dockerized agent running in your laptop.

---

## 🚀 Features

- 📬 Send **WhatsApp** or **Telegram** messages via simple prompts
- 📧 Trigger **email notifications** with subject and message
- 🗃️ Query and interact with a **MySQL database**
- 📉 Get **BSE stock prices** or set threshold alerts
- 🌦️ Check **weather** for any city in real-time
- 🔍 Perform **web search** using **Tavily Search**
- 🧭 Discover **tourist attractions** in any city
- 🛢️ Find **cheapest petrol prices** nearby (UK only – experimental)

## 🚀 Features

- 📬 Send WhatsApp or Telegram messages
Instantly message contacts or groups using simple prompts.

- 📧 Trigger email notifications
Fire off emails with custom subjects and messages.

- 🗃️ Query and interact with MySQL databases
Retrieve, update, or manage your data with ease.

- 📉 Get BSE stock prices & set threshold alerts
Monitor stocks and receive instant alerts on price movements.

- 🌦️ Check real-time weather
Get up-to-the-minute forecasts for any city.

- 🔍 Perform web searches (Tavily Search)
Search the web for anything, directly from chat.

- 🧭 Discover tourist attractions
Find must-see destinations in any city.

- 🛢️ Find the cheapest petrol prices nearby (UK only – experimental)
Locate the best fuel deals around you.

- 🗂️ Jira management
Create, update, and track Jira issues or tickets—streamline your workflow!


---

## 🧱 Tech Stack

- **Python** + **LangChain** (StructuredTool, Agents, Tools)
- **Telegram Bot API** & **Ultramsg WhatsApp API**
- **SQLAlchemy** + **MySQL Connector**
- **Tavily**, **Travalyst**, and custom LangChain tools
- **Weather**, **OpenWeatherMap**
- **Docker**, **Docker Compose**

---

## 🗂️ Project Structure# TaskTitans

```
tasktitans/
├── bot.py                         # Telegram listener + agent trigger
├── my_tools.py                    # LangChain-compatible tools (email, WhatsApp, Telegram, DB, etc.)
├── .env                           # Env vars for credentials and config
├── Dockerfile                     # Container for Telegram agent
├── docker-compose.telegram.yml    # Docker Compose for bot + services
└── README.md                      # You’re here
```

---

## ⚙️ Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/your-org/tasktitans.git
cd tasktitans
```

### 2. Prepare .env file

### Telegram Bot
TELEGRAM_BOT_TOKEN=...

### WhatsApp
ULTRAMSG_INSTANCE_ID=...
ULTRAMSG_TOKEN=...

### Email
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=...
SMTP_PASSWORD=...

### MySQL
DB_USER=ltgenai
DB_PASSWORD=xxx
DB_HOST=studentsdb
DB_PORT=3306
DB_NAME=genaideveloper

### 3. Start the containers

```bash
docker compose -f docker-compose.telegram.yml up -d
```


### 💬 Example Commands (in Telegram Group)

```bash

/watch RELIANCE below 2800        → Alert if stock drops below ₹2800
/remove RELIANCE                  → Remove stock alert
Send WhatsApp to +447911123456: Hi! Meeting at 6PM
Send email to user@example.com with subject "Reminder" and message "Project due today"
What are the tourist attractions in Paris?
What is the cheapest petrol in Harlow?
Get student emails from database
```

### 🤖 Name Origin

TaskTitans – because it empowers users to command complex task automations like a Titan from a simple messaging interface 💪📱


### 🤝 Contributions

We welcome contributions for new tools, agent logic improvements, or cool ideas! Just fork the repo and submit a PR or raise an issue.

⸻

### 📜 License

This project is licensed under the MIT License.

