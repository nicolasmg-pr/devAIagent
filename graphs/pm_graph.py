"""LangGraph graph for the PM Agent pipeline.

Flow: START → pm_agent → formatter → END
"""

from __future__ import annotations

import traceback
from typing import Optional

from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field

from agents.pm_agent import PMAgent, PMOutput


# ── Graph state ──────────────────────────────────────────────────────────────

class PMState(BaseModel):
    requirement: str = Field(..., description="Natural-language requirement")
    pm_output: Optional[PMOutput] = Field(default=None, description="Parsed PM output")
    error: Optional[str] = Field(default=None, description="Error message if any")


# ── Nodes ────────────────────────────────────────────────────────────────────

def pm_node(state: PMState) -> dict:
    """Execute the PM Agent and capture any exceptions."""
    try:
        agent = PMAgent()
        result = agent.run(state.requirement)
        return {"pm_output": result, "error": None}
    except Exception as exc:
        traceback.print_exc()
        return {"pm_output": None, "error": str(exc)}


def format_node(state: PMState) -> dict:
    """Pretty-print the PM output with emojis and priority icons."""
    if state.error:
        print(f"\n❌ Error durante la ejecución del PM Agent:\n{state.error}")
        return {}

    output = state.pm_output
    if output is None:
        print("\n⚠️  No se generó output.")
        return {}

    priority_icons = {
        "high": "🔴",
        "medium": "🟡",
        "low": "🟢",
    }

    print("\n" + "=" * 60)
    print(f"📋 Proyecto: {output.project_name}")
    print("=" * 60)
    print(f"\n📝 Resumen:\n{output.summary}\n")
    print("-" * 60)
    print(f"📌 Historias de Usuario ({len(output.user_stories)}):")
    print("-" * 60)

    for story in output.user_stories:
        icon = priority_icons.get(story.priority, "⚪")
        print(f"\n{icon} [{story.id}] {story.title}")
        print(f"   📖 {story.description}")
        print(f"   🎯 Prioridad: {story.priority}  |  📊 Puntos: {story.estimated_points}")
        print("   ✅ Criterios de aceptación:")
        for criterion in story.acceptance_criteria:
            print(f"      • {criterion}")

    print("\n" + "=" * 60)
    print(f"✨ Total de historias: {len(output.user_stories)}")
    total_points = sum(s.estimated_points for s in output.user_stories)
    print(f"📊 Puntos totales estimados: {total_points}")
    print("=" * 60 + "\n")

    return {}


# ── Graph builder ────────────────────────────────────────────────────────────

def build_pm_graph():
    """Build and compile the PM LangGraph pipeline."""
    graph = StateGraph(PMState)

    graph.add_node("pm_agent", pm_node)
    graph.add_node("formatter", format_node)

    graph.add_edge(START, "pm_agent")
    graph.add_edge("pm_agent", "formatter")
    graph.add_edge("formatter", END)

    return graph.compile()


# Pre-built graph ready for import
pm_graph = build_pm_graph()
