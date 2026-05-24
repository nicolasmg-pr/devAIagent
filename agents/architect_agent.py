"""Architect Agent – Senior Software Architect that analyzes PM output
and proposes a modern, scalable architecture with justifications."""

from __future__ import annotations

import json
import re
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
from config.llm_config import llm_architect
from tools.llm_helpers import clean_llm_response

from agents.pm_agent import PMOutput


# ── Pydantic output models ──────────────────────────────────────────────────

class TechStack(BaseModel):
    frontend: str = Field(..., description="Frontend technology")
    backend: str = Field(..., description="Backend technology")
    database: str = Field(..., description="Database technology")
    infrastructure: str = Field(..., description="Infrastructure / deployment")
    additional_tools: list[str] = Field(
        ..., description="Additional tools and libraries"
    )


class APIEndpoint(BaseModel):
    method: str = Field(..., description="HTTP method: GET, POST, PUT, DELETE")
    path: str = Field(..., description="Endpoint path, e.g. /api/v1/users")
    description: str = Field(..., description="What this endpoint does")
    request_body: Optional[str] = Field(
        default=None, description="Request body schema description"
    )
    response: str = Field(..., description="Response schema description")


class DatabaseEntity(BaseModel):
    name: str = Field(..., description="Entity / table name")
    fields: list[str] = Field(..., description="List of field definitions")
    relationships: list[str] = Field(..., description="Relationships to other entities")


class ArchitectOutput(BaseModel):
    project_name: str = Field(..., description="Project name")
    architecture_pattern: str = Field(
        ...,
        description='Architecture pattern, e.g. "Clean Architecture", "MVC", "Microservices"',
    )
    tech_stack: TechStack = Field(..., description="Chosen technology stack")
    api_endpoints: list[APIEndpoint] = Field(..., description="API endpoint definitions")
    database_entities: list[DatabaseEntity] = Field(
        ..., description="Database entity definitions"
    )
    mermaid_diagram: str = Field(
        ..., description="Architecture diagram in valid Mermaid syntax"
    )
    key_decisions: list[str] = Field(
        ..., description="Key architectural decisions with justifications"
    )
    context7_enriched: bool = Field(
        default=False, description="Whether decisions were enriched with Context7"
    )


# ── System prompt ────────────────────────────────────────────────────────────

ARCHITECT_SYSTEM_PROMPT = """\
Eres un Arquitecto de Software Senior con más de 15 años de experiencia \
en diseño de sistemas móviles y backend.

Tu tarea es recibir un documento de proyecto con historias de usuario (generado \
por un Product Manager) y proponer una arquitectura de software moderna, \
escalable y bien justificada.

REGLAS ESTRICTAS:
1. Responde ÚNICAMENTE con un JSON válido. NO incluyas texto explicativo, \
comentarios, ni bloques markdown (```).
2. El JSON debe seguir EXACTAMENTE este esquema:

{{
  "project_name": "string",
  "architecture_pattern": "string (ej: Clean Architecture, MVC, Microservices)",
  "tech_stack": {{
    "frontend": "string",
    "backend": "string",
    "database": "string",
    "infrastructure": "string",
    "additional_tools": ["string"]
  }},
  "api_endpoints": [
    {{
      "method": "GET | POST | PUT | DELETE",
      "path": "/api/v1/resource",
      "description": "string",
      "request_body": "string o null",
      "response": "string"
    }}
  ],
  "database_entities": [
    {{
      "name": "string",
      "fields": ["id: UUID PK", "name: VARCHAR(100)"],
      "relationships": ["hasMany: OtherEntity"]
    }}
  ],
  "mermaid_diagram": "graph TD\\n  A[Client] --> B[API Gateway]\\n  ...",
  "key_decisions": [
    "Decisión: justificación detallada"
  ]
}}

3. Diseña entre 6 y 15 endpoints API coherentes con las historias de usuario.
4. Define entre 3 y 8 entidades de base de datos con campos y relaciones.
5. El diagrama Mermaid debe ser sintaxis válida y representar la arquitectura propuesta.
6. Incluye entre 3 y 6 decisiones arquitectónicas importantes con su justificación.
7. Elige tecnologías modernas y justifica cada elección.
8. NO uses backticks, NO uses markdown, SOLO JSON puro.
"""


