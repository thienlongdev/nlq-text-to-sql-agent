"""
Executor agent:
- Executes validated SQL (read-only)
- Enforces SELECT-only policy (defense-in-depth)
- Returns structured results
"""

from agents.base import BaseAgent, AgentState
from core import db_ops
import logging

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


class ExecutorAgent(BaseAgent):
    name = "executor"

    def __init__(self, llm=None, **kwargs):
        super().__init__(llm=llm, **kwargs)

    def run(self, state: AgentState) -> dict:
        query = (state.get("sql_query") or "").strip()
        retry_count = state.get("retry_count", 0)

        logger.info(
            {
                "stage": "execution_start",
                "query": query,
                "retry_count": retry_count,
            }
        )
        if not query:
            return {
                "error": "Empty SQL query.",
                "retry_count": retry_count + 1,
                "last_agent": self.name,
            }

        if not is_select_query(query):
            return {
                "error": "Only SELECT queries are allowed.",
                "retry_count": retry_count + 1,
                "last_agent": self.name,
            }

        if contains_forbidden_keyword(query):
            return {
                "error": "Forbidden SQL operation detected.",
                "retry_count": retry_count + 1,
                "last_agent": self.name,
            }

        try:
            result = db_ops.execute_sql_safe(query)
        except Exception as e:
            logger.exception("Execution error")
            return {
                "error": str(e),
                "retry_count": retry_count + 1,
                "last_agent": self.name,
            }

        if result.get("success"):
            logger.info(
                {
                    "stage": "execution_success",
                    "row_count": len(result.get("data", [])),
                }
            )
            return {
                "query_result": result.get("data", []),
                "query_columns": result.get("columns", []),
                "error": None,
                "last_agent": self.name,
            }

        logger.warning(
            {
                "stage": "execution_failed",
                "error": result.get("error"),
            }
        )

        return {
            "error": result.get("error", "Unknown error"),
            "retry_count": retry_count + 1,
            "last_agent": self.name,
        }