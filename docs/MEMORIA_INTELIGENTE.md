# 🧠 Sistema de Memoria Inteligente con Niveles

## 📖 Concepto

JARVIS ahora tiene un sistema de memoria jerárquico que evita "basura semántica" y optimiza el almacenamiento solo de información realmente importante.

---

## 🎯 Niveles de Memoria

### 🔴 CRÍTICA (Permanente)
**Nunca se borra automáticamente**

**Qué guarda:**
- **Identidad:** nombre, edad, ciudad, profesión
- **Relaciones:** familia, amigos, contactos importantes

**Ejemplos:**
```
"Me llamo María" → ✅ Se guarda
"Tengo 25 años" → ✅ Se guarda
"Vivo en Madrid" → ✅ Se guarda
"Mi madre se llama Ana" → ✅ Se guarda
```

---

### 🟡 MEDIA (30 días sin uso)
**Se limpia después de 30 días si no se usa**

**Qué guarda:**
- **Preferencias repetidas** o explícitas
- **Temas frecuentes** de conversación
- **Información importante** mencionada múltiples veces

**Reglas:**
- Solo guarda si se menciona **2+ veces** o es **muy explícita**
- Incrementa contador cada vez que se menciona
- Elimina automáticamente si pasan 30 días sin uso

**Ejemplos:**
```
"Me gusta el jazz" (1ª vez) → ⚠️ Se guarda pero con count=1
"Me encanta el jazz" (2ª vez) → ✅ count=2, más importante
"Me gusta este clima" (casual) → ❌ NO se guarda
```

---

### 🟢 CORTA (7 días)
**Contexto de sesión automático**

**Qué guarda:**
- Conversación reciente (últimas 50 interacciones)
- Notas temporales de la sesión
- Se maneja automáticamente

**Ejemplos:**
```
Conversación del día → ✅ Automático
Notas de > 7 días → 🗑️ Se borran automáticamente
```

---

## ⚖️ Reglas Estrictas

### ✅ QUÉ SÍ Guardar

1. **Identidad explícita:**
   - "Me llamo...", "Tengo X años", "Vivo en..."

2. **Relaciones:**
   - "Mi madre/padre/hermano se llama..."
   - "Mi amigo X..."

3. **Preferencias claras y repetidas:**
   - Mencionadas 2+ veces
   - Muy explícitas: "Mi comida favorita es..."

### ❌ QUÉ NO Guardar

1. **Basura semántica:**
   - "Ok", "Entiendo", "Gracias", "Está bien"

2. **Comentarios casuales únicos:**
   - "Me gusta este clima" (una sola vez)
   - "Qué bonito día"

3. **Tareas y comandos:**
   - "Busca información sobre Python"
   - "Abre Chrome"

4. **Cortesía:**
   - "Buenos días", "Adiós", "Por favor"

---

## 🧹 Limpieza Automática

### Cuándo se Limpia

- **Automáticamente** al iniciar JARVIS (si pasaron >7 días desde última limpieza)
- **Manualmente** con el script `cleanup_memory.py`

### Qué se Limpia

| Nivel | Criterio | Acción |
|-------|----------|--------|
| 🔴 Crítica | - | **Nunca** se limpia |
| 🟡 Media | 30 días sin uso + count=1 | Se elimina |
| 🟢 Corta | >7 días | Se elimina |
| Conversaciones | >50 mensajes | Solo últimas 50 |

---

## 🛠️ Uso del Script de Limpieza

### Ver Estadísticas

```bash
py cleanup_memory.py --stats
```

**Salida:**
```
📊 ESTADÍSTICAS DE MEMORIA
==================================================
🔴 CRÍTICA:
  - Campos de identidad: 3
  - Relaciones: 5

🟡 MEDIA:
  - Preferencias: 8
  - Temas frecuentes: 12

🟢 CORTA:
  - Notas temporales: 2
  - Conversaciones: 50

🧹 Última limpieza: 2026-02-05T10:30:00
==================================================
```

### Limpieza Automática

```bash
py cleanup_memory.py
```

### Simular Limpieza (Dry Run)

```bash
py cleanup_memory.py --dry-run
```

