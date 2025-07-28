import os
import subprocess
from typing import Tuple, Optional, Dict, Any
import base64
import io
from PIL import Image
import pytesseract

# Handle headless environment
HEADLESS_MODE = 'DISPLAY' not in os.environ

if not HEADLESS_MODE:
    try:
        import pyautogui
        import pyperclip
        # Configure pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
    except Exception as e:
        print(f"Warning: GUI tools not available: {e}")
        HEADLESS_MODE = True
else:
    print("Running in headless mode - GUI tools will be mocked")

def screenshot() -> str:
    """Take a screenshot and return as base64 encoded string"""
    if HEADLESS_MODE:
        # Return a mock screenshot (1x1 black pixel)
        img = Image.new('RGB', (1, 1), color='black')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return img_str
    
    try:
        # Take screenshot
        screenshot_img = pyautogui.screenshot()
        
        # Convert to base64
        buffer = io.BytesIO()
        screenshot_img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return img_str
    except Exception as e:
        raise Exception(f"Failed to take screenshot: {str(e)}")

def ocr(image_data: str) -> str:
    """Perform OCR on base64 encoded image data"""
    try:
        # Decode base64 image
        img_data = base64.b64decode(image_data)
        img = Image.open(io.BytesIO(img_data))
        
        # Perform OCR
        text = pytesseract.image_to_string(img)
        return text.strip()
    except Exception as e:
        if HEADLESS_MODE:
            return f"OCR not available in headless mode: {str(e)}"
        raise Exception(f"OCR failed: {str(e)}")

def ocr_from_file(file_path: str) -> str:
    """Perform OCR on image file"""
    try:
        if not os.path.exists(file_path):
            raise Exception(f"File not found: {file_path}")
        
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img)
        return text.strip()
    except Exception as e:
        if HEADLESS_MODE:
            return f"OCR not available in headless mode: {str(e)}"
        raise Exception(f"OCR failed: {str(e)}")

def click(x: int, y: int) -> bool:
    """Click at specified coordinates"""
    if HEADLESS_MODE:
        print(f"Mock click at ({x}, {y})")
        return True
    
    try:
        pyautogui.click(x, y)
        return True
    except Exception as e:
        raise Exception(f"Click failed: {str(e)}")

def right_click(x: int, y: int) -> bool:
    """Right click at specified coordinates"""
    if HEADLESS_MODE:
        print(f"Mock right click at ({x}, {y})")
        return True
    
    try:
        pyautogui.rightClick(x, y)
        return True
    except Exception as e:
        raise Exception(f"Right click failed: {str(e)}")

def double_click(x: int, y: int) -> bool:
    """Double click at specified coordinates"""
    if HEADLESS_MODE:
        print(f"Mock double click at ({x}, {y})")
        return True
    
    try:
        pyautogui.doubleClick(x, y)
        return True
    except Exception as e:
        raise Exception(f"Double click failed: {str(e)}")

def drag(start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5) -> bool:
    """Drag from start coordinates to end coordinates"""
    if HEADLESS_MODE:
        print(f"Mock drag from ({start_x}, {start_y}) to ({end_x}, {end_y})")
        return True
    
    try:
        pyautogui.drag(end_x - start_x, end_y - start_y, duration=duration, button='left')
        return True
    except Exception as e:
        raise Exception(f"Drag failed: {str(e)}")

def type_text(text: str) -> bool:
    """Type text at current cursor position"""
    if HEADLESS_MODE:
        print(f"Mock type: {text}")
        return True
    
    try:
        pyautogui.typewrite(text)
        return True
    except Exception as e:
        raise Exception(f"Type text failed: {str(e)}")

def press_key(key: str) -> bool:
    """Press a single key"""
    if HEADLESS_MODE:
        print(f"Mock press key: {key}")
        return True
    
    try:
        pyautogui.press(key)
        return True
    except Exception as e:
        raise Exception(f"Press key failed: {str(e)}")

def key_combination(keys: list) -> bool:
    """Press a combination of keys"""
    if HEADLESS_MODE:
        print(f"Mock key combination: {'+'.join(keys)}")
        return True
    
    try:
        pyautogui.hotkey(*keys)
        return True
    except Exception as e:
        raise Exception(f"Key combination failed: {str(e)}")

def scroll(clicks: int, x: Optional[int] = None, y: Optional[int] = None) -> bool:
    """Scroll at specified position (or current mouse position)"""
    if HEADLESS_MODE:
        print(f"Mock scroll: {clicks} clicks at ({x}, {y})")
        return True
    
    try:
        if x is not None and y is not None:
            pyautogui.scroll(clicks, x=x, y=y)
        else:
            pyautogui.scroll(clicks)
        return True
    except Exception as e:
        raise Exception(f"Scroll failed: {str(e)}")

