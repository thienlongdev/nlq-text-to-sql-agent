import streamlit as st
from graph import app  

st.set_page_config(
    page_title="SQL Generator",
    layout="centered"
)

st.title("NLQ Chatbot")
st.caption("Nhập yêu cầu bằng tiếng Việt, tôi sẽ sinh ra câu lệnh SQL chuẩn cho bạn.")
if "messages" not in st.session_state:
    st.session_state.messages = []
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            st.code(message["content"], language="sql")
        else:
            st.markdown(message["content"])

if prompt := st.chat_input("Ví dụ: Tìm khách hàng mua nhiều đơn nhất năm 2023"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Đang viết code SQL..."):
            try:
                inputs = {"question": prompt}
                result = app.invoke(inputs)
                sql_query = result.get("sql_query", "")
                error = result.get("error")

                if error:
                    st.error(f"Không thể sinh SQL: {error}")
                    st.session_state.messages.append({"role": "assistant", "content": f"-- Lỗi: {error}"})
                else:
                    st.code(sql_query, language="sql")
                    st.session_state.messages.append({"role": "assistant", "content": sql_query})
                    
            except Exception as e:
                st.error(f"Lỗi hệ thống: {e}")