import traceback
from typing import Optional
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field
from agents.developer_agent import DeveloperOutput
from agents.devops_agent import LocalPreviewOutput, run_local_preview
from agents.architect_agent import _run_async_in_thread

class DevOpsState(BaseModel):
    developer_output: DeveloperOutput = Field(..., description="Developer output from stage 3")
    project_name: str = Field(..., description="Lowercase project name with dashes")
    local_preview_output: Optional[LocalPreviewOutput] = Field(default=None, description="Preview agent output")
    error: Optional[str] = Field(default=None, description="Error message if any")

def preview_node(state: DevOpsState) -> dict:
    """Execute run_local_preview, capturing exceptions."""
    try:
        # run_local_preview is async, so run it using _run_async_in_thread
        preview_output = _run_async_in_thread(run_local_preview(state.developer_output, state.project_name))
        return {"local_preview_output": preview_output}
    except Exception as exc:
        traceback.print_exc()
        return {"error": f"DevOps Agent error: {exc}"}

def format_node(state: DevOpsState) -> dict:
    """Format and print local preview status."""
    if state.error:
        print(f"\n❌ Error en DevOps Agent:\n{state.error}")
        return {}

    o = state.local_preview_output
    if not o:
        return {}

    print("\n" + "━" * 40)
    print(f"🚀 LOCAL PREVIEW — {state.project_name}")
    print("━" * 40)

    for s in o.services:
        status_icon = "✅" if s.status == "running" else ("❌" if s.status == "failed" else "⏳")
        pid_info = f" (PID: {s.pid})" if s.pid else ""
        print(f"{status_icon} {s.name}: {s.url}{pid_info}")
        if s.error:
            print(f"   ⚠️  {s.error}")
        if s.logs_tail:
            print("   Logs (últimas 3 líneas):")
            for line in s.logs_tail[-3:]:
                print(f"     | {line}")

    print()
    if o.preview_ready:
        print(f"🌐 App disponible en: {o.frontend_url}")
        print(f"🔌 API disponible en: {o.backend_url}")
        print(f"📂 Código en: ./output/{state.project_name}/")
        if o.docker_compose_generated:
            print(f"🐳 Docker Compose: ./output/{state.project_name}/docker-compose.yml")
        print()
        print("┌─────────────────────────────────────────┐")
        print("│  La app está corriendo localmente.      │")
        print("│  Pruébala en tu navegador.              │")
        print("│  Cuando estés listo para desplegar:     │")
        print("│                                         │")
        print(f"│  devAIteam deploy {state.project_name}        │")
        print("└─────────────────────────────────────────┘")
    else:
        print("⚠️  Preview automático no disponible.")
        if o.manual_instructions:
            print("\n📋 INSTRUCCIONES MANUALES DE CONFIGURACIÓN Y EJECUCIÓN:")
            print(o.manual_instructions)
            
    print("━" * 40)
    return {}

def human_preview_node(state: DevOpsState) -> dict:
    """Standard Python input() blocking prompt (not a LangGraph interrupt)."""
    # Wait for the user to press ENTER
    try:
        input("\n⏸  Presiona ENTER cuando hayas probado la app para continuar...")
    except (KeyboardInterrupt, EOFError):
        print("\nContinuando automáticamente...")
    return {}

def build_devops_graph():
    graph = StateGraph(DevOpsState)
    
    graph.add_node("preview_node", preview_node)
    graph.add_node("format_node", format_node)
    graph.add_node("human_preview_node", human_preview_node)
    
    graph.add_edge(START, "preview_node")
    graph.add_edge("preview_node", "format_node")
    graph.add_edge("format_node", "human_preview_node")
    graph.add_edge("human_preview_node", END)
    
    return graph.compile()

devops_graph = build_devops_graph()
