from graph import app

def chatbot():
    print("Bot: Chào bạn! Hãy đưa tôi text, tôi sẽ chuyển nó thành SQL.")

    while True:
        user_input = input("\nBạn: ")
        if user_input.lower().strip() in ["exit", "quit"]:
            print("Tạm biệt!")
            break
            
        inputs = {"question": user_input}
        try:
            result = app.invoke(inputs)
            data = result.get("query_result", [])
            cols = result.get("query_columns", [])
            error = result.get("error")
            sql = result.get("sql_query")
            
            if error:
                print(f"Lỗi: {error}")
            else:
                print(f"SQL Generated: \n{sql}")
            #     print(f"Kết quả ({len(data)} dòng):")
            #     if len(data) > 0:
            #         print(f"   Columns: {cols}")
            #         for row in data[:5]: 
            #             print(f"   - {row}")
            #         if len(data) > 5: print("   ... (và còn nữa)")
            #     else:
            #         print("   (Không tìm thấy dữ liệu nào)")
                    
        except Exception as e:
            print(f"System Error: {e}")

if __name__ == "__main__":
    chatbot()