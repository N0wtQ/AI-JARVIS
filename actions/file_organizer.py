"""
File Organizer Action
Organiza archivos en carpetas por tipo, fecha, etc.
Detecta la carpeta abierta en el explorador de Windows
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List

# Intentar importar win32com para detectar carpeta del explorador
try:
    import win32com.client
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False


# Categorías de archivos por extensión
FILE_CATEGORIES = {
    "Imágenes": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico", ".tiff", ".raw"],
    "Videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v"],
    "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"],
    "Documentos": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx"],
    "Comprimidos": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
    "Código": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".h", ".php", ".json", ".xml", ".sql"],
    "Ejecutables": [".exe", ".msi", ".bat", ".cmd", ".sh"],
    "Fuentes": [".ttf", ".otf", ".woff", ".woff2"],
}


def get_active_explorer_path() -> Optional[str]:
    """
    Obtiene la ruta de la carpeta activa en el Explorador de Windows
    
    Returns:
        Ruta de la carpeta o None si no se puede detectar
    """
    if not WIN32_AVAILABLE:
        return None
    
    try:
        shell = win32com.client.Dispatch("Shell.Application")
        windows = shell.Windows()
        
        # Buscar la ventana del explorador activa
        for window in windows:
            try:
                # Verificar que sea una ventana del explorador
                if "explorer" in window.FullName.lower():
                    url = window.LocationURL
                    if url:
                        # Convertir URL file:/// a ruta normal
                        if url.startswith("file:///"):
                            path = url[8:].replace("/", "\\")
                            # Decodificar caracteres especiales
                            import urllib.parse
                            path = urllib.parse.unquote(path)
                            if os.path.isdir(path):
                                return path
            except:
                continue
        
        return None
        
    except Exception as e:
        print(f"Error detectando carpeta: {e}")
        return None


def get_category(extension: str) -> str:
    """Obtiene la categoría de un archivo según su extensión"""
    ext = extension.lower()
    for category, extensions in FILE_CATEGORIES.items():
        if ext in extensions:
            return category
    return "Otros"


def organize_by_type(folder_path: str, create_folders: bool = True) -> dict:
    """
    Organiza archivos por tipo/extensión
    
    Args:
        folder_path: Ruta de la carpeta a organizar
        create_folders: Si crear subcarpetas por categoría
        
    Returns:
        dict con resultado de la operación
    """
    if not os.path.isdir(folder_path):
        return {"success": False, "message": f"La carpeta no existe: {folder_path}"}
    
    moved_files = 0
    errors = []
    
    try:
        for filename in os.listdir(folder_path):
            filepath = os.path.join(folder_path, filename)
            
            # Solo procesar archivos, no carpetas
            if os.path.isfile(filepath):
                ext = os.path.splitext(filename)[1]
                if ext:  # Solo si tiene extensión
                    category = get_category(ext)
                    
                    if create_folders:
                        # Crear carpeta de categoría si no existe
                        category_folder = os.path.join(folder_path, category)
                        if not os.path.exists(category_folder):
                            os.makedirs(category_folder)
                        
                        # Mover archivo
                        dest_path = os.path.join(category_folder, filename)
                        
                        # Si ya existe, añadir número
                        if os.path.exists(dest_path):
                            base, ext = os.path.splitext(filename)
                            counter = 1
                            while os.path.exists(dest_path):
                                dest_path = os.path.join(category_folder, f"{base}_{counter}{ext}")
                                counter += 1
                        
                        shutil.move(filepath, dest_path)
                        moved_files += 1
        
        return {
            "success": True,
            "message": f"Organizado. {moved_files} archivos movidos a carpetas por tipo.",
            "moved": moved_files
        }
        
    except Exception as e:
        return {"success": False, "message": f"Error organizando: {e}"}


def organize_by_date(folder_path: str, format: str = "year_month") -> dict:
    """
    Organiza archivos por fecha de modificación
    
    Args:
        folder_path: Ruta de la carpeta
        format: "year" (2024), "year_month" (2024-01), "year_month_day" (2024-01-15)
    """
    if not os.path.isdir(folder_path):
        return {"success": False, "message": f"La carpeta no existe: {folder_path}"}
    
    moved_files = 0
    
    try:
        for filename in os.listdir(folder_path):
            filepath = os.path.join(folder_path, filename)
            
            if os.path.isfile(filepath):
                # Obtener fecha de modificación
                mtime = os.path.getmtime(filepath)
                date = datetime.fromtimestamp(mtime)
                
                # Crear nombre de carpeta según formato
                if format == "year":
                    folder_name = str(date.year)
                elif format == "year_month_day":
                    folder_name = date.strftime("%Y-%m-%d")
                else:  # year_month
                    folder_name = date.strftime("%Y-%m")
                
                date_folder = os.path.join(folder_path, folder_name)
                if not os.path.exists(date_folder):
                    os.makedirs(date_folder)
                
                dest_path = os.path.join(date_folder, filename)
                if os.path.exists(dest_path):
                    base, ext = os.path.splitext(filename)
                    counter = 1
                    while os.path.exists(dest_path):
                        dest_path = os.path.join(date_folder, f"{base}_{counter}{ext}")
                        counter += 1
                
                shutil.move(filepath, dest_path)
                moved_files += 1
        
        return {
            "success": True,
            "message": f"Organizado por fecha. {moved_files} archivos movidos.",
            "moved": moved_files
        }
        
    except Exception as e:
        return {"success": False, "message": f"Error: {e}"}


def organize_by_size(folder_path: str) -> dict:
    """
    Organiza archivos por tamaño (Pequeño, Mediano, Grande, Muy Grande)
    """
    if not os.path.isdir(folder_path):
        return {"success": False, "message": f"La carpeta no existe: {folder_path}"}
    
    # Límites de tamaño en bytes
    SIZE_LIMITS = {
        "Pequeño (< 1MB)": 1024 * 1024,
        "Mediano (1-100MB)": 100 * 1024 * 1024,
        "Grande (100MB-1GB)": 1024 * 1024 * 1024,
        "Muy Grande (> 1GB)": float('inf')
    }
    
    moved_files = 0
    
    try:
        for filename in os.listdir(folder_path):
            filepath = os.path.join(folder_path, filename)
            
            if os.path.isfile(filepath):
                size = os.path.getsize(filepath)
                
                # Determinar categoría de tamaño
                if size < SIZE_LIMITS["Pequeño (< 1MB)"]:
                    category = "Pequeño (< 1MB)"
                elif size < SIZE_LIMITS["Mediano (1-100MB)"]:
                    category = "Mediano (1-100MB)"
                elif size < SIZE_LIMITS["Grande (100MB-1GB)"]:
                    category = "Grande (100MB-1GB)"
                else:
                    category = "Muy Grande (> 1GB)"
                
                size_folder = os.path.join(folder_path, category)
                if not os.path.exists(size_folder):
                    os.makedirs(size_folder)
                
                dest_path = os.path.join(size_folder, filename)
                if os.path.exists(dest_path):
                    base, ext = os.path.splitext(filename)
                    counter = 1
                    while os.path.exists(dest_path):
                        dest_path = os.path.join(size_folder, f"{base}_{counter}{ext}")
                        counter += 1
                
                shutil.move(filepath, dest_path)
                moved_files += 1
        
        return {
            "success": True,
            "message": f"Organizado por tamaño. {moved_files} archivos movidos.",
            "moved": moved_files
        }
        
    except Exception as e:
        return {"success": False, "message": f"Error: {e}"}


def list_folder_contents(folder_path: str) -> dict:
    """Lista el contenido de una carpeta"""
    if not os.path.isdir(folder_path):
        return {"success": False, "message": f"La carpeta no existe: {folder_path}"}
    
    try:
        files = []
        folders = []
        
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isfile(item_path):
                size = os.path.getsize(item_path)
                files.append({"name": item, "size": size})
            else:
                folders.append(item)
        
        return {
            "success": True,
            "path": folder_path,
            "files": files,
            "folders": folders,
            "message": f"Carpeta: {folder_path}\nArchivos: {len(files)}, Subcarpetas: {len(folders)}"
        }
        
    except Exception as e:
        return {"success": False, "message": f"Error: {e}"}


def organize_files(action: str = "by_type", folder_path: str = None, **kwargs) -> dict:
    """
    Función principal para organizar archivos
    
    Args:
        action: "by_type", "by_date", "by_size", "list", "detect"
        folder_path: Ruta de la carpeta (si None, detecta la carpeta abierta)
    """
    # Si no se especifica ruta, detectar la carpeta abierta
    if not folder_path:
        folder_path = get_active_explorer_path()
        if not folder_path:
            return {
                "success": False,
                "message": "No pude detectar la carpeta abierta. Abre una carpeta en el Explorador de Windows o especifica la ruta."
            }
    
    # Ejecutar acción
    if action == "by_type":
        return organize_by_type(folder_path)
    elif action == "by_date":
        date_format = kwargs.get("format", "year_month")
        return organize_by_date(folder_path, date_format)
    elif action == "by_size":
        return organize_by_size(folder_path)
    elif action == "list":
        return list_folder_contents(folder_path)
    elif action == "detect":
        if folder_path:
            return {"success": True, "message": f"Carpeta detectada: {folder_path}", "path": folder_path}
        else:
            return {"success": False, "message": "No hay carpeta del explorador abierta."}
    else:
        return {"success": False, "message": f"Acción desconocida: {action}"}
