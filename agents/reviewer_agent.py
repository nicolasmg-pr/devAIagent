"""Reviewer Agent – Human-in-the-loop code reviewer."""

from __future__ import annotations

import json
import re
from typing import Optional, Any

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
from config.llm_config import llm_reviewer
from tools.llm_helpers import clean_llm_response

from agents.developer_agent import DeveloperOutput
from agents.qa_agent import QAOutput


# ── Pydantic models ──────────────────────────────────────────────────────────

class CodeChange(BaseModel):
    file: str = Field(..., description="File to modify")
    original_snippet: str = Field(..., description="Original code snippet (max 10 lines)")
    proposed_snippet: str = Field(..., description="Proposed code snippet")
    reason: str = Field(..., description="Justification for the change")
    change_type: str = Field(
        ..., description='Type: "refactor", "bugfix", "security", "performance", or "style"'
    )


class ReviewComment(BaseModel):
    file: str = Field(..., description="File path")
    line_reference: str = Field(..., description='E.g. "línea 42" or "líneas 10-15"')
    severity: str = Field(
        ..., description='Severity: "blocking", "important", or "suggestion"'
    )
    comment: str = Field(..., description="Review comment text")
    change: Optional[CodeChange] = Field(default=None, description="Proposed code change")


class ReviewRound(BaseModel):
    round_number: int = Field(..., description="Round number (starts at 1)")
    comments: list[ReviewComment] = Field(..., description="List of review comments")
    blocking_count: int = Field(..., description="Number of blocking comments")
    important_count: int = Field(..., description="Number of important comments")
    suggestion_count: int = Field(..., description="Number of suggestion comments")
    overall_verdict: str = Field(
        ..., description='"approved", "approved_with_suggestions", or "changes_required"'
    )
    verdict_reason: str = Field(..., description="Brief reason for the verdict")
    think_content: Optional[str] = Field(default=None, description="Reasoning block from the LLM")


class HumanDecision(BaseModel):
    approved: bool = Field(..., description="Whether the human approved the round")
    feedback: str = Field(..., description="Human feedback/comment")
    timestamp: str = Field(..., description="Timestamp of the decision")


class ReviewerOutput(BaseModel):
    project_name: str = Field(..., description="Project name")
    rounds: list[ReviewRound] = Field(..., description="History of all rounds")
    human_decisions: list[HumanDecision] = Field(..., description="History of human decisions")
    final_status: str = Field(
        ..., description='"approved", "approved_with_suggestions", or "rejected"'
    )
    total_changes_proposed: int = Field(..., description="Total changes proposed")
    approved_changes: list[CodeChange] = Field(..., description="Changes that were approved")


# ── System prompts ───────────────────────────────────────────────────────────

