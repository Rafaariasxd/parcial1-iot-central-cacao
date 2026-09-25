import json
import sys
import urllib.request
import urllib.error

BASE = "https://parcial1-granja-unab-rarias.azureiotcentral.com/api"
VERSION = "2022-10-31-preview"
TOKEN = open(r"D:\Parcial1-IoT\.secrets\iotc_api.txt").read().strip()

GRUPOS = {
    "cultivo": "ZHRtaTpid2dkOHptejp0a3pxYzI0dA",
    "dosel": "ZHRtaTp3cWtwZmp2bjp6bDZpbGJ2aA",
    "estacion": "ZHRtaTp1bnhuamF0OmNiYXpvc2xh",
    "meteo": "ZHRtaTpkb3E0YWFrZzpyaGFpMHRqcQ",
    "aire": "ZHRtaTp2Y3VmbWRtYjpxOXhpbmRodWI",
    "proceso": "ZHRtaTp4NWloaXMweTpkOXB4Zmlocw",
    "riego": "ZHRtaTpwMGR4YXJ2eDpqbGR4cmFh",
    "perimetro": "ZHRtaTp1c2NzbW9qOnQ3Z3ZsMnlmaw",
}


def llamar(metodo, ruta, cuerpo=None):
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(f"{BASE}{ruta}?api-version={VERSION}", data=datos, method=metodo)
    req.add_header("Authorization", TOKEN)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            texto = r.read().decode()
            return r.status, json.loads(texto) if texto else {}
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


DISPOSITIVOS = {
    "cultivo": ["lote-cultivo-01", "lote-cultivo-02", "lote-cultivo-03"],
    "dosel": ["dosel-sombra-01"],
    "estacion": ["estacion-campo-01"],
    "meteo": ["meteorologia-predio-01"],
    "aire": ["calidad-aire-01"],
    "proceso": ["secado-fermentacion-01"],
    "riego": ["reservorio-riego-01"],
    "perimetro": ["perimetro-bodega-01"],
}


def rango(duracion, resolucion):
    return {"type": "time", "duration": duracion, "resolution": resolucion}


def linea(nombre, grupo, capacidades, x, y, w=4, h=3, duracion="P1D", resolucion="PT30M"):
    return {
        "displayName": nombre,
        "configuration": {
            "type": "lineChart",
            "capabilities": [{"capability": c, "aggregateFunction": f} for c, f in capacidades],
            "group": GRUPOS[grupo],
            "devices": DISPOSITIVOS[grupo],
            "format": {"showLegend": True, "xAxisEnabled": True, "yAxisEnabled": True},
            "queryRange": rango(duracion, resolucion),
        },
        "x": x, "y": y, "width": w, "height": h,
    }


def kpi(nombre, grupo, capacidad, funcion, x, y, duracion="P1D", w=2, h=1):
    return {
        "displayName": nombre,
        "configuration": {
            "type": "kpi",
            "capability": {"capability": capacidad, "aggregateFunction": funcion},
            "group": GRUPOS[grupo],
            "devices": DISPOSITIVOS[grupo],
            "format": {"abbreviateValue": False, "wordWrap": True},
            "queryRange": {"type": "time", "duration": duracion},
        },
        "x": x, "y": y, "width": w, "height": h,
    }


def texto(nombre, descripcion, x, y, w=4, h=1):
    return {
        "displayName": nombre,
        "configuration": {"type": "markdown", "description": descripcion, "href": "", "image": ""},
        "x": x, "y": y, "width": w, "height": h,
    }


def kpi_multi(nombre, grupo, capacidad, funcion, x, y, w=2, h=1):
    t = kpi(nombre, grupo, capacidad, funcion, x, y, w=w, h=h)
    c = t["configuration"]
    c["capabilities"] = [c.pop("capability")]
    return t


def conteo(nombre, grupo, x, y, w=2, h=2):
    return {
        "displayName": nombre,
        "configuration": {"type": "deviceCount", "group": GRUPOS[grupo], "format": {}},
        "x": x, "y": y, "width": w, "height": h,
    }


def construir():
    return [
        texto("Finca Cacao San Vicente de Chucuri", "Cuarto de control - flota de 10 dispositivos IoT, 10 origenes de envio", 0, 0, 6, 1),
        conteo("Estado de la flota de cultivo", "cultivo", 6, 0, 2, 2),
        kpi_multi("Humedad suelo promedio (%)", "cultivo", "humedadSuelo", "avg", 0, 1),
        kpi_multi("Humedad suelo maxima (%)", "cultivo", "humedadSuelo", "max", 2, 1),
        kpi_multi("Humedad suelo minima (%)", "cultivo", "humedadSuelo", "min", 4, 1),
        kpi_multi("Tanque minimo (%)", "riego", "nivelTanque", "min", 0, 2),
        kpi_multi("Temperatura de caja maxima (C)", "proceso", "temperaturaCaja", "max", 2, 2),
        kpi_multi("PM2.5 maximo", "aire", "pm25", "max", 4, 2),
        kpi_multi("Lluvia acumulada (mm)", "meteo", "lluvia", "sum", 6, 2),
        texto("Zonas de la finca", "Lote 1 (norte) - Lote 2 (centro) - Lote 3 (sur) | Dosel de sombra junto al lote 2 | Estacion de campo en el cruce de caminos | Caseta: modem 4G, reservorio y riego | Bodega: secado, fermentacion y perimetro", 0, 21, 4, 2),
        texto("Alertas activas", "Fermentacion caja caliente: temperatura de caja mayor a 42 C | Bodega temperatura alta: temperatura mayor a 28 C | Aviso por correo en cada disparo", 4, 21, 4, 2),
        linea("Humedad del suelo por lote (%)", "cultivo", [("humedadSuelo", "avg")], 0, 3),
        linea("Temperatura del suelo (C)", "cultivo", [("temperaturaSuelo", "avg")], 4, 3),
        linea("Iluminancia PAR (lx)", "cultivo", [("iluminanciaPAR", "avg")], 0, 6),
        linea("Bajo sombra: temperatura y humedad", "dosel", [("temperatura", "avg"), ("humedadRelativa", "avg")], 4, 6),
        linea("Meteorologia: temperatura y lluvia", "meteo", [("temperatura", "avg"), ("lluvia", "sum")], 0, 9),
        linea("Calidad del aire: PM2.5 y AQI", "aire", [("pm25", "avg"), ("aqi", "avg")], 4, 9),
        linea("Fermentacion: temperatura de caja (C)", "proceso", [("temperaturaCaja", "avg")], 0, 12),
        linea("Fermentacion: humedad y masa", "proceso", [("humedadRelativa", "avg"), ("masaEstimada", "avg")], 4, 12),
        linea("Riego: nivel del tanque (%)", "riego", [("nivelTanque", "avg")], 0, 15),
        linea("Bodega: temperatura", "perimetro", [("temperaturaBodega", "avg")], 4, 15),
        linea("Bodega: eventos de puerta y movimiento", "perimetro", [("puerta", "sum"), ("movimiento", "sum")], 0, 18),
        linea("Estacion de campo: lluvia y humedad foliar", "estacion", [("lluviaLote", "sum"), ("humedadFoliar", "avg")], 4, 18),
    ]


if __name__ == "__main__":
    tiles = construir()
    cuerpo = {"displayName": "Cuarto de control - Finca Cacao", "personal": False, "tiles": tiles}
    estado, resp = llamar("PUT", "/dashboards/dtmi:unab:parcial1:cuartocontrol", cuerpo)
    print(estado, resp if estado >= 300 else "ok")
