# 🤖 JARVIS - Asistente de IA Completo

**JARVIS** (Just A Rather Very Intelligent System) - Un asistente de escritorio sofisticado con interfaz gráfica animada, reconocimiento de voz, y sistema de acciones inteligentes.

---

## 📑 Índice

1. [Características Principales](#-características-principales)
2. [Requisitos](#-requisitos)
3. [Instalación](#-instalación)
4. [Configuración](#️-configuración)
5. [Uso Básico](#-uso-básico)
6. [Comandos de Voz](#-comandos-de-voz)
7. [Capacidades Avanzadas](#-capacidades-avanzadas)
8. [Optimización de Rendimiento](#-optimización-de-rendimiento)
9. [Estructura del Proyecto](#-estructura-del-proyecto)
10. [Solución de Problemas](#-solución-de-problemas)

---

## ✨ Características Principales

### 🎯 Interfaz y Experiencia
- **Interfaz Visual Animada** - Cara de JARVIS con efectos de halo que responde al habla (60 FPS)
- **Chat Visual** - Historial de conversaciones con formato elegante
- **Entrada Dual** - Texto o voz (reconocimiento offline con Vosk)
- **Salida de Voz** - Respuestas habladas naturales (Edge TTS español)
- **Adjuntar Archivos** - Analiza código y documentos directamente

### 🧠 Inteligencia y Memoria
- **Memoria Persistente** - Guarda tu nombre, preferencias, relaciones
- **Historial de Conversaciones** - Últimas 50 conversaciones
- **RAG (Base de Conocimiento)** - Lee y aprende de tus documentos (PDF, TXT, MD)
- **Sistema de Intents** - Detecta automáticamente qué acción realizar

### 🎵 Control de Aplicaciones
- **Spotify** - Reproduce música ("Pon Shakira", "Reproduce música de Queen")
- **Abrir Apps** - Chrome, Word, Excel, calculadora, VS Code, Discord
- **Sitios Web** - YouTube, Google, GitHub, Amazon, Twitter, Reddit
- **Búsquedas** - Buscar en sitios específicos ("Busca en YouTube videos de cocina")

### 💬 Comunicación
- **WhatsApp Automático** - Envía mensajes con un comando
- **Análisis Detallados** - Genera informes extensos y los envía automáticamente
- **Múltiples Plataformas** - WhatsApp (extensible a Telegram, etc.)

### 📊 Información y Utilidades
- **Clima** - Información meteorológica de cualquier ciudad
- **Búsqueda Web** - Resultados de DuckDuckGo (sin API key)
- **WolframAlpha** - Cálculos matemáticos, conversiones, datos científicos
- **Info del Sistema** - IP pública/privada, CPU, RAM, disco

---

## 📋 Requisitos

- **Python 3.7+** (recomendado 3.10)
- **Windows 10/11** (adaptable a Linux/Mac)
- **Micrófono** para entrada de voz
- **API Key** de OpenAI, Groq, o Anthropic
- **Conexión a Internet** para IA y búsquedas

---

## 🚀 Instalación

### 1. Instalar Dependencias

```powershell
py -m pip install -r requirements.txt
```

### 2. Instalar PyAudio (para voz)

En Windows:
```powershell
py -m pip install pipwin
py -m pipwin install pyaudio
```

Si falla, descarga el wheel desde [aquí](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)

### 3. Descargar Modelo de Voz en Español

```powershell
py download_vosk_model.py
```

Esto descarga el modelo Vosk en español (~38MB) para reconocimiento de voz offline.

### 4. Configurar Variables de Entorno

Copia `.env.example` a `.env` y configura:

```env
# API de IA (elige uno)
API_PROVIDER=groq
API_KEY=tu_api_key_aqui
MODEL=llama-3.3-70b-versatile

# Voz (opcional)
VOICE_ID=0
VOICE_RATE=150
VOICE_VOLUME=0.9

# WolframAlpha (opcional)
WOLFRAM_API_KEY=tu_wolfram_api_key_aqui
```

---

## ⚙️ Configuración

### Proveedores de IA

#### **Groq** (Recomendado - Gratis y Rápido)
```env
API_PROVIDER=groq
API_KEY=gsk_...
MODEL=llama-3.3-70b-versatile
```
- ✅ Gratis
- ✅ Muy rápido
- ✅ 14,400 tokens/min
- 🔗 [Obtener API key](https://console.groq.com)

#### **OpenAI** (Más Potente)
```env
API_PROVIDER=openai
API_KEY=sk-...
MODEL=gpt-3.5-turbo
```
- ✅ GPT-4 disponible
- ❌ Requiere pago
- 🔗 [Obtener API key](https://platform.openai.com)

#### **Anthropic** (Claude)
```env
API_PROVIDER=anthropic
API_KEY=sk-ant-...
MODEL=claude-3-sonnet-20240229
```
- ✅ Excelente razonamiento
- ❌ Requiere pago
- 🔗 [Obtener API key](https://console.anthropic.com)

### WolframAlpha (Opcional)

Para cálculos matemáticos y datos científicos:

1. Obtén API key gratuita: https://products.wolframalpha.com/api/
2. Plan gratuito: 2,000 consultas/mes
3. Agrega a `.env`:
   ```env
   WOLFRAM_API_KEY=tu_app_id_aqui
   ```

---

## 🎯 Uso Básico

### Iniciar JARVIS

```powershell
start.bat
```

O directamente:
```powershell
py main.py
```

### Interactuar

1. **Por Texto** - Escribe en el cuadro de texto y presiona Enter o "Enviar"
2. **Por Voz** - Haz clic en "🎤 Voz" y habla
3. **Adjuntar Archivos** - Botón "📎" para analizar documentos

---

## 🎤 Comandos de Voz

### 🧮 Cálculos y Matemáticas (WolframAlpha)

```
"Cuánto es 25 por 37"
"Calcula 156 dividido entre 12"
"Raíz cuadrada de 144"
"Resuelve x al cuadrado más 2x más 1 igual a cero"
```

### 🔄 Conversiones

```
"Convierte 100 kilómetros a millas"
"Pasa 25 grados celsius a fahrenheit"
"Cuántos litros son 5 galones"
```

### 📊 Información Científica

```
"Cuál es la velocidad de la luz"
"Distancia de la tierra a la luna"
"Población de España"
"Altura del monte Everest"
```

### 💻 Información del Sistema

```
"Cuál es mi IP pública"
"Estado del ordenador"
"Cómo está la CPU"
"Cuánta RAM tengo disponible"
```

### 🎵 Música (Spotify)

```
"Pon música FUNK"
"Reproduce Bohemian Rhapsody"
"Pon música de los 80"
```

### 🌐 Web y Búsquedas

```
"Abre YouTube"
"Busca en YouTube videos de cocina"
"Busca información sobre Python"
"Abre Google"
```

### 💬 WhatsApp

```
"Dile a mamá que llegaré tarde"
"Envía un mensaje a Juan diciendo que ya salí"
"Envíame análisis de la situación en España por WhatsApp"
```

### 🌤️ Clima

```
"Qué tiempo hace en Madrid"
"Clima de mañana en Barcelona"
"Temperatura en Valencia"
```

### 📱 Aplicaciones

```
"Abre Chrome"
"Abre la calculadora"
"Abre Word"
"Abre Visual Studio Code"
```

---

## 🔧 Capacidades Avanzadas

### 📚 Base de Conocimiento (RAG)

JARVIS puede leer y consultar tus documentos:

1. **Agregar Documentos**
   - Coloca archivos en la carpeta `knowledge/`
   - Formatos: PDF, TXT, MD, JSON, PY, CSV

2. **Indexar**
   ```powershell
   py manage_knowledge.py index
   ```

3. **Consultar**
   ```
   "¿Qué sabemos sobre inteligencia artificial?"
   "Resume el documento sobre Python"
   "Información sobre el proyecto X"
   ```

JARVIS buscará en tus documentos automáticamente y te dará respuestas basadas en ellos.

### 🧠 Sistema de Memoria

JARVIS recuerda:
- **Identidad** - Tu nombre, edad, ciudad
- **Preferencias** - Gustos, intereses
- **Relaciones** - Familia, amigos, contactos
- **Conversaciones** - Últimas 50 interacciones

Ejemplo:
```
Usuario: "Me llamo María"
JARVIS: "Encantado de conocerla, María. Lo recordaré."

[Más tarde...]
Usuario: "Cómo me llamo?"
JARVIS: "Su nombre es María."
```

### 🎯 Sistema de Intents (Detección Inteligente)

JARVIS detecta automáticamente qué quieres hacer:

| Intent | Detecta | Acción |
|--------|---------|--------|
| `chat` | Conversación | Responde normalmente |
| `open_app` | "abre Chrome" | Abre la aplicación |
| `open_site` | "abre YouTube" | Abre el sitio web |
| `play_music` | "pon Shakira" | Reproduce en Spotify |
| `send_message` | "dile a mamá..." | Envía WhatsApp |
| `weather_report` | "clima en Madrid" | Consulta el clima |
| `search` | "busca sobre Python" | Búsqueda web |
| `wolfram` | "cuánto es 2+2" | Consulta WolframAlpha |
| `system_info` | "mi IP pública" | Info del sistema |

No necesitas decir comandos específicos - habla naturalmente.

---

## ⚡ Optimización de Rendimiento

### Versión Optimizada de UI

Si JARVIS consume mucha CPU/RAM, existe una versión optimizada:

```python
# En jarvis_face_optimized.py
JarvisFaceOptimized("balanced")  # Recomendado
```

**Modos disponibles:**

| Modo | FPS | CPU | RAM | Calidad |
|------|-----|-----|-----|---------|
| **Mínimo** | 0 | 🟢 Muy Baja | 🟢 Muy Baja | ⭐⭐ |
| **Bajo** | 15 | 🟢 Baja | 🟢 Baja | ⭐⭐⭐ |
| **Balanceado** | 24 | 🟡 Media | 🟡 Media | ⭐⭐⭐⭐ |
| **Alto** | 30 | 🟡 Media-Alta | 🟡 Media | ⭐⭐⭐⭐⭐ |
| **Actual** | 60 | 🔴 Alta | 🔴 Alta | ⭐⭐⭐⭐⭐ |

**Consumo esperado:**
- Actual: 15-25% CPU, 150-200 MB RAM
- Balanceado: 3-8% CPU, 80-120 MB RAM
- Bajo: 2-5% CPU, 60-90 MB RAM

Consulta `UI_OPTIMIZATION_GUIDE.md` para más detalles.

---

## 📁 Estructura del Proyecto

```
AI-Assistant/
├── main.py                    # Interfaz principal con GUI
├── ai_handler.py              # Gestión IA + RAG
├── speech_handler.py          # Voz → Texto (Vosk)
├── voice_player.py            # Texto → Voz (Edge TTS)
├── rag_knowledge.py           # Sistema RAG
├── manage_knowledge.py        # Gestión de documentos
├── download_vosk_model.py     # Descarga modelo de voz
├── start.bat                  # Inicio rápido
│
├── actions/                   # Acciones automáticas
│   ├── __init__.py
│   ├── open_app.py           # Abrir aplicaciones
│   ├── open_url.py           # Abrir sitios web
│   ├── send_message.py       # WhatsApp
│   ├── spotify_control.py    # Música
│   ├── weather_report.py     # Clima
│   ├── web_search.py         # Búsquedas
│   ├── wolfram_query.py      # WolframAlpha
│   └── system_info.py        # Info del sistema
│
├── core/                      # Configuración del sistema
│   └── prompt.txt            # Prompt del sistema
│
├── memory/                    # Sistema de memoria
│   ├── memory_manager.py
│   ├── conversations.json    # Historial
│   └── user_memory.json      # Memoria persistente
│
├── knowledge/                 # Base de conocimiento (RAG)
│   ├── embeddings/           # Vectores
│   └── [tus documentos]      # PDFs, TXT, MD, etc.
│
├── models/                    # Modelo de voz Vosk
│   └── vosk-model-small-es-*/
│
├── jarvis_face.png           # Imagen de JARVIS
├── jarvis_icon.ico           # Icono de la app
├── .env                      # Configuración (crear)
├── .env.example              # Plantilla de configuración
├── requirements.txt          # Dependencias Python
└── README_COMPLETO.md        # Este archivo
```

---

## 🔧 Solución de Problemas

### PyAudio no se instala

**Windows:**
```powershell
py -m pip install pipwin
py -m pipwin install pyaudio
```

**Linux:**
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

**Mac:**
```bash
brew install portaudio
pip install pyaudio
```

### Micrófono no funciona

1. Verifica permisos de micrófono en configuración de Windows
2. Asegúrate que el micrófono está como dispositivo predeterminado
3. Prueba con otra aplicación que use el micrófono

### Error de API

- Verifica que la API key es correcta en `.env`
- Comprueba que tienes créditos/cuota disponible
- Asegúrate que el nombre del modelo es correcto

### WolframAlpha no responde

- Verifica que `WOLFRAM_API_KEY` está configurada en `.env`
- Comprueba que tienes internet
- Verifica que no has excedido las 2,000 consultas/mes

### JARVIS consume muchos recursos

- Usa la versión optimizada: `jarvis_face_optimized.py`
- Cambia a modo "balanced" o "low"
- Consulta `UI_OPTIMIZATION_GUIDE.md`

### Vosk no reconoce bien el español

- Verifica que el modelo se descargó correctamente en `models/`
- Habla claro y pausado
- Reduce ruido ambiente
- Asegúrate que el micrófono está cerca

### WhatsApp no envía mensajes

- Verifica que WhatsApp Web está cerrado
- La primera vez, escanea el código QR manualmente
- Asegúrate que el contacto existe en tu WhatsApp

---

## 🎨 Personalización

### Cambiar el Prompt del Sistema

Edita `core/prompt.txt` para cambiar el comportamiento de JARVIS.

### Agregar Nuevas Acciones

1. Crea un nuevo archivo en `actions/`
2. Implementa la función
3. Agrégala a `actions/__init__.py`
4. Actualiza `core/prompt.txt` con el nuevo intent
5. Agrega el handler en `main.py` → `_process_intent()`

### Cambiar la Voz

```python
from voice_player import VoicePlayer
vp = VoicePlayer()
vp.list_voices()  # Lista voces disponibles
```

Luego edita `.env`:
```env
VOICE_ID=1  # Cambia el número
```

---

## 📊 Comparación de APIs de IA

| Proveedor | Costo | Velocidad | Calidad | Límite Gratis |
|-----------|-------|-----------|---------|---------------|
| **Groq** | 🟢 Gratis | ⚡ Muy Rápida | ⭐⭐⭐⭐ | 14,400 tokens/min |
| **OpenAI** | 🔴 Pago | 🟡 Media | ⭐⭐⭐⭐⭐ | $5 crédito inicial |
| **Anthropic** | 🔴 Pago | 🟡 Media | ⭐⭐⭐⭐⭐ | Sin gratis |

**Recomendación:** Usa **Groq** para empezar (gratis y rápido).

---

## 🆓 APIs Gratuitas Usadas

- **Groq** - IA (gratis)
- **DuckDuckGo** - Búsquedas (sin API key)
- **wttr.in** - Clima (sin API key)
- **WolframAlpha** - Cálculos (2,000/mes gratis)
- **Edge TTS** - Voz (gratis)
- **Vosk** - Reconocimiento de voz (offline, gratis)

---

## 🚀 Funciones Futuras (Opcional)

- [ ] Minimizar a la bandeja del sistema
- [ ] Atajos de teclado globales
- [ ] Integración con Google Calendar
- [ ] Control de luces inteligentes
- [ ] Telegram bot integration
- [ ] Docker container
- [ ] Web interface

---

## 📝 Notas Importantes

1. **Privacidad** - Tu memoria y conversaciones se guardan localmente
2. **Offline** - Reconocimiento de voz funciona sin internet (Vosk)
3. **Extensible** - Fácil agregar nuevas acciones y capacidades
4. **Multiidioma** - Optimizado para español, pero soporta otros idiomas

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas!

- Reporta bugs
- Sugiere características
- Envía pull requests
- Mejora la documentación

---

## 📄 Licencia

MIT License - Usa, modifica y distribuye libremente.

---

## ⭐ Créditos

Creado con ❤️ para facilitar la interacción con IA en tu escritorio.

**Autor:** Almudena Bedoya  
**Versión:** 2.0  
**Última actualización:** Febrero 2026

---

## 📞 Soporte

¿Problemas o preguntas?

1. Revisa esta documentación completa
2. Consulta los README específicos:
   - `WOLFRAM_README.md` - Guía de WolframAlpha
   - `SYSTEM_INFO_README.md` - Info del sistema
   - `UI_OPTIMIZATION_GUIDE.md` - Optimización
   - `COMANDOS_VOZ.md` - Lista completa de comandos
3. Abre un issue en GitHub

---

**¡Disfruta de JARVIS!** 🎉