REVIEWER_SYSTEM_PROMPT = """\
Eres el Code Reviewer Principal (Tech Lead) del equipo. Tu misión es garantizar \
que el código generado cumplirá con los estándares más estrictos antes de pasar \
a producción. Eres meticuloso, directo y justificas cada comentario.

Tienes a tu disposición:
1. El código generado por los desarrolladores.
2. Los problemas de calidad ya detectados por el QA Agent.
3. El historial de rondas previas de code review y el feedback del humano.

REGLAS DE LA REVISIÓN:
- NO repitas los issues que ya detectó el QA Agent, asume que esos ya se corregirán. \
  Concéntrate en arquitectura, mantenibilidad profunda, lógica de negocio y bugs \
  más sutiles.
- Propón fragmentos de código concretos en "original_snippet" y "proposed_snippet" \
  cuando sugieras un cambio.
- Si el humano te da feedback o rechaza la ronda anterior, TIENES que incorporar \
  ese feedback en esta nueva ronda y ajustar tu veredicto.
- overall_verdict debe ser "approved", "approved_with_suggestions" o "changes_required".

REGLAS ESTRICTAS DE FORMATO:
1. Responde ÚNICAMENTE con un JSON válido. NO incluyas texto extra, comentarios ni markdown.
2. El JSON debe seguir EXACTAMENTE este esquema (para la clase ReviewRound):

{{
  "round_number": 1,
  "comments": [
    {{
      "file": "src/app.module.ts",
      "line_reference": "líneas 10-15",
      "severity": "blocking | important | suggestion",
      "comment": "string",
      "change": {{
        "file": "src/app.module.ts",
        "original_snippet": "string",
        "proposed_snippet": "string",
        "reason": "string",
        "change_type": "refactor | bugfix | security | performance | style"
      }}
    }}
  ],
  "blocking_count": 1,
  "important_count": 0,
  "suggestion_count": 0,
  "overall_verdict": "changes_required | approved_with_suggestions | approved",
  "verdict_reason": "string"
}}

3. Escapa correctamente comillas y saltos de línea dentro de "comment" y "snippet".
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
    cleaned = re.sub(r"```(?:json)?\s*", "", text)
    cleaned = re.sub(r"```", "", cleaned)
    return cleaned.strip()


def _parse_json_robust(text: str) -> dict:
    from json_repair import loads as repair_loads
    try:
        return json.loads(text, strict=False)
    except json.JSONDecodeError:
        return repair_loads(text)


def _invoke_with_retry(
    llm: Any,
    messages: list,
    parse_fn,
    max_retries: int = 2,
    label: str = "",
):
    last_error = None
    for attempt in range(1 + max_retries):
        response = llm.invoke(messages)
        raw_text: str = response.content  # type: ignore[assignment]
        cleaned = clean_llm_response(raw_text)

        # Extract <think> block if present
        think_match = re.search(r'<think>(.*?)</think>', raw_text, re.DOTALL)
        think_content = think_match.group(1).strip() if think_match else None

        try:
            data = _parse_json_robust(cleaned)
            result = parse_fn(data)
            if think_content and hasattr(result, 'think_content'):
                result.think_content = think_content
            return result
        except Exception as exc:
            last_error = exc
            print(f"   ⚠️  [{label}] Intento {attempt + 1} falló: {exc}")
            if attempt < max_retries:
                print(f"   🔄 [{label}] Reintentando con prompt más estricto...")
                messages = messages + [
                    HumanMessage(content=RETRY_PROMPT.format(error=str(exc)))
                ]

    raise last_error  # type: ignore[misc]


def _summarize_dev_files(dev_output: DeveloperOutput, max_chars: int = 800) -> str:
    summary = []
    for f in dev_output.backend.files + dev_output.frontend.files:
        content = f.content[:max_chars] + ("..." if len(f.content) > max_chars else "")
        summary.append({"filename": f.filename, "content": content})
    return json.dumps(summary, indent=2, ensure_ascii=False)


# ── Public API ───────────────────────────────────────────────────────────────

def run_reviewer(
    developer_output: DeveloperOutput,
    qa_output: QAOutput,
    previous_rounds: list[ReviewRound],
    human_feedback: Optional[str],
) -> ReviewRound:
    """Run the Code Reviewer agent."""
    llm = llm_reviewer

    dev_summary = _summarize_dev_files(developer_output)
    
    qa_issues = [
        {"file": issue.file, "description": issue.description, "severity": issue.severity}
        for issue in qa_output.code_issues
    ]
    qa_summary = json.dumps(qa_issues, indent=2, ensure_ascii=False)

    history_msg = ""
    if previous_rounds:
        for r in previous_rounds:
            history_msg += f"\n--- Ronda {r.round_number} ---\n"
            history_msg += f"Verdict: {r.overall_verdict} - {r.verdict_reason}\n"
            for c in r.comments:
                history_msg += f"[{c.severity}] {c.file}: {c.comment}\n"
    
    feedback_msg = ""
    if human_feedback:
        feedback_msg = f"\nFEEDBACK DEL HUMANO PARA ESTA RONDA:\n{human_feedback}\n"
    
    current_round_num = len(previous_rounds) + 1

    prompt_content = f"""
ARCHIVOS DEL DEVELOPER:
{dev_summary}

