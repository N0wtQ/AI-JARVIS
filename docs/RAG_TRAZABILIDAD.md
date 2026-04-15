# 📚 RAG con Trazabilidad

## Descripción

JARVIS ahora incluye un sistema RAG (Retrieval-Augmented Generation) mejorado con **trazabilidad completa**. Cada respuesta que utiliza conocimiento de la base de datos incluye metadatos detallados sobre las fuentes consultadas.

## 🎯 Metadatos de Trazabilidad

Cada fragmento recuperado incluye:

### 📄 Documento Fuente
- **file**: Nombre del archivo origen
- **path**: Ruta completa al archivo
- **type**: Extensión del archivo (.txt, .pdf, .md, etc.)

### 📍 Sección/Fragmento
- **chunk_id**: ID del fragmento (0-indexed)
- **total_chunks**: Total de fragmentos del documento
- **section**: Formato legible "fragmento X/Y"
- **char_start**: Posición inicial en caracteres
- **char_end**: Posición final en caracteres

### 📅 Fecha de Indexación
- **indexed_at**: Timestamp ISO 8601 del momento de indexación
- Formato: `2026-02-05T15:00:00.123456`

### 🎯 Relevancia
- **similarity**: Score de similitud coseno (0.0-1.0)
- Indica qué tan relevante es el fragmento para la consulta

### 📋 Preview
- **content_preview**: Vista previa del contenido (150 caracteres)
- Útil para debug sin ver todo el fragmento

## 🔍 Ejemplo de Metadatos

```python
{
    'source_id': 1,
    'file': 'manual_python.pdf',
    'path': '/knowledge/docs/manual_python.pdf',
    'section': 'fragmento 3/12',
    'chunk_id': 2,
    'total_chunks': 12,
    'similarity': 0.847,
    'indexed_at': '2026-02-05T14:30:15.234567',
    'content_preview': 'Las funciones lambda en Python son funciones anónimas que se definen con la palabra clave lambda. Son útiles para operaciones simples...'
}
```

## 🖥️ Interfaz de Usuario

### Botón de Fuentes 📚
Nuevo botón junto a los controles principales que muestra/oculta las fuentes RAG consultadas.

### Panel de Fuentes
Cuando se activa, muestra:

```
📚 Fuentes consultadas:

[1] manual_python.pdf
   ├─ Sección: fragmento 3/12
   ├─ Relevancia: 84%
   └─ Indexado: 05/02/2026 14:30

[2] guia_django.md
   ├─ Sección: fragmento 1/5
   ├─ Relevancia: 72%
   └─ Indexado: 04/02/2026 10:15

[3] notas_clase.txt
   ├─ Sección: fragmento 7/20
   ├─ Relevancia: 68%
   └─ Indexado: 03/02/2026 16:45
```

### Comportamiento
- **Opcional**: El panel se muestra solo si el usuario lo activa
- **Persistente**: Una vez activado, se mantiene visible para nuevas consultas
- **Automático**: Se actualiza con cada respuesta que use RAG
- **Compacto**: Máximo 150px de altura para no ocupar mucho espacio

## 🔧 Implementación Técnica

### Nuevo Método en KnowledgeBase

```python
def get_context_with_sources(query: str, max_tokens: int = 1000) -> Tuple[str, List[Dict]]:
    """
    Get relevant context with source metadata for traceability
    
    Returns:
        Tuple[str, List[Dict]]: (context_text, sources_metadata)
    """
```

**Retorna**:
1. `context_text`: Texto con referencias inline `[Fuente 1: archivo - fragmento]`
2. `sources_metadata`: Lista de diccionarios con todos los metadatos

### Flujo de Datos

```
Usuario pregunta
    ↓
AIHandler.get_response()
    ↓
knowledge_base.get_context_with_sources()
    ↓ (context, sources)
LLM genera respuesta
    ↓
parsed["rag_sources"] = sources
    ↓
AIWorkerThread emite rag_sources_ready
    ↓
GUI.display_rag_sources(sources)
    ↓ (opcional)
Usuario ve panel de fuentes
```

### Almacenamiento en Respuesta

```python
result = ai_handler.get_response(message)

# Ahora result incluye:
{
    "intent": "chat",
    "text": "Respuesta del asistente...",
    "rag_sources": [
        {source1},
        {source2},
        ...
    ]
}
```

## 💡 Beneficios

### 1. **Más Confianza**
El usuario puede verificar de dónde proviene cada dato citado.

### 2. **Debug Sencillo**
Si hay información incorrecta, es fácil rastrear el documento origen.

### 3. **Experiencia "Asistente Experto"**
Como ChatGPT con sources o Perplexity AI, da credibilidad profesional.

### 4. **Transparencia**
No es una "caja negra", el usuario sabe exactamente qué documentos se consultaron.

### 5. **Auditoría**
Permite verificar si el RAG está funcionando correctamente y usando fuentes adecuadas.

## 📊 Casos de Uso

### Investigación Técnica
```
Usuario: "¿Cómo funciona async/await en Python?"

JARVIS: "async/await permite programación asíncrona..."

Fuentes:
[1] manual_python.pdf - fragmento 8/15 (91% relevancia)
[2] asyncio_guide.md - fragmento 2/6 (85% relevancia)
```

### Documentación Interna
```
Usuario: "¿Cuál es el proceso de deploy?"

JARVIS: "El proceso tiene 3 pasos: build, test, deploy..."

Fuentes:
[1] deploy_guide.md - fragmento 1/4 (95% relevancia)
[2] CI_CD_notes.txt - fragmento 3/8 (78% relevancia)
```

### Verificación de Datos
```
Usuario: "¿Está actualizada la información sobre X?"

Usuario presiona 📚 → Ve que fue indexado hace 2 meses
Usuario: "Por favor reindexar este documento"
```

## 🛠️ Uso Programático

### Acceder a las Fuentes

```python
# En el código
result = ai_handler.get_response("Tu pregunta")

if "rag_sources" in result:
    for source in result["rag_sources"]:
        print(f"Fuente: {source['file']}")
        print(f"Relevancia: {source['similarity']:.2%}")
        print(f"Indexado: {source['indexed_at']}")
```

### Reindexar con Metadatos

```python
from rag_knowledge import get_knowledge_base

kb = get_knowledge_base()
kb.index_documents(force_reindex=True)

# Todos los documentos tendrán:
# - indexed_at con timestamp actual
# - chunk_id, total_chunks
# - char_start, char_end
```

## ⚙️ Configuración

### Mostrar Fuentes por Defecto

En `main.py`:
```python
self.show_rag_sources = True  # Mostrar siempre
```

### Cambiar Número de Fuentes

En `rag_knowledge.py`:
```python
results = self.search(query, top_k=5)  # Máximo 5 fuentes
```

### Ajustar Contexto Máximo

En `ai_handler.py`:
```python
rag_context, sources = kb.get_context_with_sources(
    user_message, 
    max_tokens=600  # Aumentar/reducir según necesidad
)
```

## 🎯 Resultado Esperado

✅ **Más confianza**: Usuario sabe de dónde viene la información  
✅ **Debug sencillo**: Fácil rastrear documentos problemáticos  
✅ **Experiencia profesional**: Como asistentes de IA premium  
✅ **Transparencia total**: No es caja negra  
✅ **Auditoría**: Verificar calidad del RAG

---

**Versión**: 2.0  
**Fecha**: Febrero 2026  
**Metadatos**: 7 campos por fuente  
**UI**: Panel opcional con toggle
