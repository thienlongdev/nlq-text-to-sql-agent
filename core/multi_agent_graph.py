"""
Multi-agent NLQ-to-SQL graph. Composes agents from the registry into a LangGraph workflow.
"""
from langgraph.graph import StateGraph, END

from agents.base import AgentState
from agents.config import get_llm
from agents.registry import get_default_registry


def build_nlq_to_sql_graph(include_executor: bool = False):
    """
    Build the compiled LangGraph: analyst -> architect -> validator -> (retry architect | end).
    If include_executor is True, after validator success go to executor then END.
    """
    llm = get_llm()
    registry = get_default_registry(llm=llm, include_executor=include_executor)

    analyst = registry.get_or_create("schema_analyst", llm=llm)
    architect = registry.get_or_create("sql_architect", llm=llm)
    validator = registry.get_or_create("validator", llm=llm)

    workflow = StateGraph(AgentState)

    workflow.add_node("analyst", analyst.run)
    workflow.add_node("architect", architect.run)
    workflow.add_node("validator", validator.run)

    workflow.set_entry_point("analyst")
    workflow.add_edge("analyst", "architect")
    workflow.add_edge("architect", "validator")

    def router(state: AgentState):
        if state.get("error") and state.get("retry_count", 0) < 3:
            return "retry"
        if include_executor and not state.get("error"):
            return "execute"
        return "end"

    if include_executor:
        executor = registry.get_or_create("executor", llm=llm)
        workflow.add_node("executor", executor.run)
        workflow.add_edge("executor", END)
        validator_edges = {"retry": "architect", "execute": "executor", "end": END}
    else:
        validator_edges = {"retry": "architect", "execute": END, "end": END}

    workflow.add_conditional_edges("validator", router, validator_edges)

    return workflow.compile()


app = build_nlq_to_sql_graph(include_executor=False)

if __name__ == "__main__":
    print(app.get_graph().draw_ascii())
