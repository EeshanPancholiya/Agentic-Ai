import re
import sqlite3
import requests
import os
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# Set your API key for Together AI
os.environ["TOGETHER_API_KEY"] = "TOGETHER_API_KEY"

# Initialize SQLite and SQLAlchemy connection
conn = sqlite3.connect("Eeshan.db")
cursor = conn.cursor()

# Create table and insert data (simplified)
cursor.execute("CREATE TABLE IF NOT EXISTS employees (id INTEGER PRIMARY KEY, name TEXT, department TEXT, salary INTEGER)")
conn.commit()
conn.close()

conn = sqlite3.connect("Eeshan.db")
cursor = conn.cursor()

# Insert multiple rows at once
employees_data = [
    ('Alice', 'HR', 60000),
    ('Bob', 'Engineering', 80000),
    ('Charlie', 'Marketing', 70000),
    ('David', 'Finance', 75000),
    ('Eve', 'HR', 62000),
    ('Frank', 'Engineering', 90000),
    ('Grace', 'Marketing', 68000),
    ('Hannah', 'Finance', 78000),
    ('Ian', 'Sales', 72000),
    ('Jack', 'Sales', 71000),
    ('Karen', 'Engineering', 95000),
    ('Leo', 'HR', 63000),
    ('Mia', 'Marketing', 74000),
    ('Nathan', 'Finance', 80000),
    ('Olivia', 'Engineering', 85000),
    ('Paul', 'Sales', 73000),
    ('Quinn', 'HR', 64000),
    ('Ryan', 'Marketing', 71000),
    ('Sophie', 'Finance', 77000),
    ('Tom', 'Sales', 76000),
    ('Uma', 'Engineering', 87000),
    ('Victor', 'Marketing', 72000),
    ('Wendy', 'Finance', 79000),
    ('Xavier', 'HR', 65000),
    ('Yara', 'Sales', 75000),
    ('Zane', 'Engineering', 93000)
]

cursor.executemany("INSERT INTO employees (name, department, salary) VALUES (?, ?, ?)", employees_data)

conn.commit()
conn.close()


DATABASE_URL = "sqlite:///Eeshan.db"
engine = create_engine(DATABASE_URL)

# Function to clean the SQL query
def clean_sql_query(sql_query):
    sql_query = re.sub(r'```sql|```', '', sql_query)  # Remove ```sql and ```
    sql_query = sql_query.strip()  # Remove any leading/trailing whitespace
    return sql_query

# Function to execute SQL query
def execute_sql(query):
    try:
        with engine.connect() as connection:
           # st.write(f"Executing Query: `{query}`")  # Debug: Log the query being executed
            result = connection.execute(text(query))
            results = result.fetchall()  # Fetch the result
            columns = result.keys()  # Get column names dynamically
            #st.write(f"Query Execution Successful. Results: {results}")  # Debug: Log the results
            return results, columns
    except Exception as e:
        st.error(f"Error executing SQL: {e}")
        return [], []
# Function to generate SQL query from plain English
def generate_sql(query):
    API_KEY = os.getenv("TOGETHER_API_KEY")
    url = "https://api.together.xyz/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
    Convert the following question into an SQL query for a SQLite database. 
    The table 'employees' has the following columns: id, name, department, salary.
    Only return the SQL query without any explanation or markdown:
    
    Question: {query}
    
    SQL Query:
    """
    data = {
        "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo-128K", 
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        return f"Error: {response.status_code}, {response.text}"

# Streamlit UI code
st.title("LLM-Powered SQL Agent")

# Debug: Check current working directory
st.write(f"Current Working Directory: {os.getcwd()}")

user_input = st.text_input("Ask a question about the database:")

if st.button("Run Query"):
    if user_input.strip() == "":
        st.warning("Please enter a question.")
    else:
        sql_query = generate_sql(user_input)
        if sql_query:
            st.write(f"Generated SQL Query: `{sql_query}`")  # Debug: Show the generated SQL query
            
            cleaned_sql_query = clean_sql_query(sql_query)
            #st.write(f"Cleaned SQL Query: `{cleaned_sql_query}`")  # Debug: Show the cleaned SQL query
            
            results, columns = execute_sql(cleaned_sql_query)
            # st.write(f"Raw Results: {results}")  # Debug: Show raw results
            
            if len(results) > 0:
                st.write("Query Results:")
                # Convert results to a DataFrame with dynamic column names
                df = pd.DataFrame(results, columns=columns)
                st.dataframe(df)  # Display results in a table format
            else:
                st.write("No data found.")
            
