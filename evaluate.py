import pandas as pd
from graph import app
import db_ops

TEST_DATASET = [
    {
        "question": "Có bao nhiêu khách hàng trong hệ thống?",
        "golden_sql": "SELECT COUNT(*) FROM customers"
    },
    {
        "question": "Liệt kê 5 đơn hàng mới nhất",
        "golden_sql": "SELECT id, created_at FROM orders ORDER BY created_at DESC LIMIT 5"
    },
    # Thêm các câu hỏi khó hơn vào đây...
]

def run_benchmark():
    results = []
    
    print(f"Bắt đầu benchmark {len(TEST_DATASET)} test cases...")
    
    for item in TEST_DATASET:
        question = item['question']
        golden_sql = item['golden_sql']
        
        # Chạy Golden Query để lấy kết quả chuẩn (Ground Truth)
        golden_res = db_ops.execute_sql_safe(golden_sql)
        if not golden_res['success']:
            print(f"Skipping '{question}' due to Golden SQL error.")
            continue
        
        golden_data = golden_res['data']
        
        # Chạy Agent System
        inputs = {"question": question}
        output = app.invoke(inputs)
        
        generated_sql = output.get('sql_query', 'N/A')
        generated_data = output.get('query_result', [])
        error = output.get('error')
        
        # So sánh kết quả (Execution Accuracy)
        # Chuyển về set hoặc sort để so sánh nếu thứ tự không quan trọng
        # Ở đây so sánh strict (chính xác)
        is_correct = (str(golden_data) == str(generated_data))
        
        results.append({
            "Question": question,
            "Correct": "Oke" if is_correct else "No",
            "Error": error if error else "",
            "Generated SQL": generated_sql
        })
        
    # Xuất báo cáo
    df = pd.DataFrame(results)
    print("\n=== KẾT QUẢ ĐÁNH GIÁ ===")
    print(df.to_markdown())
    
    accuracy = (df['Correct'] == "Oke").mean() * 100
    print(f"\nĐộ chính xác tổng thể: {accuracy:.2f}%")

if __name__ == "__main__":
    run_benchmark()