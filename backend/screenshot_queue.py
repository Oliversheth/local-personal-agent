from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import base64
import os
import uuid
from datetime import datetime
import json

from tools import screenshot, ocr, ocr_from_file
from memory import store_screenshot_analysis, retrieve_context

router = APIRouter()

# In-memory storage for screenshot queue (in production, use Redis or database)
screenshot_queue = []
extra_screenshot_queue = []

class ScreenshotItem(BaseModel):
    id: str
    timestamp: str
    path: Optional[str] = None
    preview: Optional[str] = None  # base64 encoded thumbnail
    analysis: Optional[str] = None
    ocr_text: Optional[str] = None

class ScreenshotRequest(BaseModel):
    store_in_memory: bool = True
    analyze: bool = True
    ocr: bool = True

class ScreenshotResponse(BaseModel):
    id: str
    timestamp: str
    preview: str
    analysis: Optional[str] = None
    ocr_text: Optional[str] = None

class QueueResponse(BaseModel):
    queue: List[ScreenshotItem]
    extra_queue: List[ScreenshotItem]
    total_count: int

@router.post("/screenshot", response_model=ScreenshotResponse)
async def take_screenshot_api(request: ScreenshotRequest):
    """
    Take a screenshot and optionally analyze it
    """
    try:
        # Take screenshot
        screenshot_b64 = screenshot()
        
        # Create screenshot item
        screenshot_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Initialize analysis and OCR
        analysis = None
        ocr_text = None
        
        # Perform OCR if requested
        if request.ocr:
            try:
                ocr_text = ocr(screenshot_b64)
            except Exception as e:
                print(f"OCR failed: {str(e)}")
        
        # Perform analysis if requested
        if request.analyze:
            try:
                # Import here to avoid circular imports
                import requests
                from main import OLLAMA_URL, CONTROL_MODEL, SYSTEM_PROMPT
                
                # Get context from memory
                context = retrieve_context("screenshot analysis") if request.store_in_memory else ""
                
                # Build prompt for analysis
                prompt = f"{SYSTEM_PROMPT}\n\n"
                if context:
                    prompt += f"Context from previous screenshots:\n{context}\n\n"
                
                prompt += "Analyze this screenshot and describe what you see. Focus on:\n"
                prompt += "1. UI elements and their purpose\n"
                prompt += "2. Any text or content visible\n"
                prompt += "3. Possible actions the user might want to take\n"
                
                if ocr_text:
                    prompt += f"\nOCR Text found: {ocr_text}\n"
                
                prompt += "Keep the analysis concise but informative."
                
                # Call Ollama for analysis
                response = requests.post(
                    f"{OLLAMA_URL}/api/generate",
                    json={
                        "model": CONTROL_MODEL,
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    analysis = response.json().get("response", "")
            except Exception as e:
                print(f"Analysis failed: {str(e)}")
        
        # Store in memory if requested
        if request.store_in_memory and (analysis or ocr_text):
            store_screenshot_analysis(screenshot_id, analysis or "", ocr_text or "")
        
        # Create screenshot item
        screenshot_item = ScreenshotItem(
            id=screenshot_id,
            timestamp=timestamp,
            preview=screenshot_b64,
            analysis=analysis,
            ocr_text=ocr_text
        )
        
        # Add to queue
        screenshot_queue.append(screenshot_item)
        
        # Keep only last 10 screenshots in queue
        if len(screenshot_queue) > 10:
            screenshot_queue.pop(0)
        
        return ScreenshotResponse(
            id=screenshot_id,
            timestamp=timestamp,
            preview=screenshot_b64,
            analysis=analysis,
            ocr_text=ocr_text
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to take screenshot: {str(e)}"
        )

@router.get("/queue", response_model=QueueResponse)
async def get_screenshot_queue():
    """
    Get the current screenshot queue
    """
    return QueueResponse(
        queue=screenshot_queue,
        extra_queue=extra_screenshot_queue,
        total_count=len(screenshot_queue) + len(extra_screenshot_queue)
    )

@router.delete("/queue/{screenshot_id}")
async def delete_screenshot(screenshot_id: str):
    """
    Delete a screenshot from the queue
    """
    global screenshot_queue, extra_screenshot_queue
    
    # Remove from main queue
    screenshot_queue = [item for item in screenshot_queue if item.id != screenshot_id]
    
    # Remove from extra queue
    extra_screenshot_queue = [item for item in extra_screenshot_queue if item.id != screenshot_id]
    
    return {"success": True, "message": f"Screenshot {screenshot_id} deleted"}

@router.post("/queue/clear")
async def clear_queue():
    """
    Clear the screenshot queue
    """
    global screenshot_queue, extra_screenshot_queue
    
    screenshot_queue.clear()
    extra_screenshot_queue.clear()
    
    return {"success": True, "message": "Queue cleared"}

@router.post("/queue/{screenshot_id}/move-to-extra")
async def move_to_extra_queue(screenshot_id: str):
    """
    Move a screenshot from main queue to extra queue
    """
    global screenshot_queue, extra_screenshot_queue
    
    # Find and remove from main queue
    item_to_move = None
    for i, item in enumerate(screenshot_queue):
        if item.id == screenshot_id:
            item_to_move = screenshot_queue.pop(i)
            break
    
    if item_to_move:
        extra_screenshot_queue.append(item_to_move)
        return {"success": True, "message": f"Screenshot {screenshot_id} moved to extra queue"}
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Screenshot {screenshot_id} not found in main queue"
        )

@router.get("/queue/{screenshot_id}/analyze")
async def analyze_screenshot(screenshot_id: str):
    """
    Analyze a specific screenshot
    """
    # Find screenshot in either queue
    screenshot_item = None
    for item in screenshot_queue + extra_screenshot_queue:
        if item.id == screenshot_id:
            screenshot_item = item
            break
    
    if not screenshot_item:
        raise HTTPException(
            status_code=404,
            detail=f"Screenshot {screenshot_id} not found"
        )
    
    try:
        # Import here to avoid circular imports
        import requests
        from main import OLLAMA_URL, CONTROL_MODEL, SYSTEM_PROMPT
        
        # Get context from memory
        context = retrieve_context("screenshot analysis")
        
        # Build prompt for analysis
        prompt = f"{SYSTEM_PROMPT}\n\n"
        if context:
            prompt += f"Context from previous screenshots:\n{context}\n\n"
        
        prompt += "Analyze this screenshot in detail. Describe:\n"
        prompt += "1. What application or website is shown\n"
        prompt += "2. Key UI elements and their functions\n"
        prompt += "3. Any text content visible\n"
        prompt += "4. Suggested actions the user might want to take\n"
        
        if screenshot_item.ocr_text:
            prompt += f"\nOCR Text: {screenshot_item.ocr_text}\n"
        
        # Call Ollama for analysis
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": CONTROL_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"Ollama API error: {response.text}"
            )
        
        analysis = response.json().get("response", "")
        
        # Update the screenshot item
        screenshot_item.analysis = analysis
        
        # Store in memory
        store_screenshot_analysis(screenshot_id, analysis, screenshot_item.ocr_text or "")
        
        return {
            "screenshot_id": screenshot_id,
            "analysis": analysis,
            "ocr_text": screenshot_item.ocr_text
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze screenshot: {str(e)}"
        )