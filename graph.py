import os
from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI 
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import db_ops

load_dotenv()

llm = ChatOpenAI(
    model="openai-gpt-oss-120b", 
    temperature=0,
    api_key=os.getenv("MEGA_API_KEY"),
    base_url=os.getenv("MEGA_API_BASE")
)

class AgentState(TypedDict):
    question: str                
    all_table_names: List[str]   
    selected_tables: List[str]   
    schema_context: str          
    sql_query: str               
    # query_result: list           
    # query_columns: list          
    error: Optional[str]         
    retry_count: int             

def schema_analyst(state: AgentState):
    all_tables = db_ops.get_all_tables()
    
    prompt = ChatPromptTemplate.from_template("""
    Bạn là chuyên gia Database.
    Danh sách các bảng: {table_list}
    Câu hỏi: "{question}"
    Output: Chỉ trả về tên các bảng cần thiết, ngăn cách dấu phẩy.
    """)
    
    chain = prompt | llm | StrOutputParser()
    try:
        response = chain.invoke({"table_list": ", ".join(all_tables), "question": state['question']})
        selected = [t.strip() for t in response.split(',')]
    except:
        selected = []
    
    schema_details = db_ops.get_schema_details(selected)
    return {
        "all_table_names": all_tables,
        "selected_tables": selected,
        "schema_context": schema_details,
        "retry_count": 0,
        "error": None
    }

def architect(state: AgentState):
    attempt = state.get('retry_count', 0) + 1
    
    prompt_text = """
    Bạn là chuyên gia PostgreSQL.
    Nhiệm vụ: Viết SQL trả lời câu hỏi: "{question}"
    Schema: {schema}
    
    Yêu cầu: Chỉ trả về CODE SQL thuần túy. KHÔNG markdown.
    """
    
    if state.get("error"):
        print(f"Fixing error: {state['error']}")
        prompt_text += f"\n!!! CẢNH BÁO: Code trước bị lỗi: {state['error']}. HÃY SỬA LẠI."
    
    prompt = ChatPromptTemplate.from_template(prompt_text)
    chain = prompt | llm | StrOutputParser()
    sql_query = chain.invoke({"question": state['question'], "schema": state['schema_context']})
    
    # Clean code
    sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
    if "SELECT" in sql_query.upper():
        idx = sql_query.upper().find("SELECT")
        sql_query = sql_query[idx:]
        
    return {"sql_query": sql_query}

def validator(state: AgentState):
    query = state['sql_query']
    check = db_ops.check_sql_syntax(query) 
    
    if check['valid']:
        return {"error": None}
    else:
        print(f"Syntax Error: {check['error']}")
        return {"error": check['error'], "retry_count": state["retry_count"] + 1}

# def executor(state: AgentState):
#     query = state['sql_query']
#     result = db_ops.execute_sql_safe(query)
    
#     if result['success']:
#         return {
#             "query_result": result['data'],
#             "query_columns": result['columns']
#         }
#     else:
#         return {"error": result['error'], "retry_count": state["retry_count"] + 1}

def router(state: AgentState):
    if state['error'] and state['retry_count'] < 3:
        return "retry"
    return "end"

workflow = StateGraph(AgentState)

workflow.add_node("analyst", schema_analyst)
workflow.add_node("architect", architect)
workflow.add_node("validator", validator)
# workflow.add_node("executor", executor)

workflow.set_entry_point("analyst")
workflow.add_edge("analyst", "architect")
workflow.add_edge("architect", "validator")

workflow.add_conditional_edges(
    "validator",
    router,
    {
        "retry": "architect",  # Quay lại sửa
        # "execute": "executor", # Đi tiếp để lấy data
        "end": END             # Chịu thua
    }
)

# workflow.add_edge("executor", END) 
app = workflow.compile()