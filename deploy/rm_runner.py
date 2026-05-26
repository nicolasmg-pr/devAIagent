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
    repo = os.getenv("GITHUB_OUTPUT_REPO") or os.getenv("GITHUB_PROJECT_REPO") or project_name.lower().replace(" ", "-").replace("_", "-")
    
    try:
        tools = get_mcp_tools(GITHUB_MCP_CONFIG, "stdio")
        tool_map = {t.name: t for t in tools} if tools else {}
        
        # 1. Close PR if open
        pr_match = re.search(r'pull/(\d+)', github_pr_url)
        if pr_match and "update_pull_request" in tool_map:
            pr_number = int(pr_match.group(1))
            print(f"   🐙 [GitHub MCP] Closing Pull Request #{pr_number}...")
            try:
                tool_map["update_pull_request"].invoke({
                    "owner": owner,
                    "repo": repo,
                    "pull_number": pr_number,
                    "state": "closed"
                })
                res["pr_closed"] = True
            except Exception as e:
                print(f"   ⚠️  [GitHub] Could not close PR: {e}")
                 
        # 2. Delete branch
        # We try both "feature/ai-generated-{project_name}" and branches matching "review-refinements-*"
        branch_candidates = [f"feature/ai-generated-{project_name}"]
        # If the PR url points to a simulated or real branch name, let's extract it or guess
        # Let's search refs if possible or try to delete directly
        if "delete_git_ref" in tool_map:
            # First try feature branch
            for branch in branch_candidates:
                try:
                    print(f"   🐙 [GitHub MCP] Deleting branch 'heads/{branch}'...")
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
            confirm = input(f"Delete also the repository '{owner}/{repo}' on GitHub? [y/N]: ").strip().lower()
            if confirm in ["y", "yes", "s", "si"]:
                print(f"   🐙 [GitHub MCP] Deleting repository '{owner}/{repo}'...")
                try:
                    tool_map["delete_repository"].invoke({
                        "owner": owner,
                        "repo": repo
                    })
                    res["repo_deleted"] = True
                except Exception as e:
                    print(f"   ⚠️  [GitHub] Could not delete repository: {e}")
                    res["error"] = str(e)
                     
    except Exception as e:
        res["error"] = str(e)
         
    return res

