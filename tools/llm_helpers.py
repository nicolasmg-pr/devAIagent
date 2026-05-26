import re

def clean_llm_response(raw: str) -> str:
    """
    Cleans the LLM response before parsing JSON.
    Removes:
      - <think>...</think> blocks from Qwen3.6 (in case enable_thinking fails)
      - Conversational text and markdown surrounding the JSON
      - Markdown backticks (```json ... ```)
    """
    # Remove complete <think> blocks
    cleaned = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL)
    # Remove unclosed <think> blocks (in case it was cut off)
    cleaned = re.sub(r'<think>.*$', '', cleaned, flags=re.DOTALL)

    cleaned = cleaned.strip()

    # Try to extract the JSON block by searching for the first '{' or '[' and the last '}' or ']'
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
            # Extract and return the extracted JSON block directly
            return cleaned[start_idx:end_idx + 1].strip()

    # Fallback if no braces/brackets are found, use original backticks logic
    if cleaned.startswith("```"):
        lines = cleaned.split('\n')
        lines = lines[1:] if lines[0].startswith('```') else lines
        lines = lines[:-1] if lines and lines[-1].strip() == '```' else lines
        cleaned = '\n'.join(lines)

    return cleaned.strip()
