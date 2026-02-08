\# NLQ Text-to-SQL Agent 



Hệ thống chuyển đổi câu hỏi ngôn ngữ tự nhiên (Tiếng Việt) sang câu lệnh SQL PostgreSQL hợp lệ bằng cách sử dụng LLM + LangGraph theo mô hình agent với nhiều vai trò.



\## Mục tiêu

Cho phép người dùng nhập câu hỏi tiếng Việt và nhận về SQL thuần túy.



\## Kiến trúc

User → Analyst → Architect → Validator → SQL



\## Cấu trúc project

NLQ-PROJECT/

\- app.py

\- main.py

\- graph.py

\- db\_ops.py

\- evaluate.py

\- requirements.txt

\- .gitignore

\- README.md



\## Công nghệ

\- Python

\- LangGraph

\- LangChain

\- PostgreSQL

\- Streamlit



\## Cách chạy

python main.py

streamlit run app.py



\## Ghi chú

Hệ thống chỉ sinh SQL, không thực thi.



\## Tác giả

Nguyễn Tú Thiên Long

https://github.com/thienlongdev