# ── Retry prompt ─────────────────────────────────────────────────────────────

ARCHITECT_RETRY_PROMPT = """\
Tu respuesta anterior NO fue un JSON válido. El error fue:
{error}

DEBES responder con JSON puro y válido. Sin texto extra, sin backticks, \
sin explicaciones. Solo el objeto JSON que cumpla el esquema indicado.
Asegúrate de:
- Escapar comillas internas con \"
- Usar \\n para saltos de línea dentro de strings (especialmente en mermaid_diagram)
- No dejar comas al final de arrays u objetos
- Cerrar todas las llaves y corchetes correctamente

Vuelve a generar la respuesta completa:
"""


# ── Public API ───────────────────────────────────────────────────────────────

def _clean_response(text: str) -> str:
    """Strip markdown code fences and surrounding whitespace."""
    cleaned = re.sub(r"```(?:json)?\s*", "", text)
    cleaned = re.sub(r"```", "", cleaned)
    return cleaned.strip()


def _fix_json(text: str) -> str:
    """Fix common LLM JSON errors: trailing commas before ] or }."""
    fixed = re.sub(r",\s*([}\]])", r"\1", text)
    return fixed

import asyncio
import threading
import queue
import json_repair

async def enrich_with_context7(tech_stack: TechStack) -> dict:
    """Connect to Context7 MCP and retrieve best practices for the tech stack."""
    from agents.mcp_client import get_mcp_tools, CONTEXT7_MCP_CONFIG
    
    tools = get_mcp_tools(CONTEXT7_MCP_CONFIG, "stdio")
    if not tools:
        print("⚠️ [Context7] No se pudieron cargar las herramientas de Context7. Fallback.")
        return {}
        
    tool_map = {t.name: t for t in tools}
    docs_found = {}
    
    technologies = {
        "frontend": tech_stack.frontend,
        "backend": tech_stack.backend,
        "database": tech_stack.database
    }
    
    for key, tech_name in technologies.items():
        if not tech_name or tech_name.lower() in ["none", "null", "n/a", "no"]:
            continue
            
        print(f"🔍 [Context7] Buscando ID para librería: {tech_name}")
        try:
            resolved_id = None
            if "resolve-library-id" in tool_map:
                res = tool_map["resolve-library-id"].invoke({"query": tech_name})
                import re
                match = re.search(r"(/[a-zA-Z0-9_\-\.]+/[a-zA-Z0-9_\-\.]+)", res)
                if match:
                    resolved_id = match.group(1)
                    print(f"🔍 [Context7] ID resuelto para {tech_name}: {resolved_id}")
            
            if not resolved_id:
                tech_lower = tech_name.lower()
                if "nest" in tech_lower:
                    resolved_id = "/nestjs/nest"
                elif "flutter" in tech_lower:
                    resolved_id = "/flutter/flutter"
                elif "postgres" in tech_lower:
                    resolved_id = "/postgres/postgres"
                else:
                    resolved_id = f"/{tech_lower}/{tech_lower}"
            
            doc_content = ""
            if "query-docs" in tool_map:
                doc_content = tool_map["query-docs"].invoke({
                    "libraryId": resolved_id,
                    "query": "best practices"
                })
            elif "get-library-docs" in tool_map:
                doc_content = tool_map["get-library-docs"].invoke({
                    "libraryId": resolved_id,
                    "topic": "best practices"
                })
            
            if doc_content:
                docs_found[tech_name] = doc_content
                print(f"✅ [Context7] Prácticas obtenidas para {tech_name}")
        except Exception as e:
            print(f"⚠️ [Context7] Error buscando documentación para {tech_name}: {e}")
            
    return docs_found


