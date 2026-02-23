"""Agent registry: register and resolve agents by name for the orchestrator."""
from typing import Dict, Type, Optional

from agents.base import BaseAgent
from agents.schema_analyst import SchemaAnalystAgent
from agents.sql_architect import SQLArchitectAgent
from agents.validator import ValidatorAgent
from agents.executor import ExecutorAgent


class AgentRegistry:
    """Registry of agents by name. Used by the multi-agent graph to add nodes."""

    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}
        self._classes: Dict[str, Type[BaseAgent]] = {
            "schema_analyst": SchemaAnalystAgent,
            "sql_architect": SQLArchitectAgent,
            "validator": ValidatorAgent,
            "executor": ExecutorAgent,
        }

    def register(self, name: str, agent: BaseAgent) -> None:
        self._agents[name] = agent

    def register_class(self, name: str, cls: Type[BaseAgent], **kwargs) -> BaseAgent:
        instance = cls(**kwargs)
        self._agents[name] = instance
        return instance

    def get(self, name: str) -> Optional[BaseAgent]:
        return self._agents.get(name)

    def get_or_create(self, name: str, llm=None, **kwargs) -> BaseAgent:
        if name in self._agents:
            return self._agents[name]
        if name in self._classes:
            agent = self._classes[name](llm=llm, **kwargs)
            self._agents[name] = agent
            return agent
        raise KeyError(f"Unknown agent: {name}")

    def list_names(self):
        return list(self._agents.keys()) or list(self._classes.keys())

    def build_default(self, llm=None) -> "AgentRegistry":
        """Build default pipeline agents (analyst, architect, validator). Optionally executor."""
        for name in ["schema_analyst", "sql_architect", "validator"]:
            self.get_or_create(name, llm=llm)
        return self


def get_default_registry(llm=None, include_executor: bool = False) -> AgentRegistry:
    """Return a registry with default pipeline agents. Set include_executor=True to add executor node."""
    reg = AgentRegistry().build_default(llm=llm)
    if include_executor:
        reg.get_or_create("executor", llm=llm)
    return reg
