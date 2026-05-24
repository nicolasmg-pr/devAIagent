"""LangGraph graph for the Reviewer Agent with real Human-in-the-Loop."""

from __future__ import annotations

import traceback
from typing import Optional, Annotated
import operator

from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel, Field

from agents.developer_agent import DeveloperOutput
from agents.qa_agent import QAOutput
from agents.architect_agent import _run_async_in_thread
from agents.reviewer_agent import (
    ReviewRound,
    HumanDecision,
    ReviewerOutput,
    CodeChange,
    run_reviewer,
    create_github_pr,
)


# ── Graph state ──────────────────────────────────────────────────────────────

class ReviewerState(BaseModel):
    developer_output: DeveloperOutput
    qa_output: QAOutput
    
    # We use list to append state across rounds
    rounds: Annotated[list[ReviewRound], operator.add] = Field(default_factory=list)
    human_decisions: Annotated[list[HumanDecision], operator.add] = Field(default_factory=list)
    
    current_round: Optional[ReviewRound] = None
    human_decision: Optional[HumanDecision] = None
    final_output: Optional[ReviewerOutput] = None
    github_output: Optional[dict] = Field(default=None, description="GitHub PR creation output")
    max_rounds: int = Field(default=3)
    error: Optional[str] = None


# ── Nodes ────────────────────────────────────────────────────────────────────

def review_node(state: ReviewerState) -> dict:
    """Run the reviewer agent to produce a ReviewRound."""
    try:
        round_num = len(state.rounds) + 1
        print(f"   🔍 Reviewer Agent generando revisión (Ronda {round_num})...")
        
        last_decision = None
        if state.human_decisions:
            last_decision = state.human_decisions[-1].feedback

        new_round = run_reviewer(
            state.developer_output,
            state.qa_output,
            state.rounds,
            last_decision
        )
        
        return {
            "current_round": new_round,
            "rounds": [new_round], # Annotated with operator.add
            "human_decision": None # Clear previous decision
        }
    except Exception as exc:
        traceback.print_exc()
        return {"error": f"Reviewer Agent error: {exc}"}


def format_review_node(state: ReviewerState) -> dict:
    """Format and print the current review round."""
    if state.error:
        print(f"\n❌ Error en Code Review:\n{state.error}")
        return {}

    r = state.current_round
    if not r:
        return {}

    emoji = "🟢" if "approved" in r.overall_verdict else "🔴"
    
    print("\n" + "━" * 40)
    print(f"👁  CODE REVIEW — Ronda {r.round_number}")
    print("━" * 40)

    if getattr(r, "think_content", None):
        print("🧠 RAZONAMIENTO DEL REVIEWER:")
        for line in r.think_content.strip().split("\n"):
            print(f"  > {line}")
        print()

    print(f"Veredicto: {emoji} {r.overall_verdict} — {r.verdict_reason}")
    print(f"🔴 Blocking: {r.blocking_count} | 🟠 Important: {r.important_count} | 💡 Suggestions: {r.suggestion_count}\n")

    severities = ["blocking", "important", "suggestion"]
    icons = {"blocking": "🔴 BLOCKING", "important": "🟠 IMPORTANT", "suggestion": "💡 SUGGESTION"}

    for sev in severities:
        comments = [c for c in r.comments if c.severity == sev]
        for c in comments:
            print(f"[{icons[sev]}]")
            print(f"  📄 {c.file} ({c.line_reference})")
            print(f"  {c.comment}")
            if c.change:
                print(f"    ANTES:   {c.change.original_snippet}")
                print(f"    DESPUÉS: {c.change.proposed_snippet}")
                print(f"    Razón:   {c.change.reason}")
            print()
    print("━" * 40)
    return {}


def human_input_node(state: ReviewerState) -> dict:
    """Pause the graph and ask for human input."""
    # This invokes the langgraph interrupt, suspending the graph execution.
    # The string passed to interrupt is returned to the client (main.py).
    human_input = interrupt("Esperando input del humano...")

    # When resumed, human_input receives the payload from Command(resume=value)
    human_input = str(human_input).strip()
    
    approved = human_input.lower().startswith('a') or human_input.lower().startswith('f')
    
    from datetime import datetime
    decision = HumanDecision(
        approved=approved,
        feedback=human_input,
        timestamp=datetime.now().isoformat()
    )
    
    return {
        "human_decision": decision,
        "human_decisions": [decision] # Annotated with operator.add
    }


def should_continue_node(state: ReviewerState) -> str:
    """Route based on human decision and max rounds."""
    if state.error:
        return "finalize_node"
        
    decision = state.human_decision
    if not decision:
        # Fallback if no decision found, though it shouldn't happen
        return "finalize_node"
        
    if decision.approved:
        return "finalize_node"
        
    if len(state.rounds) >= state.max_rounds:
        return "finalize_node"
        
    return "review_node"


import os
import subprocess
from agents.mcp_client import ThreadSafeMCPClient

def _apply_code_change(change: CodeChange):
    """Locate the original snippet in the local file and replace it with the proposed snippet."""
    base_dir = "/Users/nikomendez/Documents/SWdevAIgency_project"
    full_path = os.path.join(base_dir, change.file)
    if not os.path.exists(full_path):
        print(f"⚠️  [Reviewer] Archivo no encontrado para aplicar cambio: {full_path}")
        return
        
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        orig = change.original_snippet.strip()
        prop = change.proposed_snippet
        
        if orig in content:
            content = content.replace(orig, prop)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ [Reviewer] Cambio aplicado localmente con éxito en: {change.file}")
        else:
            # Simple fallback if exact match fails: search without leading/trailing whitespace
            lines = content.splitlines()
            orig_lines = orig.splitlines()
            # Try to match the subset of lines
            found = False
            for i in range(len(lines) - len(orig_lines) + 1):
                chunk = "\n".join(lines[i:i+len(orig_lines)])
                if chunk.strip() == orig:
                    lines[i:i+len(orig_lines)] = prop.splitlines()
                    content = "\n".join(lines)
                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"✅ [Reviewer] Cambio aplicado localmente (soft match) en: {change.file}")
                    found = True
                    break
            if not found:
                print(f"⚠️  [Reviewer] No se pudo encontrar el fragmento original exacto en: {change.file}")
    except Exception as e:
        print(f"❌ [Reviewer] Error aplicando cambio local en {change.file}: {e}")