def run_rm_command(project_name: str, delete_all: bool = False):
    """Execute the project removal CLI command in soft or total mode."""
    meta = get_project(project_name)
    output_path = f"./output/{project_name}"
    
    if not meta and not os.path.exists(output_path):
        print(f"\n❌ Error: The project '{project_name}' does not exist locally or in the registry.")
        projects = load_registry()
        if projects:
            print("Registered projects:")
            for p in projects:
                print(f"  - {p.project_name}")
        else:
            print("No generated projects currently found.")
        return

    size_mb = get_output_size_mb(project_name)
    
    # ── SOFT MODE ────────────────────────────────────────────────────────────
    if not delete_all:
        github_pr_str = meta.github_pr_url if (meta and meta.github_pr_url) else "(no PR created)"
        deploy_str = meta.deploy_url if (meta and meta.deploy_url) else "not deployed"
        
        print(f"""
⚠️  You are about to delete local code of '{project_name}'
   📂 To delete: ./output/{project_name}/ ({size_mb:.1f} MB)
   🐙 To keep: code on GitHub {github_pr_str}
   🚀 To keep: deployment at {deploy_str}

Confirm? [y/N]: """, end="")
        
        try:
            confirm = input().strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\n❌ Operation cancelled.")
            return
            
        if confirm not in ["y", "yes", "s", "si"]:
            print("❌ Operation cancelled.")
            return
            
        # Stop Docker compose if active
        docker_compose_path = os.path.join(output_path, "docker-compose.yml")
        if os.path.exists(docker_compose_path):
            print("   🐳 Stopping Docker services...")
            subprocess.run(["docker", "compose", "-f", docker_compose_path, "down"], capture_output=True)
            
        # Delete local files
        try:
            shutil.rmtree(output_path, ignore_errors=True)
            print(f"   ✅ Local code deleted ({size_mb:.1f} MB freed)")
        except Exception as e:
            print(f"   ⚠️  Error deleting local folder: {e}")
            
        # Update registry entry
        if meta:
            meta.local_preview_available = False
            save_project(meta)
            
        print(f"""
✅ '{project_name}' deleted locally.
   {"🐙 Code remains available at: " + meta.github_pr_url if meta and meta.github_pr_url else ""}
   {"🚀 Deployment remains active at: " + meta.deploy_url if meta and meta.deploy_url else ""}
   To regenerate: devAIteam "{meta.requirement[:60] + '...' if meta else 'your requirement'}"
""")

    # ── TOTAL MODE ───────────────────────────────────────────────────────────
    else:
        github_info = ""
        if meta and meta.github_pr_url:
            github_info = f"\n   🐙 Will close PR and delete branch on GitHub: {meta.github_pr_url}"
            
        deploy_warning = ""
        if meta and meta.deploy_url:
            deploy_warning = f"\n   ⚠️  ATTENTION: The deployment at {meta.deploy_url} will NOT be deleted automatically.\n      You will need to delete it manually from {meta.deploy_platform}."
            
        print(f"""
🚨 TOTAL DELETION of '{project_name}'
   📂 To delete: ./output/{project_name}/ ({size_mb:.1f} MB){github_info}{deploy_warning}

This action CANNOT be undone. Confirm? [y/N]: """, end="")
        
        try:
            confirm = input().strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\n❌ Operation cancelled.")
            return
            
        if confirm not in ["y", "yes", "s", "si"]:
            print("❌ Operation cancelled.")
            return
            
        # 1. Stop Docker compose with volumes
        docker_compose_path = os.path.join(output_path, "docker-compose.yml")
        if os.path.exists(docker_compose_path):
            print("   🐳 Stopping Docker services (with volumes)...")
            subprocess.run(["docker", "compose", "-f", docker_compose_path, "down", "-v"], capture_output=True)
            
        # 2. Delete local files
        try:
            shutil.rmtree(output_path, ignore_errors=True)
            print(f"   ✅ Local code deleted ({size_mb:.1f} MB freed)")
        except Exception as e:
            print(f"   ⚠️  Error deleting local folder: {e}")
            
        # 3. Delete GitHub resources if present
        if meta and meta.github_pr_url:
            print("   🐙 Deleting GitHub resources...")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                github_result = loop.run_until_complete(delete_github_resources(project_name, meta.github_pr_url))
                if github_result.get("pr_closed"):
                    print("   ✅ PR closed on GitHub")
                if github_result.get("branch_deleted"):
                    print("   ✅ Branch deleted on GitHub")
                if github_result.get("repo_deleted"):
                    print("   ✅ Repository deleted on GitHub")
                if github_result.get("error"):
                    print(f"   ⚠️  GitHub: {github_result['error']}")
            except Exception as e:
                print(f"   ⚠️  Error invoking GitHub MCP: {e}")
            finally:
                loop.close()
                 
        # 4. Remove from registry
        try:
            registry = load_registry()
            registry = [p for p in registry if p.project_name != project_name]
            with open("./output/.registry.json", "w", encoding="utf-8") as f:
                import json
                json.dump([p.model_dump() for p in registry], f, indent=2, ensure_ascii=False)
            print("   ✅ Project registry entry deleted from .registry.json")
        except Exception as e:
            print(f"   ⚠️  Error updating central registry: {e}")
            
        if meta and meta.deploy_url:
            print(f"""
✅ '{project_name}' completely deleted.
   ⚠️  Remember to manually delete the deployment at {meta.deploy_platform}:
       {meta.deploy_url}
""")
        else:
            print(f"\n✅ '{project_name}' completely deleted.\n")


def run_prune_command():
    """Detect and remove registry entries for projects whose local code directories no longer exist."""
    registry = load_registry()
    if not registry:
        print("\nRegistry is empty. Nothing to prune.\n")
        return

    to_prune = []
    for p in registry:
        output_path = f"./output/{p.project_name}"
        if not os.path.exists(output_path):
            to_prune.append(p)

    if not to_prune:
        print("\nAll registered projects exist locally. Nothing to prune.\n")
        return

    print("\n🔍 Detected projects in registry with missing local directories:")
    for idx, p in enumerate(to_prune, 1):
        print(f"  {idx}. {p.project_name} (Created: {p.created_at})")

    print(f"\nConfirm pruning these {len(to_prune)} entries from the registry? [y/N]: ", end="")
    try:
        confirm = input().strip().lower()
    except (KeyboardInterrupt, EOFError):
        print("\n❌ Operation cancelled.")
        return

    if confirm not in ["y", "yes", "s", "si"]:
        print("❌ Operation cancelled.")
        return

    pruned_names = {p.project_name for p in to_prune}
    new_registry = [p for p in registry if p.project_name not in pruned_names]

    try:
        os.makedirs("./output", exist_ok=True)
        with open("./output/.registry.json", "w", encoding="utf-8") as f:
            import json
            json.dump([p.model_dump() for p in new_registry], f, indent=2, ensure_ascii=False)
        print(f"\n✅ Successfully pruned {len(to_prune)} missing entries from the registry!\n")
    except Exception as e:
        print(f"\n❌ Error updating project registry during prune: {e}\n")

