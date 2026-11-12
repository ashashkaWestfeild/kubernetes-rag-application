from langchain_openai import ChatOpenAI

from app.config import settings


def get_langchain_llm(alias: str = "rag-llm") -> ChatOpenAI:
    """
    Returns a gateway-backed ChatOpenAI - a drop-in for ChatGroq in the LangGraph nodes.

    Why ChatOpenAI and not ChatGroq:
      The LiteLLM proxy exposes an OpenAI-compatible endpoint (LLM_GATEWAY_URL).
      ChatGroq is hardwired to Groq's API and cannot be pointed at a proxy;
      ChatOpenAI accepts a base_url, so every call goes through the gateway.

    Why an alias, not a model name:
      'rag-llm', 'guard-llm' and 'judge-llm' are defined in litellm_config.yaml,
      which maps each alias to a real model and owns retries, fallback and caching.
      Swapping a model or provider is then a config change, not a code change.
    """
    return ChatOpenAI(
        base_url=settings.LLM_GATEWAY_URL,
        api_key=settings.LLM_GATEWAY_KEY,
        model=alias,
        temperature=0,
    )