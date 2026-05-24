import os
import asyncio
from deploy.deploy_agent import run_deploy
from deploy.project_registry import load_registry, update_deploy_status

def run_deploy_command(project_name: str):
    """Deploy the project, or print instructions, and update the registry."""
    output_path = f"./output/{project_name}"
    
    if not os.path.exists(output_path):
        print(f"\n❌ Error: El directorio del proyecto '{project_name}' no existe en './output/'.")
        projects = load_registry()
        if projects:
            print("Proyectos disponibles en el registro:")
            for p in projects:
                print(f"  - {p.project_name}")
        else:
            # Check physical directories
            if os.path.exists("./output"):
                dirs = [d for d in os.listdir("./output") if os.path.isdir(os.path.join("./output", d)) and not d.startswith(".")]
                if dirs:
                    print("Directorios de proyectos disponibles:")
                    for d in dirs:
                        print(f"  - {d}")
                else:
                    print("No se encontraron proyectos generados todavía.")
            else:
                print("No se encontraron proyectos generados todavía.")
        return

    print(f"\n🚀 Iniciando proceso de despliegue para '{project_name}'...")
    
    # Run the deployment asynchronously
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        deploy_out = loop.run_until_complete(run_deploy(project_name))
    finally:
        loop.close()

    primary_url = deploy_out.primary_url
    
    if primary_url and primary_url != "not_deployed":
        print("\n" + "═" * 40)
        print("🎉 DESPLIEGUE COMPLETADO CON ÉXITO")
        print("═" * 40)
        print(f"🌐 URL: {primary_url}")
        print(f"📢 Mensaje para compartir:\n   \"{deploy_out.share_message}\"")
        
        # Determine platform deployed
        platform = "manual"
        for t in deploy_out.targets:
            if t.deploy_status == "success":
                platform = t.platform
                break
                
        # Update registry status
        update_deploy_status(project_name, "deployed", primary_url, platform)
        print("═" * 40 + "\n")
    else:
        print("\n" + "═" * 40)
        print("⚠️  GUÍA DE DESPLIEGUE MANUAL GENERADA")
        print("═" * 40)
        print(deploy_out.instructions)
        print("═" * 40 + "\n")
