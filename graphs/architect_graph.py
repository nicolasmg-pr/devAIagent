"""LangGraph graph for the Architect Agent pipeline.

Flow: START → architect_agent → formatter → END
"""

from __future__ import annotations

import traceback
from typing import Optional

from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field

from agents.pm_agent import PMOutput
from agents.architect_agent import (
    ArchitectOutput,
    run_architect_agent,
    enrich_with_context7,
    refine_architecture_with_docs,
    _run_async_in_thread,
)


# ── Graph state ──────────────────────────────────────────────────────────────

class ArchitectState(BaseModel):
    pm_output: PMOutput = Field(..., description="PM output from previous stage")
    architect_output: Optional[ArchitectOutput] = Field(
        default=None, description="Parsed Architect output"
    )
    error: Optional[str] = Field(default=None, description="Error message if any")


# ── Nodes ────────────────────────────────────────────────────────────────────

def architect_node(state: ArchitectState) -> dict:
    """Execute the Architect Agent and capture any exceptions."""
    try:
        result = run_architect_agent(state.pm_output)
        return {"architect_output": result, "error": None}
    except Exception as exc:
        traceback.print_exc()
        return {"architect_output": None, "error": str(exc)}


def context7_node(state: ArchitectState) -> dict:
    """Query Context7 MCP and refine the architectural decisions."""
    if state.error or state.architect_output is None:
        return {}

    print("🔍 [Context7 Node] Buscando documentación en Context7 y refinando arquitectura...")
    try:
        context7_docs = _run_async_in_thread(enrich_with_context7(state.architect_output.tech_stack))
        refined_output = refine_architecture_with_docs(state.architect_output, context7_docs)
        return {"architect_output": refined_output}
    except Exception as exc:
        print(f"⚠️ [Context7 Node] Falló el enriquecimiento con Context7: {exc}")
        state.architect_output.context7_enriched = False
        return {"architect_output": state.architect_output}


def format_node(state: ArchitectState) -> dict:
    """Pretty-print the Architect output with emojis and structured formatting."""
    if state.error:
        print(f"\n❌ Error durante la ejecución del Architect Agent:\n{state.error}")
        return {}

    output = state.architect_output
    if output is None:
        print("\n⚠️  No se generó output de arquitectura.")
        return {}

    print("\n" + "=" * 60)
    print(f"🏗️  ARQUITECTURA DEL PROYECTO: {output.project_name}")
    print("=" * 60)

    # ── Architecture pattern ─────────────────────────────────────────
    print(f"\n🏛️  Patrón arquitectónico: {output.architecture_pattern}")

    # ── Tech stack ───────────────────────────────────────────────────
    ts = output.tech_stack
    print("\n" + "-" * 60)
    print("🛠️  TECH STACK")
    print("-" * 60)
    print(f"   📱 Frontend:       {ts.frontend}")
    print(f"   ⚙️  Backend:        {ts.backend}")
    print(f"   🗄️  Database:       {ts.database}")
    print(f"   ☁️  Infraestructura: {ts.infrastructure}")
    if ts.additional_tools:
        print(f"   🔧 Herramientas:   {', '.join(ts.additional_tools)}")

    # ── API endpoints ────────────────────────────────────────────────
    print("\n" + "-" * 60)
    print(f"🔌 API ENDPOINTS ({len(output.api_endpoints)})")
    print("-" * 60)
    print(f"   {'Método':<8} {'Path':<30} {'Descripción'}")
    print(f"   {'─' * 8} {'─' * 30} {'─' * 40}")
    for ep in output.api_endpoints:
        print(f"   {ep.method:<8} {ep.path:<30} {ep.description}")

    # ── Database entities ────────────────────────────────────────────
    print("\n" + "-" * 60)
    print(f"🗄️  ENTIDADES DE BASE DE DATOS ({len(output.database_entities)})")
    print("-" * 60)
    for entity in output.database_entities:
        print(f"\n   📦 {entity.name}")
        print(f"      Campos: {', '.join(entity.fields[:5])}")
        if len(entity.fields) > 5:
            print(f"             ...y {len(entity.fields) - 5} más")
        if entity.relationships:
            print(f"      Relaciones: {', '.join(entity.relationships)}")

    # ── Mermaid diagram ──────────────────────────────────────────────
    print("\n" + "-" * 60)
    print("📐 DIAGRAMA DE ARQUITECTURA (Mermaid)")
    print("-" * 60)
    print("```mermaid")
    print(output.mermaid_diagram)
    print("```")

    # ── Key decisions ────────────────────────────────────────────────
    print("\n" + "-" * 60)
    print("💡 DECISIONES ARQUITECTÓNICAS CLAVE")
    print("-" * 60)
    for i, decision in enumerate(output.key_decisions, 1):
        print(f"   {i}. {decision}")

    print("-" * 60)
    enriched_status = "✅ docs enriquecidos" if output.context7_enriched else "⚠️ no disponible"
    print(f"🔍 Context7: {enriched_status}")

    print("\n" + "=" * 60 + "\n")

    return {}


# ── Graph builder ────────────────────────────────────────────────────────────

def build_architect_graph():
    """Build and compile the Architect LangGraph pipeline."""
    graph = StateGraph(ArchitectState)

    graph.add_node("architect_agent", architect_node)
    graph.add_node("context7_node", context7_node)
    graph.add_node("formatter", format_node)

    graph.add_edge(START, "architect_agent")
    graph.add_edge("architect_agent", "context7_node")
    graph.add_edge("context7_node", "formatter")
    graph.add_edge("formatter", END)

    return graph.compile()


# Pre-built graph ready for import
architect_graph = build_architect_graph()
