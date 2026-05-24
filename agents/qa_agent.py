"""QA Agent – Test generator and code reviewer that work in parallel
to produce test cases, test files, and code quality analysis."""

from __future__ import annotations

import json
import re
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
from config.llm_config import llm_qa
from tools.llm_helpers import clean_llm_response

from agents.pm_agent import PMOutput
from agents.developer_agent import DeveloperOutput


# ── Pydantic output models ──────────────────────────────────────────────────

class TestCase(BaseModel):
    id: str = Field(..., description="Unique ID: TC-001, TC-002...")
    user_story_id: str = Field(..., description="Reference to PM user story: US-001...")
    title: str = Field(..., description="Short descriptive title")
    test_type: str = Field(
        ..., description='Type of test: "unit", "integration", or "e2e"'
    )
    preconditions: list[str] = Field(..., description="Preconditions for the test")
    steps: list[str] = Field(..., description="Steps to execute the test")
    expected_result: str = Field(..., description="Expected outcome")
    priority: str = Field(
        ..., description='Priority: "critical", "high", "medium", or "low"'
    )


class CodeIssue(BaseModel):
    severity: str = Field(
        ..., description='Severity: "critical", "major", "minor", or "info"'
    )
    file: str = Field(..., description="Affected file path/name")
    description: str = Field(..., description="Description of the issue")
    suggestion: str = Field(..., description="How to fix the issue")
    category: str = Field(
        ...,
        description='Category: "security", "performance", "maintainability", "reliability", or "bug"',
    )


class TestFile(BaseModel):
    filename: str = Field(..., description="Test file name")
    path: str = Field(..., description="Relative path for the test file")
    language: str = Field(..., description="Programming language")
    content: str = Field(..., description="Full test source code")
    description: str = Field(..., description="Brief description of what is tested")


class QAOutput(BaseModel):
    project_name: str = Field(..., description="Project name")
    test_cases: list[TestCase] = Field(..., description="Functional test cases")
    test_files: list[TestFile] = Field(..., description="Generated test code files")
    code_issues: list[CodeIssue] = Field(
        ..., description="Code quality issues found"
    )
    quality_score: int = Field(
        ..., description="Quality score 0-100"
    )
    quality_summary: str = Field(
        ..., description="Executive quality summary"
    )


# ── System prompts ───────────────────────────────────────────────────────────

TEST_GENERATOR_SYSTEM_PROMPT = """\
Eres un QA Engineer Senior con más de 10 años de experiencia en testing de \
aplicaciones móviles y backend, especialista en Jest (NestJS) y Flutter widget tests.

Tu tarea es analizar las historias de usuario del PM y los archivos generados por \
el Developer, y generar:
1. Casos de prueba funcionales exhaustivos (test_cases)
2. Código de tests real y funcional (test_files)

REGLAS PARA TEST CASES:
- Genera al menos 2 TestCase por cada UserStory de prioridad "high", 1 por las demás.
- Cubre: happy path, edge cases y casos de error.
- Tipos válidos: "unit", "integration", "e2e"
- IDs secuenciales: TC-001, TC-002...
- Cada TestCase debe referenciar su user_story_id (US-001...)

REGLAS PARA TEST FILES:
- Genera al menos 3 archivos de test:
  * Un archivo .spec.ts con tests unitarios Jest para el servicio backend más importante
  * Un archivo .spec.ts con tests de integración para los endpoints principales
  * Un archivo _test.dart con widget tests de Flutter
- El código de test debe ser real, funcional y ejecutable.

REGLAS ESTRICTAS DE FORMATO:
1. Responde ÚNICAMENTE con un JSON válido. NO incluyas texto, comentarios ni markdown.
2. El JSON debe seguir EXACTAMENTE este esquema:

{{
  "test_cases": [
    {{
      "id": "TC-001",
      "user_story_id": "US-001",
      "title": "string",
      "test_type": "unit | integration | e2e",
      "preconditions": ["string"],
      "steps": ["string"],
      "expected_result": "string",
      "priority": "critical | high | medium | low"
    }}
  ],
  "test_files": [
    {{
      "filename": "expense.service.spec.ts",
      "path": "test",
      "language": "typescript",
      "content": "import {{ Test }} from '@nestjs/testing';\\n...",
      "description": "Unit tests for ExpenseService"
    }}
  ]
}}

3. Escapa correctamente comillas y saltos de línea dentro de "content".
4. NO uses backticks, NO uses markdown, SOLO JSON puro.
"""

