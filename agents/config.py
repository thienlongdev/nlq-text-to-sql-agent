"""Shared LLM and config for agents."""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


def get_llm(temperature: float = 0, **kwargs):
    """Create the default LLM used by all agents. Override with kwargs if needed."""
    return ChatOpenAI(
        model=kwargs.get("model") or "openai-gpt-oss-120b",
        temperature=kwargs.get("temperature", temperature),
        api_key=os.getenv("MEGA_API_KEY"),
        base_url=os.getenv("MEGA_URL"),
        **{k: v for k, v in kwargs.items() if k not in ("model", "temperature")}
    )
