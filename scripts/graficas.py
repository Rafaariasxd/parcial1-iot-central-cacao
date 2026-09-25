import glob
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

RAIZ = r"D:\Parcial1-IoT"
SALIDA = os.path.join(RAIZ, "evidencias", "graficas")
COLORES = ["#2f6f4e", "#b5651d", "#3b6ea5", "#8a4f7d", "#c0392b"]

datos = {}
for ruta in glob.glob(os.path.join(RAIZ, "datos", "*.csv")):
    nombre = os.path.basename(ruta)[:-4]
    if nombre == "resumen_por_dia":
        continue
    df = pd.read_csv(ruta)
    if df.empty:
        continue
    df["ts"] = pd.to_datetime(df["ts"], utc=True, format="ISO8601").dt.tz_convert("America/Bogota")
    datos[nombre] = df

resumen = []
for nombre, df in datos.items():
    for disp, g in df.groupby("id"):
        for dia, gd in g.groupby(g["ts"].dt.date):
            horas = gd["ts"].dt.floor("h").nunique()
            resumen.append((disp, str(dia), len(gd), horas))
pd.DataFrame(resumen, columns=["dispositivo", "dia", "mensajes", "horas_con_datos"]).to_csv(
    os.path.join(RAIZ, "datos", "resumen_por_dia.csv"), index=False)

SERIES = [
    ("cultivo", "humedadSuelo", "Humedad del suelo por lote (%)", "01_humedad_suelo.png"),
    ("cultivo", "temperaturaSuelo", "Temperatura del suelo (C)", "02_temperatura_suelo.png"),
    ("dosel", "temperatura", "Temperatura bajo sombra (C)", "03_dosel_temperatura.png"),
    ("meteo", "temperatura", "Meteorologia del predio: temperatura (C)", "04_meteo_temperatura.png"),
    ("aire", "pm25", "Calidad del aire: PM2.5", "05_aire_pm25.png"),
    ("proceso", "temperaturaCaja", "Fermentacion: temperatura de caja (C)", "06_fermentacion_temperatura.png"),
    ("perimetro", "temperaturaBodega", "Bodega: temperatura (C)", "07_bodega_temperatura.png"),
    ("estacion", "humedadFoliar", "Estacion de campo: humedad foliar (%)", "08_estacion_humedad_foliar.png"),
]

for clave, campo, titulo, archivo in SERIES:
    df = datos.get(clave)
    if df is None or campo not in df:
        continue
    fig, ax = plt.subplots(figsize=(10, 3.6), dpi=130)
    for i, (disp, g) in enumerate(df.groupby("id")):
        g = g.dropna(subset=[campo]).sort_values("ts")
        ax.plot(g["ts"], g[campo], lw=1.2, color=COLORES[i % len(COLORES)], label=disp)
    ax.set_title(titulo, fontsize=11, loc="left")
    ax.grid(alpha=0.25)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m %H:%M", tz=df["ts"].dt.tz))
    ax.legend(fontsize=8, frameon=False)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(os.path.join(SALIDA, archivo))
    plt.close(fig)

filas = pd.read_csv(os.path.join(RAIZ, "datos", "resumen_por_dia.csv"))
tabla = filas.pivot_table(index="dispositivo", columns="dia", values="horas_con_datos", aggfunc="sum").fillna(0).astype(int)
print(tabla)
