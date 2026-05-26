"""Developer Agent – Backend and Frontend sub-agents that generate
real, functional code based on the Architect's output."""

from __future__ import annotations

import json
import re
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
from config.llm_config import llm_developer
from tools.llm_helpers import clean_llm_response

from agents.architect_agent import ArchitectOutput
from typing import Optional, Any


# ── Pydantic output models ──────────────────────────────────────────────────

class CodeFile(BaseModel):
    filename: str = Field(..., description="File name, e.g. app.module.ts")
    path: str = Field(..., description="Relative path, e.g. src/modules/expense")
    language: str = Field(..., description="Programming language, e.g. typescript, dart")
    content: str = Field(..., description="Full source code content of the file")
    description: str = Field(..., description="Brief description of the file's purpose")


class BackendOutput(BaseModel):
    files: list[CodeFile] = Field(..., description="Generated backend files")
    setup_commands: list[str] = Field(
        ..., description="Commands to set up and run the backend"
    )
    dependencies: list[str] = Field(
        ..., description="Required packages / dependencies"
    )


class FrontendOutput(BaseModel):
    files: list[CodeFile] = Field(..., description="Generated frontend files")
    setup_commands: list[str] = Field(
        ..., description="Commands to set up and run the frontend"
    )
    dependencies: list[str] = Field(
        ..., description="Required packages / dependencies"
    )


class DeveloperOutput(BaseModel):
    project_name: str = Field(..., description="Project name")
    backend: BackendOutput = Field(..., description="Backend output")
    frontend: FrontendOutput = Field(..., description="Frontend output")
    integration_notes: list[str] = Field(
        ..., description="Notes on how to connect frontend and backend"
    )


# ── System prompts ───────────────────────────────────────────────────────────

BACKEND_SYSTEM_PROMPT = """\
You are a Senior Backend Developer with over 10 years of experience, \
specializing in NestJS, TypeScript, and Clean Architecture.

Your task is to receive a software architecture document and generate \
real, functional, and complete code for the backend of the project.

PRIORITIES:
- Correct folder structure following Clean Architecture
- TypeORM entities with correct decorators and types
- Creation DTOs with validation using class-validator
- Services with complete CRUD business logic
- REST controllers with correct NestJS decorators
- Main application Module that imports all other modules

STRICT RULES:
1. Respond ONLY with a valid JSON. Do NOT include explanatory text, \
comments, or markdown blocks (```).
2. The JSON must follow EXACTLY this schema:

{{
  "files": [
    {{
      "filename": "app.module.ts",
      "path": "src",
      "language": "typescript",
      "content": "import {{ Module }} from '@nestjs/common';\\n...",
      "description": "Root application module"
    }}
  ],
  "setup_commands": [
    "npm install",
    "npm run start:dev"
  ],
  "dependencies": [
    "@nestjs/core",
    "@nestjs/typeorm",
    "class-validator"
  ]
}}

3. Generate real and functional TypeScript code, not placeholders.
4. Include at least: app.module.ts, one entity for each DB entity, \
one creation DTO per entity, a service with basic CRUD, and a controller \
with the main endpoints.
5. Correctly escape quotes and line breaks within the "content" field.
6. Do NOT use backticks, do NOT use markdown, ONLY pure JSON.
"""

FRONTEND_SYSTEM_PROMPT = """\
You are a Senior Frontend Developer with over 10 years of experience, \
specializing in Flutter, Dart, and Clean Architecture.

Your task is to receive a software architecture document and generate \
real, functional, and complete code for the mobile frontend of the project.

PRIORITIES:
- Feature structure following Clean Architecture
- Dart data models that map backend entities
- Repositories with HTTP calls to the backend using http or dio
- Main pages with functional Material Design widgets
- Navigation between screens

STRICT RULES:
1. Respond ONLY with a valid JSON. Do NOT include explanatory text, \
comments, or markdown blocks (```).
2. The JSON must follow EXACTLY this schema:

{{
  "files": [
    {{
      "filename": "main.dart",
      "path": "lib",
      "language": "dart",
      "content": "import 'package:flutter/material.dart';\\n...",
      "description": "Application entry point"
    }}
  ],
  "setup_commands": [
    "flutter pub get",
    "flutter run"
  ],
  "dependencies": [
    "flutter",
    "http",
    "provider"
  ]
}}

3. Generate real and functional Dart code, not placeholders.
4. Include at least: main.dart, one model per main entity, \
a repository with HTTP calls, and one page per high-priority user story.
5. Correctly escape quotes and line breaks within the "content" field.
6. Do NOT use backticks, do NOT use markdown, ONLY pure JSON.
"""

