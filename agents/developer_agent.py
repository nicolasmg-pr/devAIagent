"""Developer Agent – Backend and Frontend sub-agents that generate
real, functional code based on the Architect's output."""

from __future__ import annotations

import json
import re
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
from config.llm_config import llm_developer
from tools.llm_helpers import clean_llm_response

from agents.architect_agent import ArchitectOutput
from typing import Optional, Any


# ── Pydantic output models ──────────────────────────────────────────────────

class CodeFile(BaseModel):
    filename: str = Field(..., description="File name, e.g. app.module.ts")
    path: str = Field(..., description="Relative path, e.g. src/modules/expense")
    language: str = Field(..., description="Programming language, e.g. typescript, dart")
    content: str = Field(..., description="Full source code content of the file")
    description: str = Field(..., description="Brief description of the file's purpose")


class BackendOutput(BaseModel):
    files: list[CodeFile] = Field(..., description="Generated backend files")
    setup_commands: list[str] = Field(
        ..., description="Commands to set up and run the backend"
    )
    dependencies: list[str] = Field(
        ..., description="Required packages / dependencies"
    )


class FrontendOutput(BaseModel):
    files: list[CodeFile] = Field(..., description="Generated frontend files")
    setup_commands: list[str] = Field(
        ..., description="Commands to set up and run the frontend"
    )
    dependencies: list[str] = Field(
        ..., description="Required packages / dependencies"
    )


class DeveloperOutput(BaseModel):
    project_name: str = Field(..., description="Project name")
    backend: BackendOutput = Field(..., description="Backend output")
    frontend: FrontendOutput = Field(..., description="Frontend output")
    integration_notes: list[str] = Field(
        ..., description="Notes on how to connect frontend and backend"
    )


# ── System prompts ───────────────────────────────────────────────────────────

BACKEND_SYSTEM_PROMPT = """\
Eres un Desarrollador Backend Senior con más de 10 años de experiencia, \
especialista en NestJS, TypeScript y Clean Architecture.

Tu tarea es recibir un documento de arquitectura de software y generar \
código real, funcional y completo para el backend del proyecto.

PRIORIDADES:
- Estructura de carpetas correcta siguiendo Clean Architecture
- Entidades TypeORM con decoradores y tipos correctos
- DTOs de creación con validación usando class-validator
- Servicios con lógica de negocio CRUD completa
- Controladores REST con decoradores NestJS correctos
- Module principal que importa todos los módulos

REGLAS ESTRICTAS:
1. Responde ÚNICAMENTE con un JSON válido. NO incluyas texto explicativo, \
comentarios, ni bloques markdown (```).
2. El JSON debe seguir EXACTAMENTE este esquema:

{{
  "files": [
    {{
      "filename": "app.module.ts",
      "path": "src",
      "language": "typescript",
      "content": "import {{ Module }} from '@nestjs/common';\\n...",
      "description": "Root application module"
    }}
  ],
  "setup_commands": [
    "npm install",
    "npm run start:dev"
  ],
  "dependencies": [
    "@nestjs/core",
    "@nestjs/typeorm",
    "class-validator"
  ]
}}

3. Genera código TypeScript real y funcional, no placeholders.
4. Incluye al menos: app.module.ts, una entidad por cada entidad de la BD, \
un DTO de creación por entidad, un servicio con CRUD básico, y un controlador \
con los endpoints principales.
5. Escapa correctamente las comillas y saltos de línea dentro del campo "content".
6. NO uses backticks, NO uses markdown, SOLO JSON puro.
"""

