from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Tuple
import json
import base64

from tools import (
    screenshot, ocr, ocr_from_file, click, right_click, double_click, drag,
    type_text, press_key, key_combination, scroll, read_clipboard, write_clipboard,
    get_screen_size, get_mouse_position, move_mouse, find_on_screen, wait_for_image,
    write_file, make_dir, run_shell, open_app, list_dir
)

from vision import web_screenshot, browser_ocr, click_element

router = APIRouter()

class ClickRequest(BaseModel):
    x: int
    y: int

class DragRequest(BaseModel):
    start_x: int
    start_y: int
    end_x: int
    end_y: int
    duration: float = 0.5

class TypeRequest(BaseModel):
    text: str

class KeyRequest(BaseModel):
    key: str

class KeyComboRequest(BaseModel):
    keys: List[str]

class ScrollRequest(BaseModel):
    clicks: int
    x: Optional[int] = None
    y: Optional[int] = None

class ClipboardRequest(BaseModel):
    text: str

class MouseMoveRequest(BaseModel):
    x: int
    y: int
    duration: float = 0.0

class OCRRequest(BaseModel):
    image_data: str  # base64 encoded image

class FindImageRequest(BaseModel):
    image_path: str
    confidence: float = 0.8

class WaitForImageRequest(BaseModel):
    image_path: str
    timeout: int = 10
    confidence: float = 0.8

class WriteFileRequest(BaseModel):
    path: str
    content: str

class MakeDirRequest(BaseModel):
    path: str

class RunShellRequest(BaseModel):
    command: str

class OpenAppRequest(BaseModel):
    app_name: str
    args: List[str] = []

class WebScreenshotRequest(BaseModel):
    url: str

class BrowserOCRRequest(BaseModel):
    input: str  # URL or file path

class ClickElementRequest(BaseModel):
    selector: str

@router.post("/screenshot")
async def take_screenshot_tool():
    """Take a screenshot and return base64 encoded image"""
    try:
        img_data = screenshot()
        return {"success": True, "image_data": img_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ocr")
async def perform_ocr(request: OCRRequest):
    """Perform OCR on base64 encoded image"""
    try:
        text = ocr(request.image_data)
        return {"success": True, "text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ocr/file")
async def perform_ocr_file(file_path: str):
    """Perform OCR on image file"""
    try:
        text = ocr_from_file(file_path)
        return {"success": True, "text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/click")
async def click_tool(request: ClickRequest):
    """Click at specified coordinates"""
    try:
        success = click(request.x, request.y)
        return {"success": success, "message": f"Clicked at ({request.x}, {request.y})"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/right-click")
async def right_click_tool(request: ClickRequest):
    """Right click at specified coordinates"""
    try:
        success = right_click(request.x, request.y)
        return {"success": success, "message": f"Right clicked at ({request.x}, {request.y})"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/double-click")
async def double_click_tool(request: ClickRequest):
    """Double click at specified coordinates"""
    try:
        success = double_click(request.x, request.y)
        return {"success": success, "message": f"Double clicked at ({request.x}, {request.y})"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/drag")
async def drag_tool(request: DragRequest):
    """Drag from start to end coordinates"""
    try:
        success = drag(request.start_x, request.start_y, request.end_x, request.end_y, request.duration)
        return {"success": success, "message": f"Dragged from ({request.start_x}, {request.start_y}) to ({request.end_x}, {request.end_y})"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/type")
async def type_tool(request: TypeRequest):
    """Type text at current cursor position"""
    try:
        success = type_text(request.text)
        return {"success": success, "message": f"Typed: {request.text}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/key")
async def key_tool(request: KeyRequest):
    """Press a single key"""
    try:
        success = press_key(request.key)
        return {"success": success, "message": f"Pressed key: {request.key}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/key-combo")
async def key_combo_tool(request: KeyComboRequest):
    """Press a combination of keys"""
    try:
        success = key_combination(request.keys)
        return {"success": success, "message": f"Pressed key combination: {'+'.join(request.keys)}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scroll")
async def scroll_tool(request: ScrollRequest):
    """Scroll at specified position"""
    try:
        success = scroll(request.clicks, request.x, request.y)
        return {"success": success, "message": f"Scrolled {request.clicks} clicks"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clipboard")
async def read_clipboard_tool():
    """Read text from clipboard"""
    try:
        text = read_clipboard()
        return {"success": True, "text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clipboard")
async def write_clipboard_tool(request: ClipboardRequest):
    """Write text to clipboard"""
    try:
        success = write_clipboard(request.text)
        return {"success": success, "message": f"Copied to clipboard: {request.text}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/screen-size")
async def get_screen_size_tool():
    """Get screen dimensions"""
    try:
        width, height = get_screen_size()
        return {"success": True, "width": width, "height": height}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mouse-position")
async def get_mouse_position_tool():
    """Get current mouse position"""
    try:
        x, y = get_mouse_position()
        return {"success": True, "x": x, "y": y}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/move-mouse")
async def move_mouse_tool(request: MouseMoveRequest):
    """Move mouse to specified coordinates"""
    try:
        success = move_mouse(request.x, request.y, request.duration)
        return {"success": success, "message": f"Moved mouse to ({request.x}, {request.y})"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/find-image")
async def find_image_tool(request: FindImageRequest):
    """Find an image on screen"""
    try:
        position = find_on_screen(request.image_path, request.confidence)
        if position:
            return {"success": True, "found": True, "x": position[0], "y": position[1]}
        else:
            return {"success": True, "found": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/wait-for-image")
async def wait_for_image_tool(request: WaitForImageRequest):
    """Wait for an image to appear on screen"""
    try:
        position = wait_for_image(request.image_path, request.timeout, request.confidence)
        if position:
            return {"success": True, "found": True, "x": position[0], "y": position[1]}
        else:
            return {"success": True, "found": False, "message": "Image not found within timeout"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# New "Hands" & File I/O Tools endpoints

@router.post("/write-file")
async def write_file_tool(request: WriteFileRequest):
    """Write content to a file"""
    try:
        result = write_file(request.path, request.content)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/make-dir")
async def make_dir_tool(request: MakeDirRequest):
    """Create a directory"""
    try:
        result = make_dir(request.path)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run-shell")
async def run_shell_tool(request: RunShellRequest):
    """Execute a shell command"""
    try:
        result = run_shell(request.command)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/open-app")
async def open_app_tool(request: OpenAppRequest):
    """Open an application with arguments"""
    try:
        result = open_app(request.app_name, request.args)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list-dir")
async def list_dir_tool(path: str):
    """List contents of a directory"""
    try:
        result = list_dir(path)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Vision & Browser Interaction Tools

@router.post("/web-screenshot")
async def web_screenshot_tool(request: WebScreenshotRequest):
    """Take a screenshot of a web page and return as base64 encoded image"""
    try:
        screenshot_bytes = await web_screenshot(request.url)
        # Convert bytes to base64 for JSON response
        img_data = base64.b64encode(screenshot_bytes).decode('utf-8')
        return {
            "success": True,
            "image_data": img_data,
            "url": request.url,
            "format": "png"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/browser-ocr")
async def browser_ocr_tool(request: BrowserOCRRequest):
    """Perform OCR on a URL (screenshot first) or image file"""
    try:
        text = browser_ocr(request.input)
        return {
            "success": True,
            "text": text,
            "input": request.input
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/element-click")
async def element_click_tool(request: ClickElementRequest):
    """Click an element using CSS selector via browser automation"""
    try:
        result = await click_element(request.selector)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))