Muestra qué se eliminaría sin hacerlo realmente.

### Limpiar Nivel Específico

```bash
# Limpiar solo memoria corta (temporal)
py cleanup_memory.py --clear short

# Limpiar memoria media (preferencias)
py cleanup_memory.py --clear medium

# ⚠️ Limpiar TODA la memoria (requiere confirmación)
py cleanup_memory.py --clear all
```

---

## 📊 Ejemplos Completos

### Ejemplo 1: Información Personal

```
Usuario: "Me llamo Juan"
JARVIS: "Encantado de conocerle, Juan. Lo recordaré."

→ 🔴 CRÍTICA: identity.name = "Juan" (permanente)

[Días después...]
Usuario: "Cómo me llamo?"
JARVIS: "Su nombre es Juan."
```

### Ejemplo 2: Preferencia Repetida

```
Usuario: "Me gusta el rock"
→ 🟡 MEDIA: favorite_music = "rock" (count=1)

Usuario: "Pon música rock"
→ 🟡 MEDIA: favorite_music = "rock" (count=2) ✅ Consolidada

[30 días después sin mencionar...]
→ 🧹 Se conserva (count >= 2)
```

### Ejemplo 3: Basura Semántica (NO se guarda)

```
Usuario: "Ok, gracias"
→ ❌ NO se guarda nada

Usuario: "Está bien"
→ ❌ NO se guarda nada

Usuario: "Me gusta este día" (casual, 1 vez)
→ ❌ NO se guarda
```

### Ejemplo 4: Relación

```
Usuario: "Mi hermana se llama Laura"
→ 🔴 CRÍTICA: relationships += {name: "Laura", relation: "hermana"}

[Permanente - nunca se borra]
```

---

## 🔄 Migración Automática

Si ya tenías memoria de la versión anterior, se migra automáticamente:

- Identidad → 🔴 Crítica
- Relaciones → 🔴 Crítica
- Preferencias → 🟡 Media (con count=1)
- Conversaciones → 🟢 Corta

---

## 💡 Ventajas del Nuevo Sistema

1. **Sin Basura Semántica**
   - Solo guarda información real y útil

2. **Limpieza Inteligente**
   - Elimina preferencias antiguas no usadas
   - Conserva lo importante (identidad, relaciones)

3. **Eficiencia**
   - Menos contexto enviado al LLM = respuestas más rápidas
   - Menos uso de tokens

4. **Calidad**
   - Evita respuestas raras por información obsoleta
   - Mantiene memoria relevante y actualizada

---

## 🎓 Para Desarrolladores

### Estructura de Memoria

```python
{
  "version": "2.0",
  "levels": {
    "critical": {
      "identity": {"name": "...", "age": "...", ...},
      "relationships": [{"name": "...", "relation": "...", ...}]
    },
    "medium": {
      "preferences": {"key": {"value": "...", "count": 2, ...}},
      "frequent_topics": {...}
    },
    "short": {
      "session_context": {},
      "temporary_notes": []
    }
  },
  "metadata": {
    "created": "...",
    "last_updated": "...",
    "last_cleanup": "..."
  }
}
```

### API del MemoryManager

```python
from memory.memory_manager_v2 import MemoryManager

manager = MemoryManager()

# Obtener estadísticas
stats = manager.get_statistics()

# Limpieza automática
manager.cleanup_old_data()

# Limpiar nivel específico
manager.clear_memory(level="short")

# Obtener contexto para LLM
context = manager.get_memory_context()
```

---

## 📝 Resumen

**Sistema de 3 Niveles:**
- 🔴 **Crítica** - Identidad y relaciones (permanente)
- 🟡 **Media** - Preferencias frecuentes (30 días)
- 🟢 **Corta** - Contexto temporal (7 días)

**Principio:**
> "Solo guarda lo que se repite o es explícitamente importante"

**Resultado:**
- ✅ Sin basura semántica
- ✅ Memoria limpia y relevante
- ✅ Respuestas más precisas
- ✅ Menor consumo de tokens

---

**¡Tu JARVIS ahora tiene memoria inteligente!** 🧠✨
