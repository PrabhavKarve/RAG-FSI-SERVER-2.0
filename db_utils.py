import os
import psycopg2
from decimal import Decimal, InvalidOperation
from dotenv import load_dotenv
import math

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT", 5432)

def safe_float(value):
    try:
        if value is None:
            return None
        if isinstance(value, Decimal):
            val = float(value)
            return None if math.isnan(val) else val
        return float(value)
    except (ValueError, InvalidOperation, TypeError):
        return None

def get_financial_data(company: str, statement_type: str):
    conn = psycopg2.connect(
        host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, port=DB_PORT
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT line_item, fy_2024, fy_2023
        FROM financial_statements
        WHERE company = %s AND statement_type = %s
    """, (company, statement_type))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {
            "line_item": r[0],
            "fy_2024": safe_float(r[1]),
            "fy_2023": safe_float(r[2])
        }
        for r in rows
    ]

def test_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        cur = conn.cursor()
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        tables = cur.fetchall()
        print("✅ Connected successfully!")
        print("Tables in 'public' schema:")
        for t in tables:
            print("-", t[0])

        # optional: show a row count from financial_statements if it exists
        cur.execute("SELECT COUNT(*) FROM public.financial_statements;")
        count = cur.fetchone()[0]
        print(f"Rows in financial_statements: {count}")

        cur.close()
        conn.close()
    except Exception as e:
        print("❌ Connection failed:", e)

if __name__ == "__main__":
    test_connection()