FRONTEND_SYSTEM_PROMPT = """\
Eres un Desarrollador Frontend Senior con más de 10 años de experiencia, \
especialista en Flutter, Dart y Clean Architecture.

Tu tarea es recibir un documento de arquitectura de software y generar \
código real, funcional y completo para el frontend móvil del proyecto.

PRIORIDADES:
- Estructura de features siguiendo Clean Architecture
- Modelos de datos Dart que mapean las entidades del backend
- Repositorios con llamadas HTTP al backend usando http o dio
- Páginas principales con widgets Material Design funcionales
- Navegación entre pantallas

REGLAS ESTRICTAS:
1. Responde ÚNICAMENTE con un JSON válido. NO incluyas texto explicativo, \
comentarios, ni bloques markdown (```).
2. El JSON debe seguir EXACTAMENTE este esquema:

{{
  "files": [
    {{
      "filename": "main.dart",
      "path": "lib",
      "language": "dart",
      "content": "import 'package:flutter/material.dart';\\n...",
      "description": "Application entry point"
    }}
  ],
  "setup_commands": [
    "flutter pub get",
    "flutter run"
  ],
  "dependencies": [
    "flutter",
    "http",
    "provider"
  ]
}}

3. Genera código Dart real y funcional, no placeholders.
4. Incluye al menos: main.dart, un modelo por cada entidad principal, \
un repositorio con llamadas HTTP, y una página por cada historia de usuario \
de alta prioridad.
5. Escapa correctamente las comillas y saltos de línea dentro del campo "content".
6. NO uses backticks, NO uses markdown, SOLO JSON puro.
"""

RETRY_PROMPT = """\
Tu respuesta anterior NO fue un JSON válido. El error fue:
{error}

DEBES responder con JSON puro y válido. Sin texto extra, sin backticks, \
sin explicaciones. Solo el objeto JSON que cumpla el esquema indicado.
Asegúrate de:
- Escapar comillas internas con \\\"
- Usar \\n para saltos de línea dentro de strings
- No dejar comas al final de arrays u objetos
- Cerrar todas las llaves y corchetes correctamente

Vuelve a generar la respuesta completa:
"""


# ── Helpers ──────────────────────────────────────────────────────────────────

def _clean_response(text: str) -> str:
    """Strip markdown code fences and surrounding whitespace."""
    cleaned = re.sub(r"```(?:json)?\s*", "", text)
    cleaned = re.sub(r"```", "", cleaned)
    return cleaned.strip()


def _fix_json(text: str) -> str:
    """Fix common LLM JSON errors: trailing commas before ] or }."""
    fixed = re.sub(r",\s*([}\]])", r"\1", text)
    return fixed


def _parse_json_robust(text: str) -> dict:
    """Parse JSON with fallback to json_repair for malformed LLM output."""
    from json_repair import loads as repair_loads

    try:
        return json.loads(text, strict=False)
    except json.JSONDecodeError:
        return repair_loads(text)


def _invoke_with_retry(llm: Any, messages: list, model_class: type, max_retries: int = 2):
    """Invoke the LLM, parse JSON, and retry with a stricter prompt on failure."""
    last_error = None
    for attempt in range(1 + max_retries):
        response = llm.invoke(messages)
        raw_text: str = response.content  # type: ignore[assignment]
        cleaned = clean_llm_response(raw_text)

        try:
            data = _parse_json_robust(cleaned)
            return model_class.model_validate(data)
        except Exception as exc:
            last_error = exc
            print(f"   ⚠️  Intento {attempt + 1} falló: {exc}")
            if attempt < max_retries:
                print(f"   🔄 Reintentando con prompt más estricto...")
                messages = messages + [
                    HumanMessage(content=RETRY_PROMPT.format(error=str(exc)))
                ]

    raise last_error  # type: ignore[misc]


# ── Public API ───────────────────────────────────────────────────────────────

import os
from langgraph.prebuilt import create_react_agent
from agents.mcp_client import ThreadSafeMCPClient
import json_repair

from agents.ui_designer_agent import UIDesignerOutput
import asyncio
import threading
import queue

def _write_generated_files(files: list[CodeFile]):
    """Auto-save generated code files to the project directory."""
    base_dir = "/Users/nikomendez/Documents/SWdevAIgency_project"
    for f in files:
        target_dir = os.path.join(base_dir, f.path)
        os.makedirs(target_dir, exist_ok=True)
        file_path = os.path.join(target_dir, f.filename)
        print(f"💾 Guardando archivo: {file_path}")
        with open(file_path, "w", encoding="utf-8") as out:
            out.write(f.content)


