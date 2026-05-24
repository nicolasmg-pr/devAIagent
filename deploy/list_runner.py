import os
from deploy.project_registry import load_registry

def format_col(val: str, width: int, align="left") -> str:
    val = str(val)
    if len(val) > width:
        val = val[:width-3] + "..."
    if align == "right":
        return val.rjust(width)
    elif align == "center":
        return val.center(width)
    else:
        return val.ljust(width)

def run_list_command():
    """Load registry and render a beautiful unicode summary table and expanded details."""
    projects = load_registry()
    
    if not projects:
        print("\nNo hay proyectos generados todavía.")
        print("Crea uno con:")
        print('  devAIteam "describe tu app"\n')
        return

    n = len(projects)
    
    # Render table header
    print("\n╔" + "═" * 70 + "╗")
    title_text = f"  devAIteam — PROYECTOS GENERADOS ({n} total)"
    print("║" + title_text.ljust(70) + "║")
    print("╠" + "═" * 6 + "╦" + "═" * 23 + "╦" + "═" * 10 + "╦" + "═" * 13 + "╦" + "═" * 14 + "╣")
    print("║ " + format_col("#", 4) + " ║ " + format_col("Proyecto", 21) + " ║ " + format_col("QA Score", 8) + " ║ " + format_col("Deploy", 11) + " ║ " + format_col("Tamaño", 12) + " ║")
    print("╠" + "═" * 6 + "╬" + "═" * 23 + "╬" + "═" * 10 + "╬" + "═" * 13 + "╬" + "═" * 14 + "╣")
    
    # Render table rows
    for idx, p in enumerate(projects, 1):
        num_str = str(idx)
        score_str = f"{p.quality_score}/100" if p.quality_score is not None else "N/A"
        
        # Format Deploy Status beautifully
        if p.deploy_status == "deployed":
            deploy_str = f"✅ {p.deploy_platform or 'custom'}"
        elif p.deploy_status == "deploying":
            deploy_str = "⏳ local"
        else:
            deploy_str = "❌ none"
            
        size_str = f"{p.output_size_mb:.1f} MB"
        
        print("║ " + format_col(num_str, 4, "center") + " ║ " + format_col(p.project_name, 21) + " ║ " + format_col(score_str, 8, "center") + " ║ " + format_col(deploy_str, 11) + " ║ " + format_col(size_str, 12, "right") + " ║")
        
    print("╚" + "═" * 6 + "╩" + "═" * 23 + "╩" + "═" * 10 + "╩" + "═" * 13 + "╩" + "═" * 14 + "╝\n")
    
    # Render expanded project details
    for idx, p in enumerate(projects, 1):
        print(f"📁 {p.project_name}")
        
        # Format timestamp if possible
        created_formatted = p.created_at
        if "T" in created_formatted:
            # Replace T with space and strip microseconds
            created_formatted = created_formatted.replace("T", " ").split(".")[0]
            
        req_trimmed = p.requirement.strip()
        if len(req_trimmed) > 80:
            req_trimmed = req_trimmed[:77] + "..."
            
        print(f"   📅 Creado: {created_formatted}")
        print(f"   📝 \"{req_trimmed}\"")
        print(f"   🛠  Stack: {p.tech_stack}")
        print(f"   📄 Archivos: {p.files_count} generados · {p.output_size_mb:.1f} MB en ./output/{p.project_name}/")
        
        score_val = f"{p.quality_score}/100" if p.quality_score is not None else "N/A"
        print(f"   🧪 QA Score: {score_val}")
        
        preview_val = "✅ disponible" if p.local_preview_available else "❌ no disponible"
        print(f"   🌐 Preview local: {preview_val}")
        
        pr_val = p.github_pr_url if p.github_pr_url else "no hay PR"
        print(f"   🐙 GitHub PR: {pr_val}")
        
        dep_val = f"✅ {p.deploy_url} ({p.deploy_platform})" if p.deploy_status == "deployed" else "❌ no desplegado"
        print(f"   🚀 Deploy: {dep_val}")
        
        print("\n   Comandos disponibles:")
        print(f"     devAIteam deploy {p.project_name}   (redesplegar)")
        print(f"     devAIteam rm {p.project_name}       (borrar código local)")
        print(f"     devAIteam rm {p.project_name} --all (borrar local + GitHub)")
        print("-" * 50 + "\n")
