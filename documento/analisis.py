import os

import pandas as pd

RAIZ = r"D:\Parcial1-IoT"
TZ = "America/Bogota"


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


def stats(g, campo):
    g = g.dropna(subset=[campo]).sort_values("ts")
    fmax = g.loc[g[campo].idxmax()]
    fmin = g.loc[g[campo].idxmin()]
    return {
        "min": g[campo].min(), "max": g[campo].max(), "prom": g[campo].mean(),
        "fecha_max": fecha(fmax["ts"]), "hora_max": hora(fmax["ts"]),
        "fecha_min": fecha(fmin["ts"]), "hora_min": hora(fmin["ts"]),
    }


def analisis_humedad_suelo():
    df = cargar("cultivo")
    s1 = stats(df[df["id"] == "lote-cultivo-01"], "humedadSuelo")
    s3 = stats(df[df["id"] == "lote-cultivo-03"], "humedadSuelo")
    if s1["fecha_max"] == s1["fecha_min"]:
        cuando = f"los dos el {s1['fecha_max']}, apenas unas horas de diferencia"
    else:
        cuando = f"el pico el {s1['fecha_max']} y la bajada el {s1['fecha_min']}"
    return (
        "La humedad de suelo tiene forma de diente de sierra: baja poco a poco por la evapotranspiración y sube de "
        "golpe cuando el simulador marca un riego. El lote 1 usa el simulador nativo de IoT Central, que genera "
        f"valores al azar en todo el rango permitido, por eso llega a picos de {s1['max']:.0f} % y bajadas hasta "
        f"{s1['min']:.0f} % ({cuando}). El lote 3, que corre el script propio con límites realistas, se mantuvo "
        f"mucho más parejo: entre {s3['min']:.0f} % y {s3['max']:.0f} %, con un promedio de {s3['prom']:.0f} %."
    )


def analisis_temperatura_suelo():
    df = cargar("cultivo")
    s = stats(df[df["id"] == "lote-cultivo-01"], "temperaturaSuelo")
    return (
        "Esta variable solo la mandan el lote 1 (simulador nativo) y el lote 2, que todavía está pendiente de "
        "conectar por Wokwi, así que en la gráfica aparece un solo dispositivo. El máximo se dio el "
        f"{s['fecha_max']} a las {s['hora_max']} ({s['max']:.0f} grados) y el mínimo el {s['fecha_min']} a las "
        f"{s['hora_min']} ({s['min']:.0f} grados); otra vez se nota que el simulador nativo no respeta un rango "
        "realista de temperatura de suelo, porque salta entre valores muy bajos y muy altos de un rato a otro."
    )


def analisis_dosel():
    df = cargar("dosel")
    g = df[df["id"] == "dosel-sombra-01"]
    t = stats(g, "temperatura")
    h = stats(g, "humedadRelativa")
    return (
        "Bajo el dosel de sombra la temperatura y la humedad van en contra: cuando una sube la otra baja, porque las "
        f"dos siguen la misma hora del día. La temperatura se mantuvo entre {t['min']:.1f} y {t['max']:.1f} °C, con "
        f"el punto más caliente el {t['fecha_max']} a las {t['hora_max']}. La humedad relativa fue al revés: subió "
        f"hasta {h['max']:.0f} % de madrugada ({h['fecha_max']}, {h['hora_max']}) y bajó a {h['min']:.0f} % al medio "
        "día."
    )


def analisis_meteo():
    df = cargar("meteo")
    g = df[df["id"] == "meteorologia-predio-01"]
    t = stats(g, "temperatura")
    lluvia_total = g["lluvia"].fillna(0).sum()
    dias_con_lluvia = sorted(g.loc[g["lluvia"].fillna(0) > 0, "ts"].dt.strftime("%d/%m").unique())
    return (
        "Esta serie no la simula nada: llega directo de la API de Open-Meteo para las coordenadas del predio. La "
        f"temperatura del aire estuvo entre {t['min']:.1f} y {t['max']:.1f} °C, con el pico el {t['fecha_max']} a "
        f"las {t['hora_max']}. En total llovió {lluvia_total:.1f} mm durante la ventana capturada, repartidos en "
        f"{len(dias_con_lluvia)} de los días con datos ({', '.join(dias_con_lluvia)})."
    )


def analisis_aire():
    df = cargar("aire")
    g = df[df["id"] == "calidad-aire-01"]
    pm = stats(g, "pm25")
    aqi_max = g["aqi"].max()
    return (
        "El PM2.5 y el índice de calidad del aire vienen de Azure Maps Weather (Atlas Weather), consultado para la "
        f"ubicación de la finca. El PM2.5 se mantuvo bajo casi toda la ventana, entre {pm['min']:.1f} y "
        f"{pm['max']:.1f} (promedio {pm['prom']:.1f}), y el índice de calidad del aire no pasó de {aqi_max:.0f}, es "
        "decir que el aire de la zona se mantuvo en niveles aceptables."
    )


def analisis_fermentacion():
    df = cargar("proceso")
    g = df[df["id"] == "secado-fermentacion-01"].dropna(subset=["temperaturaCaja"]).sort_values("ts")
    inicio, fin = g.iloc[0], g.iloc[-1]
    return (
        f"La temperatura de la caja sube poco a poco a medida que avanza la fermentación: arrancó en "
        f"{inicio['temperaturaCaja']:.1f} °C el {fecha(inicio['ts'])} y para el {fecha(fin['ts'])} ya iba en "
        f"{fin['temperaturaCaja']:.1f} °C, con un pico de {g['temperaturaCaja'].max():.1f}. Esto pasa porque el "
        "script simula el calentamiento normal del proceso de fermentación del cacao con el paso de los días, no "
        "una lectura tomada al azar."
    )


def analisis_bodega():
    df = cargar("perimetro")
    g = df[df["id"] == "perimetro-bodega-01"]
    t = stats(g, "temperaturaBodega")
    eventos_puerta = int(g["puerta"].fillna(0).sum())
    eventos_mov = int(g["movimiento"].fillna(0).sum())
    return (
        f"La temperatura de la bodega osciló entre {t['min']:.1f} y {t['max']:.1f} °C, con el pico el "
        f"{t['fecha_max']} a las {t['hora_max']}. En la ventana capturada se registraron {eventos_puerta} lecturas "
        f"con la puerta abierta y {eventos_mov} con movimiento detectado; esos son justo los eventos que la regla "
        "de alerta de la bodega está vigilando."
    )


def analisis_estacion():
    df = cargar("estacion")
    g = df[df["id"] == "estacion-campo-01"]
    hf = stats(g, "humedadFoliar")
    lluvia_total = g["lluviaLote"].fillna(0).sum()
    return (
        "La humedad foliar sube cuando el script simula lluvia en la tarde y vuelve a bajar el resto del día, por "
        f"eso la línea se ve tan dentada: llegó a {hf['max']:.0f} % el {hf['fecha_max']} a las {hf['hora_max']} y "
        f"bajó hasta {hf['min']:.0f} % en las horas secas. La lluvia acumulada del lote en toda la ventana fue de "
        f"{lluvia_total:.1f} mm."
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
