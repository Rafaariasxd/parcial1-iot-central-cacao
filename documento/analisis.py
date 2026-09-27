import os

import pandas as pd

RAIZ = r"D:\Parcial1-IoT"
TZ = "America/Bogota"

NOMBRES = {
    "lote-cultivo-01": "Lote de cultivo 1",
    "lote-cultivo-02": "Lote de cultivo 2",
    "lote-cultivo-03": "Lote de cultivo 3",
    "dosel-sombra-01": "Dosel de sombra",
    "estacion-campo-01": "Estacion de campo",
    "meteorologia-predio-01": "Meteorologia del predio",
    "calidad-aire-01": "Calidad de aire",
    "secado-fermentacion-01": "Secado y fermentacion",
    "reservorio-riego-01": "Reservorio de riego",
    "perimetro-bodega-01": "Perimetro y bodega",
}


def cargar(nombre):
    ruta = os.path.join(RAIZ, "datos", f"{nombre}.csv")
    df = pd.read_csv(ruta)
    if df.empty:
        return df
    df["ts"] = pd.to_datetime(df["ts"], utc=True, format="ISO8601").dt.tz_convert(TZ)
    return df


def hora(ts):
    return ts.strftime("%H:%M")


def fecha(ts):
    return ts.strftime("%d/%m")


def frase_variacion(campo, disp, g):
    g = g.dropna(subset=[campo]).sort_values("ts")
    mn, mx = g[campo].min(), g[campo].max()
    prom = g[campo].mean()
    fila_max = g.loc[g[campo].idxmax()]
    fila_min = g.loc[g[campo].idxmin()]
    return (
        f"{NOMBRES.get(disp, disp)}: se movio entre {mn:.1f} y {mx:.1f}, con un promedio de {prom:.1f}. "
        f"El valor mas alto se dio el {fecha(fila_max['ts'])} a las {hora(fila_max['ts'])} "
        f"y el mas bajo el {fecha(fila_min['ts'])} a las {hora(fila_min['ts'])}."
    )


def analisis_humedad_suelo():
    df = cargar("cultivo")
    partes = [frase_variacion("humedadSuelo", d, g) for d, g in df.groupby("id")]
    return (
        "La humedad de suelo tiene un patron de diente de sierra: baja poco a poco por la evapotranspiracion y "
        "sube de golpe cuando el simulador marca un riego. El lote 1 usa el simulador nativo de IoT Central, que "
        "genera numeros aleatorios en todo el rango de la variable, por eso se mueve mas brusco que el lote 3, que "
        "corre el script propio con limites realistas. " + " ".join(partes)
    )


def analisis_temperatura_suelo():
    df = cargar("cultivo")
    partes = [frase_variacion("temperaturaSuelo", d, g) for d, g in df.groupby("id") if g["temperaturaSuelo"].notna().any()]
    return (
        "Esta variable solo la envian el lote 1 (simulador nativo) y el lote 2, que todavia esta pendiente de "
        "conectar por Wokwi; por eso la grafica muestra un solo dispositivo. " + " ".join(partes)
    )


def analisis_dosel():
    df = cargar("dosel")
    g = df[df["id"] == "dosel-sombra-01"]
    t = frase_variacion("temperatura", "dosel-sombra-01", g)
    hr = frase_variacion("humedadRelativa", "dosel-sombra-01", g)
    return (
        "Bajo el dosel de sombra la temperatura y la humedad se mueven al contrario: cuando una sube la otra baja, "
        "porque las dos dependen de la misma hora del dia. " + t + " En cuanto a la humedad relativa, " + hr.split(": ", 1)[1]
    )


def analisis_meteo():
    df = cargar("meteo")
    g = df[df["id"] == "meteorologia-predio-01"]
    t = frase_variacion("temperatura", "meteorologia-predio-01", g)
    lluvia_total = g["lluvia"].fillna(0).sum()
    dias_con_lluvia = g.loc[g["lluvia"].fillna(0) > 0, "ts"].dt.strftime("%d/%m").unique()
    return (
        "Estos datos vienen directo de la API de Open-Meteo, sin simular nada. " + t +
        f" En total llovio {lluvia_total:.1f} mm durante la ventana capturada"
        + (f", con lluvia registrada el {', '.join(dias_con_lluvia)}." if len(dias_con_lluvia) else ", sin lluvia registrada en esos dias.")
    )


def analisis_aire():
    df = cargar("aire")
    g = df[df["id"] == "calidad-aire-01"]
    pm = frase_variacion("pm25", "calidad-aire-01", g)
    aqi_max = g["aqi"].max()
    return (
        "El PM2.5 y el indice de calidad del aire salen de Azure Maps Weather (Atlas Weather) para la ubicacion del "
        "predio. " + pm + f" El indice de calidad de aire (AQI) llego a un maximo de {aqi_max:.0f} en la ventana capturada."
    )


def analisis_fermentacion():
    df = cargar("proceso")
    g = df[df["id"] == "secado-fermentacion-01"].dropna(subset=["temperaturaCaja"]).sort_values("ts")
    inicio = g.iloc[0]
    fin = g.iloc[-1]
    return (
        f"La temperatura de la caja de fermentacion sube poco a poco a medida que pasan los dias del proceso: "
        f"empezo en {inicio['temperaturaCaja']:.1f} el {fecha(inicio['ts'])} y llego a {fin['temperaturaCaja']:.1f} "
        f"el {fecha(fin['ts'])}, con un maximo de {g['temperaturaCaja'].max():.1f}. "
        f"Esto es porque el script simula el avance de la fermentacion, que se calienta con los dias."
    )


def analisis_bodega():
    df = cargar("perimetro")
    g = df[df["id"] == "perimetro-bodega-01"]
    t = frase_variacion("temperaturaBodega", "perimetro-bodega-01", g)
    eventos_puerta = int(g["puerta"].fillna(0).sum())
    eventos_mov = int(g["movimiento"].fillna(0).sum())
    return (
        t + f" Ademas se registraron {eventos_puerta} lecturas con la puerta abierta y {eventos_mov} con movimiento "
        "detectado, que son los eventos que revisan las reglas de seguridad de la bodega."
    )


def analisis_estacion():
    df = cargar("estacion")
    g = df[df["id"] == "estacion-campo-01"]
    hf = frase_variacion("humedadFoliar", "estacion-campo-01", g)
    lluvia_total = g["lluviaLote"].fillna(0).sum()
    return (
        "La humedad foliar sube cuando el script simula lluvia en la tarde y baja el resto del dia. " + hf +
        f" La lluvia acumulada del lote en la ventana capturada fue de {lluvia_total:.1f} mm."
    )


ANALISIS = {
    "01_humedad_suelo.png": analisis_humedad_suelo,
    "02_temperatura_suelo.png": analisis_temperatura_suelo,
    "03_dosel_temperatura.png": analisis_dosel,
    "04_meteo_temperatura.png": analisis_meteo,
    "05_aire_pm25.png": analisis_aire,
    "06_fermentacion_temperatura.png": analisis_fermentacion,
    "07_bodega_temperatura.png": analisis_bodega,
    "08_estacion_humedad_foliar.png": analisis_estacion,
}


def texto_para(archivo):
    return ANALISIS[archivo]()
