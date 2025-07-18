from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel
import requests
import os
from typing import List, Optional
import json

# Load environment variables
load_dotenv()

app = FastAPI(title="Local AI Assistant API", version="1.0.0")

# Include screenshot queue router
from screenshot_queue import router as screenshot_router
app.include_router(screenshot_router, prefix="/api/screenshot", tags=["screenshots"])

# Include tools router
from tools_router import router as tools_router
app.include_router(tools_router, prefix="/api/tools", tags=["tools"])

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

# System prompt
SYSTEM_PROMPT = """You are an OS-level automation assistant. Always think step-by-step. Use screenshot(), ocr(), click(x,y), type(text), read_clipboard(), write_clipboard() and retrieve_context() as needed. For coding tasks, prefer deepseek-coder. Ask clarifying questions if uncertain."""

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

class Model(BaseModel):
    id: str
    object: str = "model"
    created: int = 1234567890
    owned_by: str = "local"

class ModelsResponse(BaseModel):
    object: str = "list"
    data: List[Model]

@app.post("/v1/chat/completions", response_model=ChatResponse)
async def chat_completions(request: ChatRequest):
    """
    OpenAI-compatible chat completions endpoint
    """
    try:
        # Prepare context retrieval
        from memory import retrieve_context
        
        # Get the last user message for context
        user_message = ""
        for msg in reversed(request.messages):
            if msg.role == "user":
                user_message = msg.content
                break
        
        # Retrieve context from memory
        context = retrieve_context(user_message) if user_message else ""
        
        # Build the prompt
        prompt = SYSTEM_PROMPT + "\n\n"
        if context:
            prompt += f"Context:\n{context}\n\n"
        
        # Add conversation history
        for message in request.messages:
            prompt += f"{message.role}: {message.content}\n"
        
        # Call Ollama API
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
        response_text = response_data.get("response", "")
        
        # Check if this is a code task that needs the code model
        if response_text.startswith("CODE_TASK_DETECTED:"):
            # Extract task description
            task = response_text.replace("CODE_TASK_DETECTED:", "").strip()
            
            # Call the code model
            code_response = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": CODE_MODEL,
                    "prompt": f"{SYSTEM_PROMPT}\n\nCoding Task: {task}",
                    "stream": False
                },
                timeout=60
            )
            
            if code_response.status_code == 200:
                code_data = code_response.json()
                response_text = code_data.get("response", response_text)
        
        # Return OpenAI-compatible response
        return ChatResponse(
            choices=[
                Choice(
                    message=Message(
                        role="assistant",
                        content=response_text
                    )
                )
            ]
        )
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to connect to Ollama: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/v1/models", response_model=ModelsResponse)
async def list_models():
    """
    List available models from Ollama
    """
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=30)
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch models from Ollama: {response.text}"
            )
        
        ollama_models = response.json().get("models", [])
        models = [
            Model(id=model["name"]) 
            for model in ollama_models
        ]
        
        return ModelsResponse(data=models)
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to connect to Ollama: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "ollama_url": OLLAMA_URL}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)