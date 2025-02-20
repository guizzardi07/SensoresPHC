import requests

# Base URL of the Flask API
base_url = "http://69.28.90.79:5000"  # Update this if your Flask app is running on a different host or port

def obtener_ultimo_dato(topic):
    # Make a GET request to the /api/dato endpoint with the 'topic' parameter
    url=base_url+"/api/dato?topic="+ topic
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        print(f"Ultimo dato para el tema '{topic}': {data}")
        
        return data
    else:
        print(f"Error al obtener el ultimo dato. Codigo de estado: {response.status_code}")
    

def obtener_datos_rango_fechas(topic, fecha_inicio, fecha_fin):
    # Make a GET request to the /api/rango endpoint with the 'topic', 'fecha_inicio', and 'fecha_fin' parameters
    response = requests.get(
        f"{base_url}/api/rango",
        params={"topic": topic, "fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin},
    )

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        print(f"Datos para el tema '{topic}' en el rango de fechas {fecha_inicio} a {fecha_fin}: {data}")
        return data

    else:
        print(f"Error al obtener datos en el rango de fechas. Codigo de estado: {response.status_code}")

# Example usage

dic_rangos = {}
if __name__ == "__main__":
    # Specify the topic for testing
    for i in range(9,13):
        test_topic = f"telemetria_{i}/nivel"

        # Example 1: Get the latest data for a topic
        obtener_ultimo_dato(test_topic)

        # Example 2: Get data within a date range for a topic
        dic_rangos[i] = obtener_datos_rango_fechas(test_topic, "2024-06-01 00:00:00", "2024-06-15 00:00:00")

# telemetria_9/nivel para el equipo ubicado en Arroyo San Francisco y Montevideo.
# telemetria_10/nivel para el equipo ubicado en Granja Educativa Almirante Brown
# telemetria_11/nivel para el equipo ubicado Estaci�n de Bombeo Los Olmos.
# telemetria_12/nivel para el equipo ubicado Arroyo Las Piedras y Libano.
# telemetria_13/nivel para el equipo ubicado Parque Finky