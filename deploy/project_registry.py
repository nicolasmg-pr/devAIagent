import os
import json
from typing import Optional, List
from pydantic import BaseModel, Field

class ProjectMeta(BaseModel):
    project_name: str
    created_at: str
    requirement: str
    tech_stack: str
    files_count: int
    quality_score: Optional[int] = None
    deploy_status: str = "not_deployed"
    deploy_url: Optional[str] = None
    deploy_platform: Optional[str] = None
    local_preview_available: bool = False
    github_pr_url: Optional[str] = None
    output_size_mb: float = 0.0

REGISTRY_PATH = "./output/.registry.json"

def _ensure_output_dir():
    os.makedirs(os.path.dirname(REGISTRY_PATH), exist_ok=True)

def load_registry() -> List[ProjectMeta]:
    _ensure_output_dir()
    if not os.path.exists(REGISTRY_PATH):
        return []
    try:
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return [ProjectMeta.model_validate(p) for p in data]
    except Exception as e:
        print(f"⚠️ Error cargando el registro de proyectos: {e}")
    return []

def save_project(meta: ProjectMeta) -> None:
    _ensure_output_dir()
    registry = load_registry()
    
    # Check if project exists, and replace or add it
    updated = False
    for i, p in enumerate(registry):
        if p.project_name == meta.project_name:
            registry[i] = meta
            updated = True
            break
            
    if not updated:
        registry.append(meta)
        
    try:
        with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
            json.dump([p.model_dump() for p in registry], f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"❌ Error guardando el registro de proyectos: {e}")

def get_project(project_name: str) -> Optional[ProjectMeta]:
    registry = load_registry()
    for p in registry:
        if p.project_name == project_name:
            return p
    return None

def update_deploy_status(project_name: str, status: str, url: str, platform: str) -> None:
    meta = get_project(project_name)
    if meta:
        meta.deploy_status = status
        meta.deploy_url = url
        meta.deploy_platform = platform
        save_project(meta)
    else:
        print(f"⚠️ No se encontró el proyecto '{project_name}' en el registro para actualizar deploy.")
