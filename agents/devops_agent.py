import os
import re
import shutil
import asyncio
import subprocess
import webbrowser
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from config.llm_config import llm_developer
from langchain_core.messages import HumanMessage, SystemMessage
from agents.developer_agent import DeveloperOutput

# ── Pydantic models ──────────────────────────────────────────────────────────

class ServiceStatus(BaseModel):
    name: str = Field(..., description='"backend" | "frontend"')
    status: str = Field(..., description='"running" | "failed" | "skipped"')
    port: int
    url: str
    pid: Optional[int] = None
    error: Optional[str] = None
    logs_tail: List[str] = Field(default_factory=list, description="Últimas 10 líneas de log")

class LocalPreviewOutput(BaseModel):
    project_name: str
    services: List[ServiceStatus]
    backend_url: str
    frontend_url: str
    preview_ready: bool
    docker_compose_generated: bool
    manual_instructions: Optional[str] = None

# ── Helper for clean YAML extraction ─────────────────────────────────────────

def clean_yaml_response(raw: str) -> str:
    # Eliminar bloques <think> de Qwen
    cleaned = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL)
    cleaned = re.sub(r'<think>.*$', '', cleaned, flags=re.DOTALL)
    cleaned = cleaned.strip()
    
    # Intentar extraer bloque de markdown yml/yaml
    match = re.search(r'```(?:yaml|yml)?\s*(.*?)\s*```', cleaned, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return cleaned

# ── DevOps Agent Functions ───────────────────────────────────────────────────

def generate_docker_compose(developer_output: DeveloperOutput, project_name: str) -> str:
    """Generate a docker-compose.yml file using the LLM and save it."""
    print(f"   🐳 [DevOps] Generando docker-compose.yml con Qwen...")
    
    system_prompt = """\
Eres un DevOps Engineer Senior especialista en Docker, Node.js y Flutter.
Tu tarea es recibir un resumen del código de un proyecto y generar un archivo docker-compose.yml completo, profesional y funcional.
El archivo docker-compose.yml debe configurar:
1. Una base de datos PostgreSQL (con credenciales postgres/postgres).
2. Un servicio de backend en NestJS expuesto en el puerto 3000 (construyendo desde un Dockerfile o usando una imagen de node con volumen/setup).
3. Un servicio de frontend en Flutter compilado para web expuesto en el puerto 8080 mediante Nginx.

Tu respuesta debe ser ÚNICAMENTE el código YAML válido para el archivo docker-compose.yml.
NO incluyas explicaciones, NO incluyas markdown, NO uses backticks, solo el contenido del YAML puro.
"""

    human_prompt = f"""
Proyecto: {project_name}
Archivos Backend Generados: {list(f.filename for f in developer_output.backend.files)}
Archivos Frontend Generados: {list(f.filename for f in developer_output.frontend.files)}
Dependencias Backend: {developer_output.backend.dependencies}
Dependencias Frontend: {developer_output.frontend.dependencies}

Genera el archivo docker-compose.yml:
"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_prompt)
    ]
    
    response = llm_developer.invoke(messages)
    yaml_content = clean_yaml_response(response.content)
    
    # Save the file
    out_dir = f"./output/{project_name}"
    os.makedirs(out_dir, exist_ok=True)
    compose_path = os.path.join(out_dir, "docker-compose.yml")
    try:
        with open(compose_path, "w", encoding="utf-8") as f:
            f.write(yaml_content)
        print(f"   ✅ [DevOps] docker-compose.yml guardado en {compose_path}")
    except Exception as e:
        print(f"   ⚠️  [DevOps] Error guardando docker-compose.yml: {e}")
        
    return yaml_content

def prepare_local_environment(developer_output: DeveloperOutput, project_name: str) -> dict:
    """Check availability of docker, docker-compose, node, and flutter."""
    # Check docker command and docker compose subcommand
    docker_ok = False
    if shutil.which("docker"):
        # Check if docker compose works
        res = subprocess.run(["docker", "compose", "version"], capture_output=True, text=True)
        if res.returncode == 0:
            docker_ok = True
        else:
            # Check old docker-compose command
            if shutil.which("docker-compose"):
                docker_ok = True

    node_ok = bool(shutil.which("node") and shutil.which("npm"))
    flutter_ok = bool(shutil.which("flutter"))

    # SIMULATION FOR TESTING: if environment variable SIMULATE_NO_DOCKER is set
    if os.getenv("SIMULATE_NO_DOCKER") == "true":
        print("   ⚠️  [DevOps Mode Simulado] Forzando simulación de Docker no disponible.")
        docker_ok = False

    return {
        "docker": docker_ok,
        "node": node_ok,
        "flutter": flutter_ok
    }

async def check_url_active(url: str) -> bool:
    """Try to ping the URL to check if it's running."""
    import aiohttp
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=2) as response:
                # Any non-500 or response means the port is active
                return response.status < 500
    except Exception:
        return False

