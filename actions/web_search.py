"""
Web Search Action
Performs web searches and clicks on first organic result
"""

import requests
from typing import Optional
import webbrowser
import urllib.parse
import time

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False


def web_search(query: str, auto_click: bool = True) -> dict:
    """
    Search the web using Google and optionally click first organic result
    
    Args:
        query: Search query
        auto_click: Whether to automatically click the first non-sponsored result
        
    Returns:
        dict with search results
    """
    try:
        # Use Google for search
        search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        webbrowser.open(search_url)
        
        if auto_click and PYAUTOGUI_AVAILABLE:
            # Wait for page to load
            time.sleep(4)
            
            # In Google, need tabs to reach first organic result
            for _ in range(30):
                pyautogui.press('tab')
                time.sleep(0.08)
            
            # Press Enter to open the first result
            pyautogui.press('enter')
            
            return {
                "success": True,
                "query": query,
                "message": f"Buscando '{query}' y abriendo el primer resultado."
            }
        
        return {
            "success": True,
            "query": query,
            "message": f"Buscando '{query}' en Google."
        }
        
    except Exception as e:
        # Fallback: just open browser
        search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        webbrowser.open(search_url)
        return {
            "success": False,
            "query": query,
            "message": f"Abriendo búsqueda para '{query}'."
        }
