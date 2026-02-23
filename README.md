# NLQ Text-to-SQL Agent

Hệ thống chuyển đổi câu hỏi ngôn ngữ tự nhiên (Tiếng Việt) sang câu lệnh SQL PostgreSQL hợp lệ, sử dụng LLM kết hợp LangGraph theo mô hình multi-agent nhiều vai trò.

Mục tiêu của project là cho phép người dùng không cần biết SQL vẫn có thể truy vấn cơ sở dữ liệu chính xác và an toàn.

# Mục tiêu

Nhập câu hỏi bằng tiếng Việt

Phân tích ngữ nghĩa và ý định truy vấn

Sinh SQL thuần, hợp lệ với PostgreSQL

Kiểm tra và xác thực SQL trước khi trả kết quả

Hạn chế truy vấn nguy hiểm (DROP, DELETE, UPDATE, …)

# Kiến trúc hệ thống

Luồng xử lý theo mô hình multi-agent với LangGraph:

User → Schema Analyst → SQL Architect → Validator → Executor → SQL Result

Vai trò

User: Nhập câu hỏi tiếng Việt

Schema Analyst: Phân tích schema, bảng, cột liên quan

SQL Architect: Xây dựng cấu trúc và câu lệnh SQL

Validator: Kiểm tra cú pháp, tính hợp lệ và an toàn

Executor: Thực thi truy vấn và trả kết quả

SQL Result: Câu lệnh SQL và dữ liệu truy vấn
# Cấu trúc project
```
nlq-text-to-sql-agent/
├── agents/
│   ├── base.py
│   ├── config.py
│   ├── executor.py
│   ├── registry.py
│   ├── schema_analyst.py
│   ├── sql_architect.py
│   └── validator.py
│
├── core/
│   ├── db_ops.py
│   ├── main.py
│   └── multi_agent_graph.py
│
├── venv/
├── .dockerignore
├── .env
├── .gitignore
├── api.py
├── UI.py
├── backup.sql
├── docker-compose.yml
├── Dockerfile
├── README.md
└── requirements.txt
```

# Công nghệ sử dụng

Python

LangGraph

LangChain

PostgreSQL

Large Language Model 

Docker

# Cài đặt

## Clone repo
```
git clone https://github.com/thienlongdev/nlq-text-to-sql-agent.git
cd nlq-text-to-sql-agent
```
## Cài thư viện
```
pip install -r requirements.txt
```
## Cấu hình môi trường

### Tạo file .env và thêm:
```
MEGA_API_KEY=your_api_key
MEGA_URL=your_llm_endpoint
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_db
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database
DB_USER=your_user
DB_PASSWORD=your_password
```

### Lưu ý:

- Nếu chạy local → DB_HOST=localhost

- Nếu chạy bằng Docker Compose → DB_HOST=db
# Chạy chương trình
```
python -m streamlit run UI.py
```
## Ví dụ câu hỏi:
```
Liệt kê 5 khách hàng có nhiều đơn hàng nhất
```
## Ví dụ SQL trả về:
```
SELECT
    c.custid,
    c.companyname,
    COUNT(s.orderid) AS order_count
FROM
    customer c
JOIN
    salesorder s ON c.custid = s.custid
GROUP BY
    c.custid,
    c.companyname
ORDER BY
    order_count DESC
LIMIT 5;
```
