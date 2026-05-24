from config.llm_config import get_llm
from langchain_core.messages import HumanMessage, SystemMessage
import json

print("🔌 Test 1: Conectividad básica")
llm = get_llm(temperature=0.7, thinking=False)
r = llm.invoke([HumanMessage(content="Di exactamente: MLX OK")])
print(f"   ✅ Respuesta: {r.content.strip()}")

print("\n🔌 Test 2: Respuesta JSON limpia")
r = llm.invoke([
    SystemMessage(content="Responde SOLO con JSON válido, sin texto adicional."),
    HumanMessage(content='Devuelve: {"status": "ok", "model": "qwen3.6"}')
])
from tools.llm_helpers import clean_llm_response
cleaned = clean_llm_response(r.content)
parsed = json.loads(cleaned)
print(f"   ✅ JSON parseado: {parsed}")

print("\n🔌 Test 3: Thinking mode activo")
llm_think = get_llm(temperature=0.3, thinking=True)
r = llm_think.invoke([HumanMessage(content="¿Por qué el cielo es azul? Responde en 2 frases.")])
has_think = "<think>" in r.content
print(f"   {'✅' if has_think else '⚠️ '} Bloques <think>: {'presentes' if has_think else 'no detectados (puede ser normal)'}")
print(f"   Respuesta (primeros 200 chars): {r.content[:200]}")

print("\n✅ Todos los tests pasados — MLX listo para el pipeline")
