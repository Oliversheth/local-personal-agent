from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel
import requests
import os
from typing import List, Optional, Dict, Any
import json
import asyncio

# Load environment variables
load_dotenv()

# Import multi-agent system
from multi_agent import MultiAgentOrchestrator, AgentRole, TaskStatus
from enterprise_tools import EnterpriseTools
from quant.trading_system import QuantSystem, BollingerBandsStrategy, MomentumStrategy
from datetime import datetime

app = FastAPI(title="Autonomous AI Agent System", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "file://*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
CONTROL_MODEL = os.getenv("CONTROL_MODEL", "codellama:instruct")
CODE_MODEL = os.getenv("CODE_MODEL", "deepseek-coder")

# Enhanced system prompt for multi-agent coordination
SYSTEM_PROMPT = """You are part of an autonomous multi-agent AI system capable of end-to-end execution of complex tasks.

AVAILABLE AGENTS:
- Planner Agent (codellama:instruct): Breaks objectives into subtasks and coordinates execution
- Designer Agent (codellama:instruct): Creates specifications, architectures, and strategic designs  
- Coder Agent (deepseek-coder): Implements code, configurations, and technical solutions
- Context Agent: Maintains memory and system awareness

AVAILABLE TOOLS:
1. Enterprise Development:
   - write_file(path, content): Create/modify files
   - run_shell(command): Execute shell commands
   - git_init/commit/push: Git operations
   - docker_build/run: Docker operations
   - install_dependencies(lang, packages): Package installation
   - create_project(name, type): Scaffold projects
   - deploy_local(type): Local deployment

2. System Automation:
   - screenshot(): Capture screen
   - ocr(image): Extract text from images
   - click(x, y): Mouse operations
   - type(text): Keyboard input
   - read/write_clipboard(): Clipboard operations

3. Quantitative Trading:
   - backtest_strategy(strategy, params): Run strategy backtests
   - optimize_strategy(strategy, ranges): Parameter optimization
   - generate_market_data(symbol, dates): Create test data
   - risk_analysis(portfolio, limits): Risk assessment

4. Memory & Context:
   - store_context(id, content): Store information
   - retrieve_context(query): Get relevant context
   - update_memory(session_data): Update knowledge base

CAPABILITIES:
- Build complete full-stack applications (React, Python, Node.js, Go)
- Develop quantitative trading strategies with backtesting
- Create enterprise-grade deployments with Docker/K8s
- Implement CI/CD pipelines and testing frameworks
- Perform complex automation and system interactions
- Maintain persistent context across sessions

Always think step-by-step, coordinate with other agents as needed, and execute tasks autonomously until completion."""

# Initialize systems
orchestrator = MultiAgentOrchestrator(OLLAMA_URL, CONTROL_MODEL, CODE_MODEL)
enterprise_tools = EnterpriseTools()
quant_system = QuantSystem()

# Initialize trading strategies
quant_system.register_strategy("bollinger_bands", BollingerBandsStrategy())
quant_system.register_strategy("momentum", MomentumStrategy())

# Pydantic models
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

class Choice(BaseModel):
    message: Message

class ChatResponse(BaseModel):
    choices: List[Choice]

class TaskSubmissionRequest(BaseModel):
    objective: str
    context: Optional[str] = None
    priority: str = "normal"

class TaskStatusResponse(BaseModel):
    session_id: str
    status: str
    progress: float
    current_task: Optional[str]
    tasks: List[Dict[str, Any]]

# Active sessions tracking
active_sessions: Dict[str, Dict[str, Any]] = {}

@app.post("/v1/chat/completions", response_model=ChatResponse)
async def chat_completions(request: ChatRequest, background_tasks: BackgroundTasks):
    """
    Enhanced chat completions with multi-agent orchestration
    """
    try:
        # Check if this is a complex task that needs multi-agent handling
        user_message = ""
        for msg in reversed(request.messages):
            if msg.role == "user":
                user_message = msg.content
                break
        
        # Detect if this requires multi-agent processing
        if await _requires_multi_agent(user_message):
            # Start multi-agent processing in background
            session_id = await _start_multi_agent_task(user_message, background_tasks)
            
            response_content = f"""I've initiated a multi-agent team to handle your complex request: "{user_message}"

Your task has been assigned session ID: {session_id}

The system will:
1. **Planner Agent** will break down your objective into detailed subtasks
2. **Designer Agent** will create specifications and architectural designs  
3. **Coder Agent** will implement the solution with code and configurations
4. **Context Agent** will maintain awareness and memory throughout

You can monitor progress at `/v1/tasks/{session_id}/status` or through the Task Dashboard.

The team is now working autonomously to complete your request end-to-end."""
        else:
            # Handle as regular chat with context retrieval
            from memory import retrieve_context
            
            context = retrieve_context(user_message) if user_message else ""
            
            prompt = SYSTEM_PROMPT + "\n\n"
            if context:
                prompt += f"Context:\n{context}\n\n"
            
            for message in request.messages:
                prompt += f"{message.role}: {message.content}\n"
            
            ollama_response = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": CONTROL_MODEL,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            
            if ollama_response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"Ollama API error: {ollama_response.text}"
                )
            
            response_data = ollama_response.json()
            response_content = response_data.get("response", "")
        
        return ChatResponse(
            choices=[
                Choice(
                    message=Message(
                        role="assistant",
                        content=response_content
                    )
                )
            ]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

async def _requires_multi_agent(message: str) -> bool:
    """Determine if a message requires multi-agent processing"""
    complex_keywords = [
        "build", "create", "develop", "implement", "deploy", "application", "app",
        "trading", "strategy", "backtest", "system", "full-stack", "enterprise",
        "automated", "end-to-end", "complete", "comprehensive", "production"
    ]
    
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in complex_keywords)

