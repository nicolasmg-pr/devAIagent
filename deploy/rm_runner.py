import os
import re
import shutil
import asyncio
import subprocess
from typing import Optional
from deploy.project_registry import get_project, load_registry, save_project

def get_output_size_mb(project_name: str) -> float:
    """Calculate the recursive size of `./output/{project_name}` in MB."""
    total_size = 0
    output_path = f"./output/{project_name}"
    if not os.path.exists(output_path):
        return 0.0
    for dirpath, dirnames, filenames in os.walk(output_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                if os.path.exists(fp):
                    total_size += os.path.getsize(fp)
            except Exception:
                pass
    return total_size / (1024 * 1024)

async def delete_github_resources(project_name: str, github_pr_url: Optional[str]) -> dict:
    """Connect to GitHub MCP, close active PRs, delete branches, and optionally delete the repo."""
    from agents.mcp_client import get_mcp_tools, GITHUB_MCP_CONFIG
    
    res = {
        "pr_closed": False,
        "branch_deleted": False,
        "repo_deleted": False,
        "error": None
    }
    
    if not github_pr_url:
        return res
        
    owner = os.getenv("GITHUB_OWNER", "nikomendez")
    repo = os.getenv("GITHUB_REPO", "ai-dev-team")
    
    try:
        tools = get_mcp_tools(GITHUB_MCP_CONFIG, "stdio")
        tool_map = {t.name: t for t in tools} if tools else {}
        
        # 1. Close PR if open
        pr_match = re.search(r'pull/(\d+)', github_pr_url)
        if pr_match and "update_pull_request" in tool_map:
            pr_number = int(pr_match.group(1))
            print(f"   🐙 [GitHub MCP] Cerrando Pull Request #{pr_number}...")
            try:
                tool_map["update_pull_request"].invoke({
                    "owner": owner,
                    "repo": repo,
                    "pull_number": pr_number,
                    "state": "closed"
                })
                res["pr_closed"] = True
            except Exception as e:
                print(f"   ⚠️  [GitHub] No se pudo cerrar la PR: {e}")
                
        # 2. Delete branch
        # We try both "feature/ai-generated-{project_name}" and branches matching "review-refinements-*"
        branch_candidates = [f"feature/ai-generated-{project_name}"]
        # If the PR url points to a simulated or real branch name, let's extract it or guess
        # Let's search refs if possible or try to delete directly
        if "delete_git_ref" in tool_map:
            # First try feature branch
            for branch in branch_candidates:
                try:
                    print(f"   🐙 [GitHub MCP] Eliminando rama 'heads/{branch}'...")
                    tool_map["delete_git_ref"].invoke({
                        "owner": owner,
                        "repo": repo,
                        "ref": f"heads/{branch}"
                    })
                    res["branch_deleted"] = True
                except Exception:
                    pass
                    
        # 3. Check if repo empty and ask to delete
        # For simplicity and robust prompt-driven behavior:
        # If the repo delete tool is present and we want to allow it:
        if "delete_repository" in tool_map:
            confirm = input(f"¿Borrar también el repositorio '{owner}/{repo}' en GitHub? [s/N]: ").strip().lower()
            if confirm == "s":
                print(f"   🐙 [GitHub MCP] Eliminando repositorio '{owner}/{repo}'...")
                try:
                    tool_map["delete_repository"].invoke({
                        "owner": owner,
                        "repo": repo
                    })
                    res["repo_deleted"] = True
                except Exception as e:
                    print(f"   ⚠️  [GitHub] No se pudo borrar el repositorio: {e}")
                    res["error"] = str(e)
                    
    except Exception as e:
        res["error"] = str(e)
        
    return res

def run_rm_command(project_name: str, delete_all: bool = False):
    """Execute the project removal CLI command in soft or total mode."""
    meta = get_project(project_name)
    output_path = f"./output/{project_name}"
    
    if not meta and not os.path.exists(output_path):
        print(f"\n❌ Error: El proyecto '{project_name}' no existe localmente ni en el registro.")
        projects = load_registry()
        if projects:
            print("Proyectos registrados:")
            for p in projects:
                print(f"  - {p.project_name}")
        else:
            print("No hay proyectos generados actualmente.")
        return

    size_mb = get_output_size_mb(project_name)
    
    # ── MODO SOFT ────────────────────────────────────────────────────────────
    if not delete_all:
        github_pr_str = meta.github_pr_url if (meta and meta.github_pr_url) else "(no hay PR)"
        deploy_str = meta.deploy_url if (meta and meta.deploy_url) else "no desplegado"
        
        print(f"""
⚠️  Vas a borrar el código local de '{project_name}'
   📂 Se eliminará: ./output/{project_name}/ ({size_mb:.1f} MB)
   🐙 Se mantiene: código en GitHub {github_pr_str}
   🚀 Se mantiene: deploy en {deploy_str}

¿Confirmar? [s/N]: """, end="")
        
        try:
            confirm = input().strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\n❌ Operación cancelada.")
            return
            
        if confirm != "s":
            print("❌ Operación cancelada.")
            return
            
        # Stop Docker compose if active
        docker_compose_path = os.path.join(output_path, "docker-compose.yml")
        if os.path.exists(docker_compose_path):
            print("   🐳 Deteniendo servicios Docker...")
            subprocess.run(["docker", "compose", "-f", docker_compose_path, "down"], capture_output=True)
            
        # Delete local files
        try:
            shutil.rmtree(output_path, ignore_errors=True)
            print(f"   ✅ Código local eliminado ({size_mb:.1f} MB liberados)")
        except Exception as e:
            print(f"   ⚠️  Error eliminando carpeta local: {e}")
            
        # Update registry entry
        if meta:
            meta.local_preview_available = False
            save_project(meta)
            
        print(f"""
✅ '{project_name}' eliminado localmente.
   {"🐙 El código sigue disponible en: " + meta.github_pr_url if meta and meta.github_pr_url else ""}
   {"🚀 El deploy sigue activo en: " + meta.deploy_url if meta and meta.deploy_url else ""}
   Para regenerarlo: devAIteam "{meta.requirement[:60] + '...' if meta else 'tu requerimiento'}"
""")

    # ── MODO TOTAL ───────────────────────────────────────────────────────────
    else:
        github_info = ""
        if meta and meta.github_pr_url:
            github_info = f"\n   🐙 Se cerrará PR y borrará rama en GitHub: {meta.github_pr_url}"
            
        deploy_warning = ""
        if meta and meta.deploy_url:
            deploy_warning = f"\n   ⚠️  ATENCIÓN: El deploy en {meta.deploy_url} NO se borrará automáticamente.\n      Deberás eliminarlo manualmente desde {meta.deploy_platform}."
            
        print(f"""
🚨 BORRADO TOTAL de '{project_name}'
   📂 Se eliminará: ./output/{project_name}/ ({size_mb:.1f} MB){github_info}{deploy_warning}

Esta acción NO se puede deshacer. ¿Confirmar? [s/N]: """, end="")
        
        try:
            confirm = input().strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\n❌ Operación cancelada.")
            return
            
        if confirm != "s":
            print("❌ Operación cancelada.")
            return
            
        # 1. Stop Docker compose with volumes
        docker_compose_path = os.path.join(output_path, "docker-compose.yml")
        if os.path.exists(docker_compose_path):
            print("   🐳 Deteniendo servicios Docker (con volúmenes)...")
            subprocess.run(["docker", "compose", "-f", docker_compose_path, "down", "-v"], capture_output=True)
            
        # 2. Delete local files
        try:
            shutil.rmtree(output_path, ignore_errors=True)
            print(f"   ✅ Código local eliminado ({size_mb:.1f} MB liberados)")
        except Exception as e:
            print(f"   ⚠️  Error eliminando carpeta local: {e}")
            
        # 3. Delete GitHub resources if present
        if meta and meta.github_pr_url:
            print("   🐙 Eliminando recursos de GitHub...")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                github_result = loop.run_until_complete(delete_github_resources(project_name, meta.github_pr_url))
                if github_result.get("pr_closed"):
                    print("   ✅ PR cerrada en GitHub")
                if github_result.get("branch_deleted"):
                    print("   ✅ Rama eliminada en GitHub")
                if github_result.get("repo_deleted"):
                    print("   ✅ Repositorio eliminado en GitHub")
                if github_result.get("error"):
                    print(f"   ⚠️  GitHub: {github_result['error']}")
            except Exception as e:
                print(f"   ⚠️  Error al invocar GitHub MCP: {e}")
            finally:
                loop.close()
                
        # 4. Remove from registry
        try:
            registry = load_registry()
            registry = [p for p in registry if p.project_name != project_name]
            with open("./output/.registry.json", "w", encoding="utf-8") as f:
                import json
                json.dump([p.model_dump() for p in registry], f, indent=2, ensure_ascii=False)
            print("   ✅ Registro de proyecto eliminado de .registry.json")
        except Exception as e:
            print(f"   ⚠️  Error actualizando registro central: {e}")
            
        if meta and meta.deploy_url:
            print(f"""
✅ '{project_name}' eliminado completamente.
   ⚠️  Recuerda eliminar el deploy manualmente en {meta.deploy_platform}:
       {meta.deploy_url}
""")
        else:
            print(f"\n✅ '{project_name}' eliminado completamente.\n")
