# NLQ Text-to-SQL Agent (Vietnamese → PostgreSQL)

Hệ thống chuyển đổi câu hỏi ngôn ngữ tự nhiên (Tiếng Việt) sang câu lệnh SQL PostgreSQL hợp lệ, sử dụng LLM kết hợp LangGraph theo mô hình agent đa vai trò.

Mục tiêu của project là cho phép người dùng không cần biết SQL vẫn có thể truy vấn cơ sở dữ liệu chính xác và an toàn.

# Mục tiêu

Nhập câu hỏi bằng tiếng Việt

Phân tích ngữ nghĩa và ý định truy vấn

Sinh SQL thuần, hợp lệ với PostgreSQL

Kiểm tra và xác thực SQL trước khi trả kết quả

Hạn chế truy vấn nguy hiểm (DROP, DELETE, …)

# Kiến trúc hệ thống

Luồng xử lý theo mô hình multi-agent với LangGraph:

User → Analyst → Architect → Validator → SQL

Vai trò

User: Nhập câu hỏi tiếng Việt

Analyst: Phân tích ý định, bảng, cột, điều kiện

Architect: Xây dựng cấu trúc câu SQL

Validator: Kiểm tra cú pháp, an toàn, schema

SQL: Câu lệnh SQL cuối cùng

# Cấu trúc project
```
NLQ-PROJECT/
├── app.py              # Entry point / giao diện chạy
├── main.py             # Logic điều phối
├── graph.py            # LangGraph workflow
├── db_ops.py           # Thao tác PostgreSQL
├── evaluate.py         # Đánh giá kết quả sinh SQL
├── requirements.txt    # Thư viện cần cài đặt
├── .gitignore
└── README.md
```

# Công nghệ sử dụng

Python

LangGraph

LangChain

PostgreSQL

Large Language Model (LLM)

# Cài đặt

## Clone repo
```
git clone <repo-url>
cd NLQ-PROJECT
```
## Cài thư viện
```
pip install -r requirements.txt
```
## Cấu hình môi trường

### Tạo file .env và thêm:
```
MEGA_API_KEY=your_api_key
MEGA_API_BASE=your_url
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database
DB_USER=your_user
DB_PASSWORD=your_password
```
# Chạy chương trình
```
python app.py
```
## Ví dụ câu hỏi:
```
Liệt kê 5 khách hàng có nhiều đơn hàng nhất
```
## Ví dụ SQL trả về:
```
SELECT customer_id, COUNT(*) AS total_orders
FROM orders
GROUP BY customer_id
ORDER BY total_orders DESC
LIMIT 5;
```
# Ghi chú

SQL trả về là SQL thuần, không kèm giải thích

Có thể mở rộng: hỗ trợ nhiều CSDL, trả kết quả truy vấn, logging & đánh giá chất lượng SQL
