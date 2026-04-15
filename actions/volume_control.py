"""
Volume Control Action
Controls system volume using keyboard media keys
"""

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False


def volume_control(action: str, amount: int = 2) -> dict:
    """
    Control system volume and media playback
    
    Args:
        action: "up", "down", "mute", "pause", "play", "next", "previous"
        amount: Number of times to press the key (each press ~2% volume)
        
    Returns:
        dict with result status
    """
    if not PYAUTOGUI_AVAILABLE:
        return {
            "success": False,
            "message": "pyautogui no está disponible."
        }
    
    try:
        if action == "up":
            for _ in range(amount):
                pyautogui.press('volumeup')
            return {
                "success": True,
                "message": "Volumen subido."
            }
        
        elif action == "down":
            for _ in range(amount):
                pyautogui.press('volumedown')
            return {
                "success": True,
                "message": "Volumen bajado."
            }
        
        elif action == "mute":
            pyautogui.press('volumemute')
            return {
                "success": True,
                "message": "Volumen silenciado/activado."
            }
        
        elif action in ["pause", "play", "playpause"]:
            pyautogui.press('playpause')
            return {
                "success": True,
                "message": "Reproducción pausada/reanudada."
            }
        
        elif action == "next":
            pyautogui.press('nexttrack')
            return {
                "success": True,
                "message": "Siguiente canción."
            }
        
        elif action == "previous":
            pyautogui.press('prevtrack')
            return {
                "success": True,
                "message": "Canción anterior."
            }
        
        else:
            return {
                "success": False,
                "message": f"Acción no reconocida: {action}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }
