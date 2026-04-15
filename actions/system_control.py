"""
System Control Action
Control avanzado del sistema: apagar, reiniciar, bloquear, captura, ventanas, etc.
"""

import subprocess
import os
import time
import ctypes
from datetime import datetime

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False


def shutdown_pc(delay: int = 0) -> dict:
    """Apagar el ordenador"""
    try:
        if delay > 0:
            subprocess.run(f'shutdown /s /t {delay}', shell=True)
            return {"success": True, "message": f"El ordenador se apagará en {delay} segundos."}
        else:
            subprocess.run('shutdown /s /t 5', shell=True)
            return {"success": True, "message": "Apagando el ordenador en 5 segundos."}
    except Exception as e:
        return {"success": False, "message": f"Error al apagar: {e}"}


def restart_pc(delay: int = 0) -> dict:
    """Reiniciar el ordenador"""
    try:
        if delay > 0:
            subprocess.run(f'shutdown /r /t {delay}', shell=True)
            return {"success": True, "message": f"El ordenador se reiniciará en {delay} segundos."}
        else:
            subprocess.run('shutdown /r /t 5', shell=True)
            return {"success": True, "message": "Reiniciando el ordenador en 5 segundos."}
    except Exception as e:
        return {"success": False, "message": f"Error al reiniciar: {e}"}


def cancel_shutdown() -> dict:
    """Cancelar apagado/reinicio programado"""
    try:
        subprocess.run('shutdown /a', shell=True)
        return {"success": True, "message": "Apagado cancelado."}
    except Exception as e:
        return {"success": False, "message": f"Error: {e}"}


def sleep_pc() -> dict:
    """Suspender el ordenador"""
    try:
        # Usar rundll32 para suspender
        subprocess.run('rundll32.exe powrprof.dll,SetSuspendState 0,1,0', shell=True)
        return {"success": True, "message": "Suspendiendo el ordenador."}
    except Exception as e:
        return {"success": False, "message": f"Error al suspender: {e}"}


def hibernate_pc() -> dict:
    """Hibernar el ordenador"""
    try:
        subprocess.run('shutdown /h', shell=True)
        return {"success": True, "message": "Hibernando el ordenador."}
    except Exception as e:
        return {"success": False, "message": f"Error al hibernar: {e}"}


def lock_pc() -> dict:
    """Bloquear la pantalla"""
    try:
        ctypes.windll.user32.LockWorkStation()
        return {"success": True, "message": "Pantalla bloqueada."}
    except Exception as e:
        return {"success": False, "message": f"Error al bloquear: {e}"}


def take_screenshot(save_to_desktop: bool = True) -> dict:
    """Capturar pantalla"""
    if not PYAUTOGUI_AVAILABLE:
        return {"success": False, "message": "pyautogui no disponible."}
    
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if save_to_desktop:
            desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
            filepath = os.path.join(desktop, f"captura_{timestamp}.png")
        else:
            filepath = f"captura_{timestamp}.png"
        
        screenshot = pyautogui.screenshot()
        screenshot.save(filepath)
        return {"success": True, "message": f"Captura guardada en {filepath}", "path": filepath}
    except Exception as e:
        return {"success": False, "message": f"Error al capturar: {e}"}


def minimize_window() -> dict:
    """Minimizar ventana actual"""
    if not PYAUTOGUI_AVAILABLE:
        return {"success": False, "message": "pyautogui no disponible."}
    try:
        pyautogui.hotkey('win', 'down')
        return {"success": True, "message": "Ventana minimizada."}
    except Exception as e:
        return {"success": False, "message": f"Error: {e}"}


def maximize_window() -> dict:
    """Maximizar ventana actual"""
    if not PYAUTOGUI_AVAILABLE:
        return {"success": False, "message": "pyautogui no disponible."}
    try:
        pyautogui.hotkey('win', 'up')
        return {"success": True, "message": "Ventana maximizada."}
    except Exception as e:
        return {"success": False, "message": f"Error: {e}"}


def close_window() -> dict:
    """Cerrar ventana actual"""
    if not PYAUTOGUI_AVAILABLE:
        return {"success": False, "message": "pyautogui no disponible."}
    try:
        pyautogui.hotkey('alt', 'F4')
        return {"success": True, "message": "Ventana cerrada."}
    except Exception as e:
        return {"success": False, "message": f"Error: {e}"}


