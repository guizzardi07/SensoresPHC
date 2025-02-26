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

# https://cloud.fdx-ingenieria.com.ar/login
# msabger@gmail.com 1234

def lee_TablaSensores(ruta_csv,Grupo):
    df = pd.read_csv(ruta_csv,encoding = "ISO-8859-1")

    # Definir las columnas que se van a usar en el JSON (ajustar según el CSV)
    columnas = ["nombre", "fdx_id", "sitecode", "propietario", "abrev", "lon", "lat", "cero_ign", "rio","ubicacion","grupo"]

    # Verificar que el CSV tenga las columnas necesarias
    for col in df.columns:
        if col not in df.columns:
            df[col] = None  # Si falta una columna, se agrega con valores nulos
    columnas = df.columns

    df = df[df['grupo']==Grupo]

    # Convertir a la estructura de JSON esperada
    sensores_dict = {}
    for _, row in df.iterrows():
        nombre_sensor = row["nombre"]
        if pd.isna(nombre_sensor):
            continue  # Ignorar filas sin nombre
        sensores_dict[nombre_sensor] = {col: row[col] if not pd.isna(row[col]) else None for col in columnas}

    # """Lee un archivo JSON con datos de sensores."""
    # with open(ruta_sensores_id_file, 'r', encoding='utf-8') as file:
    #     return json.load(file)[0]

    return sensores_dict

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

def generar_informe(datos_sensores, TablaResumen, nombre_pdf="informe_hidrometrico"):
    TablaResumen.to_csv(nombre_pdf+".csv",index=False,encoding = "ISO-8859-1")
    """Genera un informe en PDF con los datos de los sensores."""
    c = canvas.Canvas(nombre_pdf+".pdf", pagesize=letter)
    width, height = letter
    
    # Título
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, f"Informe de Red Hidrométrica - {datetime.now().strftime('%Y-%m-%d')}")
    
    # Total de estaciones
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Total de estaciones: {len(datos_sensores)}")
    
    # Resumen de Sensores
    y_position = height - 100
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_position, "Resumen de Sensores")
    y_position -= 20

    for _, row in TablaResumen.iterrows():
        c.setFont("Helvetica", 12)
        c.drawString(50, y_position, f"ID: {row['fdx_id']}, Nombre: {row['nombre']}")
        y_position -= 15
        c.drawString(50, y_position, f"Último dato: {row['Dias_UltDato']:.2f} días")
        y_position -= 15
        c.drawString(50, y_position, f"Prom. Señal (10H): {row['Senal_Media']:.1f}%")
        y_position -= 15
        c.drawString(50, y_position, f"Batería: {row['bateria']:.1f}%, Pérdida Batería (1 semana): {row['Bat_Perdida_1S']:.1f}%")
        y_position -= 30  # Espaciado entre sensores

        # Si se queda sin espacio en la página, crear una nueva
        if y_position < 100:
            c.showPage()
            y_position = height - 50

    # Nueva página para los detalles de cada sensor
    c.showPage()

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
        c.drawString(50, y_position, f"Batería: {datos.loc[last_id, 'bateria']} %")
        y_position -= 20
        c.drawString(50, y_position, f"Señal: {datos.loc[last_id, 'senal']} %")
        y_position -= 40

        # Insertar imagen del gráfico
        img_path = graficar_variables(datos_json['nombre'], datos)
        img_width, img_height = 400, 300
        
        if y_position - img_height < 50:  # Si no hay espacio, salto de página
            c.showPage()
            y_position = height - 100
        
        c.drawImage(img_path, 50, y_position - img_height, width=img_width, height=img_height)
        y_position -= img_height + 20  # Espaciado entre imágenes
        y_position -= 140

        c.showPage()  # Salto de página para el siguiente sensor

    c.save()

def procesar_datos(sensores):
    """Obtiene los datos de la API para cada sensor y los almacena."""
    datos_sensores = []
    TablaResumen = pd.DataFrame(columns=["fdx_id", "nombre", "Dias_UltDato", "bateria","Senal_Media", "Bat_Perdida_1S"])
    
    for sensor in sensores.keys():
        nombre = sensores[sensor]['nombre']
        fdx_id = sensores[sensor]['fdx_id']
        datos = consultar_api("pabloegarcia@gmail.com", nombre, fdx_id)
        
        if isinstance(datos, pd.DataFrame) and not datos.empty:
            datos['bateria'] = datos['bateria'] / 10
            datos['senal'] = (datos['senal'] / 30 * 100).round(1)
            
            Fecha_UltimoDato = datos['hora'].max()
            Tiempo_UltimoDato = (datetime.now() - Fecha_UltimoDato).total_seconds() / 3600 / 24  # en dias
            mean_senal_10H = datos[datos['hora'] >= Fecha_UltimoDato - timedelta(hours=10)]['senal'].mean()

            bat_act = datos.loc[datos.index[-1], 'bateria']
            bat_1W_ago = datos[datos['hora'] >= Fecha_UltimoDato - timedelta(days=7)]["bateria"].iloc[0] if not datos.empty else None
            bat_lost_1W = datos["bateria"].iloc[-1] - bat_1W_ago if bat_1W_ago is not None else None
            
            TablaResumen = pd.concat([TablaResumen, pd.DataFrame([{
                "fdx_id": fdx_id,
                "nombre": nombre,
                "Dias_UltDato": Tiempo_UltimoDato,
                "Senal_Media": mean_senal_10H,
                "bateria": bat_act,
                "Bat_Perdida_1S": bat_lost_1W
            }])], ignore_index=True)
            
            datos_sensores.append({
                'id': fdx_id,
                'nombre': nombre,
                'datos_json': sensores[sensor],
                'datos': datos
            })
    TablaResumen = TablaResumen.sort_values(by='fdx_id')
    TablaResumen['Dias_UltDato']=TablaResumen['Dias_UltDato'].round(2)
    TablaResumen['Senal_Media']=TablaResumen['Senal_Media'].round(1)
    TablaResumen['bateria']=TablaResumen['bateria'].round(1)
    TablaResumen['Bat_Perdida_1S']=TablaResumen['Bat_Perdida_1S'].round(1)

    return datos_sensores, TablaResumen


ruta = os.path.abspath(os.curdir).replace("\\" , "/") + "/"
ruta_csv = os.path.join(ruta,'Sensolres_base.csv')
Grupo = 'Delta' # Todos
nombre_pdf ="SensoresDelta"

if __name__ == "__main__":
    sensores = lee_TablaSensores(ruta_csv,Grupo)
    datos_sensores, TablaResumen = procesar_datos(sensores)
    generar_informe(datos_sensores,TablaResumen,nombre_pdf)
