# -*- coding: utf-8 -*-
import os, json
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from fpdf import FPDF

def leer_json(ruta_sensores_id_file):
    """Lee un archivo JSON con datos de sensores."""
    with open(ruta_sensores_id_file, 'r', encoding='utf-8') as file:
        return json.load(file)[0]

def consultar_api(user, nombre, site_id, start_date=None, end_date=None, variables=None):
    """
    Consulta la API de FDX Ingeniería y devuelve los datos como un DataFrame de pandas.

    Parámetros:
    - user: str -> Usuario de la API.
    - site_id: int -> ID del sitio a consultar.
    - start_date: str, opcional -> Fecha de inicio en formato 'YYYY-MM-DD'. Si no se proporciona, se establece una semana atrás.
    - end_date: str, opcional -> Fecha de fin en formato 'YYYY-MM-DD'. Si no se proporciona, se establece la fecha de hoy.
    - variables: list[str], opcional -> Lista de variables específicas a solicitar.

    Retorna:
    - pd.DataFrame con los datos obtenidos.
    """
    if end_date is None:
        end_date = (datetime.now()+ timedelta(days=1)).strftime('%Y-%m-%d')
    if start_date is None:
        dias_consulta=360
        start_date = (datetime.now() - timedelta(days=dias_consulta)).strftime('%Y-%m-%d')
    base_url = "http://api.fdx-ingenieria.com.ar/api_new"
    query_params = {
        "user": user,
        "site_id": site_id,
        "query": "filter_site",
        "date": f"{start_date}@{end_date}"
    }

    if variables:
        query_params["variables"] = ",".join(variables)

    response = requests.get(base_url, params=query_params)

    if response.status_code == 200:
        try:
            json_data = response.json()
            df = pd.DataFrame(json_data)

            if df.empty:
                print(f"El DataFrame para el sitio {nombre} (id:{site_id}), no tiene datos en los ultimos {dias_consulta} días.")
                return None  # O devolver un DataFrame vacío, según tus necesidades

            df["hora"] = pd.to_datetime(df["hora"])
            df = df.sort_values(by='hora')
            # Cambiar el tipo de dato de las columnas
            for col in ["nivel", "bateria", "senal"]:
              try:
                df[col] = df[col].astype(float)
              except ValueError as e:
                print(f"Error al convertir la columna {col} a float: {e}")
                # Puedes manejar el error como prefieras, por ejemplo, rellenar con NaN
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            return df
        except ValueError:
            print("Error al decodificar la respuesta JSON.")
            # print(ValueError)
            print(response.json())
            return None
    else:
        print(f"Error en la solicitud: {response.status_code}")
        return None

def graficar_variables0(nombre,df):
    """
    Genera gráficos para visualizar nivel, batería y señal en el período consultado.

    Parámetros:
    - df: DataFrame con los datos a graficar.
    """
    if isinstance(df, pd.DataFrame):
      if df.empty:
          print("El DataFrame está vacío.")
          return
      else:
        fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

        fig.suptitle(nombre, fontsize=14, fontweight='bold')  # Título general

        axes[0].plot(df["hora"], df["nivel"], label="Nivel", color="blue")
        axes[0].set_title("Nivel")
        axes[0].grid(True)  # Agregar grilla

        axes[1].plot(df["hora"], df["bateria"], label="Batería", color="green")
        axes[1].set_title("Batería")
        axes[1].grid(True)  # Agregar grilla

        axes[2].plot(df["hora"], df["senal"], label="Señal", color="red")
        axes[2].set_title("Señal")
        axes[2].grid(True)  # Agregar grilla

        fecha_actual = datetime.now()

        for ax in axes:
            ax.axvline(x=fecha_actual, color='black', linestyle='--', label='Hoy')  # Línea vertical
            #ax.legend()  # Mostrar leyenda

        plt.tight_layout(rect=[0, 0, 1, 0.96])  # Ajustar para que no sobreponga el título
        plt.show()
    else:
      print("El DataFrame está vacío.")
      return

