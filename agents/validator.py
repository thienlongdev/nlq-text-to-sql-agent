"""
Validator agent:
- Only allows safe SELECT queries
- Blocks dangerous SQL operations
- Validates syntax using EXPLAIN (no execution)
"""

from agents.base import BaseAgent, AgentState
import db_ops
import logging
import re

logger = logging.getLogger(__name__)

FORBIDDEN_KEYWORDS = {
    "DROP",
    "DELETE",
    "UPDATE",
    "INSERT",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "GRANT",
    "REVOKE",
}


def contains_forbidden_keyword(query: str) -> bool:
    upper_query = query.upper()
    return any(keyword in upper_query for keyword in FORBIDDEN_KEYWORDS)


def is_select_query(query: str) -> bool:
    return query.strip().upper().startswith("SELECT")


class ValidatorAgent(BaseAgent):
    name = "validator"

    def __init__(self, llm=None, **kwargs):
        super().__init__(llm=llm, **kwargs)

    def run(self, state: AgentState) -> dict:
        query = (state.get("sql_query") or "").strip()
        retry_count = state.get("retry_count", 0)

        logger.info(
            {
                "stage": "validation_start",
                "query": query,
                "retry_count": retry_count,
            }
        )

        # 1️⃣ Empty query check
        if not query:
            return {
                "error": "Empty SQL query.",
                "retry_count": retry_count + 1,
                "last_agent": self.name,
            }

        # 2️⃣ Only allow SELECT queries
        if not is_select_query(query):
            return {
                "error": "Only SELECT queries are allowed.",
                "retry_count": retry_count + 1,
                "last_agent": self.name,
            }

        # 3️⃣ Block dangerous keywords
        if contains_forbidden_keyword(query):
            return {
                "error": "Forbidden SQL operation detected.",
                "retry_count": retry_count + 1,
                "last_agent": self.name,
            }

        # 4️⃣ Enforce LIMIT (optional safety guard)
        if "LIMIT" not in query.upper():
            query = query.rstrip(";") + " LIMIT 100"
            logger.info({"stage": "limit_appended", "modified_query": query})

        # 5️⃣ Syntax validation using EXPLAIN
        check = db_ops.check_sql_syntax(query)

        if check.get("valid"):
            logger.info({"stage": "validation_success"})
            return {
                "error": None,
                "sql_query": query,  # return possibly modified query
                "last_agent": self.name,
            }

        logger.warning(
            {
                "stage": "validation_failed",
                "error": check.get("error"),
            }
        )

        return {
            "error": check.get("error"),
            "retry_count": retry_count + 1,
            "last_agent": self.name,
        }