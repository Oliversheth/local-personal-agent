import asyncio
import io
import os
from typing import Dict, Any
from urllib.parse import urlparse

try:
    import pyppeteer
    from pyppeteer import launch
    PYPPETEER_AVAILABLE = True
except ImportError:
    print("Warning: pyppeteer not available")
    PYPPETEER_AVAILABLE = False

try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    print("Warning: OCR tools not available")
    OCR_AVAILABLE = False

from tools import HEADLESS_MODE

async def web_screenshot(url: str) -> bytes:
    """
    Launch headless Chromium, navigate to URL, take a full-page screenshot, return PNG bytes.
    """
    if not PYPPETEER_AVAILABLE:
        raise Exception("pyppeteer is not available - cannot take web screenshots")
    
    if HEADLESS_MODE:
        # In headless mode, return a mock screenshot
        img = Image.new('RGB', (1920, 1080), color='white')
        # Add some text to indicate this is a mock
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    if not url:
        raise Exception("URL is required")
    
    # Validate URL format
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise Exception(f"Invalid URL format: {url}")
    
    browser = None
    try:
        # Launch headless browser with more robust settings for containerized environments
        browser = await launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox', 
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-features=TranslateUI',
                '--disable-ipc-flooding-protection',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ],
            ignoreHTTPSErrors=True,
            slowMo=0,
            devtools=False
        )
        
        # Create new page
        page = await browser.newPage()
        
        # Set viewport size for consistent screenshots
        await page.setViewport({'width': 1920, 'height': 1080})
        
        # Navigate to URL with timeout
        await page.goto(url, {'waitUntil': 'networkidle2', 'timeout': 30000})
        
        # Wait a bit for any dynamic content to load
        await asyncio.sleep(2)
        
        # Take full page screenshot
        screenshot_bytes = await page.screenshot({
            'fullPage': True,
            'type': 'png'
        })
        
        return screenshot_bytes
        
    except Exception as e:
        raise Exception(f"Failed to take web screenshot: {str(e)}")
    finally:
        if browser:
            try:
                await browser.close()
            except Exception:
                pass  # Ignore closing errors

def browser_ocr(input_str: str) -> str:
    """
    If input is a URL, call web_screenshot first; then run pytesseract.image_to_string on the PNG.
    Return extracted text.
    """
    if not OCR_AVAILABLE:
        return "OCR tools not available"
    
    if not input_str:
        raise Exception("Input is required")
    
    try:
        # Check if input is a URL
        parsed = urlparse(input_str)
        is_url = bool(parsed.scheme and parsed.netloc)
        
        if is_url:
            # It's a URL - take screenshot first
            if not PYPPETEER_AVAILABLE:
                raise Exception("pyppeteer is not available - cannot screenshot URLs for OCR")
            
            # Handle event loop issue for URL screenshots
            try:
                # Try to get the current event loop
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is running, we need to run in a separate thread
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(_run_web_screenshot, input_str)
                        screenshot_bytes = future.result()
                else:
                    screenshot_bytes = loop.run_until_complete(web_screenshot(input_str))
            except RuntimeError:
                # No event loop exists, create a new one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    screenshot_bytes = loop.run_until_complete(web_screenshot(input_str))
                finally:
                    loop.close()
            
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(screenshot_bytes))
        else:
            # Assume it's a file path
            if not os.path.exists(input_str):
                raise Exception(f"File not found: {input_str}")
            
            image = Image.open(input_str)
        
        # Perform OCR
        text = pytesseract.image_to_string(image)
        return text.strip()
        
    except Exception as e:
        if HEADLESS_MODE:
            return f"OCR failed in headless mode: {str(e)}"
        raise Exception(f"Browser OCR failed: {str(e)}")

async def click_element(selector: str) -> Dict[str, Any]:
    """
    In Electron's webview context, use page.click(selector) via pyppeteer.
    Return {"selector": selector, "clicked": true}.
    """
    if not PYPPETEER_AVAILABLE:
        return {
            "selector": selector,
            "clicked": False,
            "success": False,
            "error": "pyppeteer is not available",
            "message": f"Cannot click element {selector} - pyppeteer not available"
        }
    
    if HEADLESS_MODE:
        return {
            "selector": selector,
            "clicked": True,
            "success": True,
            "message": f"Mock clicked element: {selector} (headless mode)"
        }
    
    if not selector:
        return {
            "selector": selector,
            "clicked": False,
            "success": False,
            "error": "Selector is required",
            "message": "Selector cannot be empty"
        }
    
    browser = None
    try:
        # Launch headless browser with robust settings
        browser = await launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-features=TranslateUI',
                '--disable-ipc-flooding-protection',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ],
            ignoreHTTPSErrors=True,
            slowMo=0,
            devtools=False
        )
        
        # Create new page
        page = await browser.newPage()
        
        # For Electron webview context, we would typically connect to an existing page
        # but for this implementation, we'll demonstrate with a basic page
        await page.goto('about:blank')
        
        # Try to click the element by selector
        await page.click(selector)
        
        return {
            "selector": selector,
            "clicked": True,
            "success": True,
            "message": f"Successfully clicked element: {selector}"
        }
        
    except Exception as e:
        return {
            "selector": selector,
            "clicked": False,
            "success": False,
            "error": str(e),
            "message": f"Failed to click element: {selector}"
        }
    finally:
        if browser:
            try:
                await browser.close()
            except Exception:
                pass  # Ignore closing errors

# Synchronous wrappers for use in FastAPI endpoints
def web_screenshot_sync(url: str) -> bytes:
    """Synchronous wrapper for web_screenshot"""
    try:
        # Try to get the current event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is running, we need to run in a separate thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(_run_web_screenshot, url)
                return future.result()
        else:
            return loop.run_until_complete(web_screenshot(url))
    except RuntimeError:
        # No event loop exists, create a new one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(web_screenshot(url))
        finally:
            loop.close()

def click_element_sync(selector: str) -> Dict[str, Any]:
    """Synchronous wrapper for click_element"""
    try:
        # Try to get the current event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is running, we need to run in a separate thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(_run_click_element, selector)
                return future.result()
        else:
            return loop.run_until_complete(click_element(selector))
    except RuntimeError:
        # No event loop exists, create a new one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(click_element(selector))
        finally:
            loop.close()

def _run_web_screenshot(url: str) -> bytes:
    """Helper function to run web_screenshot in a new event loop"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(web_screenshot(url))
    finally:
        loop.close()

def _run_click_element(selector: str) -> Dict[str, Any]:
    """Helper function to run click_element in a new event loop"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(click_element(selector))
    finally:
        loop.close()
