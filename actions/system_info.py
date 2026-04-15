import psutil
import socket
import requests
import platform
from datetime import datetime


def get_private_ip():
    """Obtiene la dirección IP privada del sistema"""
    try:
        # Crear un socket para obtener la IP privada
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        private_ip = s.getsockname()[0]
        s.close()
        return private_ip
    except Exception:
        return "No disponible"


def get_public_ip():
    """Obtiene la dirección IP pública del sistema"""
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        return response.json()['ip']
    except Exception:
        return "No disponible"


def get_cpu_info():
    """Obtiene información del CPU"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count(logical=False)
        cpu_count_logical = psutil.cpu_count(logical=True)
        cpu_freq = psutil.cpu_freq()
        
        return {
            'uso': f"{cpu_percent}%",
            'nucleos_fisicos': cpu_count,
            'nucleos_logicos': cpu_count_logical,
            'frecuencia_actual': f"{cpu_freq.current:.2f} MHz" if cpu_freq else "N/A",
            'frecuencia_maxima': f"{cpu_freq.max:.2f} MHz" if cpu_freq else "N/A"
        }
    except Exception as e:
        return {'error': str(e)}


def get_ram_info():
    """Obtiene información de la RAM"""
    try:
        ram = psutil.virtual_memory()
        
        return {
            'total': f"{ram.total / (1024**3):.2f} GB",
            'disponible': f"{ram.available / (1024**3):.2f} GB",
            'usada': f"{ram.used / (1024**3):.2f} GB",
            'porcentaje_uso': f"{ram.percent}%"
        }
    except Exception as e:
        return {'error': str(e)}


def get_disk_info():
    """Obtiene información del disco"""
    try:
        disk = psutil.disk_usage('/')
        
        return {
            'total': f"{disk.total / (1024**3):.2f} GB",
            'usado': f"{disk.used / (1024**3):.2f} GB",
            'libre': f"{disk.free / (1024**3):.2f} GB",
            'porcentaje_uso': f"{disk.percent}%"
        }
    except Exception as e:
        return {'error': str(e)}


def get_battery_info():
    """Obtiene información de la batería (si existe)"""
    try:
        battery = psutil.sensors_battery()
        if battery:
            return {
                'porcentaje': f"{battery.percent}%",
                'conectado': "Sí" if battery.power_plugged else "No",
                'tiempo_restante': f"{battery.secsleft // 60} minutos" if battery.secsleft != psutil.POWER_TIME_UNLIMITED and battery.secsleft != psutil.POWER_TIME_UNKNOWN else "N/A"
            }
        else:
            return None
    except Exception:
        return None


def get_system_info():
    """Obtiene información completa del sistema"""
    try:
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        current_time = datetime.now()
        uptime = current_time - boot_time
        
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        return {
            'sistema_operativo': f"{platform.system()} {platform.release()}",
            'version': platform.version(),
            'arquitectura': platform.machine(),
            'nombre_equipo': platform.node(),
            'tiempo_encendido': f"{hours}h {minutes}m {seconds}s"
        }
    except Exception as e:
        return {'error': str(e)}


def get_network_info():
    """Obtiene información de red"""
    try:
        net_io = psutil.net_io_counters()
        
        return {
            'bytes_enviados': f"{net_io.bytes_sent / (1024**2):.2f} MB",
            'bytes_recibidos': f"{net_io.bytes_recv / (1024**2):.2f} MB",
            'paquetes_enviados': net_io.packets_sent,
            'paquetes_recibidos': net_io.packets_recv
        }
    except Exception as e:
        return {'error': str(e)}


def format_system_report():
    """Genera un reporte formateado del sistema"""
    print("\n" + "="*60)
    print("REPORTE DEL SISTEMA".center(60))
    print("="*60 + "\n")
    
    # IPs
    print("📡 INFORMACIÓN DE RED")
    print(f"  IP Pública:  {get_public_ip()}")
    print(f"  IP Privada:  {get_private_ip()}")
    
    net_info = get_network_info()
    if 'error' not in net_info:
        print(f"  Datos enviados:  {net_info['bytes_enviados']}")
        print(f"  Datos recibidos: {net_info['bytes_recibidos']}")
    
    print("\n" + "-"*60 + "\n")
    
    # Sistema
    print("💻 INFORMACIÓN DEL SISTEMA")
    sys_info = get_system_info()
    if 'error' not in sys_info:
        print(f"  SO:          {sys_info['sistema_operativo']}")
        print(f"  Equipo:      {sys_info['nombre_equipo']}")
        print(f"  Arquitectura: {sys_info['arquitectura']}")
        print(f"  Tiempo encendido: {sys_info['tiempo_encendido']}")
    
    print("\n" + "-"*60 + "\n")
    
    # CPU
    print("🔧 PROCESADOR (CPU)")
    cpu_info = get_cpu_info()
    if 'error' not in cpu_info:
        print(f"  Uso actual:   {cpu_info['uso']}")
        print(f"  Núcleos físicos:  {cpu_info['nucleos_fisicos']}")
        print(f"  Núcleos lógicos:  {cpu_info['nucleos_logicos']}")
        print(f"  Frecuencia actual: {cpu_info['frecuencia_actual']}")
        print(f"  Frecuencia máxima: {cpu_info['frecuencia_maxima']}")
    
    print("\n" + "-"*60 + "\n")
    
    # RAM
    print("🧠 MEMORIA RAM")
    ram_info = get_ram_info()
    if 'error' not in ram_info:
        print(f"  Total:       {ram_info['total']}")
        print(f"  Usada:       {ram_info['usada']}")
        print(f"  Disponible:  {ram_info['disponible']}")
        print(f"  Uso:         {ram_info['porcentaje_uso']}")
    
    print("\n" + "-"*60 + "\n")
    
    # Disco
    print("💾 ALMACENAMIENTO")
    disk_info = get_disk_info()
    if 'error' not in disk_info:
        print(f"  Total:       {disk_info['total']}")
        print(f"  Usado:       {disk_info['usado']}")
        print(f"  Libre:       {disk_info['libre']}")
        print(f"  Uso:         {disk_info['porcentaje_uso']}")
    
    # Batería (si existe)
    battery_info = get_battery_info()
    if battery_info:
        print("\n" + "-"*60 + "\n")
        print("🔋 BATERÍA")
        print(f"  Nivel:       {battery_info['porcentaje']}")
        print(f"  Conectado:   {battery_info['conectado']}")
        print(f"  Tiempo restante: {battery_info['tiempo_restante']}")
    
    print("\n" + "="*60 + "\n")


def get_system_status_text():
    """Genera un reporte en texto simple para el asistente AI"""
    report = []
    
    # IPs
    report.append(f"Tu IP pública es {get_public_ip()} y tu IP privada es {get_private_ip()}.")
    
    # CPU
    cpu_info = get_cpu_info()
    if 'error' not in cpu_info:
        report.append(f"El procesador tiene un uso del {cpu_info['uso']}, con {cpu_info['nucleos_fisicos']} núcleos físicos y {cpu_info['nucleos_logicos']} núcleos lógicos.")
    
    # RAM
    ram_info = get_ram_info()
    if 'error' not in ram_info:
        report.append(f"La memoria RAM tiene {ram_info['total']} en total, con {ram_info['disponible']} disponibles. El uso actual es del {ram_info['porcentaje_uso']}.")
    
    # Disco
    disk_info = get_disk_info()
    if 'error' not in disk_info:
        report.append(f"El disco tiene {disk_info['total']} en total, con {disk_info['libre']} libres. El uso es del {disk_info['porcentaje_uso']}.")
    
    # Sistema
    sys_info = get_system_info()
    if 'error' not in sys_info:
        report.append(f"El sistema es {sys_info['sistema_operativo']} y lleva encendido {sys_info['tiempo_encendido']}.")
    
    # Batería
    battery_info = get_battery_info()
    if battery_info:
        report.append(f"La batería está al {battery_info['porcentaje']} y {'está conectado' if battery_info['conectado'] == 'Sí' else 'no está conectado'} a la corriente.")
    
    return " ".join(report)


if __name__ == "__main__":
    # Para probar el módulo directamente
    format_system_report()
