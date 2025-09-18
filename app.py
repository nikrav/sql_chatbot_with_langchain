import os
import streamlit as st
import sqlite3
import pandas as pd
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# ==========================
# Load environment variables
# ==========================
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("⚠️ GROQ_API_KEY not found. Please set it in a .env file.")
else:
    os.environ["GROQ_API_KEY"] = api_key

# ==========================
# Streamlit UI
# ==========================
st.title("🗄️ SQL Chatbot with LangChain + Groq")
st.write("Upload a SQLite database (.db) or a CSV file, then ask questions in natural language.")

uploaded_file = st.file_uploader("Upload a file", type=["db", "csv"])

if uploaded_file is not None and api_key:
    # Handle CSV → SQLite
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
        db_path = "uploaded.db"
        conn = sqlite3.connect(db_path)
        df.to_sql("data", conn, if_exists="replace", index=False)
        tables = [("data",)]
    else:
        db_path = "uploaded.db"
        with open(db_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

    st.write("📂 Tables in DB:", [t[0] for t in tables])

    # Extract schema dynamically
    cursor = conn.cursor()
    schema = ""
    for t in tables:
        t_name = t[0]
        cursor.execute(f"PRAGMA table_info({t_name});")
        cols = cursor.fetchall()
        col_names = [c[1] for c in cols]
        schema += f"\nTable {t_name}: {col_names}"

    # Show schema to user for clarity
    st.write("📑 Schema detected:", schema)

    question = st.text_input("Ask about your data:")

    if question:
        # Prompt template with strict instructions
        template = f"""
        You are an assistant that converts English questions into SQL queries.
        Only use the tables and columns shown below. Do NOT invent new names.

        Database schema:
        {schema}

        Question: {{question}}

        Return ONLY the SQL query. 
        Do not include explanations, comments, or markdown fences.
        """
        prompt = PromptTemplate(template=template, input_variables=["question"])
        sql_chain = LLMChain(llm=ChatGroq(model="llama-3.1-8b-instant"), prompt=prompt)

        # Generate SQL
        raw_sql = sql_chain.run(question).strip()

        # Clean code fences if present
        if "```" in raw_sql:
            raw_sql = raw_sql.split("```")[1]
            if raw_sql.lower().startswith("sql"):
                raw_sql = raw_sql[3:]
        sql_query = raw_sql.strip()

        st.code(sql_query, language="sql")

        # Execute query safely
        try:
            result = pd.read_sql_query(sql_query, conn)
            st.dataframe(result)

            # Optional chart
            if len(result.columns) == 2 and result[result.columns[1]].dtype in ["int64", "float64"]:
                st.bar_chart(result.set_index(result.columns[0]))

        except Exception as e:
            st.error(f"Error executing query: {e}")
