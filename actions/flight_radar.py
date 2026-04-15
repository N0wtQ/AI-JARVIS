"""
Flight Radar Action
Detects location via IP and opens FlightRadar24
With visual control effect - JARVIS takes control
"""

import requests
import webbrowser
from typing import Optional

# Try to import visual control, fallback to normal if not available
try:
    from actions.pc_control import open_url_visual
    VISUAL_CONTROL = True
except ImportError:
    VISUAL_CONTROL = False


def get_location_from_ip() -> dict:
    """
    Get current location from IP address
    
    Returns:
        dict with lat, lon, city, country or error
    """
    # Try multiple geolocation services for reliability
    services = [
        {
            "url": "http://ip-api.com/json/",
            "lat_key": "lat",
            "lon_key": "lon",
            "city_key": "city",
            "country_key": "country"
        },
        {
            "url": "https://ipapi.co/json/",
            "lat_key": "latitude",
            "lon_key": "longitude",
            "city_key": "city",
            "country_key": "country_name"
        }
    ]
    
    for service in services:
        try:
            response = requests.get(service["url"], timeout=10)
            if response.status_code == 200:
                data = response.json()
                lat = data.get(service["lat_key"])
                lon = data.get(service["lon_key"])
                
                if lat and lon:
                    return {
                        "success": True,
                        "lat": lat,
                        "lon": lon,
                        "city": data.get(service["city_key"], "Desconocida"),
                        "country": data.get(service["country_key"], "")
                    }
        except Exception:
            continue
    
    return {
        "success": False,
        "message": "No se pudo detectar la ubicación"
    }


def open_flight_radar(lat: Optional[float] = None, lon: Optional[float] = None, zoom: int = 10) -> dict:
    """
    Open FlightRadar24 at specified or detected location
    
    Args:
        lat: Optional latitude (auto-detect if not provided)
        lon: Optional longitude (auto-detect if not provided)
        zoom: Zoom level (default 10)
        
    Returns:
        dict with success status and message
    """
    try:
        # If no coordinates provided, detect from IP
        if lat is None or lon is None:
            location = get_location_from_ip()
            
            if not location.get("success"):
                # Fallback: open FlightRadar24 main page
                webbrowser.open("https://www.flightradar24.com")
                return {
                    "success": True,
                    "message": "No pude detectar tu ubicación automáticamente. He abierto FlightRadar24 para que permitas la geolocalización manualmente."
                }
            
            lat = location["lat"]
            lon = location["lon"]
            city = location.get("city", "tu ubicación")
            country = location.get("country", "")
        else:
            city = "coordenadas especificadas"
            country = ""
        
        # Build FlightRadar24 URL with coordinates
        # Format: https://www.flightradar24.com/LAT,LON/ZOOM
        url = f"https://www.flightradar24.com/{lat},{lon}/{zoom}"
        
        location_str = f"{city}, {country}" if country else city
        
        # Use visual control if available (JARVIS takes control effect)
        if VISUAL_CONTROL:
            open_url_visual(url, browser="chrome")
        else:
            webbrowser.open(url)
        
        return {
            "success": True,
            "lat": lat,
            "lon": lon,
            "city": city,
            "country": country,
            "url": url,
            "message": f"Abriendo FlightRadar24 en {location_str}. Puedes ver los vuelos cerca de ti en tiempo real."
        }
        
    except Exception as e:
        # Fallback: open main page
        webbrowser.open("https://www.flightradar24.com")
        return {
            "success": False,
            "message": f"Error al abrir FlightRadar24: {str(e)}. He abierto la página principal."
        }


def check_nearby_flights() -> dict:
    """
    Convenience function that opens FlightRadar24 at detected location
    
    Returns:
        dict with success status and message
    """
    return open_flight_radar()