RETRY_PROMPT = """\
Your previous response was NOT valid JSON. The error was:
{error}

You MUST respond with pure and valid JSON. No extra text, no backticks, \
no explanations. Only the JSON object that complies with the indicated schema.
Make sure to:
- Escape internal quotes with \\\"
- Use \\n for line breaks inside strings
- Do not leave trailing commas in arrays or objects
- Close all braces and brackets correctly

Regenerate the complete response:
"""


# ── Helpers ──────────────────────────────────────────────────────────────────

def _clean_response(text: str) -> str:
    """Strip markdown code fences and surrounding whitespace."""
    cleaned = re.sub(r"```(?:json)?\s*", "", text)
    cleaned = re.sub(r"```", "", cleaned)
    return cleaned.strip()


def _fix_json(text: str) -> str:
    """Fix common LLM JSON errors: trailing commas before ] or }."""
    fixed = re.sub(r",\s*([}\]])", r"\1", text)
    return fixed


def _parse_json_robust(text: str) -> dict:
    """Parse JSON with fallback to json_repair for malformed LLM output."""
    from json_repair import loads as repair_loads

    try:
        return json.loads(text, strict=False)
    except json.JSONDecodeError:
        return repair_loads(text)


def _invoke_with_retry(llm: Any, messages: list, model_class: type, max_retries: int = 2):
    """Invoke the LLM, parse JSON, and retry with a stricter prompt on failure."""
    last_error = None
    for attempt in range(1 + max_retries):
        response = llm.invoke(messages)
        raw_text: str = response.content  # type: ignore[assignment]
        cleaned = clean_llm_response(raw_text)

        try:
            data = _parse_json_robust(cleaned)
            return model_class.model_validate(data)
        except Exception as exc:
            last_error = exc
            print(f"   ⚠️  Attempt {attempt + 1} failed: {exc}")
            if attempt < max_retries:
                print(f"   🔄 Retrying with stricter prompt...")
                messages = messages + [
                    HumanMessage(content=RETRY_PROMPT.format(error=str(exc)))
                ]

    raise last_error  # type: ignore[misc]


# ── Public API ───────────────────────────────────────────────────────────────

import os
from langgraph.prebuilt import create_react_agent
from agents.mcp_client import ThreadSafeMCPClient
import json_repair

from agents.ui_designer_agent import UIDesignerOutput
import asyncio
import threading
import queue

def _write_generated_files(files: list[CodeFile]):
    """Auto-save generated code files to the project directory."""
    base_dir = "/Users/nikomendez/Documents/SWdevAIgency_project"
    for f in files:
        target_dir = os.path.join(base_dir, f.path)
        os.makedirs(target_dir, exist_ok=True)
        file_path = os.path.join(target_dir, f.filename)
        print(f"💾 Saving file: {file_path}")
        with open(file_path, "w", encoding="utf-8") as out:
            out.write(f.content)


