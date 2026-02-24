"""
Base types and interface for the NLQ-to-SQL multi-agent system.
"""

from abc import ABC, abstractmethod
from typing import TypedDict, List, Optional, Any


class AgentState(TypedDict, total=False):
    """
    Shared state passed between all agents in the pipeline.
    Each agent reads from this state and returns only updated fields.
    """
    question: str
    all_table_names: List[str]
    selected_tables: List[str]
    schema_context: str
    sql_query: str
    query_result: list
    query_columns: list
    error: Optional[str]
    retry_count: int
    last_agent: str
    messages: List[dict]


class BaseAgent(ABC):
    """
    Base class for all pipeline agents.

    - Agents MUST NOT mutate the input state.
    - Agents MUST return a dict of updated fields only.
    """

    name: str = "base"

    def __init__(self, llm: Any = None, **kwargs):
        """
        Optional LLM injection.
        Agents that don't use LLM can ignore this.
        """
        self.llm = llm

    @abstractmethod
    def run(self, state: AgentState) -> dict:
        """
        Process state and return a partial state update.
        Must not mutate state directly.
        """
        pass

    def __call__(self, state: AgentState) -> dict:
        """
        Allow agent instance to be called like a function.
        """
        return self.run(state)