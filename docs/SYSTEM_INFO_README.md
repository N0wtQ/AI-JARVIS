# 📊 Módulo de Información del Sistema

Este módulo te permite obtener información completa del estado de tu ordenador, incluyendo IPs, CPU, RAM, disco, y más.

## 🚀 Uso Rápido

### Opción 1: Reporte Completo (Visual)
Para obtener un reporte completo y formateado:

```python
from actions.system_info import format_system_report

format_system_report()
```

### Opción 2: Texto Simple (Para AI)
Para obtener un texto simple que el asistente pueda leer:

```python
from actions.system_info import get_system_status_text

texto = get_system_status_text()
print(texto)
```

### Opción 3: Información Específica
Para obtener solo información específica:

```python
from actions.system_info import (
    get_public_ip,
    get_private_ip,
    get_cpu_info,
    get_ram_info,
    get_disk_info,
    get_battery_info,
    get_system_info,
    get_network_info
)

# Solo IPs
print(f"IP Pública: {get_public_ip()}")
print(f"IP Privada: {get_private_ip()}")

# Solo CPU
cpu = get_cpu_info()
print(f"CPU: {cpu['uso']} - {cpu['nucleos_logicos']} núcleos")

# Solo RAM
ram = get_ram_info()
print(f"RAM: {ram['porcentaje_uso']} usado - {ram['disponible']} libres")
```

## 📋 Funciones Disponibles

### `get_public_ip()`
Retorna la dirección IP pública del sistema.

**Retorno:** `str` - IP pública o "No disponible"

---

### `get_private_ip()`
Retorna la dirección IP privada del sistema.

**Retorno:** `str` - IP privada o "No disponible"

---

### `get_cpu_info()`
Retorna información detallada del procesador.

**Retorno:** `dict` con las siguientes claves:
- `uso`: Porcentaje de uso actual
- `nucleos_fisicos`: Número de núcleos físicos
- `nucleos_logicos`: Número de núcleos lógicos
- `frecuencia_actual`: Frecuencia actual en MHz
- `frecuencia_maxima`: Frecuencia máxima en MHz

---

### `get_ram_info()`
Retorna información de la memoria RAM.

**Retorno:** `dict` con las siguientes claves:
- `total`: RAM total en GB
- `disponible`: RAM disponible en GB
- `usada`: RAM usada en GB
- `porcentaje_uso`: Porcentaje de uso

---

### `get_disk_info()`
Retorna información del disco principal.

**Retorno:** `dict` con las siguientes claves:
- `total`: Espacio total en GB
- `usado`: Espacio usado en GB
- `libre`: Espacio libre en GB
- `porcentaje_uso`: Porcentaje de uso

---

### `get_battery_info()`
Retorna información de la batería (si existe).

**Retorno:** `dict` o `None` si no hay batería
- `porcentaje`: Nivel de batería
- `conectado`: "Sí" o "No"
- `tiempo_restante`: Tiempo estimado en minutos o "N/A"

---

### `get_system_info()`
Retorna información general del sistema.

**Retorno:** `dict` con las siguientes claves:
- `sistema_operativo`: Nombre y versión del SO
- `version`: Versión detallada
- `arquitectura`: Arquitectura del sistema
- `nombre_equipo`: Nombre del ordenador
- `tiempo_encendido`: Tiempo desde el último arranque

---

### `get_network_info()`
Retorna estadísticas de red.

**Retorno:** `dict` con las siguientes claves:
- `bytes_enviados`: MB enviados
- `bytes_recibidos`: MB recibidos
- `paquetes_enviados`: Cantidad de paquetes enviados
- `paquetes_recibidos`: Cantidad de paquetes recibidos

---

### `format_system_report()`
Imprime un reporte completo y formateado del sistema.

**Retorno:** `None` (imprime directamente)

---

### `get_system_status_text()`
Genera un texto simple con toda la información del sistema, ideal para que el asistente AI lo lea.

**Retorno:** `str` - Texto descriptivo del estado del sistema

---

## 💡 Ejemplos de Uso

### Ejemplo 1: Comando de voz
```python
# Cuando el usuario pregunta: "¿Cuál es mi IP pública?"
from actions.system_info import get_public_ip

respuesta = f"Tu IP pública es {get_public_ip()}"
```

### Ejemplo 2: Monitoreo de recursos
```python
from actions.system_info import get_ram_info, get_cpu_info

ram = get_ram_info()
cpu = get_cpu_info()

# Verificar si los recursos están bajos
if float(ram['porcentaje_uso'].replace('%', '')) > 80:
    print("⚠️ La RAM está casi llena")

if float(cpu['uso'].replace('%', '')) > 90:
    print("⚠️ La CPU está sobrecargada")
```

### Ejemplo 3: Reporte periódico
```python
from actions.system_info import get_system_status_text

# Cada cierto tiempo, el asistente puede informar del estado
estado = get_system_status_text()
# El asistente lee el texto y lo comunica al usuario
```

## 🧪 Probar el Módulo

### Prueba directa:
```bash
py actions\system_info.py
```

### Prueba con ejemplos:
```bash
py example_system_info.py
```

## 📦 Dependencias

Este módulo requiere:
- `psutil` - Para información del sistema
- `requests` - Para obtener la IP pública
- `socket` - Para obtener la IP privada (incluido en Python)
- `platform` - Para información del SO (incluido en Python)
- `datetime` - Para cálculos de tiempo (incluido en Python)

Todas estas dependencias ya están instaladas si ejecutaste `pip install -r requirements.txt`.

## 🔧 Integración con el Asistente

Para integrar este módulo en tu asistente AI, puedes:

1. **Detectar palabras clave** en la entrada del usuario:
   - "IP", "dirección IP", "IP pública", "IP privada"
   - "CPU", "procesador", "uso del procesador"
   - "RAM", "memoria"
   - "disco", "almacenamiento", "espacio"
   - "estado del sistema", "información del ordenador"

2. **Llamar a la función apropiada** según las palabras clave detectadas

3. **Responder al usuario** con la información obtenida

### Ejemplo de integración:
```python
def procesar_comando(texto_usuario):
    texto_lower = texto_usuario.lower()
    
    if "ip pública" in texto_lower or "ip publica" in texto_lower:
        from actions.system_info import get_public_ip
        return f"Tu IP pública es {get_public_ip()}"
    
    elif "estado del sistema" in texto_lower or "estado del ordenador" in texto_lower:
        from actions.system_info import get_system_status_text
        return get_system_status_text()
    
    elif "cpu" in texto_lower or "procesador" in texto_lower:
        from actions.system_info import get_cpu_info
        cpu = get_cpu_info()
        return f"La CPU está al {cpu['uso']} de uso"
    
    # ... más condiciones
```

## ✨ Características

- ✅ Obtiene IP pública e IP privada
- ✅ Monitorea uso de CPU en tiempo real
- ✅ Muestra estado de la RAM (total, usada, disponible)
- ✅ Información del disco (espacio total, usado, libre)
- ✅ Estado de la batería (si existe)
- ✅ Información del sistema operativo
- ✅ Tiempo de encendido del ordenador
- ✅ Estadísticas de red (datos enviados/recibidos)
- ✅ Formato visual para humanos
- ✅ Formato de texto simple para AI
- ✅ Manejo de errores robusto

---

**¡Listo para usar!** 🎉
