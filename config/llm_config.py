"""
Centralized LLM configuration for the entire project.
Switching the local engine only requires editing this file.
"""

from langchain_openai import ChatOpenAI

# --- Base MLX Configuration ---
MLX_BASE_URL = "http://localhost:8000/v1"
MLX_MODEL = "Qwen3.6-35B-A3B-UD-MLX-4bit"
MLX_API_KEY = "EMPTY"  # MLX does not require authentication

def get_llm(
    temperature: float = 0.7,
    thinking: bool = False,
    max_tokens: int = 8192,
) -> ChatOpenAI:
    """
    Returns the LLM configured for local MLX.

    Args:
        temperature: 0.0-1.0. Use 0.3 for precise tasks (QA, Reviewer),
                     0.7 for generation (Developer, Designer),
                     1.0 for creativity (PM, Architect)
        thinking: If True, activates reasoning mode of Qwen3.6
                  (generates <think> blocks). Only for Code Reviewer.
                  If False, direct response without visible chain-of-thought.
        max_tokens: Token limit in response.
    """
    return ChatOpenAI(
        base_url=MLX_BASE_URL,
        api_key=MLX_API_KEY,
        model=MLX_MODEL,
        temperature=temperature,
        max_tokens=max_tokens,
        extra_body={
            "enable_thinking": thinking,
        }
    )

# --- Preconfigured instances for each agent ---
# We use __getattr__ to return a new instance on each access,
# which prevents concurrency errors from Pydantic in parallel LangGraph threads.

llm_pm: ChatOpenAI
llm_architect: ChatOpenAI
llm_designer: ChatOpenAI
llm_developer: ChatOpenAI
llm_qa: ChatOpenAI
llm_reviewer: ChatOpenAI

def __getattr__(name: str) -> ChatOpenAI:
    if name == "llm_pm":
        return get_llm(temperature=1.0, thinking=False)
    elif name == "llm_architect":
        return get_llm(temperature=1.0, thinking=False)
    elif name == "llm_designer":
        return get_llm(temperature=0.7, thinking=False)
    elif name == "llm_developer":
        return get_llm(temperature=0.7, thinking=False)
    elif name == "llm_qa":
        return get_llm(temperature=0.3, thinking=False)
    elif name == "llm_reviewer":
        return get_llm(temperature=0.3, thinking=True, max_tokens=16384)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