def read_clipboard() -> str:
    """Read text from clipboard"""
    if HEADLESS_MODE:
        return "Mock clipboard content"
    
    try:
        return pyperclip.paste()
    except Exception as e:
        raise Exception(f"Read clipboard failed: {str(e)}")

def write_clipboard(text: str) -> bool:
    """Write text to clipboard"""
    if HEADLESS_MODE:
        print(f"Mock write to clipboard: {text}")
        return True
    
    try:
        pyperclip.copy(text)
        return True
    except Exception as e:
        raise Exception(f"Write clipboard failed: {str(e)}")

def get_screen_size() -> Tuple[int, int]:
    """Get screen dimensions"""
    if HEADLESS_MODE:
        return (1920, 1080)  # Mock screen size
    
    try:
        return pyautogui.size()
    except Exception as e:
        raise Exception(f"Get screen size failed: {str(e)}")

def get_mouse_position() -> Tuple[int, int]:
    """Get current mouse position"""
    if HEADLESS_MODE:
        return (960, 540)  # Mock mouse position
    
    try:
        return pyautogui.position()
    except Exception as e:
        raise Exception(f"Get mouse position failed: {str(e)}")

def move_mouse(x: int, y: int, duration: float = 0.0) -> bool:
    """Move mouse to specified coordinates"""
    if HEADLESS_MODE:
        print(f"Mock move mouse to ({x}, {y})")
        return True
    
    try:
        pyautogui.moveTo(x, y, duration=duration)
        return True
    except Exception as e:
        raise Exception(f"Move mouse failed: {str(e)}")

def find_on_screen(image_path: str, confidence: float = 0.8) -> Optional[Tuple[int, int]]:
    """Find an image on screen and return its center coordinates"""
    if HEADLESS_MODE:
        print(f"Mock find on screen: {image_path}")
        return None
    
    try:
        if not os.path.exists(image_path):
            raise Exception(f"Image file not found: {image_path}")
        
        location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        if location:
            center = pyautogui.center(location)
            return (center.x, center.y)
        return None
    except Exception as e:
        raise Exception(f"Find on screen failed: {str(e)}")

def wait_for_image(image_path: str, timeout: int = 10, confidence: float = 0.8) -> Optional[Tuple[int, int]]:
    """Wait for an image to appear on screen"""
    if HEADLESS_MODE:
        print(f"Mock wait for image: {image_path}")
        return None
    
    import time
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            location = find_on_screen(image_path, confidence)
            if location:
                return location
            time.sleep(0.5)
        except Exception:
            time.sleep(0.5)
    
    return None

def write_file(path: str, content: str) -> Dict[str, Any]:
    """Write content to a file"""
    try:
        # Create directory if it doesn't exist
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            "success": True,
            "message": f"File written successfully: {path}",
            "path": path,
            "size": len(content)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to write file: {path}"
        }

def make_dir(path: str) -> Dict[str, Any]:
    """Create a directory"""
    try:
        os.makedirs(path, exist_ok=True)
        return {
            "success": True,
            "message": f"Directory created successfully: {path}",
            "path": path
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to create directory: {path}"
        }

def run_shell(command: str) -> Dict[str, Any]:
    """Execute a shell command"""
    try:
        # Run the command and capture output
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )
        
        return {
            "success": result.returncode == 0,
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "command": command
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Command timed out after 30 seconds",
            "command": command
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "command": command
        }

def open_app(app_name: str, args: list[str]) -> Dict[str, Any]:
    """Open an application with arguments"""
    try:
        # Build the command
        command = [app_name] + args
        
        # Start the process without waiting for it to finish
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        return {
            "success": True,
            "message": f"Application started successfully: {app_name}",
            "app_name": app_name,
            "args": args,
            "pid": process.pid
        }
    except FileNotFoundError:
        return {
            "success": False,
            "error": f"Application not found: {app_name}",
            "app_name": app_name
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "app_name": app_name
        }

def list_dir(path: str) -> Dict[str, Any]:
    """List contents of a directory"""
    try:
        if not os.path.exists(path):
            return {
                "success": False,
                "error": f"Path does not exist: {path}",
                "path": path
            }
        
        if not os.path.isdir(path):
            return {
                "success": False,
                "error": f"Path is not a directory: {path}",
                "path": path
            }
        
        # Get directory contents
        items = []
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            is_dir = os.path.isdir(item_path)
            
            try:
                stat_info = os.stat(item_path)
                size = stat_info.st_size if not is_dir else None
                modified = stat_info.st_mtime
            except:
                size = None
                modified = None
            
            items.append({
                "name": item,
                "type": "directory" if is_dir else "file",
                "size": size,
                "modified": modified
            })
        
        # Sort items: directories first, then files, both alphabetically
        items.sort(key=lambda x: (x["type"] != "directory", x["name"].lower()))
        
        return {
            "success": True,
            "path": path,
            "items": items,
            "count": len(items)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "path": path
        }