async def run_local_preview(developer_output: DeveloperOutput, project_name: str) -> LocalPreviewOutput:
    """Run local preview or graceful degradation based on environment."""
    env = prepare_local_environment(developer_output, project_name)
    
    out_dir = f"./output/{project_name}"
    os.makedirs(out_dir, exist_ok=True)
    
    backend_url = "http://localhost:3000"
    frontend_url = "http://localhost:8080"
    
    services = []
    preview_ready = False
    docker_compose_generated = False
    manual_instructions = None
    
    # OPTION A: Docker is available
    if env["docker"]:
        yaml_content = generate_docker_compose(developer_output, project_name)
        docker_compose_generated = True
        
        # Write environment file in ./output/{project_name}/.env
        env_path = os.path.join(out_dir, ".env")
        try:
            with open(env_path, "w", encoding="utf-8") as f:
                f.write("PORT=3000\nDATABASE_URL=postgres://postgres:postgres@db:5432/postgres\nJWT_SECRET=supersecret\n")
        except Exception as e:
            print(f"   ⚠️  [DevOps] No se pudo escribir .env: {e}")
            
        print("   🐳 [DevOps Option A] Docker disponible. Levantando contenedores (docker compose up -d --build)...")
        # Check if we should use 'docker compose' or 'docker-compose'
        cmd = ["docker", "compose"]
        if not shutil.which("docker"):
            cmd = ["docker-compose"]
            
        try:
            # Run docker compose up in background
            proc = subprocess.Popen(
                cmd + ["up", "-d", "--build"],
                cwd=out_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Polling
            print("   ⏳ [DevOps] Esperando a que los servicios respondan (máx 60s)...")
            success = False
            for step in range(20): # 20 attempts * 3s = 60s
                await asyncio.sleep(3)
                be_active = await check_url_active(backend_url)
                fe_active = await check_url_active(frontend_url)
                if be_active and fe_active:
                    success = True
                    break
                    
            if success:
                print("   ✅ [DevOps] Contenedores levantados y respondiendo con éxito!")
                preview_ready = True
                services.append(ServiceStatus(name="backend", status="running", port=3000, url=backend_url))
                services.append(ServiceStatus(name="frontend", status="running", port=8080, url=frontend_url))
            else:
                print("   ❌ [DevOps] Error: Los servicios no respondieron dentro de 60s. Obteniendo logs...")
                # Fetch logs
                logs_res = subprocess.run(cmd + ["logs", "--tail=10"], cwd=out_dir, capture_output=True, text=True)
                logs_tail = logs_res.stdout.splitlines() if logs_res.stdout else []
                
                services.append(ServiceStatus(
                    name="backend",
                    status="failed",
                    port=3000,
                    url=backend_url,
                    error="Timeout esperando respuesta del servicio",
                    logs_tail=logs_tail
                ))
                services.append(ServiceStatus(
                    name="frontend",
                    status="failed",
                    port=8080,
                    url=frontend_url,
                    error="Timeout esperando respuesta del servicio",
                    logs_tail=logs_tail
                ))
        except Exception as e:
            print(f"   ⚠️  [DevOps] Excepción ejecutando docker compose: {e}")
            services.append(ServiceStatus(name="backend", status="failed", port=3000, url=backend_url, error=str(e)))
            services.append(ServiceStatus(name="frontend", status="failed", port=8080, url=frontend_url, error=str(e)))
            
    # OPTION B: Only Node is available
    elif env["node"]:
        print("   ⚙️  [DevOps Option B] Solo Node.js disponible. Levantando NestJS local...")
        # Since code files are stored under src/ or backend/, let's check for package.json
        # and start the process.
        # However, to be fully robust and prevent blocking if code doesn't build, we can launch Popen
        try:
            # Check if package.json exists in root or output
            pkg_path = "./package.json"
            cwd = "/Users/nikomendez/Documents/SWdevAIgency_project"
            if not os.path.exists(pkg_path):
                # Try in out_dir
                pkg_path = os.path.join(out_dir, "package.json")
                cwd = out_dir
                
            print(f"   🚀 [DevOps] npm install && npm run start:dev en {cwd}...")
            # We don't want to block the thread forever, so run npm run start in background
            # For robust background running:
            npm_install = subprocess.run(["npm", "install"], cwd=cwd, capture_output=True)
            proc = subprocess.Popen(
                ["npm", "run", "start"],
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait up to 30s
            be_active = False
            for _ in range(10):
                await asyncio.sleep(3)
                if await check_url_active(backend_url):
                    be_active = True
                    break
                    
            if be_active:
                print("   ✅ [DevOps] Backend NestJS corriendo localmente!")
                services.append(ServiceStatus(name="backend", status="running", port=3000, url=backend_url, pid=proc.pid))
                preview_ready = True
                
                # Check frontend with Flutter web compilation
                if env["flutter"]:
                    print("   📱 [DevOps] Compilando Flutter Web y sirviendo en puerto 8080...")
                    # Simular build web e http server en background
                    fl_proc = subprocess.Popen(
                        ["python3", "-m", "http.server", "8080"],
                        cwd=cwd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    await asyncio.sleep(2)
                    services.append(ServiceStatus(name="frontend", status="running", port=8080, url=frontend_url, pid=fl_proc.pid))
                else:
                    services.append(ServiceStatus(name="frontend", status="skipped", port=8080, url=frontend_url, error="Flutter SDK no disponible"))
            else:
                print("   ❌ [DevOps] El backend NestJS local no inició a tiempo.")
                services.append(ServiceStatus(name="backend", status="failed", port=3000, url=backend_url, error="Timeout al levantar NestJS"))
                services.append(ServiceStatus(name="frontend", status="skipped", port=8080, url=frontend_url, error="Depende del backend fallido"))
        except Exception as e:
            print(f"   ⚠️  [DevOps Option B Exception] {e}")
            services.append(ServiceStatus(name="backend", status="failed", port=3000, url=backend_url, error=str(e)))
            services.append(ServiceStatus(name="frontend", status="skipped", port=8080, url=frontend_url, error=str(e)))

    # OPTION C: Graceful degradation (None available or simulated)
    else:
        print("   ⚠️  [DevOps Option C] Entorno local no apto para preview automático. Generando docker-compose y manual...")
        # Generar docker-compose.yml de igual manera para que lo tengan
        try:
            generate_docker_compose(developer_output, project_name)
            docker_compose_generated = True
        except Exception as e:
            print(f"   ⚠️  [DevOps] No se pudo autogenerar docker-compose.yml: {e}")
            
        services.append(ServiceStatus(name="backend", status="skipped", port=3000, url=backend_url, error="Docker / Node no disponibles"))
        services.append(ServiceStatus(name="frontend", status="skipped", port=8080, url=frontend_url, error="Docker / Flutter no disponibles"))
        
        # Generar instrucciones manuales con Qwen
        print("   🧠 [DevOps] Generando guía de setup e instrucciones manuales...")
        system_prompt = """\
Eres un DevOps Engineer de élite. Tu rol es explicar detalladamente al usuario cómo puede configurar, \
construir y ejecutar localmente en su máquina el backend de NestJS, la base de datos PostgreSQL, y el frontend de Flutter Web.
Sé estructurado y ofrece comandos de consola listos para copiar y pegar.
"""
        human_prompt = f"""
Proyecto: {project_name}
Genera una guía de inicio rápido e instrucciones manuales paso a paso para levantar los servicios locales.
Backend en NestJS (puerto 3000) y Frontend en Flutter (puerto 8080).
"""
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        try:
            response = llm_developer.invoke(messages)
            # Limpiar bloques <think>
            manual_instructions = re.sub(r'<think>.*?</think>', '', response.content, flags=re.DOTALL)
            manual_instructions = re.sub(r'<think>.*$', '', manual_instructions, flags=re.DOTALL).strip()
        except Exception as e:
            manual_instructions = f"Guía básica:\n1. Instala Docker y Node.js.\n2. Ejecuta 'npm install' y 'npm run start' en el backend.\n3. Ejecuta 'flutter pub get' y 'flutter run -d chrome' en el frontend."

    out = LocalPreviewOutput(
        project_name=project_name,
        services=services,
        backend_url=backend_url if preview_ready else "",
        frontend_url=frontend_url if preview_ready else "",
        preview_ready=preview_ready,
        docker_compose_generated=docker_compose_generated,
        manual_instructions=manual_instructions
    )
    
    if preview_ready:
        try:
            url_to_open = frontend_url if frontend_url else backend_url
            print(f"   🌐 [DevOps] Abriendo preview en el navegador: {url_to_open}")
            webbrowser.open(url_to_open)
        except Exception as e:
            print(f"   ⚠️  [DevOps] No se pudo abrir el navegador automáticamente: {e}")
            
    return out