async def _start_multi_agent_task(objective: str, background_tasks: BackgroundTasks) -> str:
    """Start multi-agent task processing"""
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Store session info
    active_sessions[session_id] = {
        "objective": objective,
        "status": "initiated",
        "progress": 0.0,
        "start_time": datetime.now(),
        "current_task": "Initializing multi-agent system"
    }
    
    # Start processing in background
    background_tasks.add_task(_process_multi_agent_task, session_id, objective)
    
    return session_id

async def _process_multi_agent_task(session_id: str, objective: str):
    """Process multi-agent task in background"""
    try:
        active_sessions[session_id]["status"] = "processing"
        active_sessions[session_id]["current_task"] = "Planning and coordination"
        
        # Run multi-agent orchestration
        result = await orchestrator.process_goal(objective)
        
        # Update session with results
        active_sessions[session_id].update({
            "status": "completed",
            "progress": 100.0,
            "result": result,
            "end_time": datetime.now()
        })
        
    except Exception as e:
        active_sessions[session_id].update({
            "status": "failed",
            "error": str(e),
            "end_time": datetime.now()
        })

@app.post("/v1/tasks/submit")
async def submit_task(request: TaskSubmissionRequest, background_tasks: BackgroundTasks):
    """Submit a high-level task for autonomous execution"""
    session_id = await _start_multi_agent_task(request.objective, background_tasks)
    
    return {
        "session_id": session_id,
        "status": "submitted",
        "objective": request.objective,
        "message": "Task submitted for autonomous execution"
    }

@app.get("/v1/tasks/{session_id}/status", response_model=TaskStatusResponse)
async def get_task_status(session_id: str):
    """Get status of a specific task"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_data = active_sessions[session_id]
    orchestrator_status = orchestrator.get_session_status(session_id)
    
    return TaskStatusResponse(
        session_id=session_id,
        status=session_data.get("status", "unknown"),
        progress=session_data.get("progress", 0.0),
        current_task=session_data.get("current_task"),
        tasks=orchestrator_status.get("tasks", [])
    )

@app.get("/v1/tasks")
async def list_tasks():
    """List all active and recent tasks"""
    return {
        "active_sessions": len([s for s in active_sessions.values() if s.get("status") == "processing"]),
        "total_sessions": len(active_sessions),
        "sessions": [
            {
                "session_id": sid,
                "objective": data.get("objective", ""),
                "status": data.get("status", "unknown"),
                "progress": data.get("progress", 0.0),
                "start_time": data.get("start_time").isoformat() if data.get("start_time") else None
            }
            for sid, data in active_sessions.items()
        ]
    }

@app.get("/v1/models")
async def list_models():
    """List available models from Ollama"""
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=30)
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch models from Ollama: {response.text}"
            )
        
        ollama_models = response.json().get("models", [])
        models = [
            {"id": model["name"], "object": "model", "created": 1234567890, "owned_by": "local"}
            for model in ollama_models
        ]
        
        return {"object": "list", "data": models}
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to connect to Ollama: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Enhanced health check with system status"""
    return {
        "status": "healthy",
        "ollama_url": OLLAMA_URL,
        "active_sessions": len(active_sessions),
        "agents_available": ["planner", "designer", "coder", "context"],
        "tools_available": ["enterprise_dev", "automation", "trading", "memory"],
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)