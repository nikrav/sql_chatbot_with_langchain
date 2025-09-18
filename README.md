# 🗄️ SQL Chatbot with LangChain + Groq

This is a **Streamlit app** that lets you upload a **SQLite database** (`.db`) or a **CSV file**, and then ask questions about the data in **natural language**.  
The app uses **LangChain** with **Groq LLMs** to generate SQL queries automatically, execute them on your database, and display the results (with optional charts).  

---

## ✨ Features
- Upload **CSV** → automatically converted into a SQLite table.  
- Upload **SQLite DB** → queries run directly on it.  
- Ask questions in plain English → get back SQL queries + results.  
- Supports interactive data exploration.  
- Auto-detects tables and schema.  
- Simple UI powered by Streamlit.  

---

## 🚀 Getting Started

### 1️⃣ Clone this repository
```bash
git clone https://github.com/nikrav/sql_chatbot_with_langchain.git
cd sql_chatbot_with_langchain
