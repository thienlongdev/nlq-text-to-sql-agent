import os
import psycopg2
from dotenv import load_dotenv

# Load biến môi trường
load_dotenv()

def get_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS")
        )
        return conn
    except Exception as e:
        print(f"Lỗi kết nối DB: {e}")
        raise e 

def get_all_tables():
    """Lấy danh sách bảng (chỉ lấy bảng thường, bỏ qua bảng hệ thống)"""
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
                return [row[0] for row in cur.fetchall()] # ['users', 'products', 'orders'], fetchall: [('users',), ('orders',)]
    except Exception as e:
        print(f"Lỗi lấy danh sách bảng: {e}")
        return []

def get_foreign_keys(table_name, cur):
    """Hàm phụ: Lấy danh sách khóa ngoại của 1 bảng"""
    query = f"""
    SELECT
        kcu.column_name, 
        ccu.table_name AS foreign_table_name,
        ccu.column_name AS foreign_column_name 
    FROM 
        information_schema.key_column_usage AS kcu
        JOIN information_schema.referential_constraints AS rc 
            ON kcu.constraint_name = rc.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu 
            ON rc.unique_constraint_name = ccu.constraint_name
    WHERE kcu.table_name = '{table_name}';
    """
    cur.execute(query)
    return cur.fetchall() # ('user_id', 'users', 'id') : nghĩa là: cột user_id của bảng hiện tại trỏ tới cột id của bảng users

def get_schema_details(table_names):
    """
    Lấy DDL chi tiết:
    1. Tên cột & Kiểu dữ liệu.
    2. Quan hệ (Foreign Keys) -> Cực quan trọng cho LLM JOIN bảng.
    """
    schema_text = ""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                for table in table_names:
                    # 1. Lấy thông tin cột
                    cur.execute(f"""
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_name = '{table}';
                    """) 
                    columns = cur.fetchall() # list[tuple[str, str]]
                    
                    # 2. Lấy thông tin khóa ngoại
                    fks = get_foreign_keys(table, cur)

                    # 3. Format text cho LLM đọc
                    schema_text += f"TABLE: {table}\n"
                    schema_text += "COLUMNS:\n"
                    for col, dtype in columns:
                        schema_text += f" - {col} ({dtype})\n" #  - user_id (integer)

                    if fks:
                        schema_text += "RELATIONSHIPS (Foreign Keys):\n"
                        for col, f_table, f_col in fks:
                            schema_text += f" - {col} -> {f_table}({f_col})\n" # - user_id -> users(id)
                    
                    schema_text += "\n" # Xuống dòng giữa các bảng
                    
        return schema_text
        """ Ex:
            TABLE: orders
            COLUMNS:
            - id (integer)
            - user_id (integer)
            RELATIONSHIPS:
            - user_id -> users(id)

        """
    except Exception as e:
        print(f"Lỗi lấy schema: {e}")
        return ""

def check_sql_syntax(query):
    """Kiểm tra cú pháp bằng EXPLAIN (không chạy lệnh thật)"""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f"EXPLAIN {query}")
                return {"valid": True, "error": None}
    except Exception as e:
        return {"valid": False, "error": str(e)}
        

# def execute_sql_safe(query):
#     """Thực thi SQL an toàn"""
#     try:
#         with get_connection() as conn:
#             with conn.cursor() as cur:
#                 cur.execute(query)
                
#                 # Kiểm tra xem query có trả về dữ liệu không (SELECT)
#                 if cur.description: # Chỉ SELECT mới có
#                     columns = [desc[0] for desc in cur.description] # ["id", "name", "price"]
#                     results = cur.fetchall()
#                     return {"success": True, "data": results, "columns": columns}
                
#                 # Trường hợp INSERT/UPDATE/DELETE
#                 conn.commit() 
#                 return {"success": True, "data": [], "columns": []}
                
#     except psycopg2.Error as e:
#         return {"success": False, "error": f"Postgres Error: {e.pgcode} - {e.pgerror}"}
#     except Exception as e:
#         return {"success": False, "error": str(e)}

