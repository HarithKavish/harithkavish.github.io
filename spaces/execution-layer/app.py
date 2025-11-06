"""
Execution Layer - Tool Calling & Action Execution
HuggingFace Space: harithkavish/execution-layer
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import os
import httpx
from datetime import datetime

app = FastAPI(
    title="Execution Layer",
    description="Tool calling and action execution service",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration - Specialized for action execution
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "HarithKavish")

# System purpose for this layer
EXECUTION_MISSION = """This layer handles all external actions, tool calls, and API integrations.
Specialized for: GitHub API calls, web requests, data fetching, external tool execution."""

# Request/Response Models
class ExecuteActionRequest(BaseModel):
    action: str
    parameters: Dict[str, Any]

class ExecuteActionResponse(BaseModel):
    status: str
    result: Any
    execution_time_ms: float
    action: str

class ListToolsResponse(BaseModel):
    tools: List[Dict]
    count: int


# Available tools/actions
AVAILABLE_TOOLS = {
    "check_project_status": {
        "description": "Check if a GitHub project/space is online",
        "parameters": {
            "project_name": "Name of the project (e.g., 'SkinNet-Analyzer')"
        }
    },
    "get_github_stats": {
        "description": "Get GitHub repository statistics",
        "parameters": {
            "repo_name": "Repository name"
        }
    },
    "get_current_time": {
        "description": "Get current date and time",
        "parameters": {}
    },
    "calculate": {
        "description": "Perform mathematical calculations",
        "parameters": {
            "expression": "Math expression to evaluate"
        }
    }
}


@app.on_event("startup")
async def startup_event():
    """Initialize Execution Layer."""
    print("🚀 Loading Execution Layer...")
    print("   🔧 Specialized for: Tool Calling & External Actions")
    print(f"   Mission: {EXECUTION_MISSION}")
    print(f"   Available Tools: {len(AVAILABLE_TOOLS)}")
    for tool_name in AVAILABLE_TOOLS.keys():
        print(f"      • {tool_name}")
    print("✓ Execution Layer ready!")


async def check_project_status(project_name: str) -> Dict:
    """Check if a project/service is online."""
    
    # Map project names to URLs
    project_urls = {
        "skinnet": "https://harithkavish.github.io/SkinNet-Analyzer/",
        "skinnet-analyzer": "https://harithkavish.github.io/SkinNet-Analyzer/",
        "object-detector": "https://harithkavish.github.io/Multi-Object-Detection-using-YOLO/",
        "portfolio": "https://harithkavish.github.io/"
    }
    
    url = project_urls.get(project_name.lower())
    
    if not url:
        return {
            "status": "unknown",
            "message": f"Project '{project_name}' not found in registry"
        }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            
            return {
                "status": "online" if response.status_code == 200 else "offline",
                "status_code": response.status_code,
                "url": url,
                "response_time_ms": response.elapsed.total_seconds() * 1000
            }
    except Exception as e:
        return {
            "status": "unreachable",
            "error": str(e),
            "url": url
        }


async def get_github_stats(repo_name: str) -> Dict:
    """Get GitHub repository statistics."""
    
    if not GITHUB_TOKEN:
        return {"error": "GitHub token not configured"}
    
    try:
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}"
            response = await client.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "name": data.get("name"),
                    "description": data.get("description"),
                    "stars": data.get("stargazers_count"),
                    "forks": data.get("forks_count"),
                    "watchers": data.get("watchers_count"),
                    "language": data.get("language"),
                    "last_updated": data.get("updated_at"),
                    "url": data.get("html_url")
                }
            else:
                return {"error": f"Repository not found: {repo_name}"}
                
    except Exception as e:
        return {"error": str(e)}


def get_current_time() -> Dict:
    """Get current date and time."""
    now = datetime.now()
    return {
        "datetime": now.isoformat(),
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "day_of_week": now.strftime("%A"),
        "timezone": "UTC"
    }


def calculate(expression: str) -> Dict:
    """Safely evaluate mathematical expression."""
    try:
        # Simple whitelist of allowed operations
        allowed_chars = set("0123456789+-*/.()")
        if not all(c in allowed_chars or c.isspace() for c in expression):
            return {"error": "Invalid characters in expression"}
        
        result = eval(expression, {"__builtins__": {}}, {})
        return {
            "expression": expression,
            "result": result
        }
    except Exception as e:
        return {
            "error": f"Calculation failed: {str(e)}",
            "expression": expression
        }


@app.post("/execute", response_model=ExecuteActionResponse)
async def execute_action(request: ExecuteActionRequest):
    """Execute an action/tool."""
    
    start_time = datetime.now()
    
    action = request.action
    params = request.parameters
    
    # Route to appropriate handler
    if action == "check_project_status":
        result = await check_project_status(params.get("project_name", ""))
    
    elif action == "get_github_stats":
        result = await get_github_stats(params.get("repo_name", ""))
    
    elif action == "get_current_time":
        result = get_current_time()
    
    elif action == "calculate":
        result = calculate(params.get("expression", ""))
    
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown action: {action}. Available: {list(AVAILABLE_TOOLS.keys())}"
        )
    
    execution_time = (datetime.now() - start_time).total_seconds() * 1000
    
    return ExecuteActionResponse(
        status="completed",
        result=result,
        execution_time_ms=round(execution_time, 2),
        action=action
    )


@app.get("/tools", response_model=ListToolsResponse)
async def list_tools():
    """List available tools/actions."""
    tools = [
        {
            "name": name,
            "description": info["description"],
            "parameters": info["parameters"]
        }
        for name, info in AVAILABLE_TOOLS.items()
    ]
    
    return ListToolsResponse(
        tools=tools,
        count=len(tools)
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "execution-layer",
        "version": "1.0.0",
        "available_tools": len(AVAILABLE_TOOLS),
        "github_integration": GITHUB_TOKEN is not None
    }


@app.get("/")
async def root():
    """Root endpoint with service info."""
    return {
        "service": "Execution Layer",
        "description": "Tool calling and action execution service",
        "version": "1.0.0",
        "endpoints": {
            "POST /execute": "Execute an action/tool",
            "GET /tools": "List available tools",
            "GET /health": "Health check"
        },
        "available_tools": list(AVAILABLE_TOOLS.keys()),
        "status": "operational"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
