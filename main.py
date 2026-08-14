## 1. extract schema
from sqlalchemy import create_engine, inspect
import json
import re

db_url = "sqlite:///database.db"

def extract_schema(db_url):
    engine = create_engine(db_url)
    inspector = inspect(engine)
    schema = {}

    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        schema[table_name] = [col['name'] for col in columns]

    return json.dumps(schema)

# 2. TEXT TO SQL (Gemini AI)
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
import os
import sqlite3
from dotenv import load_dotenv


load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

def text_to_sql(schema, prompt):
    SYSTEM_PROMPT = """
    You are an expert SQL generator. Given a database schema and a user prompt, generate a valid SQL query that answers the prompt. 
    Only use the tables and columns provided in the schema. ALWAYS ensure the SQL syntax is correct and avoid using any unsupported features. 
    Output only the SQL as your response will be directly used to query data from the database. No preamble please. Do not use <think> tags.
    """

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("user", "Schema:\n{schema}\n\nQuestion: {user_prompt}\n\nSQL Query:")
    ])

    model = ChatGoogleGenerativeAI(model = "gemini-2.5-flash")

    chain = prompt_template | model

    raw_response= chain.invoke({"schema" : schema , "user_prompt" : prompt})
    cleaned_response = re.sub(r"<think>.*?<think>", "", raw_response.content, flags=re.DOTALL)
    cleaned_response = re.sub(r"```sql\s*|```", "", cleaned_response, flags=re.IGNORECASE)
    return cleaned_response.strip()

def get_data_from_database(prompt):
    schema = extract_schema(db_url)
    sql_query = text_to_sql(schema, prompt)
    ## execute the sql query
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    response  = cursor.execute(sql_query)
    results = response.fetchall()
    conn.close()
    return results