async def save_files_to_filesystem(developer_output: DeveloperOutput):
    """Save backend and frontend generated files to the filesystem using MCP or fallback to python."""
    from agents.mcp_client import get_mcp_tools, FILESYSTEM_MCP_CONFIG
    
    # 1. Connect to Filesystem MCP
    tools = get_mcp_tools(FILESYSTEM_MCP_CONFIG, "stdio")
    tool_map = {t.name: t for t in tools} if tools else {}
    
    output_dir = "./output"
    os.makedirs(output_dir, exist_ok=True)
    
    all_files = []
    if developer_output.backend and developer_output.backend.files:
        all_files.extend(developer_output.backend.files)
    if developer_output.frontend and developer_output.frontend.files:
        all_files.extend(developer_output.frontend.files)
        
    mcp_available = "write_file" in tool_map
    
    for f in all_files:
        rel_path = os.path.join(f.path, f.filename)
        
        if mcp_available:
            try:
                full_path = os.path.join("/Users/nikomendez/Documents/SWdevAIgency_project", rel_path)
                parent_dir = os.path.dirname(full_path)
                os.makedirs(parent_dir, exist_ok=True)
                
                print(f"🚀 [Filesystem MCP] Guardando archivo: {rel_path}...")
                tool_map["write_file"].invoke({
                    "path": full_path,
                    "content": f.content
                })
                print(f"📄 Guardado: {f.path}/{f.filename}")
                continue
            except Exception as e:
                print(f"⚠️ [Filesystem MCP] Error escribiendo {rel_path} vía MCP: {e}. Usando fallback local...")
        
        # Fallback to python
        try:
            fallback_full_path = os.path.join(output_dir, rel_path)
            parent_dir = os.path.dirname(fallback_full_path)
            os.makedirs(parent_dir, exist_ok=True)
            with open(fallback_full_path, "w", encoding="utf-8") as out_f:
                out_f.write(f.content)
            print(f"📄 Guardado (Local Fallback): {f.path}/{f.filename}")
        except Exception as e:
            print(f"❌ Error escribiendo archivo local de fallback: {e}")


