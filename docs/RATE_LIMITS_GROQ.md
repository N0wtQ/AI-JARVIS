# 🚦 Solución: Error 429 - Rate Limit de Groq

## ❌ El Problema

```
Error comunicando con la IA: 429 Client Error: Too Many Requests
```

Esto significa que has excedido el límite de solicitudes por minuto de Groq.

---

## 📊 Límites de Groq (Plan Gratuito)

| Modelo | Tokens/Minuto | Solicitudes/Min | Tokens/Día |
|--------|---------------|-----------------|------------|
| **llama-3.1-8b-instant** | 30,000 | 30 | 14,400 |
| llama-3.3-70b-versatile | 6,000 | 30 | 14,400 |
| mixtral-8x7b-32768 | 5,000 | 30 | 14,400 |

---

## ✅ Soluciones Implementadas

### 1. Retry Automático con Backoff ⚡

He actualizado `ai_handler.py` para:
- ✅ Reintentar automáticamente 3 veces
- ✅ Esperar 2, 4, 8 segundos entre intentos
- ✅ Mensaje claro si falla después de 3 intentos

**Ya está funcionando** - no necesitas hacer nada.

### 2. Modelo Optimizado 🚀

El archivo `.env` ya está configurado con:
```env
MODEL=llama-3.1-8b-instant
```

Este modelo tiene los **límites más altos** (30,000 tokens/min).

---

## 🔧 Soluciones Adicionales

### Opción 1: Esperar un Momento ⏱️

Si el error persiste:
1. **Espera 60 segundos**
2. Intenta de nuevo

Los límites se resetean cada minuto.

### Opción 2: Reducir Contexto RAG 📉

Si usas muchos documentos:

Edita `ai_handler.py` línea 124:
```python
# Antes
rag_context = self.knowledge_base.get_context(user_message, max_tokens=400)

# Después (más pequeño)
rag_context = self.knowledge_base.get_context(user_message, max_tokens=200)
```

### Opción 3: Limpiar Historial 🧹

Limpia el historial de vez en cuando para reducir tokens:

En la interfaz de JARVIS, o manualmente:
```python
self.ai_handler.clear_history()
```

### Opción 4: Cambiar de Proveedor 🔄

#### **A) Usar OpenAI** (Requiere pago)

Edita `.env`:
```env
API_PROVIDER=openai
API_KEY=sk-tu_api_key_de_openai
MODEL=gpt-3.5-turbo
```

**Ventajas:**
- Sin límites tan estrictos
- Más estable

**Desventajas:**
- Requiere pago (~$0.002 por solicitud)

#### **B) Crear Múltiples Cuentas Groq** (Gratis)

1. Crea otra cuenta en https://console.groq.com
2. Obtén nueva API key
3. Cambia cuando alcances el límite

---

## 📈 Monitorear Uso

Verifica tu uso en:
🔗 https://console.groq.com/settings/limits

Aquí verás:
- Solicitudes usadas hoy
- Tokens consumidos
- Límites restantes

---

## 💡 Mejores Prácticas

### 1. No hagas consultas muy seguidas
- Espera 2-3 segundos entre mensajes
- Evita enviar muchos mensajes seguidos

### 2. Desactiva RAG si no lo necesitas
Si no usas documentos:
```python
# En ai_handler.py, línea 123
if False and self.knowledge_base and RAG_AVAILABLE:  # Desactivado
```

### 3. Historial corto
El historial ya está limitado a 10 mensajes (línea 169-170 de ai_handler.py).

### 4. Usa comandos directos
En lugar de:
```
"JARVIS, por favor, podrías buscarme información sobre..."
```

Di:
```
"Busca información sobre..."
```

Menos tokens = menos probabilidad de rate limit.

---

## 🎯 Resumen Rápido

**Si ves error 429:**

1. ✅ **Espera 60 segundos** y reintenta
2. ✅ El sistema ya reintenta automáticamente
3. ✅ Ya estás usando el modelo con límites más altos
4. ⚠️ Si persiste, considera OpenAI (de pago)

**Para evitarlo:**
- No envíes mensajes muy seguidos
- Mantén el historial corto
- Usa comandos concisos

---

## 📊 Comparación de Límites

| Proveedor | Gratis | Límite/Min | Precio |
|-----------|--------|------------|--------|
| **Groq** | ✅ Sí | 30 req/min | $0 |
| **OpenAI** | ❌ No | Sin límite | ~$0.002/req |
| **Anthropic** | ❌ No | Sin límite | ~$0.003/req |

---

## 🔍 Debug

Para ver cuántos tokens estás usando:

```python
# En ai_handler.py, antes de la línea 204
print(f"Tokens en prompt: {len(str(messages))}")
```

Esto te dirá aproximadamente cuántos tokens estás enviando.

---

**Nota:** Con los cambios implementados, JARVIS ahora maneja automáticamente los rate limits. Solo espera un momento si ves el error. 🎉
