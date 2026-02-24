import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )
        conn.autocommit = False
        return conn
    except Exception as e:
        print(f"[DB ERROR] Connection failed: {e}")
        raise


def get_all_tables():
    query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE';
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                return [row[0] for row in cur.fetchall()]
    except Exception as e:
        print(f"[DB ERROR] get_all_tables: {e}")
        return []


def get_foreign_keys(table_name, cur):
    query = """
        SELECT
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.key_column_usage AS kcu
        JOIN information_schema.referential_constraints AS rc
            ON kcu.constraint_name = rc.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
            ON rc.unique_constraint_name = ccu.constraint_name
        WHERE kcu.table_name = %s;
    """
    cur.execute(query, (table_name,))
    return cur.fetchall()


def get_schema_details(table_names):
    schema_text = ""

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:

                for table in table_names:
                    cur.execute("""
                        SELECT column_name, data_type
                        FROM information_schema.columns
                        WHERE table_name = %s;
                    """, (table,))
                    columns = cur.fetchall()

                    # Get foreign keys
                    fks = get_foreign_keys(table, cur)

                    # Format schema for LLM
                    schema_text += f"TABLE: {table}\n"
                    schema_text += "COLUMNS:\n"

                    for col, dtype in columns:
                        schema_text += f" - {col} ({dtype})\n"

                    if fks:
                        schema_text += "RELATIONSHIPS (Foreign Keys):\n"
                        for col, f_table, f_col in fks:
                            schema_text += f" - {col} -> {f_table}({f_col})\n"

                    schema_text += "\n"

        return schema_text

    except Exception as e:
        print(f"[DB ERROR] get_schema_details: {e}")
        return ""

def check_sql_syntax(query):
    """
    Validate SQL using EXPLAIN.
    Does NOT execute query.
    """

    if not query or not query.strip():
        return {"valid": False, "error": "Empty SQL query"}

    cleaned = query.strip().rstrip(";")

    print("\n------ VALIDATING SQL ------")
    print(cleaned)
    print("----------------------------\n")

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SET statement_timeout = 2000;")

                cur.execute("EXPLAIN " + cleaned)

        return {"valid": True, "error": None}

    except psycopg2.Error as e:
        return {
            "valid": False,
            "error": f"Postgres Error {e.pgcode}: {e.pgerror}",
        }

    except Exception as e:
        return {
            "valid": False,
            "error": str(e),
        }

def execute_sql_safe(query):
    """
    Execute SQL safely.
    - SELECT → return data
    - DML → commit
    """

    if not query or not query.strip():
        return {"success": False, "error": "Empty SQL query"}

    cleaned = query.strip().rstrip(";")

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:

                cur.execute(cleaned)

                # If SELECT
                if cur.description:
                    columns = [desc[0] for desc in cur.description]
                    results = cur.fetchall()
                    return {
                        "success": True,
                        "data": results,
                        "columns": columns,
                    }

                # If INSERT/UPDATE/DELETE
                conn.commit()
                return {"success": True, "data": [], "columns": []}

    except psycopg2.Error as e:
        return {
            "success": False,
            "error": f"Postgres Error {e.pgcode}: {e.pgerror}",
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }