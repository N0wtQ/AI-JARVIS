"""
PC Control Action
Provides visual control of the computer (mouse, keyboard, browser)
Gives the sensation that JARVIS is taking control
"""

import pyautogui
import time
import subprocess
import os
from typing import Optional, Tuple

# Safety settings
pyautogui.FAILSAFE = True  # Move mouse to corner to abort
pyautogui.PAUSE = 0.05  # Small pause between actions


def move_mouse_smoothly(x: int, y: int, duration: float = 0.5):
    """
    Move mouse smoothly to coordinates
    
    Args:
        x: Target X coordinate
        y: Target Y coordinate
        duration: Time to complete movement
    """
    pyautogui.moveTo(x, y, duration=duration, tween=pyautogui.easeInOutQuad)


def click_at(x: int, y: int, duration: float = 0.3):
    """
    Move to position and click
    
    Args:
        x: Target X coordinate
        y: Target Y coordinate
        duration: Time to move to position
    """
    move_mouse_smoothly(x, y, duration)
    time.sleep(0.1)
    pyautogui.click()


def type_text(text: str, interval: float = 0.03):
    """
    Type text with visual typing effect
    
    Args:
        text: Text to type
        interval: Time between keystrokes
    """
    pyautogui.typewrite(text, interval=interval)


def type_text_unicode(text: str, interval: float = 0.02):
    """
    Type text supporting unicode/special characters
    
    Args:
        text: Text to type (supports Spanish characters, etc.)
        interval: Time between keystrokes
    """
    for char in text:
        pyautogui.write(char)
        time.sleep(interval)


def press_key(key: str):
    """Press a single key"""
    pyautogui.press(key)


def hotkey(*keys):
    """Press a hotkey combination (e.g., 'ctrl', 'l' for address bar)"""
    pyautogui.hotkey(*keys)


def get_screen_size() -> Tuple[int, int]:
    """Get screen dimensions"""
    return pyautogui.size()


def open_browser_visual(url: str, typing_speed: float = 0.02) -> dict:
    """
    Open browser and navigate to URL with visual effect
    Shows JARVIS "taking control" - opens browser, clicks address bar, types URL
    
    Args:
        url: URL to navigate to
        typing_speed: Speed of typing effect
        
    Returns:
        dict with success status and message
    """
    try:
        screen_width, screen_height = get_screen_size()
        
        # Open default browser (starts minimized or in background usually)
        # We'll use a blank page first, then navigate
        subprocess.Popen(['cmd', '/c', 'start', 'chrome', '--new-window', 'about:blank'], 
                        shell=True, 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        
        # Wait for browser to open
        time.sleep(1.5)
        
        # Focus on address bar with Ctrl+L (works in most browsers)
        hotkey('ctrl', 'l')
        time.sleep(0.3)
        
        # Clear any existing text
        hotkey('ctrl', 'a')
        time.sleep(0.1)
        
        # Type the URL with visual effect
        # Use typewrite for ASCII URLs, pyperclip for unicode if needed
        pyautogui.typewrite(url, interval=typing_speed)
        
        time.sleep(0.2)
        
        # Press Enter to navigate
        press_key('enter')
        
        return {
            "success": True,
            "url": url,
            "message": f"Navegando a {url}"
        }
        
    except Exception as e:
        # Fallback: just open URL normally
        import webbrowser
        webbrowser.open(url)
        return {
            "success": True,
            "url": url,
            "message": f"Abriendo {url} (modo normal)"
        }


def open_url_visual(url: str, browser: str = "default") -> dict:
    """
    Open URL with visual control effect
    
    Args:
        url: URL to open
        browser: Browser to use (default, chrome, firefox, edge)
        
    Returns:
        dict with success and message
    """
    try:
        # First, try to find an existing browser window
        # Open new browser window
        browsers = {
            "chrome": "chrome",
            "firefox": "firefox", 
            "edge": "msedge",
            "default": ""
        }
        
        browser_cmd = browsers.get(browser.lower(), "")
        
        if browser_cmd:
            # Open specific browser with blank page
            subprocess.Popen(f'start {browser_cmd} about:blank', 
                           shell=True,
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
        else:
            # Open default browser
            subprocess.Popen('start about:blank', 
                           shell=True,
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
        
        time.sleep(1.2)
        
        # Select address bar
        hotkey('ctrl', 'l')
        time.sleep(0.2)
        
        # Select all and delete
        hotkey('ctrl', 'a')
        time.sleep(0.1)
        
        # Type URL character by character for visual effect
        pyautogui.typewrite(url, interval=0.025)
        
        time.sleep(0.15)
        press_key('enter')
        
        return {
            "success": True,
            "url": url,
            "message": f"He abierto {url}"
        }
        
    except Exception as e:
        import webbrowser
        webbrowser.open(url)
        return {
            "success": True,
            "url": url, 
            "message": f"Abriendo {url}"
        }


def search_in_browser_visual(query: str, search_engine: str = "google") -> dict:
    """
    Open browser and search with visual typing effect
    
    Args:
        query: Search query
        search_engine: google, duckduckgo, bing
        
    Returns:
        dict with success and message
    """
    search_urls = {
        "google": "https://www.google.com/search?q=",
        "duckduckgo": "https://duckduckgo.com/?q=",
        "bing": "https://www.bing.com/search?q="
    }
    
    base_url = search_urls.get(search_engine.lower(), search_urls["google"])
    
    try:
        # Open browser
        subprocess.Popen('start chrome about:blank', 
                        shell=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL)
        
        time.sleep(1.2)
        
        # Go to address bar
        hotkey('ctrl', 'l')
        time.sleep(0.2)
        hotkey('ctrl', 'a')
        time.sleep(0.1)
        
        # Type search URL + query
        full_url = base_url + query.replace(' ', '+')
        pyautogui.typewrite(full_url, interval=0.02)
        
        time.sleep(0.15)
        press_key('enter')
        
        return {
            "success": True,
            "query": query,
            "message": f"Buscando: {query}"
        }
        
    except Exception as e:
        import webbrowser
        webbrowser.open(base_url + query.replace(' ', '+'))
        return {
            "success": True,
            "query": query,
            "message": f"Buscando: {query}"
        }


def scroll_page(direction: str = "down", amount: int = 3):
    """
    Scroll the current page
    
    Args:
        direction: "up" or "down"
        amount: Number of scroll units
    """
    if direction.lower() == "up":
        pyautogui.scroll(amount)
    else:
        pyautogui.scroll(-amount)


def take_screenshot(filename: Optional[str] = None) -> str:
    """
    Take a screenshot
    
    Args:
        filename: Optional filename (auto-generated if not provided)
        
    Returns:
        Path to saved screenshot
    """
    if not filename:
        filename = f"screenshot_{int(time.time())}.png"
    
    screenshot = pyautogui.screenshot()
    screenshot.save(filename)
    return filename