async def save_files_to_filesystem(developer_output: DeveloperOutput):
    """Save backend and frontend generated files to the filesystem using MCP or fallback to python."""
    from agents.mcp_client import get_mcp_tools, FILESYSTEM_MCP_CONFIG
    
    # 1. Connect to Filesystem MCP
    tools = get_mcp_tools(FILESYSTEM_MCP_CONFIG, "stdio")
    tool_map = {t.name: t for t in tools} if tools else {}
    
    output_dir = "./output"
    os.makedirs(output_dir, exist_ok=True)
    
    all_files = []
    if developer_output.backend and developer_output.backend.files:
        all_files.extend(developer_output.backend.files)
    if developer_output.frontend and developer_output.frontend.files:
        all_files.extend(developer_output.frontend.files)
        
    mcp_available = "write_file" in tool_map
    
    for f in all_files:
        rel_path = os.path.join(f.path, f.filename)
        
        if mcp_available:
            try:
                full_path = os.path.join("/Users/nikomendez/Documents/SWdevAIgency_project", rel_path)
                parent_dir = os.path.dirname(full_path)
                os.makedirs(parent_dir, exist_ok=True)
                
                print(f"🚀 [Filesystem MCP] Saving file: {rel_path}...")
                tool_map["write_file"].invoke({
                    "path": full_path,
                    "content": f.content
                })
                print(f"📄 Saved: {f.path}/{f.filename}")
                continue
            except Exception as e:
                print(f"⚠️ [Filesystem MCP] Error writing {rel_path} via MCP: {e}. Using local fallback...")
        
        # Fallback to python
        try:
            fallback_full_path = os.path.join(output_dir, rel_path)
            parent_dir = os.path.dirname(fallback_full_path)
            os.makedirs(parent_dir, exist_ok=True)
            with open(fallback_full_path, "w", encoding="utf-8") as out_f:
                out_f.write(f.content)
            print(f"📄 Saved (Local Fallback): {f.path}/{f.filename}")
        except Exception as e:
            print(f"❌ Error writing local fallback file: {e}")

    # ── Safe Setup Command Execution ─────────────────────────────────────────
    try:
        base_dir = "/Users/nikomendez/Documents/SWdevAIgency_project"
        safe_commands = []
        all_cmds = []
        if developer_output.backend and developer_output.backend.setup_commands:
            all_cmds.extend(developer_output.backend.setup_commands)
        if developer_output.frontend and developer_output.frontend.setup_commands:
            all_cmds.extend(developer_output.frontend.setup_commands)
            
        for cmd in all_cmds:
            cmd_lower = cmd.lower().strip()
            # Whitelist safe dependencies installation and client generation commands
            if any(k in cmd_lower for k in ["install", "pub get", "generate", "ci", "build"]):
                # Exclude interactive/blocking server/migration commands to prevent hangs
                if not any(b in cmd_lower for b in ["start", "run", "watch", "migrate"]):
                    safe_commands.append(cmd)
                    
        if safe_commands:
            print(f"\n📦 [Setup] Detected {len(safe_commands)} safe setup commands to automatically execute...")
            for cmd in safe_commands:
                print(f"⚙️ [Setup] Running: {cmd} ...")
                proc = await asyncio.create_subprocess_shell(
                    cmd,
                    cwd=base_dir,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await proc.communicate()
                if proc.returncode == 0:
                    print(f"✅ [Setup] Successfully completed: {cmd}")
                else:
                    err_msg = stderr.decode().strip() or stdout.decode().strip()
                    print(f"⚠️ [Setup] '{cmd}' finished or warned: {err_msg[:200]}")
    except Exception as exc:
        print(f"⚠️ [Setup] Error executing safe setup commands: {exc}")


def run_backend_agent(architect_output: ArchitectOutput, designer_output: Optional[UIDesignerOutput] = None) -> BackendOutput:
    """Generate backend code from the architect's output and write files to disk."""
    
    # Connect Context7 and Filesystem
    context7_client = ThreadSafeMCPClient("npx", ["-y", "@upstash/context7-mcp@latest"])
    filesystem_client = ThreadSafeMCPClient("npx", ["-y", "@modelcontextprotocol/server-filesystem", "/Users/nikomendez/Documents/SWdevAIgency_project"])
    
    tools = context7_client.get_tools() + filesystem_client.get_tools()
    
    llm = llm_developer

    agent = create_react_agent(llm, tools=tools)
    arch_json = architect_output.model_dump_json(indent=2)
    
    prompt = (
        f"{BACKEND_SYSTEM_PROMPT}\n\n"
        "Generate the complete backend code based on this architecture. "
        "If you need to consult documentation about NestJS, TypeORM, Postgres, etc., use Context7. "
        "Additionally, you can use Filesystem tools to verify files if needed. "
        "IMPORTANT: DO NOT search, list, or read files in directories outside the current project's backend, "
        "especially NEVER enter folders like 'gestor_gastos' or 'fintrack_app'. "
        "Only operate within the development context of this current project.\n\n"
        f"{arch_json}"
    )

    print("☕  Backend Developer Agent consulting tools and writing backend...")
    response = agent.invoke({"messages": [HumanMessage(content=prompt)]}, config={"recursion_limit": 10})
    
    final_message = response["messages"][-1].content
    cleaned = clean_llm_response(final_message)
    cleaned = _fix_json(cleaned)

    try:
        data = json_repair.loads(cleaned)
        return BackendOutput.model_validate(data)
    except Exception as exc:
        print(f"   ⚠️ Backend parsing failed: {exc}. Retrying with direct prompt...")
        messages = [
            SystemMessage(content=BACKEND_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
            HumanMessage(content=RETRY_PROMPT.format(error=str(exc)))
        ]
        retry_res = llm.invoke(messages)
        cleaned_retry = clean_llm_response(retry_res.content)
        cleaned_retry = _fix_json(cleaned_retry)
        data = json_repair.loads(cleaned_retry)
        return BackendOutput.model_validate(data)


def run_frontend_agent(architect_output: ArchitectOutput, designer_output: Optional[UIDesignerOutput] = None) -> FrontendOutput:
    """Generate frontend code from the architect's output and write files to disk."""
    
    # Connect Context7 and Filesystem
    context7_client = ThreadSafeMCPClient("npx", ["-y", "@upstash/context7-mcp@latest"])
    filesystem_client = ThreadSafeMCPClient("npx", ["-y", "@modelcontextprotocol/server-filesystem", "/Users/nikomendez/Documents/SWdevAIgency_project"])
    
    tools = context7_client.get_tools() + filesystem_client.get_tools()
    
    llm = llm_developer

    agent = create_react_agent(llm, tools=tools)
    
    arch_json = architect_output.model_dump_json(indent=2)
    
    # Format DESIGN.md and screen references
    ui_context = ""
    system_prompt = FRONTEND_SYSTEM_PROMPT
    if designer_output:
        system_prompt += "\nImplement the screens faithfully following the design system from the attached DESIGN.md. Colors, typography, and spacing must match the defined tokens exactly."
        ui_context += "# DESIGN.md\n"
        ui_context += f"{designer_output.design_system_notes}\n\n"
        ui_context += "## SCREENS AND VIEWS REFERENCE:\n"
        for scr in designer_output.screens:
            ui_context += f"### Screen: {scr.name}\n"
            ui_context += f"Description: {scr.description}\n"
            if getattr(scr, 'stitch_screen_url', None):
                ui_context += f"Stitch URL: {scr.stitch_screen_url}\n"
            if getattr(scr, 'html_content', None):
                html_snippet = scr.html_content
                if len(html_snippet) > 800:
                    html_snippet = html_snippet[:800] + "\n... [TRUNCATED FOR CONTEXT WINDOW] ..."
                ui_context += f"HTML Reference (Truncated):\n```html\n{html_snippet}\n```\n"
            ui_context += "\n"
    else:
        ui_context = "No UI design provided."
        
    prompt = (
        f"Generate the complete Flutter frontend code based on this architecture and the provided screen design (Google Stitch). "
        "If you need to consult documentation about Flutter, Widgets, http, etc., use Context7. "
        "Additionally, you can use Filesystem tools to verify files if needed. "
        "IMPORTANT: DO NOT search, list, or read files in directories outside the current project's frontend, "
        "especially NEVER enter folders like 'gestor_gastos' or 'fintrack_app'. "
        "Only operate within the development context of this current project.\n\n"
        f"ARCHITECTURE:\n{arch_json}\n\n"
        f"INTERFACE DESIGN AND SCREENS:\n{ui_context}"
    )

    print("📱  Frontend Developer Agent consulting tools and writing frontend...")
    response = agent.invoke({"messages": [HumanMessage(content=prompt)]}, config={"recursion_limit": 10})
    
    final_message = response["messages"][-1].content
    cleaned = clean_llm_response(final_message)
    cleaned = _fix_json(cleaned)

    try:
        data = json_repair.loads(cleaned)
        return FrontendOutput.model_validate(data)
    except Exception as exc:
        print(f"   ⚠️ Frontend parsing failed: {exc}. Retrying with direct prompt...")
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt),
            HumanMessage(content=RETRY_PROMPT.format(error=str(exc)))
        ]
        retry_res = llm.invoke(messages)
        cleaned_retry = clean_llm_response(retry_res.content)
        cleaned_retry = _fix_json(cleaned_retry)
        data = json_repair.loads(cleaned_retry)
        return FrontendOutput.model_validate(data)
