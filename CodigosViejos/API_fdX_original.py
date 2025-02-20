import requests 
import pandas as pd 
import datetime 
import matplotlib.pyplot as plt 
 
#Las Piedras y Líbano (3): 03-08-2017
#San Francisco y Montevideo (5): 17-04-2018
#Las Piedras y Monteverde (29): 19-11-2020
#San Francisco y 821 (8): 21-12-2020

dic_id = {
        # 'LasPiedras_Libano':'3',
        # 'SanFrancisco_Montevideo': '5',
        # 'LasPiedras_Monteverde': '29',
        # 'SanFrancisco_DrTorre': '8',
        'Carabelas': '30',
        'Zemek': '46',
        'CarapachayOUT': '6',
        'INTA Delta': '48',
        'ParanaMini': '28',
        'Borches': '7',
        'ARAUCO VP': '24',
        'Palmas': '54',
        'Guazu': '56',
        'Atucha II': '41',
        ## 'Atucha II - Canal UPA interior': '42',
        'Atucha UPA int': '43',
        'Toro': '52',
        ## 'Toro_': '57'
        }

dic_series = {}
dic_series2 = {}
dic_series3 = {}

for k in dic_id:
    print(k)
    df = pd.DataFrame()
    for y in [2023, 2024]:
        print(y)
        req = f'http://api.fdx-ingenieria.com.ar/api_new?user=pabloegarcia@gmail.com&site_id={dic_id[k]}&query=filter_site&date={y}-01-01@{y}-12-31' 
        # falla cuando son muchos registros. hacer consultas por periodos más cortos.
        data = requests.get(req) 
        json_data = data.json()
        if json_data != []: 
            serie = pd.DataFrame(json_data) 
            serie['fecha'] = pd.to_datetime(serie['hora'])
            df = pd.concat([df, serie], ignore_index=True)

    # dic_series[k] = df[['nivel', 'fecha']].set_index('fecha').astype('float')
    dic_series2[k] = df
    dic_series3[k] = json_data

# for k in dic_series2:
#     dic_series2[k].to_csv(k + '.csv')



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