import pandas as pd
import matplotlib.pyplot as plt

# Cargar los datos
df = pd.read_csv("Visitas_Web.csv", parse_dates=["Fecha"], dayfirst=True)
df["Fecha"] = pd.to_datetime(df["Fecha"])
df = df.sort_values("Fecha")

df["MediaMovil_1m"] = df["Visitas"].rolling(window=30).mean()

# Crear la visualización
plt.figure(figsize=(10, 5))
plt.plot(df["Fecha"], df["Visitas"], linestyle='-',linewidth=0.5, color='k', label="Visitas Diarias",alpha=0.5)
plt.plot(df["Fecha"], df["MediaMovil_1m"], linestyle='-',linewidth=2, color='b', label="Media Mensual")
plt.xlabel("Fecha", size=18)
plt.ylabel("Cantidad de Visitas", size=18)
plt.title("Visitas a la Página Web")
# plt.xticks(rotation=45)
plt.grid(True, axis='y', linestyle='-.', linewidth=0.3)
plt.tick_params(axis='both', labelsize=14)
plt.legend(prop={'size': 16})
plt.grid()
plt.show()

