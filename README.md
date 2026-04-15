# 🤖 JARVIS - Asistente de IA Completo

**JARVIS** (Just A Rather Very Intelligent System) - Un asistente de escritorio sofisticado con interfaz gráfica animada, reconocimiento de voz, y sistema de acciones inteligentes.

---

## 🚀 Inicio Rápido

```powershell
# 1. Instalar dependencias
py -m pip install -r requirements.txt

# 2. Descargar modelo de voz
py scripts/download_vosk_model.py

# 3. Configurar API keys
# Copia .env.example a .env y agrega tus keys

# 4. Iniciar JARVIS
py main.py
# o
start.bat
```

---

## 📁 Estructura del Proyecto

```
AI-Assistant/
│
├── 📂 actions/              # Acciones automáticas
│   ├── open_app.py         # Abrir aplicaciones
│   ├── wolfram_query.py    # WolframAlpha
│   ├── system_info.py      # Info del sistema
│   └── ...
│
├── 📂 assets/               # Recursos visuales
│   ├── jarvis_face.png     # Cara de JARVIS
│   ├── jarvis_icon.ico     # Icono de la app
│   └── ...
│
├── 📂 core/                 # Configuración del sistema
│   └── prompt.txt          # Prompt del sistema
│
├── 📂 docs/                 # 📚 Documentación
│   ├── README.md           # Documentación principal
│   ├── COMANDOS_VOZ.md     # Lista de comandos
│   ├── MEMORIA_INTELIGENTE.md
│   ├── WOLFRAM_README.md
│   ├── SYSTEM_INFO_README.md
│   └── ...
│
├── 📂 memory/               # Sistema de memoria
│   ├── memory_manager_v2.py
│   ├── user_memory.json    # Memoria persistente
│   └── conversations.json  # Historial
│
├── 📂 models/               # Modelos de voz (Vosk)
│   └── vosk-model-small-es-*/
│
├── 📂 knowledge/            # Base de conocimiento (RAG)
│   ├── embeddings/
│   └── [tus documentos]
│
├── 📂 scripts/              # 🛠️ Scripts de utilidad
│   ├── cleanup_memory.py   # Limpieza de memoria
│   ├── migrate_memory.py   # Migración
│   ├── download_vosk_model.py
│   └── manage_knowledge.py
│
├── 📂 tests/                # 🧪 Pruebas
│   ├── test_garbage_filter.py
│   └── example_system_info.py
│
├── 📄 main.py               # 🎯 Aplicación principal
├── 📄 ai_handler.py         # Gestión IA
├── 📄 speech_handler.py     # Voz → Texto
├── 📄 voice_player.py       # Texto → Voz
├── 📄 rag_knowledge.py      # Sistema RAG
├── 📄 start.bat             # Inicio rápido
├── 📄 .env                  # Configuración (crear)
├── 📄 .env.example          # Plantilla
└── 📄 requirements.txt      # Dependencias
```

---

## ✨ Características Principales

### 🎯 Interfaz
- Cara animada de JARVIS (60 FPS)
- Chat visual con historial
- Entrada por texto o voz
- Salida de voz natural

### 🧠 Inteligencia
- **Memoria con Niveles** (🔴 Crítica, 🟡 Media, 🟢 Corta)
- **RAG** - Lee tus documentos
- **Filtrado de basura semántica** - Memoria limpia
- **Sistema de Intents** - Detección automática de acciones

### 🎵 Acciones
- Spotify, Clima
- WolframAlpha (cálculos, conversiones)
- Info del sistema (IP, CPU, RAM)
- Búsquedas web, abrir apps

---

## 🛠️ Scripts de Utilidad

### Gestión de Memoria
```bash
# Ver estadísticas
py scripts/cleanup_memory.py --stats

# Limpiar memoria automáticamente
py scripts/cleanup_memory.py

# Limpiar solo basura semántica
py scripts/cleanup_memory.py --garbage

# Migrar de versión antigua
py scripts/migrate_memory.py
```

### Base de Conocimiento
```bash
# Indexar documentos
py scripts/manage_knowledge.py index

# Agregar documento
py scripts/manage_knowledge.py add path/to/doc.pdf

# Listar documentos
py scripts/manage_knowledge.py list
```

### Pruebas
```bash
# Test de filtro de basura semántica
py tests/test_garbage_filter.py

# Ejemplo de info del sistema
py tests/example_system_info.py
```

---

## 📚 Documentación

Toda la documentación está en la carpeta `docs/`:

- **[docs/README.md](docs/README.md)** - Documentación completa
- **[docs/COMANDOS_VOZ.md](docs/COMANDOS_VOZ.md)** - Lista completa de comandos
- **[docs/MEMORIA_INTELIGENTE.md](docs/MEMORIA_INTELIGENTE.md)** - Sistema de memoria
- **[docs/WOLFRAM_README.md](docs/WOLFRAM_README.md)** - WolframAlpha
- **[docs/SYSTEM_INFO_README.md](docs/SYSTEM_INFO_README.md)** - Info del sistema
- **[docs/RATE_LIMITS_GROQ.md](docs/RATE_LIMITS_GROQ.md)** - Solución error 429
- **[docs/UI_OPTIMIZATION_GUIDE.md](docs/UI_OPTIMIZATION_GUIDE.md)** - Optimización

---

## ⚙️ Configuración

### API Keys necesarias

Edita `.env`:

```env
# IA (Elige uno)
API_PROVIDER=groq
API_KEY=gsk_...
MODEL=llama-3.1-8b-instant

# WolframAlpha (Opcional)
WOLFRAM_API_KEY=tu_app_id

# Voz
EDGE_VOICE=es-ES-AlvaroNeural
```

### Obtener API Keys

- **Groq (Gratis):** https://console.groq.com
- **WolframAlpha (2000/mes gratis):** https://products.wolframalpha.com/api/

---

## 🎤 Comandos de Voz

### Ejemplos rápidos:

```
"Cuánto es 25 por 37"
"Convierte 100 km a millas"
"Cuál es mi IP pública"
"Abre YouTube"
"Pon música de Shakira"
"Qué tiempo hace en Madrid"
```

**Ver lista completa:** [docs/COMANDOS_VOZ.md](docs/COMANDOS_VOZ.md)

---

## 🔧 Solución de Problemas

### Error 429 (Rate Limit)
```bash
# Ver guía
type docs\RATE_LIMITS_GROQ.md
```

### Consumo alto de CPU
```bash
# Ver guía de optimización
type docs\UI_OPTIMIZATION_GUIDE.md
```

### Memoria con basura
```bash
# Limpiar automáticamente
py scripts\cleanup_memory.py --garbage
```

---

## 📊 Estadísticas

Ver estado actual:
```bash
py scripts/cleanup_memory.py --stats
```

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas!

1. Reporta bugs
2. Sugiere características
3. Envía pull requests
4. Mejora la documentación

---

## 📄 Licencia

MIT License - Usa, modifica y distribuye libremente.

---

## ⭐ Créditos

**Autor:** Almudena Bedoya  
**Versión:** 2.0  
**Última actualización:** Febrero 2026

---

**¡Disfruta de JARVIS!** 🎉

Para documentación completa, consulta: [docs/README.md](docs/README.md)