ISSUES DEL QA AGENT (YA DETECTADOS, NO REPETIR):
{qa_summary}
"""

    if history_msg:
        prompt_content += f"\nHISTORIAL DE RONDAS ANTERIORES:{history_msg}"
    
    if feedback_msg:
        prompt_content += feedback_msg
    
    prompt_content += f"\nGenera la revisión de código para la RONDA {current_round_num}."

    messages = [
        SystemMessage(content=REVIEWER_SYSTEM_PROMPT),
        HumanMessage(content=prompt_content),
    ]

    def parse_output(data: dict) -> ReviewRound:
        data["round_number"] = current_round_num
        return ReviewRound.model_validate(data)

    return _invoke_with_retry(llm, messages, parse_output, label="CodeReviewer")


async def create_github_pr(reviewer_output: ReviewerOutput, developer_output: DeveloperOutput) -> dict:
    """Connect to GitHub MCP, create a branch, push review refinements, and open a Pull Request."""
    from agents.mcp_client import get_mcp_tools, GITHUB_MCP_CONFIG
    import os
    import time
    import re as std_re
    
    # 1. Connect to GitHub MCP
    tools = get_mcp_tools(GITHUB_MCP_CONFIG, "stdio")
    tool_map = {t.name: t for t in tools} if tools else {}
    
    owner = os.getenv("GITHUB_OWNER", "nikomendez")
    repo = os.getenv("GITHUB_REPO", "ai-dev-team")
    
    # Check if tools are present and valid
    github_available = all(k in tool_map for k in ["create_branch", "create_or_update_file", "create_pull_request"])
    
    branch_name = f"review-refinements-{int(time.time())}"
    
    if github_available:
        try:
            print(f"🐙 [GitHub MCP] Iniciando creación de rama '{branch_name}' en {owner}/{repo}...")
            create_branch_res = tool_map["create_branch"].invoke({
                "owner": owner,
                "repo": repo,
                "branch": branch_name,
                "base_branch": "main"
            })
            print(f"✅ Rama '{branch_name}' creada: {create_branch_res}")
            
            # Push changed files
            for change in reviewer_output.approved_changes:
                file_content = ""
                for dev_file in developer_output.backend.files + developer_output.frontend.files:
                    if dev_file.filename == os.path.basename(change.file) or dev_file.path in change.file:
                        file_content = dev_file.content
                        break
                        
                if change.original_snippet and change.proposed_snippet and file_content:
                    file_content = file_content.replace(change.original_snippet, change.proposed_snippet)
                elif change.proposed_snippet:
                    file_content = change.proposed_snippet
                    
                if not file_content:
                    file_content = change.proposed_snippet
                    
                print(f"🚀 [GitHub MCP] Actualizando archivo {change.file} en la rama {branch_name}...")
                tool_map["create_or_update_file"].invoke({
                    "owner": owner,
                    "repo": repo,
                    "path": change.file,
                    "message": f"Apply review refinements for {change.file}: {change.reason}",
                    "content": file_content,
                    "branch": branch_name
                })
                
            # Create Pull Request
            pr_body = (
                f"# Review Refinements - AI Dev Team\n\n"
                f"Este Pull Request contiene cambios automáticos propuestos por el Code Reviewer Agent "
                f"y aprobados por el humano en la ronda final.\n\n"
                f"## Resumen de cambios:\n"
            )
            for c in reviewer_output.approved_changes:
                pr_body += f"- **{c.file}**: {c.reason} ({c.change_type})\n"
                
            print(f"🐙 [GitHub MCP] Abriendo Pull Request para la rama '{branch_name}'...")
            pr_res = tool_map["create_pull_request"].invoke({
                "owner": owner,
                "repo": repo,
                "title": f"Review Refinements - AI Dev Team ({branch_name})",
                "body": pr_body,
                "head": branch_name,
                "base": "main"
            })
            
            pr_url = f"https://github.com/{owner}/{repo}/pull/new/{branch_name}"
            match = std_re.search(r'(https://github\.com/[^\s"]+/pull/\d+)', str(pr_res))
            if match:
                pr_url = match.group(1)
                
            print(f"✅ Pull Request creado exitosamente: {pr_url}")
            return {
                "status": "success",
                "pr_url": pr_url,
                "branch": branch_name,
                "info": str(pr_res)
            }
            
        except Exception as e:
            print(f"⚠️ [GitHub MCP] Falló flujo en GitHub: {e}. Usando fallback simulado...")
            
    # Fallback / Simulated
    print("⚠️ [GitHub PR] GitHub MCP no disponible o falló la conexión. Simulando creación de PR localmente.")
    simulated_pr_url = f"https://github.com/{owner}/{repo}/pull/simulated_{branch_name}"
    return {
        "status": "simulated",
        "pr_url": simulated_pr_url,
        "branch": branch_name,
        "reason": "GitHub MCP no disponible o sin credenciales, se simuló el PR de forma local."
    }
