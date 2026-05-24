"""AI Dev Team – Entry point.

Invokes the full pipeline: PM Agent → Architect Agent → Developer Agent → QA Agent → Reviewer Agent → DevOps Agent.
"""

import sys
from dotenv import load_dotenv
load_dotenv()

from graphs.pm_graph import pm_graph
from graphs.architect_graph import architect_graph
from graphs.ui_designer_graph import ui_designer_graph
from graphs.developer_graph import developer_graph
from graphs.qa_graph import qa_graph
from graphs.reviewer_graph import reviewer_graph, reviewer_config
from graphs.devops_graph import devops_graph

from langgraph.types import Command

def main() -> None:
    args = sys.argv[1:]

    # Sin argumentos: mostrar ayuda y pedir requerimiento interactivo
    if not args:
        print("""
  ╔══════════════════════════════════════════════════════╗
  ║                    devAIteam                        ║
  ║         Tu equipo de desarrollo IA local            ║
  ╠══════════════════════════════════════════════════════╣
  ║  GENERAR proyecto:                                  ║
  ║    devAIteam "describe tu app"                      ║
  ║                                                     ║
  ║  GESTIONAR proyectos:                               ║
  ║    devAIteam list                  ver proyectos    ║
  ║    devAIteam deploy <proyecto>     desplegar        ║
  ║    devAIteam rm <proyecto>         borrar local     ║
  ║    devAIteam rm <proyecto> --all   borrar todo      ║
  ╚══════════════════════════════════════════════════════╝
      """)
        print("🤖 Describe tu proyecto (o CTRL+C para salir):")
        try:
            requirement = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nOperación cancelada.")
            return
        if not requirement:
            return
        args = [requirement]

    command = args[0].lower()

    # devAIteam list
    if command == "list":
        from deploy.list_runner import run_list_command
        run_list_command()
        return

    # devAIteam deploy <project>
    if command == "deploy":
        if len(args) < 2:
            print("❌ Uso: devAIteam deploy <nombre_proyecto>")
            return
        from deploy.deploy_runner import run_deploy_command
        run_deploy_command(args[1])
        return

    # devAIteam rm <project> [--all]
    if command == "rm":
        if len(args) < 2:
            print("❌ Uso: devAIteam rm <nombre_proyecto> [--all]")
            return
        delete_all = "--all" in args
        from deploy.rm_runner import run_rm_command
        run_rm_command(args[1], delete_all=delete_all)
        return

    # Si no es un comando del CLI, se trata del requerimiento original del usuario
    requirement = " ".join(args)

    # ── Stage 1: PM Agent ────────────────────────────────────────────
    print("🤖 PM Agent ejecutando...")
    pm_result = pm_graph.invoke({"requirement": requirement})

    if pm_result.get("error"):
        print("❌ PM Agent falló. Abortando pipeline.")
        return

    # ── Stage 2: Architect Agent ─────────────────────────────────────
    print("\n🏗️  Architect Agent ejecutando...")
    arch_result = architect_graph.invoke({"pm_output": pm_result["pm_output"]})

    if arch_result.get("error"):
        print("❌ Architect Agent falló. Abortando pipeline.")
        return

    # ── Stage 2.5: UI Designer Agent ─────────────────────────────────
    print("\n🎨 UI Designer Agent ejecutando...")
    ui_result = ui_designer_graph.invoke({"architect_output": arch_result["architect_output"]})

    if "ui_designer_output" not in ui_result or ui_result["ui_designer_output"] is None:
        print("⚠️ UI Designer Agent falló o no devolvió output. Continuando sin UI.")
        ui_output = None
    else:
        ui_output = ui_result["ui_designer_output"]

    # ── Stage 3: Developer Agent (backend + frontend en paralelo) ────
    print("\n💻 Developer Agent ejecutando (backend + frontend en paralelo)...")
    dev_result = developer_graph.invoke(
        {
            "architect_output": arch_result["architect_output"],
            "ui_designer_output": ui_output
        }
    )

    if dev_result.get("error"):
        print("❌ Developer Agent falló. Abortando pipeline.")
        return

    # ── Stage 4: QA Agent (tests + code review en paralelo) ──────────
    print("\n🧪 QA Agent ejecutando (tests + code review en paralelo)...")
    qa_result = qa_graph.invoke({
        "pm_output": pm_result["pm_output"],
        "developer_output": dev_result["developer_output"],
    })

    if qa_result.get("error"):
        print("❌ QA Agent falló. Abortando pipeline.")
        return

    # ── Stage 5: Reviewer Agent (Human-in-the-loop) ──────────────────
    print("\n👁  Code Reviewer ejecutando (con human-in-the-loop)...")
    
    # Initialize state
    initial_state = {
        "developer_output": dev_result["developer_output"],
        "qa_output": qa_result["qa_output"]
    }
    
    rev_result = reviewer_graph.invoke(initial_state, reviewer_config)
    
    # Loop for human-in-the-loop interruption
    while rev_result and not rev_result.get("final_output"):
        print("┌─────────────────────────────────────────┐")
        print("│  ¿Apruebas esta revisión?               │")
        print("│  [a] Aprobar                            │")
        print("│  [s] Aprobar con sugerencias            │")
        print("│  [r] Rechazar y pedir nueva ronda       │")
        print("│  [f] Aprobar y finalizar pipeline       │")
        print("└─────────────────────────────────────────┘")
        try:
            user_input = input("Escribe tu opción y feedback opcional: ")
        except EOFError:
            # Handle non-interactive environments gracefully
            user_input = "a Aprobado automáticamente (EOF)"
            
        rev_result = reviewer_graph.invoke(Command(resume=user_input), reviewer_config)
    
    # ── Stage 6: DevOps Agent (Local Preview) ────────────────────────
    print("\n🚀 DevOps Agent ejecutando — levantando preview local...")
    
    proj_name = dev_result["developer_output"].project_name.lower().replace(" ", "-").replace("_", "-")
    
    initial_devops_state = {
        "developer_output": dev_result["developer_output"],
        "project_name": proj_name
    }
    
    try:
        devops_res = devops_graph.invoke(initial_devops_state)
        local_preview_output = devops_res.get("local_preview_output")
    except Exception as exc:
        print(f"⚠️  DevOps Agent falló: {exc}")
        local_preview_output = None

    # ── Pipeline data extraction ─────────────────────────────────────
    pm_out = pm_result["pm_output"]
    arch_out = arch_result["architect_output"]
    dev_out = dev_result["developer_output"]
    qa_out = qa_result.get("qa_output")
    rev_out = rev_result.get("final_output")

    n_stories = len(pm_out.user_stories)
    n_endpoints = len(arch_out.api_endpoints)
    n_entities = len(arch_out.database_entities)
    n_dev_files = len(dev_out.backend.files) + len(dev_out.frontend.files)

    if qa_out:
        n_tests = len(qa_out.test_cases)
        qa_score = qa_out.quality_score
    else:
        n_tests = 0
        qa_score = "N/A"
        
    if rev_out:
        rev_rounds = len(rev_out.rounds)
        rev_status = rev_out.final_status
    else:
        rev_rounds = 0
        rev_status = "N/A"

    # ── Save project metadata in registry ────────────────────────────
    try:
        from deploy.project_registry import ProjectMeta, save_project
        from deploy.rm_runner import get_output_size_mb
        from datetime import datetime
        
        size_mb = get_output_size_mb(proj_name)
        preview_ready = local_preview_output.preview_ready if local_preview_output else False
        pr_url = rev_result.get("github_output", {}).get("pr_url") if rev_result else None
        
        meta = ProjectMeta(
            project_name=proj_name,
            created_at=datetime.now().isoformat(),
            requirement=requirement,
            tech_stack=f"{arch_out.tech_stack.frontend} + {arch_out.tech_stack.backend} + {arch_out.tech_stack.database}",
            files_count=n_dev_files,
            quality_score=qa_score if isinstance(qa_score, int) else None,
            deploy_status="not_deployed",
            local_preview_available=preview_ready,
            github_pr_url=pr_url,
            output_size_mb=size_mb
        )
        save_project(meta)
        print(f"💾 Metadatos del proyecto '{proj_name}' guardados en el registro central.")
    except Exception as exc:
        print(f"⚠️  No se pudieron guardar los metadatos en el registro central: {exc}")

    # MCP Usage determination
    arch_mcp = "Real MCP (Context7)" if getattr(arch_out, "context7_enriched", False) else "Simulated (Fallback)"
    
    design_mcp = "Simulated (Fallback)"
    if ui_output and ui_output.screens:
        if any(s.stitch_screen_url for s in ui_output.screens):
            design_mcp = "Real MCP (Google Stitch)"
            
    dev_mcp = "Real MCP (Filesystem)"
    
    qa_playwright_mcp = "Simulated (aiohttp Fallback)"
    e2e_out = qa_result.get("e2e_output")
    if e2e_out:
        if any(res.get("status") == "success" for res in e2e_out.values()):
            qa_playwright_mcp = "Real MCP (Playwright)"
            
    qa_fs_mcp = "Real MCP (Filesystem)" if qa_result.get("test_saved") else "Simulated (Local Fallback)"
    
    rev_github_mcp = "Simulated (Local/Fallback)"
    gh_out = rev_result.get("github_output")
    if gh_out and gh_out.get("status") == "success":
        rev_github_mcp = f"Real MCP (GitHub PR: {gh_out.get('pr_url')})"

    print("\n╔══════════════════════════════════════════════════════════════════════════╗")
    print("║                       STATUS PIPELINE COMPLETO ✅                        ║")
    print("╠══════════════════════════════════════════════════════════════════════════╣")
    print(f"║ 📋 PM Agent:       {str(n_stories).ljust(2)} historias de usuario.                                 ║")
    print(f"║ 🏗️  Architect:      {str(n_endpoints).ljust(2)} endpoints, {str(n_entities).ljust(2)} entidades.                           ║")
    print(f"║    ↳ Context7:     {arch_mcp.ljust(53)} ║")
    print(f"║ 🎨 Designer:       {str(len(ui_output.screens) if ui_output else 0).ljust(2)} pantallas generadas.                                  ║")
    print(f"║    ↳ Stitch:       {design_mcp.ljust(53)} ║")
    print(f"║ 💻 Developer:      {str(n_dev_files).ljust(2)} archivos código de desarrollo.                       ║")
    print(f"║    ↳ Filesystem:   {dev_mcp.ljust(53)} ║")
    print(f"║ 🧪 QA Agent:       {str(n_tests).ljust(2)} tests, score: {str(qa_score).ljust(3)}/100.                                 ║")
    print(f"║    ↳ Playwright:   {qa_playwright_mcp.ljust(53)} ║")
    print(f"║    ↳ Filesystem:   {qa_fs_mcp.ljust(53)} ║")
    print(f"║ 👁  Reviewer:      {str(rev_rounds).ljust(2)} rondas, estado final: {rev_status.ljust(24)} ║")
    print(f"║    ↳ GitHub:       {rev_github_mcp[:53].ljust(53)} ║")
    
    devops_val = "Not running"
    if local_preview_output and local_preview_output.preview_ready:
        devops_val = f"{local_preview_output.backend_url} · {local_preview_output.frontend_url}"
    elif local_preview_output and local_preview_output.docker_compose_generated:
        devops_val = "Simulated / Docker Compose Generated"
    print(f"║ 🚀 DevOps:        {devops_val[:53].ljust(53)} ║")
    print("╚══════════════════════════════════════════════════════════════════════════╝\n")

if __name__ == "__main__":
    main()