def graficar_variables(nombre, df):
    """
    Genera gráficos para visualizar nivel, batería y señal en el período consultado.
    """
    if df.empty:
        print("El DataFrame está vacío.")
        return None
    
    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    fig.suptitle(nombre, fontsize=14, fontweight='bold')

    axes[0].scatter(df["hora"], df["nivel"], label="Nivel", color="blue")
    axes[0].set_title("Nivel")
    axes[0].grid(True)

    axes[1].scatter(df["hora"], df["bateria"], label="Batería", color="green")
    axes[1].set_title("Batería")
    axes[1].grid(True)

    axes[2].scatter(df["hora"], df["senal"], label="Señal", color="red")
    axes[2].set_title("Señal")
    axes[2].grid(True)
    
    fecha_actual = datetime.now()
    for ax in axes:
        ax.axvline(x=fecha_actual, color='black', linestyle='--', label='Hoy')
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    img_name = nombre+".png"
    img_path = os.path.join('Figuras_Temp',img_name)

    plt.savefig(img_path, format='png', dpi=100)
    plt.close(fig)
    return img_path


def generar_informe(datos_sensores, nombre_pdf="informe_hidrometrico.pdf"):
    """Genera un informe en PDF con los datos de los sensores."""
    c = canvas.Canvas(nombre_pdf, pagesize=letter)
    width, height = letter
    
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, f"Informe de Red Hidrométrica - {datetime.now().strftime('%Y-%m-%d')}")
    
    total_estaciones = len(datos_sensores)
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Total de estaciones: {total_estaciones}")
    
    for sensor in datos_sensores:
        y_position = height - 120
        datos_json = sensor['datos_json']
        datos = sensor['datos']
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_position, f"Sensor: {datos_json['nombre']} (ID: {datos_json['fdx_id']})")
        y_position -= 20
        
        c.setFont("Helvetica", 12)
        c.drawString(50, y_position, f"Marca: {datos.loc[0, 'marca']}, Modelo: {datos.loc[0, 'modelo']}, Serie: {datos.loc[0, 'serie']}")
        y_position -= 20
        c.drawString(50, y_position, f"Ubicación: Lat {datos_json['lat']}, Lon {datos_json['lon']}")
        y_position -= 20
        c.drawString(50, y_position, f"Río: {datos_json['rio']}")
        y_position -= 20

        last_id = datos.index[-1]
        c.drawString(50, y_position, f"Último dato: {datos.loc[last_id, 'hora']}")
        y_position -= 20
        c.drawString(50, y_position, f"Batería: {datos.loc[last_id, 'bateria']/10} %")
        y_position -= 20
        c.drawString(50, y_position, f"Señal: {round(datos.loc[last_id, 'senal']/30*100,1)} %")
        y_position -= 40
        
        img_path = graficar_variables(datos_json['nombre'], datos)

        # Insertar la imagen en el PDF
        img_width = 400
        img_height = 300
        if y_position - img_height < 50:  # Salto de página si no hay espacio
            c.showPage()
            y_position = height - 100
        
        c.drawImage(img_path, 50, y_position - img_height, width=img_width, height=img_height)
        y_position -= img_height + 20  # Espaciado entre imágenes
        y_position -= 140
        c.showPage() 
    c.save()

def procesar_datos(sensores):
    """Obtiene los datos de la API para cada sensor y los almacena."""
    datos_sensores = []
    for sensor in sensores.keys():
        nombre = sensores[sensor]['nombre']
        fdx_id = sensores[sensor]['fdx_id']
        datos = consultar_api("pabloegarcia@gmail.com", nombre, fdx_id) # start_date='YYYY-MM-DD', end_date='YYYY-MM-DD'
        
        if isinstance(datos, pd.DataFrame):
            datos_sensores.append({
                'id': fdx_id,
                'nombre': nombre,
                'datos_json':sensores[sensor],
                'datos': datos
            })
    return datos_sensores

if __name__ == "__main__":
    ruta = os.path.abspath(os.curdir).replace("\\" , "/") + "/"
    ruta_json = os.path.join(ruta,'Sensores.json')
    sensores = leer_json(ruta_json)
    datos_sensores = procesar_datos(sensores)
    generar_informe(datos_sensores)