def close_app(app_name: str) -> dict:
    """
    Cerrar una aplicación específica por nombre
    
    Args:
        app_name: Nombre del proceso (ej: 'spotify', 'chrome', 'notepad')
    """
    # Mapeo de nombres comunes a nombres de proceso
    app_mapping = {
        "spotify": "Spotify.exe",
        "chrome": "chrome.exe",
        "firefox": "firefox.exe",
        "edge": "msedge.exe",
        "notepad": "notepad.exe",
        "word": "WINWORD.EXE",
        "excel": "EXCEL.EXE",
        "discord": "Discord.exe",
        "steam": "steam.exe",
        "explorer": "explorer.exe",
        "vlc": "vlc.exe",
    }
    
    # Obtener nombre de proceso real
    process_name = app_mapping.get(app_name.lower(), f"{app_name}.exe")
    
    try:
        result = subprocess.run(
            f'taskkill /IM "{process_name}" /F',
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return {"success": True, "message": f"{app_name.capitalize()} cerrado."}
        elif "no se encontró" in result.stderr.lower() or "not found" in result.stderr.lower():
            return {"success": False, "message": f"{app_name.capitalize()} no está abierto."}
        else:
            return {"success": False, "message": f"No se pudo cerrar {app_name}."}
    except Exception as e:
        return {"success": False, "message": f"Error al cerrar {app_name}: {e}"}


def minimize_all() -> dict:
    """Minimizar todas las ventanas (mostrar escritorio)"""
    if not PYAUTOGUI_AVAILABLE:
        return {"success": False, "message": "pyautogui no disponible."}
    try:
        pyautogui.hotkey('win', 'd')
        return {"success": True, "message": "Mostrando escritorio."}
    except Exception as e:
        return {"success": False, "message": f"Error: {e}"}


def open_file_explorer(path: str = None) -> dict:
    """Abrir explorador de archivos"""
    try:
        if path:
            subprocess.Popen(f'explorer "{path}"', shell=True)
            return {"success": True, "message": f"Abriendo {path}"}
        else:
            subprocess.Popen('explorer', shell=True)
            return {"success": True, "message": "Abriendo explorador de archivos."}
    except Exception as e:
        return {"success": False, "message": f"Error: {e}"}


def open_task_manager() -> dict:
    """Abrir administrador de tareas"""
    try:
        subprocess.Popen('taskmgr', shell=True)
        return {"success": True, "message": "Abriendo administrador de tareas."}
    except Exception as e:
        return {"success": False, "message": f"Error: {e}"}


def open_settings() -> dict:
    """Abrir configuración de Windows"""
    try:
        subprocess.Popen('start ms-settings:', shell=True)
        return {"success": True, "message": "Abriendo configuración."}
    except Exception as e:
        return {"success": False, "message": f"Error: {e}"}


def empty_recycle_bin() -> dict:
    """Vaciar papelera de reciclaje"""
    try:
        # Usar PowerShell para vaciar papelera silenciosamente
        subprocess.run(
            'powershell -command "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"',
            shell=True,
            capture_output=True
        )
        return {"success": True, "message": "Papelera vaciada."}
    except Exception as e:
        return {"success": False, "message": f"Error: {e}"}


def set_brightness(level: int) -> dict:
    """Ajustar brillo de pantalla (0-100)"""
    try:
        level = max(0, min(100, level))  # Clamp 0-100
        # Usar PowerShell con WMI
        cmd = f'''powershell -command "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{level})"'''
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return {"success": True, "message": f"Brillo ajustado a {level}%."}
        else:
            return {"success": False, "message": "No se pudo ajustar el brillo. Es posible que tu pantalla no lo soporte."}
    except Exception as e:
        return {"success": False, "message": f"Error: {e}"}


def switch_window() -> dict:
    """Cambiar a la siguiente ventana (Alt+Tab)"""
    if not PYAUTOGUI_AVAILABLE:
        return {"success": False, "message": "pyautogui no disponible."}
    try:
        pyautogui.hotkey('alt', 'tab')
        return {"success": True, "message": "Cambiando ventana."}
    except Exception as e:
        return {"success": False, "message": f"Error: {e}"}


def system_control(action: str, **kwargs) -> dict:
    """
    Control principal del sistema
    
    Actions:
        shutdown - Apagar PC
        restart - Reiniciar PC
        cancel_shutdown - Cancelar apagado
        sleep - Suspender
        hibernate - Hibernar
        lock - Bloquear pantalla
        screenshot - Captura de pantalla
        minimize - Minimizar ventana
        maximize - Maximizar ventana
        close - Cerrar ventana actual
        close_app - Cerrar aplicación específica (requiere app_name)
        desktop - Mostrar escritorio
        explorer - Abrir explorador
        task_manager - Administrador de tareas
        settings - Configuración
        empty_trash - Vaciar papelera
        brightness - Ajustar brillo (requiere level)
        switch - Cambiar ventana
    """
    actions = {
        "shutdown": lambda: shutdown_pc(kwargs.get('delay', 0)),
        "restart": lambda: restart_pc(kwargs.get('delay', 0)),
        "cancel_shutdown": cancel_shutdown,
        "sleep": sleep_pc,
        "hibernate": hibernate_pc,
        "lock": lock_pc,
        "screenshot": lambda: take_screenshot(kwargs.get('save_to_desktop', True)),
        "minimize": minimize_window,
        "maximize": maximize_window,
        "close": close_window,
        "close_app": lambda: close_app(kwargs.get('app_name', '')),
        "desktop": minimize_all,
        "explorer": lambda: open_file_explorer(kwargs.get('path')),
        "task_manager": open_task_manager,
        "settings": open_settings,
        "empty_trash": empty_recycle_bin,
        "brightness": lambda: set_brightness(kwargs.get('level', 50)),
        "switch": switch_window,
    }
    
    if action.lower() in actions:
        return actions[action.lower()]()
    else:
        return {"success": False, "message": f"Acción desconocida: {action}"}