def run_backend_agent(architect_output: ArchitectOutput, designer_output: Optional[UIDesignerOutput] = None) -> BackendOutput:
    """Generate backend code from the architect's output and write files to disk."""
    
    # Connect Context7 and Filesystem
    context7_client = ThreadSafeMCPClient("npx", ["-y", "@upstash/context7-mcp@latest"])
    filesystem_client = ThreadSafeMCPClient("npx", ["-y", "@modelcontextprotocol/server-filesystem", "/Users/nikomendez/Documents/SWdevAIgency_project"])
    
    tools = context7_client.get_tools() + filesystem_client.get_tools()
    
    llm = llm_developer

    agent = create_react_agent(llm, tools=tools)
    arch_json = architect_output.model_dump_json(indent=2)
    
    prompt = (
        f"{BACKEND_SYSTEM_PROMPT}\n\n"
        "Genera el código backend completo basado en esta arquitectura. "
        "Si necesitas consultar documentación sobre NestJS, TypeORM, Postgres, etc., usa Context7. "
        "Adicionalmente, puedes usar las herramientas de Filesystem para verificar archivos si lo necesitas. "
        "IMPORTANTE: NO busques, listes ni leas archivos en directorios ajenos al backend de este proyecto actual, "
        "especialmente NUNCA entres en carpetas como 'gestor_gastos' o 'fintrack_app'. "
        "Solo opera dentro del contexto de desarrollo de este proyecto actual.\n\n"
        f"{arch_json}"
    )

    print("☕  Backend Developer Agent consultando herramientas y escribiendo backend...")
    response = agent.invoke({"messages": [HumanMessage(content=prompt)]}, config={"recursion_limit": 10})
    
    final_message = response["messages"][-1].content
    cleaned = clean_llm_response(final_message)
    cleaned = _fix_json(cleaned)

    try:
        data = json_repair.loads(cleaned)
        return BackendOutput.model_validate(data)
    except Exception as exc:
        print(f"   ⚠️ Falló parseo de backend: {exc}. Reintentando con prompt directo...")
        messages = [
            SystemMessage(content=BACKEND_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
            HumanMessage(content=RETRY_PROMPT.format(error=str(exc)))
        ]
        retry_res = llm.invoke(messages)
        cleaned_retry = clean_llm_response(retry_res.content)
        cleaned_retry = _fix_json(cleaned_retry)
        data = json_repair.loads(cleaned_retry)
        return BackendOutput.model_validate(data)


def run_frontend_agent(architect_output: ArchitectOutput, designer_output: Optional[UIDesignerOutput] = None) -> FrontendOutput:
    """Generate frontend code from the architect's output and write files to disk."""
    
    # Connect Context7 and Filesystem
    context7_client = ThreadSafeMCPClient("npx", ["-y", "@upstash/context7-mcp@latest"])
    filesystem_client = ThreadSafeMCPClient("npx", ["-y", "@modelcontextprotocol/server-filesystem", "/Users/nikomendez/Documents/SWdevAIgency_project"])
    
    tools = context7_client.get_tools() + filesystem_client.get_tools()
    
    llm = llm_developer

    agent = create_react_agent(llm, tools=tools)
    
    arch_json = architect_output.model_dump_json(indent=2)
    
    # Format DESIGN.md and screen references
    ui_context = ""
    system_prompt = FRONTEND_SYSTEM_PROMPT
    if designer_output:
        system_prompt += "\nImplementa las pantallas siguiendo fielmente el sistema de diseño del DESIGN.md adjunto. Los colores, tipografía y espaciados deben coincidir exactamente con los tokens definidos."
        ui_context += "# DESIGN.md\n"
        ui_context += f"{designer_output.design_system_notes}\n\n"
        ui_context += "## SCREENS AND VIEWS REFERENCE:\n"
        for scr in designer_output.screens:
            ui_context += f"### Screen: {scr.name}\n"
            ui_context += f"Description: {scr.description}\n"
            if getattr(scr, 'stitch_screen_url', None):
                ui_context += f"Stitch URL: {scr.stitch_screen_url}\n"
            if getattr(scr, 'html_content', None):
                html_snippet = scr.html_content
                if len(html_snippet) > 800:
                    html_snippet = html_snippet[:800] + "\n... [TRUNCATED FOR CONTEXT WINDOW] ..."
                ui_context += f"HTML Reference (Truncated):\n```html\n{html_snippet}\n```\n"
            ui_context += "\n"
    else:
        ui_context = "No hay diseño UI provisto."
        
    prompt = (
        f"Genera el código frontend Flutter completo basado en esta arquitectura y en el diseño de pantallas (Google Stitch) provisto. "
        "Si necesitas consultar documentación sobre Flutter, Widgets, http, etc., usa Context7. "
        "Adicionalmente, puedes usar las herramientas de Filesystem para verificar archivos si lo necesitas. "
        "IMPORTANTE: NO busques, listes ni leas archivos en directorios ajenos al frontend de este proyecto actual, "
        "especialmente NUNCA entres en carpetas como 'gestor_gastos' o 'fintrack_app'. "
        "Solo opera dentro del contexto de desarrollo de este proyecto actual.\n\n"
        f"ARQUITECTURA:\n{arch_json}\n\n"
        f"DISEÑO Y PANTALLAS DE INTERFAZ:\n{ui_context}"
    )

    print("📱  Frontend Developer Agent consultando herramientas y escribiendo frontend...")
    response = agent.invoke({"messages": [HumanMessage(content=prompt)]}, config={"recursion_limit": 10})
    
    final_message = response["messages"][-1].content
    cleaned = clean_llm_response(final_message)
    cleaned = _fix_json(cleaned)

    try:
        data = json_repair.loads(cleaned)
        return FrontendOutput.model_validate(data)
    except Exception as exc:
        print(f"   ⚠️ Falló parseo de frontend: {exc}. Reintentando con prompt directo...")
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt),
            HumanMessage(content=RETRY_PROMPT.format(error=str(exc)))
        ]
        retry_res = llm.invoke(messages)
        cleaned_retry = clean_llm_response(retry_res.content)
        cleaned_retry = _fix_json(cleaned_retry)
        data = json_repair.loads(cleaned_retry)
        return FrontendOutput.model_validate(data)
