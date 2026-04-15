"""
Weather Report Action
Gets weather information using wttr.in (free, no API key required)
"""

import requests
from typing import Optional


def get_weather(city: str, time: Optional[str] = None) -> dict:
    """
    Get weather for a city using wttr.in
    
    Args:
        city: City name
        time: Optional time specifier (today, tomorrow, etc.)
        
    Returns:
        dict with weather information
    """
    # Try multiple times with increasing timeout
    max_retries = 2
    timeouts = [15, 30]
    
    for attempt in range(max_retries):
        try:
            # wttr.in API - free and no API key needed
            # Using format codes for structured data
            url = f"https://wttr.in/{city}"
            params = {
                "format": "j1",  # JSON format
                "lang": "es"
            }
            
            response = requests.get(url, params=params, timeout=timeouts[attempt])
        
            if response.status_code != 200:
                if attempt < max_retries - 1:
                    continue  # Try again
                return {
                    "success": False,
                    "city": city,
                    "message": f"No pude obtener el clima para {city}. Verifica el nombre de la ciudad."
                }
                
            data = response.json()
        
            # Current conditions
            current = data.get("current_condition", [{}])[0]
            
            # Location info
            area = data.get("nearest_area", [{}])[0]
            area_name = area.get("areaName", [{}])[0].get("value", city)
            country = area.get("country", [{}])[0].get("value", "")
            
            # Weather data
            temp_c = current.get("temp_C", "?")
            feels_like = current.get("FeelsLikeC", "?")
            humidity = current.get("humidity", "?")
            weather_desc = current.get("lang_es", [{}])[0].get("value", 
                           current.get("weatherDesc", [{}])[0].get("value", "Desconocido"))
            wind_kmph = current.get("windspeedKmph", "?")
            
            # Build response
            weather_text = (
                f"Clima en {area_name}, {country}:\n"
                f"Temperatura: {temp_c}°C (sensación térmica: {feels_like}°C)\n"
                f"Condición: {weather_desc}\n"
                f"Humedad: {humidity}%\n"
                f"Viento: {wind_kmph} km/h"
            )
            
            # Add forecast if requested
            if time and time.lower() in ["mañana", "tomorrow"]:
                forecast = data.get("weather", [{}])
                if len(forecast) > 1:
                    tomorrow = forecast[1]
                    max_temp = tomorrow.get("maxtempC", "?")
                    min_temp = tomorrow.get("mintempC", "?")
                    weather_text += (
                        f"\n\nPronóstico para mañana:\n"
                        f"Máxima: {max_temp}°C, Mínima: {min_temp}°C"
                    )
            
            return {
                "success": True,
                "city": area_name,
                "country": country,
                "temperature": temp_c,
                "feels_like": feels_like,
                "condition": weather_desc,
                "humidity": humidity,
                "wind": wind_kmph,
                "message": weather_text
            }
            
        except requests.Timeout:
            if attempt < max_retries - 1:
                continue  # Try again with longer timeout
            return {
                "success": False,
                "city": city,
                "message": f"La consulta del clima tardó demasiado después de varios intentos. Verifica tu conexión."
            }
            
        except Exception as e:
            if attempt < max_retries - 1:
                continue  # Try again
            return {
                "success": False,
                "city": city,
                "message": f"Error al obtener el clima: {str(e)}"
            }
    
    # Should not reach here, but just in case
    return {
        "success": False,
        "city": city,
        "message": f"No pude obtener el clima para {city} después de varios intentos."
    }


def get_weather_simple(city: str) -> str:
    """
    Get simple weather text for a city
    
    Args:
        city: City name
        
    Returns:
        Weather description string
    """
    result = get_weather(city)
    return result.get("message", f"No pude obtener el clima para {city}")
