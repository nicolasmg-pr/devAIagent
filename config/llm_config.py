"""
Configuración centralizada del LLM para todo el proyecto.
Cambiar de motor local solo requiere editar este archivo.
"""

from langchain_openai import ChatOpenAI

# --- Configuración base MLX ---
MLX_BASE_URL = "http://localhost:8000/v1"
MLX_MODEL = "Qwen3.6-35B-A3B-UD-MLX-4bit"
MLX_API_KEY = "EMPTY"  # MLX no requiere autenticación

def get_llm(
    temperature: float = 0.7,
    thinking: bool = False,
    max_tokens: int = 8192,
) -> ChatOpenAI:
    """
    Devuelve el LLM configurado para MLX local.

    Args:
        temperature: 0.0-1.0. Usar 0.3 para tareas precisas (QA, Reviewer),
                     0.7 para generación (Developer, Designer),
                     1.0 para creatividad (PM, Architect)
        thinking: Si True, activa el modo de razonamiento de Qwen3.6
                  (genera bloques <think>). Solo para Code Reviewer.
                  Si False, respuesta directa sin chain-of-thought visible.
        max_tokens: Límite de tokens en la respuesta.
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

# --- Instancias preconfiguradas para cada agente ---
# Usamos __getattr__ para devolver una nueva instancia en cada acceso,
# lo que previene errores de concurrencia de Pydantic en hilos paralelos de LangGraph.

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