def _run_async_in_thread(coro):
    """Run an async coroutine synchronously in a separate thread to prevent loop conflicts."""
    q = queue.Queue()
    def worker():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            res = loop.run_until_complete(coro)
            q.put((True, res))
        except Exception as e:
            q.put((False, e))
        finally:
            loop.close()
    t = threading.Thread(target=worker, daemon=True)
    t.start()
    t.join()
    success, val = q.get()
    if success:
        return val
    raise val


def refine_architecture_with_docs(arch_output: ArchitectOutput, context7_docs: dict) -> ArchitectOutput:
    """Refine key decisions using documentation from Context7."""
    llm = llm_architect
    
    context7_enriched = False
    if context7_docs:
        context7_enriched = True
        docs_str = json.dumps(context7_docs, indent=2, ensure_ascii=False)
        print("💡 [Architect] Refinando decisiones con mejores prácticas de Context7...")
        refine_prompt = (
            f"Revisa estas decisiones arquitectónicas a la luz de las mejores prácticas "
            f"actuales documentadas:\n{docs_str}\n\n"
            f"Decisiones actuales: {json.dumps(arch_output.key_decisions, indent=2, ensure_ascii=False)}\n\n"
            "¿Hay algo que cambiarías? Devuelve ÚNICAMENTE un objeto JSON que actualice la lista de key_decisions "
            "con los nuevos insights. Formato:\n"
            "{\n"
            "  \"key_decisions\": [\n"
            "    \"Decisión: justificación detallada\"\n"
            "  ]\n"
            "}"
        )
        try:
            refine_res = llm.invoke([
                SystemMessage(content="Eres un Arquitecto de Software Senior. Responde estrictamente con JSON."),
                HumanMessage(content=refine_prompt)
            ])
            refine_cleaned = clean_llm_response(refine_res.content)
            refine_data = json_repair.loads(refine_cleaned)
            if "key_decisions" in refine_data and isinstance(refine_data["key_decisions"], list):
                arch_output.key_decisions = refine_data["key_decisions"]
                print("✅ [Architect] Decisiones actualizadas con éxito.")
        except Exception as refine_err:
            print(f"⚠️ [Architect] Error refinando decisiones con Context7: {refine_err}")

    arch_output.context7_enriched = context7_enriched
    return arch_output


def run_architect_agent(pm_output: PMOutput) -> ArchitectOutput:
    """Send the PM output to the Architect LLM and parse its JSON response."""
    llm = llm_architect

    pm_json = pm_output.model_dump_json(indent=2)
    
    # 1. Normal architect analysis
    messages = [
        SystemMessage(content=ARCHITECT_SYSTEM_PROMPT),
        HumanMessage(
            content=(
                "Analiza el siguiente documento de proyecto generado por el PM "
                "y propón una arquitectura de software completa:\n\n"
                f"{pm_json}"
            )
        ),
    ]
    
    print("🏗️  Architect Agent generando arquitectura inicial...")
    response = llm.invoke(messages)
    cleaned = clean_llm_response(response.content)
    cleaned = _fix_json(cleaned)

    try:
        data = json_repair.loads(cleaned)
        return ArchitectOutput.model_validate(data)
    except Exception as exc:
        print(f"   ⚠️ Falló parseo de arquitectura: {exc}. Reintentando con prompt directo...")
        messages = messages + [
            HumanMessage(content=ARCHITECT_RETRY_PROMPT.format(error=str(exc)))
        ]
        retry_res = llm.invoke(messages)
        cleaned_retry = clean_llm_response(retry_res.content)
        cleaned_retry = _fix_json(cleaned_retry)
        data = json_repair.loads(cleaned_retry)
        return ArchitectOutput.model_validate(data)
