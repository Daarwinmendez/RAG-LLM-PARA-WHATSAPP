import requests
import json

# URL del endpoint de tu API corriendo localmente
api_url = "http://127.0.0.1:8000/query"

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Datos de la consulta que queremos enviar
data = {
    "user_id": "user-test-001",
    "query": "¿Qué herramienta ofrece FormeSX para ayudar a los nuevos empleados?"  # Cambia esto por la consulta que desees
}

print(f"Enviando petición POST a: {api_url}")
print(f"Datos: {json.dumps(data, indent=2)}")

try:
    # Realizar la petición POST
    response = requests.post(api_url, headers=headers, data=json.dumps(data))
    
    # Verificar que la petición fue exitosa (código 200)
    response.raise_for_status() 
    
    print("\n--- ¡Respuesta recibida! ---")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

except requests.exceptions.RequestException as e:
    print(f"\n--- Error al conectar con la API ---")
    print(f"Detalle del error: {e}")
    print("Asegúrate de que el servidor FastAPI esté corriendo con: uvicorn main:app --reload")