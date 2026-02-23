"""Schema Analyst agent: selects relevant tables and builds schema context."""
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from agents.base import BaseAgent, AgentState
from agents.config import get_llm
from core import db_ops


class SchemaAnalystAgent(BaseAgent):
    name = "schema_analyst"

    def __init__(self, llm=None):
        self.llm = llm or get_llm()

    def run(self, state: AgentState) -> dict:
        all_tables = db_ops.get_all_tables()
        question = state.get("question") or ""

        prompt = ChatPromptTemplate.from_template("""
        Bạn là chuyên gia Database.
        Danh sách các bảng: {table_list}
        Câu hỏi: "{question}"
        Output: Chỉ trả về tên các bảng cần thiết, ngăn cách dấu phẩy.
        """)
        chain = prompt | self.llm | StrOutputParser()
        try:
            response = chain.invoke({
                "table_list": ", ".join(all_tables),
                "question": question,
            })
            selected = [t.strip() for t in response.split(",") if t.strip()]
        except Exception:
            selected = []

        schema_details = db_ops.get_schema_details(selected)
        return {
            "all_table_names": all_tables,
            "selected_tables": selected,
            "schema_context": schema_details,
            "retry_count": 0,
            "error": None,
            "last_agent": self.name,
        }
