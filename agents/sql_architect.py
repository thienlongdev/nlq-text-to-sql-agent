"""SQL Architect agent: generates PostgreSQL SQL from question + schema."""
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from agents.base import BaseAgent, AgentState
from agents.config import get_llm


class SQLArchitectAgent(BaseAgent):
    name = "sql_architect"

    def __init__(self, llm=None):
        self.llm = llm or get_llm()

    def run(self, state: AgentState) -> dict:
        question = state.get("question") or ""
        schema_context = state.get("schema_context") or ""
        error = state.get("error")
        retry_count = state.get("retry_count", 0)
        attempt = retry_count + 1

        prompt_text = """
        Bạn là chuyên gia PostgreSQL.
        Nhiệm vụ: Viết SQL trả lời câu hỏi: "{question}"
        Schema: {schema}

        Yêu cầu: Chỉ trả về CODE SQL thuần túy. KHÔNG markdown.
        """
        if error:
            prompt_text += f"\n!!! CẢNH BÁO: Code trước bị lỗi: {error}. HÃY SỬA LẠI."

        prompt = ChatPromptTemplate.from_template(prompt_text)
        chain = prompt | self.llm | StrOutputParser()
        sql_query = chain.invoke({"question": question, "schema": schema_context})

        # Clean code
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        sql_query = sql_query.strip()

        # Remove markdown only
        if sql_query.startswith("```"):
            sql_query = sql_query.split("```")[1]

        sql_query = sql_query.strip()

        return {
            "sql_query": sql_query,
            "last_agent": self.name,
        }
