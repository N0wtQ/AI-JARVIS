"""
Channel Manager
Gestor central que conecta todos los canales con el AIHandler de JARVIS
"""

import os
import asyncio
import threading
from typing import Dict, Optional, Callable, Set
from ai_handler import AIHandler

# Import actions
from actions.open_app import open_app, open_url
from actions.web_search import web_search
from actions.weather_report import get_weather
from actions.spotify_control import spotify_control
from actions.wolfram_query import query_wolfram
from actions.system_info import get_system_status_text, get_public_ip, get_private_ip, get_ram_info, get_cpu_info, get_disk_info
from actions.flight_radar import open_flight_radar
from actions.volume_control import volume_control
from actions.run_command import run_command
from actions.system_control import system_control
from actions.file_organizer import organize_files


class ChannelManager:
    """
    Gestor central de canales.
    Mantiene una instancia compartida de AIHandler para todos los canales.
    """
    
    def __init__(self):
        self.ai_handler = AIHandler()
        self.channels: Dict[str, any] = {}
        self.running = False
        
        # Config for remote PC control
        self.allow_remote_pc_control = os.getenv("TELEGRAM_ALLOW_PC_CONTROL", "false").lower() == "true"
        
        # Intents that require local PC (won't work remotely)
        self.local_only_intents: Set[str] = {
            "open_app", "organize_files"
        }
        
        # Intents that can be enabled for remote (dangerous)
        self.remote_dangerous_intents: Set[str] = {
            "pc_control"  # shutdown, restart, sleep, etc.
        }
        
        # Intents that work remotely and return info
        self.info_intents: Set[str] = {
            "system_info", "weather_report", "search", "wolfram", "flight_radar",
            "open_site", "play_music", "volume_control", "run_command"
        }
        
    def process_message(self, message: str, channel: str, user_id: str, user_name: str = "Usuario") -> str:
        """
        Procesa un mensaje de cualquier canal y devuelve la respuesta.
        
        Args:
            message: El mensaje del usuario
            channel: Nombre del canal (telegram, discord, whatsapp, etc.)
            user_id: ID único del usuario en ese canal
            user_name: Nombre del usuario (opcional)
            
        Returns:
            Respuesta de JARVIS como string
        """
        # Log del mensaje entrante
        print(f"📨 [{channel.upper()}] {user_name} ({user_id}): {message}")
        
        try:
            # Obtener respuesta del AI Handler
            result = self.ai_handler.get_response(message)
            
            # Extraer el texto de la respuesta
            response_text = result.get("text", "Lo siento, no pude procesar tu mensaje.")
            
            # Manejar intents que requieren acción
            intent = result.get("intent", "chat")
            parameters = result.get("parameters", {})
            
            # Para canales remotos, algunas acciones no tienen sentido
            is_remote_channel = channel != "local"
            
            if is_remote_channel:
                # Siempre bloquear acciones puramente locales
                if intent in self.local_only_intents:
                    response_text = f"⚠️ La acción '{intent}' solo está disponible en el PC local.\n\n{response_text}"
                
                # Para pc_control, depende de la configuración
                elif intent in self.remote_dangerous_intents:
                    if not self.allow_remote_pc_control:
                        response_text = f"⚠️ Control remoto del PC deshabilitado.\n\n{response_text}"
                    else:
                        action_result = self._execute_action(intent, parameters)
                        if action_result:
                            response_text = f"{response_text}\n\n{action_result}"
                
                # Ejecutar intents informativos (system_info, weather, etc.)
                elif intent in self.info_intents:
                    action_result = self._execute_action(intent, parameters)
                    if action_result:
                        response_text = f"{response_text}\n\n{action_result}"
            else:
                # Canal local - ejecutar todas las acciones
                if intent != "chat":
                    action_result = self._execute_action(intent, parameters)
                    if action_result:
                        response_text = f"{response_text}\n\n{action_result}"
            
            # Log de la respuesta
            print(f"📤 [{channel.upper()}] JARVIS: {response_text[:100]}...")
            
            return response_text
            
        except Exception as e:
            error_msg = f"Error procesando mensaje: {str(e)}"
            print(f"❌ [{channel.upper()}] {error_msg}")
            return f"Lo siento, ocurrió un error: {str(e)}"
    
    def register_channel(self, name: str, channel_instance):
        """Registra un canal en el gestor"""
        self.channels[name] = channel_instance
        print(f"✅ Canal registrado: {name}")
    
    def get_ai_handler(self) -> AIHandler:
        """Devuelve el AIHandler compartido"""
        return self.ai_handler
    
    def get_memory(self) -> Dict:
        """Devuelve la memoria actual"""
        return self.ai_handler.get_memory()
    
    def clear_history(self):
        """Limpia el historial de conversación"""
        self.ai_handler.clear_history()
    
    def _execute_action(self, intent: str, parameters: dict) -> str:
        """
        Ejecuta acciones basadas en el intent detectado.
        """
        try:
            print(f"🎯 Ejecutando intent: {intent}")
            print(f"📦 Parámetros: {parameters}")
            
            if intent == "system_info":
                info_type = parameters.get("info_type", "full")
                if info_type == "ip":
                    pub_ip = get_public_ip()
                    priv_ip = get_private_ip()
                    return f"🌐 IP Pública: {pub_ip}\n🏠 IP Privada: {priv_ip}"
                elif info_type == "ram":
                    ram = get_ram_info()
                    if 'error' not in ram:
                        return f"💾 RAM: {ram['total']} total, {ram['disponible']} disponibles ({ram['porcentaje_uso']} uso)"
                    return "No pude obtener la información de RAM."
                elif info_type == "cpu":
                    cpu = get_cpu_info()
                    if 'error' not in cpu:
                        return f"🖥️ CPU: {cpu['uso']} uso, {cpu['nucleos_fisicos']} núcleos, {cpu['frecuencia_actual']}"
                    return "No pude obtener la información del CPU."
                elif info_type == "disk":
                    disk = get_disk_info()
                    if 'error' not in disk:
                        return f"💿 Disco: {disk['total']} total, {disk['libre']} libres ({disk['porcentaje_uso']} uso)"
                    return "No pude obtener la información del disco."
                else:
                    return get_system_status_text()
            
            elif intent == "weather_report":
                city = parameters.get("city", "")
                time_param = parameters.get("time")
                if city:
                    result = get_weather(city, time_param)
                    return result.get("message", "")
            
            elif intent == "search":
                query = parameters.get("query", "")
                if query:
                    result = web_search(query)
                    return result.get("message", "")
            
            elif intent == "open_site":
                site = parameters.get("site", "")
                query = parameters.get("query")
                if site:
                    result = open_url(site, query)
                    return result.get("message", "")
            
            elif intent == "play_music":
                song_query = parameters.get("song_query", "")
                action = parameters.get("action", "play")
                if song_query:
                    result = spotify_control(action, song_query)
                    return result.get("message", "")
                else:
                    result = volume_control("pause")
                    return result.get("message", "")
            
            elif intent == "wolfram":
                query = parameters.get("query", "")
                if query:
                    result = query_wolfram(query)
                    return f"🔢 WolframAlpha: {result}"
            
            elif intent == "flight_radar":
                result = open_flight_radar()
                return result.get("message", "")
            
            elif intent == "volume_control":
                action = parameters.get("action", "up")
                amount = parameters.get("amount", 2)
                result = volume_control(action, amount)
                return result.get("message", "")
            
            elif intent == "run_command":
                command = parameters.get("command", "")
                shell = parameters.get("shell", "cmd")
                if command:
                    result = run_command(command, shell)
                    return result.get("message", "")
            
            elif intent == "pc_control":
                action = parameters.get("action", "")
                if action:
                    extra_params = {k: v for k, v in parameters.items() if k != "action"}
                    result = system_control(action, **extra_params)
                    return result.get("message", "")
            
            elif intent == "open_app":
                app_name = parameters.get("app_name", "")
                if app_name:
                    result = open_app(app_name)
                    return result.get("message", "")
            
            elif intent == "organize_files":
                action = parameters.get("action", "by_type")
                folder_path = parameters.get("folder_path")
                result = organize_files(action, folder_path)
                return result.get("message", "")
            
            return ""
            
        except Exception as e:
            return f"❌ Error ejecutando acción: {str(e)}"


# Instancia global del gestor de canales
_channel_manager: Optional[ChannelManager] = None


def get_channel_manager() -> ChannelManager:
    """Obtiene la instancia global del gestor de canales"""
    global _channel_manager
    if _channel_manager is None:
        _channel_manager = ChannelManager()
    return _channel_manager
