# 🧮 Integración de WolframAlpha

WolframAlpha es un motor computacional que puede responder preguntas, resolver ecuaciones, hacer cálculos complejos y mucho más.

## 🆓 Obtener API Key Gratuita

### Plan Gratuito
- **2,000 consultas/mes** (aproximadamente 66 consultas por día)
- Sin costo
- Perfecto para uso personal

### Pasos para obtener tu API Key:

1. **Ve al sitio oficial:**
   - Visita: https://products.wolframalpha.com/api/

2. **Regístrate:**
   - Haz clic en "Get API Access" o "Sign up"
   - Crea una cuenta con tu email

3. **Selecciona el plan gratuito:**
   - Elige "Free Plan" (2,000 consultas/mes)
   - Acepta los términos y condiciones

4. **Obtén tu App ID (API Key):**
   - Después de registrarte, verás tu "App ID"
   - Este es tu API Key

5. **Configura tu archivo .env:**
   - Copia el archivo `.env.example` a `.env` (si no lo has hecho)
   - Agrega tu API Key:
   ```
   WOLFRAM_API_KEY=TU-API-KEY-AQUI
   ```

## 🚀 Uso Básico

### Importar el módulo:
```python
from actions.wolfram_query import query_wolfram, calculate, get_fact, convert_units
```

### Ejemplos de Uso:

#### 1. Cálculos matemáticos
```python
from actions.wolfram_query import calculate

result = calculate("25 * 37 + 158")
print(result)  # 1083

result = calculate("sqrt(144)")
print(result)  # 12

result = calculate("sin(45 degrees)")
print(result)  # 1/√2 (approximately 0.707107)
```

#### 2. Conversión de unidades
```python
from actions.wolfram_query import convert_units

result = convert_units("100 km to miles")
print(result)  # 62.1371 miles

result = convert_units("25 celsius to fahrenheit")
print(result)  # 77 °F

result = convert_units("5 feet to meters")
print(result)  # 1.524 meters
```

#### 3. Resolver ecuaciones
```python
from actions.wolfram_query import solve_equation

result = solve_equation("x^2 + 2x + 1 = 0")
print(result)  # x = -1

result = solve_equation("2x + 5 = 15")
print(result)  # x = 5
```

#### 4. Obtener información
```python
from actions.wolfram_query import get_fact

result = get_fact("speed of light")
print(result)

result = get_fact("population of Spain")
print(result)

result = get_fact("distance from earth to moon")
print(result)
```

#### 5. Consultas generales
```python
from actions.wolfram_query import query_wolfram

result = query_wolfram("what is the weather in Madrid")
print(result)

result = query_wolfram("derivative of x^3")
print(result)

result = query_wolfram("integral of sin(x)")
print(result)
```

## 📋 Funciones Disponibles

### `query_wolfram(question)`
Función general para cualquier tipo de consulta.

**Parámetros:**
- `question` (str): Pregunta o consulta a realizar

**Retorna:** `str` - Respuesta de WolframAlpha

---

### `calculate(expression)`
Realiza cálculos matemáticos.

**Parámetros:**
- `expression` (str): Expresión matemática

**Ejemplos:**
- `"25 * 37 + 158"`
- `"sqrt(144)"`
- `"sin(45 degrees)"`
- `"log(100)"`

---

### `convert_units(conversion)`
Convierte unidades.

**Parámetros:**
- `conversion` (str): Conversión a realizar

**Ejemplos:**
- `"100 km to miles"`
- `"25 celsius to fahrenheit"`
- `"5 feet to meters"`
- `"1 year to seconds"`

---

### `solve_equation(equation)`
Resuelve ecuaciones matemáticas.

**Parámetros:**
- `equation` (str): Ecuación a resolver

**Ejemplos:**
- `"x^2 + 2x + 1 = 0"`
- `"2x + 5 = 15"`
- `"solve 3x - 7 = 14"`

---

### `get_fact(topic)`
Obtiene información sobre un tema.

**Parámetros:**
- `topic` (str): Tema sobre el que obtener información

**Ejemplos:**
- `"speed of light"`
- `"population of Spain"`
- `"distance from earth to moon"`
- `"height of mount everest"`

---

### `get_detailed_result(question, max_pods=5)`
Obtiene resultados detallados con múltiples "pods" de información.

**Parámetros:**
- `question` (str): Pregunta a realizar
- `max_pods` (int): Número máximo de pods a devolver (default: 5)

