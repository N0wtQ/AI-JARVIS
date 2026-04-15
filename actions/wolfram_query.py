import wolframalpha
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


def get_wolfram_client():
    """Obtiene el cliente de WolframAlpha configurado"""
    api_key = os.getenv('WOLFRAM_API_KEY')
    
    if not api_key or api_key == 'your_wolfram_api_key_here':
        raise ValueError(
            "API Key de WolframAlpha no configurada. "
            "Por favor, obtén una API key gratuita en https://products.wolframalpha.com/api/ "
            "y agrégala al archivo .env como WOLFRAM_API_KEY"
        )
    
    return wolframalpha.Client(api_key)


def query_wolfram(question):
    """
    Realiza una consulta a WolframAlpha
    
    Args:
        question (str): Pregunta o cálculo a realizar
        
    Returns:
        str: Respuesta de WolframAlpha o mensaje de error
    """
    try:
        client = get_wolfram_client()
        res = client.query(question)
        
        # Intentar obtener la respuesta principal
        try:
            answer = next(res.results).text
            return answer
        except StopIteration:
            # Si no hay respuesta directa, intentar obtener cualquier información relevante
            if res.success:
                results = []
                for pod in res.pods:
                    if pod.text:
                        results.append(f"{pod.title}: {pod.text}")
                
                if results:
                    return "\n".join(results[:3])  # Primeros 3 resultados
                else:
                    return "WolframAlpha no pudo procesar la consulta o no encontró resultados."
            else:
                return "WolframAlpha no pudo procesar la consulta."
                
    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"Error al consultar WolframAlpha: {str(e)}"


def calculate(expression):
    """
    Realiza un cálculo matemático usando WolframAlpha
    
    Args:
        expression (str): Expresión matemática a calcular
        
    Returns:
        str: Resultado del cálculo
    """
    return query_wolfram(expression)


def get_fact(topic):
    """
    Obtiene información o hechos sobre un tema usando WolframAlpha
    
    Args:
        topic (str): Tema sobre el que obtener información
        
    Returns:
        str: Información sobre el tema
    """
    return query_wolfram(topic)


def solve_equation(equation):
    """
    Resuelve una ecuación usando WolframAlpha
    
    Args:
        equation (str): Ecuación a resolver (ej: "solve x^2 + 2x + 1 = 0")
        
    Returns:
        str: Solución de la ecuación
    """
    if not equation.lower().startswith('solve'):
        equation = f"solve {equation}"
    return query_wolfram(equation)


def convert_units(conversion):
    """
    Convierte unidades usando WolframAlpha
    
    Args:
        conversion (str): Conversión a realizar (ej: "100 km to miles")
        
    Returns:
        str: Resultado de la conversión
    """
    return query_wolfram(conversion)


def get_detailed_result(question, max_pods=5):
    """
    Obtiene resultados detallados de WolframAlpha con múltiples pods
    
    Args:
        question (str): Pregunta a realizar
        max_pods (int): Número máximo de pods a devolver
        
    Returns:
        dict: Diccionario con los resultados organizados por pod
    """
    try:
        client = get_wolfram_client()
        res = client.query(question)
        
        if not res.success:
            return {"error": "WolframAlpha no pudo procesar la consulta"}
        
        results = {}
        count = 0
        
        for pod in res.pods:
            if count >= max_pods:
                break
                
            if pod.text:
                results[pod.title] = pod.text
                count += 1
        
        return results if results else {"error": "No se encontraron resultados"}
        
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Error al consultar WolframAlpha: {str(e)}"}


def format_wolfram_response(question):
    """
    Formatea una respuesta de WolframAlpha de manera amigable
    
    Args:
        question (str): Pregunta a realizar
        
    Returns:
        str: Respuesta formateada
    """
    answer = query_wolfram(question)
    return f"Según WolframAlpha: {answer}"


# Función principal para testing
if __name__ == "__main__":
    print("\n" + "="*60)
    print("PRUEBA DE WOLFRAMALPHA".center(60))
    print("="*60 + "\n")
    
    # Verificar si la API key está configurada
    try:
        client = get_wolfram_client()
        print("✅ API Key de WolframAlpha configurada correctamente\n")
        
        # Ejemplos de consultas
        print("Ejemplo 1: Cálculo matemático")
        print(f"Pregunta: ¿Cuánto es 25 * 37 + 158?")
        result = calculate("25 * 37 + 158")
        print(f"Respuesta: {result}\n")
        
        print("-"*60 + "\n")
        
        print("Ejemplo 2: Conversión de unidades")
        print(f"Pregunta: 100 km a millas")
        result = convert_units("100 km to miles")
        print(f"Respuesta: {result}\n")
        
        print("-"*60 + "\n")
        
        print("Ejemplo 3: Información científica")
        print(f"Pregunta: ¿Cuál es la velocidad de la luz?")
        result = get_fact("speed of light")
        print(f"Respuesta: {result}\n")
        
    except ValueError as e:
        print(f"❌ {e}")
        print("\nPara obtener una API key gratuita:")
        print("1. Ve a: https://products.wolframalpha.com/api/")
        print("2. Haz clic en 'Get API Access'")
        print("3. Selecciona el plan gratuito (2,000 consultas/mes)")
        print("4. Crea una cuenta o inicia sesión")
        print("5. Copia tu App ID (API Key)")
        print("6. Agrégala al archivo .env como WOLFRAM_API_KEY=tu_api_key_aqui")
