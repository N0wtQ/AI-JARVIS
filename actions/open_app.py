"""
Open App Action
Opens applications on Windows
With visual control for web URLs
"""

import subprocess
import os
import webbrowser
import urllib.parse

# Try to import visual control
try:
    from actions.pc_control import open_url_visual
    VISUAL_CONTROL = True
except ImportError:
    VISUAL_CONTROL = False


# Common app mappings for Windows
APP_MAPPINGS = {
    # Browsers
    "brave": "C:\\Users\\N0wtq\\AppData\\Local\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
    "google chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "firefox": "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
    "edge": "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
    "microsoft edge": "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
    "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    
    # Microsoft Office
    "word": "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
    "excel": "C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE",
    "powerpoint": "C:\\Program Files\\Microsoft Office\\root\\Office16\\POWERPNT.EXE",
    "outlook": "C:\\Program Files\\Microsoft Office\\root\\Office16\\OUTLOOK.EXE",
    "onenote": "C:\\Program Files\\Microsoft Office\\root\\Office16\\ONENOTE.EXE",
    "teams": "teams",
    
    # System apps
    "notepad": "%windir%\\system32\\notepad.exe",
    "bloc de notas": "%windir%\\system32\\notepad.exe",
    "calculadora": "%windir%\\system32\\calc.exe",
    "calculator": "%windir%\\system32\\calc.exe",
    "cmd": "%windir%\\system32\\cmd.exe",
    "powershell": "%SystemRoot%\\system32\\WindowsPowerShell\\v1.0\\powershell.exe",
    
    # Communication
    "telegram": "C:\\Users\\N0wtq\\AppData\\Roaming\\Telegram Desktop\\Telegram.exe",
    "whatsapp": "whatsapp",
    "slack": "slack",
    "zoom": "zoom",
    "skype": "skype",
    
    # Media
    "spotify": "C:\\Users\\N0wtq\\AppData\\Roaming\\Spotify\\Spotify.exe",
    "vlc": "vlc",
    
    # Development
    "vscode": "C:\\Users\\N0wtq\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
    "visual studio code": "C:\\Users\\N0wtq\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
    "visual studio": "C:\\Users\\N0wtq\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
    
    # Other
    "steam": "steam",
    "epic games": "EpicGamesLauncher",
}


def normalize_app_name(app_name: str) -> str:
    """Normalize app name to find the correct executable"""
    app_lower = app_name.lower().strip()
    
    # Check mappings
    if app_lower in APP_MAPPINGS:
        return APP_MAPPINGS[app_lower]
    
    # Try common variations
    variations = [
        app_lower,
        app_lower.replace(" ", ""),
        app_lower.replace(" ", "-"),
        app_lower.replace(" ", "_"),
    ]
    
    for var in variations:
        if var in APP_MAPPINGS:
            return APP_MAPPINGS[var]
    
    # Return original if no mapping found
    return app_name


def open_app(app_name: str) -> dict:
    """
    Open an application on Windows
    
    Args:
        app_name: Name of the application to open
        
    Returns:
        dict with success status and message
    """
    try:
        normalized_name = normalize_app_name(app_name)
        
        # Try to open using start command (works for most apps)
        result = subprocess.Popen(
            f'start "" "{normalized_name}"',
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        return {
            "success": True,
            "message": f"Abriendo {app_name}...",
            "app": normalized_name
        }
        
    except FileNotFoundError:
        return {
            "success": False,
            "message": f"No encontré la aplicación '{app_name}'. Verifica que esté instalada.",
            "app": app_name
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error al abrir {app_name}: {str(e)}",
            "app": app_name
        }


def list_common_apps() -> list:
    """List commonly available apps"""
    return list(APP_MAPPINGS.keys())


# URL mappings for web sites
WEB_URLS = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "twitter": "https://twitter.com",
    "x": "https://x.com",
    "facebook": "https://www.facebook.com",
    "instagram": "https://www.instagram.com",
    "linkedin": "https://www.linkedin.com",
    "github": "https://github.com",
    "reddit": "https://www.reddit.com",
    "amazon": "https://www.amazon.es",
    "netflix": "https://www.netflix.com",
    "twitch": "https://www.twitch.tv",
}

# Search URL patterns
SEARCH_URLS = {
    "youtube": "https://www.youtube.com/results?search_query={query}",
    "google": "https://www.google.com/search?q={query}",
    "amazon": "https://www.amazon.es/s?k={query}",
    "github": "https://github.com/search?q={query}",
    "twitter": "https://twitter.com/search?q={query}",
    "x": "https://x.com/search?q={query}",
    "reddit": "https://www.reddit.com/search/?q={query}",
}


def _open_url_with_effect(url: str):
    """Open URL with visual effect if available"""
    if VISUAL_CONTROL:
        open_url_visual(url, browser="chrome")
    else:
        webbrowser.open(url)


def open_url(site: str, search_query: str = None) -> dict:
    """
    Open a website or perform a search on a specific site
    Uses visual control (JARVIS takes control effect)
    
    Args:
        site: Website name (youtube, google, etc.)
        search_query: Optional search query
        
    Returns:
        dict with success status and message
    """
    try:
        site_lower = site.lower().strip()
        
        if search_query:
            # Perform search on the site
            if site_lower in SEARCH_URLS:
                encoded_query = urllib.parse.quote(search_query)
                url = SEARCH_URLS[site_lower].format(query=encoded_query)
                _open_url_with_effect(url)
                return {
                    "success": True,
                    "message": f"Buscando '{search_query}' en {site}...",
                    "url": url
                }
            else:
                # Fallback: open site homepage
                if site_lower in WEB_URLS:
                    _open_url_with_effect(WEB_URLS[site_lower])
                    return {
                        "success": True,
                        "message": f"Abriendo {site}. No puedo buscar directamente ahí.",
                        "url": WEB_URLS[site_lower]
                    }
        else:
            # Just open the site
            if site_lower in WEB_URLS:
                _open_url_with_effect(WEB_URLS[site_lower])
                return {
                    "success": True,
                    "message": f"Abriendo {site}...",
                    "url": WEB_URLS[site_lower]
                }
        
        return {
            "success": False,
            "message": f"No conozco el sitio '{site}'. Sitios disponibles: {', '.join(WEB_URLS.keys())}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error al abrir {site}: {str(e)}"
        }