def _get_git_repo_name() -> Optional[tuple[str, str]]:
    """Get GitHub owner and repo from local git remote url."""
    try:
        url = subprocess.check_output(["git", "config", "--get", "remote.origin.url"], text=True).strip()
        if "github.com" in url:
            parts = url.split("github.com")[-1].strip(":/").replace(".git", "").split("/")
            if len(parts) >= 2:
                return parts[-2], parts[-1]
    except Exception:
        pass
    return None


def finalize_node(state: ReviewerState) -> dict:
    """Build the final output and apply code changes locally."""
    if state.error:
        return {}

    final_status = "rejected"
    if state.human_decisions:
        last_decision = state.human_decisions[-1]
        if last_decision.approved:
            # Check the AI's verdict from the last round
            last_round = state.rounds[-1]
            if last_round.overall_verdict == "approved_with_suggestions":
                final_status = "approved_with_suggestions"
            else:
                final_status = "approved"

    # Gather all changes proposed
    total_changes = 0
    approved_changes = []
    for r in state.rounds:
        for c in r.comments:
            if c.change:
                total_changes += 1
                if final_status in ["approved", "approved_with_suggestions"]:
                    approved_changes.append(c.change)

    # Apply approved changes locally
    if final_status in ["approved", "approved_with_suggestions"] and approved_changes:
        print(f"💾 Aplicando {len(approved_changes)} cambios aprobados al espacio de trabajo...")
        for change in approved_changes:
            _apply_code_change(change)

    out = ReviewerOutput(
        project_name=state.developer_output.project_name,
        rounds=state.rounds,
        human_decisions=state.human_decisions,
        final_status=final_status,
        total_changes_proposed=total_changes,
        approved_changes=approved_changes
    )
    return {"final_output": out}


def github_node(state: ReviewerState) -> dict:
    """Create GitHub branch, push changes, and open PR if approved."""
    if state.error or state.final_output is None:
        return {}
        
    if state.final_output.final_status not in ["approved", "approved_with_suggestions"]:
        return {}
        
    if not state.final_output.approved_changes:
        return {}
        
    print("🐙 [Github Node] Creando rama y abriendo Pull Request en GitHub...")
    try:
        github_res = _run_async_in_thread(create_github_pr(state.final_output, state.developer_output))
        return {"github_output": github_res}
    except Exception as exc:
        print(f"⚠️ [Github Node] Falló la integración con GitHub: {exc}")
        return {"github_output": {"status": "failed", "error": str(exc)}}


def format_final_node(state: ReviewerState) -> dict:
    """Print the final summary of the Code Review phase."""
    if state.error:
        return {}
        
    out = state.final_output
    if not out:
        return {}

    print("\n╔══════════════════════════════════════════╗")
    print("║        CODE REVIEW COMPLETADO            ║")
    print("╠══════════════════════════════════════════╣")
    print(f"║ Estado: {out.final_status.ljust(32)} ║")
    print(f"║ Rondas: {str(len(out.rounds)).ljust(2)} de {str(state.max_rounds).ljust(25)} ║")
    print(f"║ Cambios propuestos: {str(out.total_changes_proposed).ljust(20)} ║")
    print(f"║ Cambios aprobados: {str(len(out.approved_changes)).ljust(21)} ║")
    print(f"║ Decisiones humanas: {str(len(out.human_decisions)).ljust(20)} ║")
    
    if state.github_output:
        res = state.github_output
        if res.get("status") in ["success", "simulated"]:
            pr_val = res.get("pr_url", "")
            branch_val = res.get("branch", "")
            print(f"║ PR: {pr_val[:35].ljust(36)} ║")
            print(f"║ Rama: {branch_val[:33].ljust(34)} ║")
        else:
            print("║ PR: Falló la creación en GitHub         ║")
    else:
        print("║ PR: No se requirió/creó push a GitHub    ║")
        
    print("╚══════════════════════════════════════════╝\n")
    return {}


# ── Graph builder ────────────────────────────────────────────────────────────

def build_reviewer_graph():
    graph = StateGraph(ReviewerState)

    graph.add_node("review_node", review_node)
    graph.add_node("format_review_node", format_review_node)
    graph.add_node("human_input_node", human_input_node)
    graph.add_node("finalize_node", finalize_node)
    graph.add_node("github_node", github_node)
    graph.add_node("format_final_node", format_final_node)

    graph.add_edge(START, "review_node")
    graph.add_edge("review_node", "format_review_node")
    graph.add_edge("format_review_node", "human_input_node")
    
    # Conditional edge from human input
    graph.add_conditional_edges(
        "human_input_node",
        should_continue_node,
        {
            "finalize_node": "finalize_node",
            "review_node": "review_node"
        }
    )
    
    graph.add_edge("finalize_node", "github_node")
    graph.add_edge("github_node", "format_final_node")
    graph.add_edge("format_final_node", END)

    # Use MemorySaver to allow pausing and resuming with interrupt()
    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer)

# Pre-built graph ready for import
reviewer_graph = build_reviewer_graph()
reviewer_config = {"configurable": {"thread_id": "review-session-1"}}
