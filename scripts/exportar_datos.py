import csv
import panel_api as p

CONSULTAS = {
    "cultivo": ("dtmi:bwgd8zmz:tkzqc24t", ["humedadSuelo", "temperaturaSuelo", "conductividad", "iluminanciaPAR"]),
    "dosel": ("dtmi:wqkpfjvn:zl6ilbvh", ["temperatura", "humedadRelativa", "iluminancia"]),
    "estacion": ("dtmi:unxnjat:cbazosla", ["lluviaLote", "humedadFoliar"]),
    "meteo": ("dtmi:doq4aakg:rhai0tjq", ["temperatura", "humedadRelativa", "lluvia", "viento", "radiacion"]),
    "aire": ("dtmi:vcufmdmb:q9xindhub", ["pm25", "humedadRelativa", "aqi"]),
    "proceso": ("dtmi:x5ihis0y:d9pxfihs", ["temperaturaCaja", "humedadRelativa", "masaEstimada"]),
    "riego": ("dtmi:p0dxarvx:jldxraa", ["nivelTanque", "caudal"]),
    "perimetro": ("dtmi:uscsmoj:t7gvl2yfk", ["temperaturaBodega", "puerta", "movimiento"]),
}

for nombre, (plantilla, campos) in CONSULTAS.items():
    columnas = ", ".join(campos)
    q = f'SELECT $id, $ts, {columnas} FROM {plantilla} WHERE WITHIN_WINDOW(P7D)'
    estado, resp = p.llamar("POST", "/query", {"query": q})
    if estado != 200:
        print(nombre, estado, str(resp)[:200])
        continue
    filas = resp.get("results", [])
    with open(rf"D:\Parcial1-IoT\datos\{nombre}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "ts"] + campos)
        for r in filas:
            w.writerow([r.get("$id"), r.get("$ts")] + [r.get(c) for c in campos])
    print(nombre, len(filas))