CODE_REVIEWER_SYSTEM_PROMPT = """\
Eres un Code Reviewer Senior con expertise en seguridad, rendimiento y buenas \
prácticas para NestJS (TypeScript) y Flutter (Dart).

Tu tarea es analizar el código generado por el equipo de desarrollo con ojo \
crítico y exhaustivo.

BUSCA ESPECÍFICAMENTE:
- Inyección SQL o NoSQL
- Falta de validación de input
- N+1 queries y problemas de rendimiento en BD
- Memory leaks
- Missing error handling / try-catch
- Hardcoded secrets o API keys
- Violaciones de principios SOLID
- Código duplicado
- Falta de tipos (any, dynamic)
- Falta de sanitización de datos del usuario
- Endpoints sin autenticación/autorización
- Missing null checks

REGLAS PARA QUALITY SCORE:
- Empieza en 100 y resta por cada issue encontrado:
  * critical: -15
  * major: -8
  * minor: -3
  * info: -1
- El score mínimo es 0.

REGLAS ESTRICTAS DE FORMATO:
1. Responde ÚNICAMENTE con un JSON válido. NO incluyas texto, comentarios ni markdown.
2. El JSON debe seguir EXACTAMENTE este esquema:

{{
  "code_issues": [
    {{
      "severity": "critical | major | minor | info",
      "file": "src/modules/expense/expense.service.ts",
      "description": "string describing the issue",
      "suggestion": "string with how to fix it",
      "category": "security | performance | maintainability | reliability | bug"
    }}
  ],
  "quality_score": 72,
  "quality_summary": "string with executive summary"
}}

3. Sé específico: menciona el archivo y la ubicación del problema cuando puedas.
4. NO uses backticks, NO uses markdown, SOLO JSON puro.
"""

