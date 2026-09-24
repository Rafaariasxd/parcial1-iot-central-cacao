import base64
import hashlib
import hmac
import json
import random
import time
import urllib.error
import urllib.parse
import urllib.request

from comun import Apagon, ciclo_dia, clave_dispositivo, leer_env

ID = "perimetro-bodega-01"
INTERVALO = 90
HOST_DPS = "global.azure-devices-provisioning.net"

scope, clave_grupo = leer_env()
clave = clave_dispositivo(clave_grupo, ID)


def sas(recurso, politica=None, ttl=3600):
    expira = int(time.time()) + ttl
    uri = urllib.parse.quote(recurso, safe="")
    firma = hmac.new(base64.b64decode(clave), f"{uri}\n{expira}".encode(), hashlib.sha256).digest()
    token = f"SharedAccessSignature sr={uri}&sig={urllib.parse.quote(base64.b64encode(firma).decode(), safe='')}&se={expira}"
    if politica:
        token += f"&skn={politica}"
    return token


def llamar(metodo, url, token, cuerpo=None):
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(url, data=datos, method=metodo)
    req.add_header("Authorization", token)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            texto = r.read().decode()
            return r.status, json.loads(texto) if texto else {}
    except urllib.error.HTTPError as e:
        return e.code, {}


def registrar():
    token = sas(f"{scope}/registrations/{ID}", "registration")
    base = f"https://{HOST_DPS}/{scope}/registrations/{ID}"
    estado, doc = llamar("PUT", f"{base}/register?api-version=2021-06-01", token, {"registrationId": ID})
    for _ in range(30):
        if doc.get("status") == "assigned":
            return doc["registrationState"]["assignedHub"]
        time.sleep(2)
        estado, doc = llamar("GET", f"{base}/operations/{doc['operationId']}?api-version=2021-06-01", token)
    raise SystemExit("DPS no asigno hub")


hub = registrar()
apagon = Apagon(ID, 180, 35)
url = f"https://{hub}/devices/{ID}/messages/events?api-version=2020-03-13"

while True:
    if apagon.activo():
        print("fuera de linea", flush=True)
        time.sleep(30)
        continue
    datos = {
        "temperaturaBodega": round(ciclo_dia(23.0, 29.5) + random.uniform(-0.3, 0.3), 2),
        "puerta": 1 if random.random() < 0.06 else 0,
        "movimiento": 1 if random.random() < 0.1 else 0,
    }
    estado, _ = llamar("POST", url, sas(f"{hub}/devices/{ID}"), datos)
    print(estado, datos, flush=True)
    time.sleep(INTERVALO)
