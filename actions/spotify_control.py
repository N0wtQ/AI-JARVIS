"""
Spotify Control Action
Controls Spotify playback using web URLs and app control
"""

import webbrowser
import urllib.parse
import subprocess
import time

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False


def play_spotify_song(song_query: str, auto_play: bool = True) -> dict:
    """
    Search and play a song on Spotify
    
    Args:
        song_query: Song name or "artist - song" format
        auto_play: If True, attempts to auto-play (requires pyautogui)
        
    Returns:
        dict with result status
    """
    try:
        # Use Spotify URI scheme to search directly in the app
        encoded_query = urllib.parse.quote(song_query)
        spotify_uri = f"spotify:search:{encoded_query}"
        
        # Open Spotify app with search query (only opens the app, not web)
        subprocess.Popen(f'start "" "{spotify_uri}"', shell=True)
        
        if auto_play and PYAUTOGUI_AVAILABLE:
            try:
                # Wait for Spotify to fully load the search results
                time.sleep(4)
                
                # Press space to play the first result
                pyautogui.press('space')
                
                return {
                    "success": True,
                    "message": f"Reproduciendo '{song_query}' en Spotify.",
                    "query": song_query
                }
            except Exception as e:
                return {
                    "success": True,
                    "message": f"Abrí la búsqueda de '{song_query}' en Spotify. Haz clic en la canción para reproducirla.",
                    "query": song_query
                }
        
        return {
            "success": True,
            "message": f"Busqué '{song_query}' en Spotify. Haz clic en la canción para reproducirla.",
            "query": song_query
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error al buscar en Spotify: {str(e)}",
            "query": song_query
        }


def open_spotify() -> dict:
    """
    Just open Spotify app or web
    
    Returns:
        dict with result status
    """
    try:
        # Try to open Spotify app
        result = subprocess.Popen('start "" "spotify:"', shell=True)
        return {
            "success": True,
            "message": "Abriendo Spotify..."
        }
    except Exception as e:
        # Fallback to web
        webbrowser.open("https://open.spotify.com")
        return {
            "success": True,
            "message": "Abriendo Spotify Web..."
        }


def spotify_control(action: str = "open", song_query: str = None) -> dict:
    """
    Main Spotify control function
    
    Args:
        action: "open" or "play"
        song_query: Song to play (if action is "play")
        
    Returns:
        dict with result
    """
    if action == "play" and song_query:
        return play_spotify_song(song_query)
    else:
        return open_spotify()
