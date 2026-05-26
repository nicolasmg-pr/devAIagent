import asyncio
import threading
from typing import List, Dict, Any, Optional
from langchain_core.tools import StructuredTool
from pydantic import create_model, Field

class ThreadSafeMCPClient:
    """A thread-safe synchronous wrapper around asynchronous MCP stdio clients.
    
    Manages the lifecycle of stdio MCP servers in a background event loop.
    """

    def __init__(self, command: str, args: List[str], env: Optional[Dict[str, str]] = None):
        self.command = command
        self.args = args
        self.env = env
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        
        self.raw_tools = []
        self.session = None
        self.client_context = None
        
        # Connect synchronously and fetch tools
        try:
            self.raw_tools = self._run_async(self._connect_and_list())
            print(f"🔌 [MCP] Connected to {command} {' '.join(args)}. {len(self.raw_tools)} tools loaded.")
        except Exception as e:
            print(f"⚠️ [MCP] Error connecting to {command} {' '.join(args)}: {e}")

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def _run_async(self, coro):
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return future.result()

    async def _connect_and_list(self):
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        
        server_params = StdioServerParameters(
            command=self.command,
            args=self.args,
            env=self.env
        )
        self.client_context = stdio_client(server_params)
        self.read, self.write = await self.client_context.__aenter__()
        self.session = ClientSession(self.read, self.write)
        await self.session.__aenter__()
        await self.session.initialize()
        
        tools_list = await self.session.list_tools()
        return tools_list.tools

    def call_tool(self, name: str, arguments: dict) -> str:
        try:
            return self._run_async(self._call_tool(name, arguments))
        except Exception as e:
            return f"Error executing tool {name}: {e}"

    async def _call_tool(self, name: str, arguments: dict) -> str:
        res = await self.session.call_tool(name, arguments)
        output_text = ""
        for block in res.content:
            if getattr(block, "type", None) == "text":
                output_text += getattr(block, "text", "") + "\n"
        
        output_stripped = output_text.strip()
        if len(output_stripped) > 7000:
            print(f"⚠️  [MCP] Truncating response from {name} ({len(output_stripped)} characters -> 7000)")
            output_stripped = output_stripped[:7000] + "\n\n... [TRUNCATED - Output too long for LLM context window] ..."
        return output_stripped

    def get_tools(self) -> List[StructuredTool]:
        lc_tools = []
        for tool_def in self.raw_tools:
            name = tool_def.name
            description = tool_def.description or ""
            input_schema = tool_def.inputSchema or {}
            
            # Build Pydantic args model dynamically
            fields = {}
            properties = input_schema.get("properties", {})
            required = input_schema.get("required", [])
            
            for prop_name, prop_details in properties.items():
                prop_type_str = prop_details.get("type", "string")
                prop_desc = prop_details.get("description", "")
                
                python_type = str
                if prop_type_str == "integer":
                    python_type = int
                elif prop_type_str == "boolean":
                    python_type = bool
                elif prop_type_str == "number":
                    python_type = float
                elif prop_type_str == "array":
                    python_type = list
                elif prop_type_str == "object":
                    python_type = dict
                    
                is_req = prop_name in required
                default = ... if is_req else None
                fields[prop_name] = (python_type, Field(default=default, description=prop_desc))
            
            args_schema = create_model(f"{name}_args", **fields)
            
            def _create_func(tool_name: str):
                def _tool_func(**kwargs) -> str:
                    filtered_args = {k: v for k, v in kwargs.items() if v is not None}
                    return self.call_tool(tool_name, filtered_args)
                return _tool_func

            lc_tool = StructuredTool.from_function(
                func=_create_func(name),
                name=name,
                description=description,
                args_schema=args_schema,
            )
            lc_tools.append(lc_tool)
        return lc_tools

import os

CONTEXT7_MCP_CONFIG = {
    "command": "npx",
    "args": ["-y", "@upstash/context7-mcp@latest"]
}

FILESYSTEM_MCP_CONFIG = {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/nikomendez/Documents/SWdevAIgency_project"]
}

PLAYWRIGHT_MCP_CONFIG = {
    "command": "npx",
    "args": ["-y", "@playwright/mcp@latest"]
}

GITHUB_MCP_CONFIG = {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"]
}

def get_mcp_tools(mcp_config: dict, transport: str = "stdio") -> List[StructuredTool]:
    """Helper function to connect to an MCP server and return its tools with graceful degradation."""
    try:
        env = None
        if "server-github" in "".join(mcp_config.get("args", [])):
            token = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN") or os.environ.get("GITHUB_TOKEN")
            if not token:
                print("⚠️ [MCP] GITHUB_PERSONAL_ACCESS_TOKEN or GITHUB_TOKEN not found in env.")
                return []
            env = {"GITHUB_PERSONAL_ACCESS_TOKEN": token}
            
        client = ThreadSafeMCPClient(
            command=mcp_config["command"],
            args=mcp_config["args"],
            env=env
        )
        tools = client.get_tools()
        if not tools:
            print(f"⚠️ [MCP] No tools retrieved from {mcp_config.get('command')}")
            return []
        return tools
    except Exception as e:
        print(f"⚠️ [MCP] Connection with MCP server {mcp_config.get('command')} failed: {e}")
        return []