RETRY_PROMPT = """\
Tu respuesta anterior NO fue un JSON válido. El error fue:
{error}

DEBES responder con JSON puro y válido. Sin texto extra, sin backticks, \
sin explicaciones. Solo el objeto JSON que cumpla el esquema indicado.
Asegúrate de:
- Escapar comillas internas con \"
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


def _invoke_with_retry(
    llm: Any,
    messages: list,
    parse_fn,
    max_retries: int = 2,
    label: str = "",
):
    """Invoke the LLM, parse JSON with parse_fn, retry on failure."""
    last_error = None
    for attempt in range(1 + max_retries):
        response = llm.invoke(messages)
        raw_text: str = response.content  # type: ignore[assignment]
        cleaned = clean_llm_response(raw_text)
        cleaned = _fix_json(cleaned)

        try:
            data = json.loads(cleaned, strict=False)
            return parse_fn(data)
        except (json.JSONDecodeError, Exception) as exc:
            last_error = exc
            print(f"   ⚠️  [{label}] Intento {attempt + 1} falló: {exc}")
            if attempt < max_retries:
                print(f"   🔄 [{label}] Reintentando con prompt más estricto...")
                messages = messages + [
                    HumanMessage(content=RETRY_PROMPT.format(error=str(exc)))
                ]

    raise last_error  # type: ignore[misc]


def _summarize_dev_files(dev_output: DeveloperOutput, max_content_chars: int = 500) -> str:
    """Serialize developer files with truncated content to fit context window."""
    summary = {"backend_files": [], "frontend_files": []}

    for f in dev_output.backend.files:
        summary["backend_files"].append({
            "filename": f.filename,
            "path": f.path,
            "language": f.language,
            "description": f.description,
            "content": f.content[:max_content_chars] + ("..." if len(f.content) > max_content_chars else ""),
        })

    for f in dev_output.frontend.files:
        summary["frontend_files"].append({
            "filename": f.filename,
            "path": f.path,
            "language": f.language,
            "description": f.description,
            "content": f.content[:max_content_chars] + ("..." if len(f.content) > max_content_chars else ""),
        })

    return json.dumps(summary, indent=2, ensure_ascii=False)


def _full_dev_code(dev_output: DeveloperOutput) -> str:
    """Serialize all developer code files for deep review."""
    files = []
    for f in dev_output.backend.files + dev_output.frontend.files:
        files.append({
            "filename": f.filename,
            "path": f.path,
            "language": f.language,
            "content": f.content,
        })
    return json.dumps(files, indent=2, ensure_ascii=False)


# ── Public API ───────────────────────────────────────────────────────────────

import os
from langgraph.prebuilt import create_react_agent
from agents.mcp_client import ThreadSafeMCPClient
import json_repair

async def run_e2e_tests(developer_output: DeveloperOutput) -> dict:
    """Connect to Playwright MCP and perform basic E2E verification or simulate via HTTP."""
    from agents.mcp_client import get_mcp_tools, PLAYWRIGHT_MCP_CONFIG
    import aiohttp
    import re
    
    # 1. Detect URLs or endpoints
    urls_to_test = ["http://localhost:3000"]
    for f in developer_output.backend.files:
        paths = re.findall(r"@Get\(['\"]([^'\"]+)['\"]\)", f.content)
        for p in paths:
            if p and not p.startswith("http"):
                clean_path = p.strip("/")
                url = f"http://localhost:3000/{clean_path}"
                if url not in urls_to_test:
                    urls_to_test.append(url)
                    
    print(f"🕵️  [QA E2E] Endpoints detectados para probar: {urls_to_test}")
    
    # 2. Connect to Playwright MCP
    tools = get_mcp_tools(PLAYWRIGHT_MCP_CONFIG, "stdio")
    tool_map = {t.name: t for t in tools} if tools else {}
    
    e2e_results = {}
    
    if "playwright_navigate" in tool_map and "playwright_screenshot" in tool_map:
        print("🎭 [QA E2E] Playwright MCP disponible. Iniciando pruebas E2E...")
        for url in urls_to_test:
            try:
                print(f"🌐 Navegando a: {url}")
                nav_res = tool_map["playwright_navigate"].invoke({"url": url})
                screenshot_name = f"screenshot_{re.sub(r'[^a-zA-Z0-9]', '_', url)}.png"
                screenshot_path = f"./output/tests/{screenshot_name}"
                os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
                
                tool_map["playwright_screenshot"].invoke({
                    "path": screenshot_path
                })
                e2e_results[url] = {
                    "status": "success",
                    "screenshot_path": screenshot_path,
                    "info": str(nav_res)
                }
            except Exception as e:
                print(f"⚠️ Error navegando/capturando {url}: {e}")
                e2e_results[url] = {
                    "status": "error",
                    "error": str(e)
                }
    else:
        print("⚠️ [QA E2E] Playwright MCP no disponible. Usando fallback con aiohttp...")
        async with aiohttp.ClientSession() as session:
            for url in urls_to_test:
                try:
                    print(f"🔗 Haciendo GET (aiohttp) a: {url}")
                    timeout = aiohttp.ClientTimeout(total=5)
                    async with session.get(url, timeout=timeout) as response:
                        e2e_results[url] = {
                            "status": "simulated",
                            "http_code": response.status,
                            "reason": response.reason,
                            "screenshot_path": "no disponible (simulado)"
                        }
                except Exception as e:
                    e2e_results[url] = {
                        "status": "simulated_error",
                        "error": str(e),
                        "screenshot_path": "no disponible (simulado)"
                    }
                    
    return e2e_results


async def generate_test_files_with_filesystem(test_files: list[TestFile]):
    """Save QA test files to ./output/tests/ using Filesystem MCP or Python fallback."""
    from agents.mcp_client import get_mcp_tools, FILESYSTEM_MCP_CONFIG
    
    tools = get_mcp_tools(FILESYSTEM_MCP_CONFIG, "stdio")
    tool_map = {t.name: t for t in tools} if tools else {}
    
    test_dir = "./output/tests"
    os.makedirs(test_dir, exist_ok=True)
    
    mcp_available = "write_file" in tool_map
    
    for f in test_files:
        rel_path = os.path.join("tests", f.filename)
        
        if mcp_available:
            try:
                full_path = os.path.join("/Users/nikomendez/Documents/SWdevAIgency_project/output", rel_path)
                parent_dir = os.path.dirname(full_path)
                os.makedirs(parent_dir, exist_ok=True)
                
                print(f"🚀 [Filesystem MCP] Guardando archivo de prueba: {rel_path}...")
                tool_map["write_file"].invoke({
                    "path": full_path,
                    "content": f.content
                })
                print(f"📄 Guardado test: {rel_path}")
                continue
            except Exception as e:
                print(f"⚠️ [Filesystem MCP] Error escribiendo test {rel_path}: {e}. Fallback local...")
                
        try:
            fallback_full_path = os.path.join(test_dir, f.filename)
            parent_dir = os.path.dirname(fallback_full_path)
            os.makedirs(parent_dir, exist_ok=True)
            with open(fallback_full_path, "w", encoding="utf-8") as out_f:
                out_f.write(f.content)
            print(f"📄 Guardado test (Local Fallback): output/tests/{f.filename}")
        except Exception as e:
            print(f"❌ Error escribiendo archivo de test local: {e}")


def run_test_generator(
    pm_output: PMOutput, developer_output: DeveloperOutput
) -> dict:
    """Generate test cases and test files from PM stories + Developer files, using Playwright if needed."""
    
    # Connect Playwright MCP
    playwright_client = ThreadSafeMCPClient("npx", ["-y", "@playwright/mcp@latest"])
    tools = playwright_client.get_tools()
    
    llm = llm_qa

    agent = create_react_agent(llm, tools=tools)
    
    stories_json = json.dumps(
        [s.model_dump() for s in pm_output.user_stories],
        indent=2,
        ensure_ascii=False,
    )
    dev_summary = _summarize_dev_files(developer_output)
    
    prompt = (
        f"{TEST_GENERATOR_SYSTEM_PROMPT}\n\n"
        "Genera casos de prueba y código de tests basado en estas historias de usuario y archivos del Developer. "
        "Si necesitas validar o interactuar con un navegador para generar/comprobar flujos de UI, usa las herramientas de Playwright:\n\n"
        f"HISTORIAS DE USUARIO:\n{stories_json}\n\n"
        f"ARCHIVOS DEL DEVELOPER:\n{dev_summary}"
    )

    print("🧪  QA Agent (Test Generator) consultando herramientas y generando pruebas...")
    response = agent.invoke({"messages": [HumanMessage(content=prompt)]}, config={"recursion_limit": 10})
    
    final_message = response["messages"][-1].content
    cleaned = clean_llm_response(final_message)
    cleaned = _fix_json(cleaned)

    try:
        data = json_repair.loads(cleaned)
        test_cases = [TestCase.model_validate(tc) for tc in data["test_cases"]]
        test_files = [TestFile.model_validate(tf) for tf in data["test_files"]]
        return {"test_cases": test_cases, "test_files": test_files}
    except Exception as exc:
        print(f"   ⚠️ Falló parseo de pruebas: {exc}. Reintentando con prompt directo...")
        messages = [
            SystemMessage(content=TEST_GENERATOR_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
            HumanMessage(content=RETRY_PROMPT.format(error=str(exc)))
        ]
        retry_res = llm.invoke(messages)
        cleaned_retry = clean_llm_response(retry_res.content)
        cleaned_retry = _fix_json(cleaned_retry)
        data = json_repair.loads(cleaned_retry)
        test_cases = [TestCase.model_validate(tc) for tc in data["test_cases"]]
        test_files = [TestFile.model_validate(tf) for tf in data["test_files"]]
        return {"test_cases": test_cases, "test_files": test_files}


def run_code_reviewer(developer_output: DeveloperOutput) -> dict:
    """Review developer code for quality issues."""
    llm = llm_qa

    code_json = _full_dev_code(developer_output)

    messages = [
        SystemMessage(content=CODE_REVIEWER_SYSTEM_PROMPT),
        HumanMessage(
            content=(
                "Analiza el siguiente código generado por el equipo de desarrollo "
                "y reporta todos los problemas de calidad que encuentres:\n\n"
                f"{code_json}"
            )
        ),
    ]

    def parse_review_output(data: dict) -> dict:
        code_issues = [CodeIssue.model_validate(ci) for ci in data["code_issues"]]
        quality_score = max(0, min(100, int(data["quality_score"])))
        quality_summary = str(data["quality_summary"])
        return {
            "code_issues": code_issues,
            "quality_score": quality_score,
            "quality_summary": quality_summary,
        }

    return _invoke_with_retry(llm, messages, parse_review_output, label="CodeReview")


def merge_qa_outputs(
    project_name: str,
    test_output: dict,
    review_output: dict,
) -> QAOutput:
    """Combine test generator and code reviewer outputs into a QAOutput."""
    return QAOutput(
        project_name=project_name,
        test_cases=test_output["test_cases"],
        test_files=test_output["test_files"],
        code_issues=review_output["code_issues"],
        quality_score=review_output["quality_score"],
        quality_summary=review_output["quality_summary"],
    )