**Retorna:** `dict` - Diccionario con los resultados organizados

---

### `format_wolfram_response(question)`
Formatea una respuesta para el asistente AI.

**Parámetros:**
- `question` (str): Pregunta a realizar

**Retorna:** `str` - Respuesta formateada con prefijo "Según WolframAlpha:"

## 🎯 Ejemplos de Integración con el Asistente

### Ejemplo 1: Detección de cálculos matemáticos
```python
def procesar_comando(texto_usuario):
    texto_lower = texto_usuario.lower()
    
    # Detectar palabras clave de cálculo
    calc_keywords = ["calcular", "cuánto es", "resultado de", "calcula"]
    
    if any(keyword in texto_lower for keyword in calc_keywords):
        from actions.wolfram_query import calculate
        
        # Extraer la expresión (después de la palabra clave)
        expresion = texto_usuario.split("calcular")[-1].strip()
        resultado = calculate(expresion)
        
        return f"El resultado es: {resultado}"
```

### Ejemplo 2: Conversión de unidades
```python
def procesar_comando(texto_usuario):
    texto_lower = texto_usuario.lower()
    
    if "convertir" in texto_lower or "a cuánto equivale" in texto_lower:
        from actions.wolfram_query import convert_units
        
        resultado = convert_units(texto_usuario)
        return resultado
```

### Ejemplo 3: Consultas de conocimiento
```python
def procesar_comando(texto_usuario):
    texto_lower = texto_usuario.lower()
    
    # Detectar preguntas científicas o de conocimiento
    knowledge_keywords = ["cuál es", "qué es", "dime", "información sobre"]
    
    if any(keyword in texto_lower for keyword in knowledge_keywords):
        from actions.wolfram_query import query_wolfram
        
        respuesta = query_wolfram(texto_usuario)
        return respuesta
```

## 🧪 Probar el Módulo

Para probar que todo funciona correctamente:

```bash
py actions\wolfram_query.py
```

Si tu API Key no está configurada, verás instrucciones de cómo obtenerla.

Si está configurada, verás ejemplos de consultas funcionando.

## 💡 Tipos de Consultas Soportadas

WolframAlpha puede responder:

### Matemáticas
- ✅ Cálculos aritméticos
- ✅ Álgebra
- ✅ Cálculo (derivadas, integrales)
- ✅ Ecuaciones
- ✅ Trigonometría
- ✅ Estadística

### Ciencias
- ✅ Física (fórmulas, constantes)
- ✅ Química (elementos, compuestos)
- ✅ Astronomía (planetas, distancias)
- ✅ Biología

### Datos
- ✅ Geografía (población, área)
- ✅ Clima actual
- ✅ Conversión de unidades
- ✅ Fechas y tiempo
- ✅ Finanzas (tasas de cambio)

### Y mucho más...

## ⚠️ Limitaciones del Plan Gratuito

- **2,000 consultas/mes** (se reinicia cada mes)
- **No queries por segundo** (puedes hacer varias consultas seguidas)
- **Tiempo de respuesta** estándar (puede ser un poco más lento)
- **Sin soporte comercial**

## 🔧 Manejo de Errores

El módulo maneja automáticamente los errores:

```python
from actions.wolfram_query import query_wolfram

# Si la API key no está configurada
resultado = query_wolfram("2+2")
# Retorna: "API Key de WolframAlpha no configurada..."

# Si WolframAlpha no puede procesar la consulta
resultado = query_wolfram("asdfghjkl")
# Retorna: "WolframAlpha no pudo procesar la consulta"

# Si hay un error de conexión
# Retorna: "Error al consultar WolframAlpha: [mensaje de error]"
```

## 📚 Recursos Adicionales

- **Documentación oficial:** https://products.wolframalpha.com/api/documentation/
- **Ejemplos de consultas:** https://www.wolframalpha.com/examples/
- **Dashboard de uso:** https://products.wolframalpha.com/api/dashboard.html

## ✨ Características

- ✅ API gratuita con 2,000 consultas/mes
- ✅ Cálculos matemáticos avanzados
- ✅ Conversión de unidades
- ✅ Resolución de ecuaciones
- ✅ Consultas de conocimiento general
- ✅ Información científica
- ✅ Manejo robusto de errores
- ✅ Fácil integración con el asistente AI

---

**¡Listo para usar!** 🎉

Una vez que agregues tu API Key al archivo `.env`, podrás hacer consultas ilimitadas (dentro del límite de 2,000/mes).
