import re

def clean_llm_response(raw: str) -> str:
    """
    Limpia la respuesta del LLM antes de parsear JSON.
    Elimina:
      - Bloques <think>...</think> de Qwen3.6 (por si enable_thinking falla)
      - Texto conversacional y markdown alrededor del JSON
      - Backticks de markdown (```json ... ```)
    """
    # Eliminar bloques <think> completos
    cleaned = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL)
    # Eliminar bloques <think> sin cerrar (por si se cortó)
    cleaned = re.sub(r'<think>.*$', '', cleaned, flags=re.DOTALL)

    cleaned = cleaned.strip()

    # Intentar extraer el bloque JSON buscando la primera '{' o '[' y la última '}' o ']'
    first_brace = cleaned.find('{')
    first_bracket = cleaned.find('[')
    
    start_idx = -1
    end_char = ''
    if first_brace != -1 and (first_bracket == -1 or first_brace < first_bracket):
        start_idx = first_brace
        end_char = '}'
    elif first_bracket != -1:
        start_idx = first_bracket
        end_char = ']'
        
    if start_idx != -1:
        end_idx = cleaned.rfind(end_char)
        if end_idx != -1 and end_idx > start_idx:
            # Extraer y devolver directamente el bloque JSON extraído
            return cleaned[start_idx:end_idx + 1].strip()

    # Fallback si no se encuentran llaves/corchetes, usar lógica original de backticks
    if cleaned.startswith("```"):
        lines = cleaned.split('\n')
        lines = lines[1:] if lines[0].startswith('```') else lines
        lines = lines[:-1] if lines and lines[-1].strip() == '```' else lines
        cleaned = '\n'.join(lines)

    return cleaned.strip()
