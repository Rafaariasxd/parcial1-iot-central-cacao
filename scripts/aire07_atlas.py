import json
import os
import time
import urllib.request

from azure.iot.device import IoTHubDeviceClient, Message, ProvisioningDeviceClient

from comun import clave_dispositivo, leer_env

ID = "calidad-aire-01"
INTERVALO = 900
HOST_DPS = "global.azure-devices-provisioning.net"
LAT_LON = "6.88,-73.41"
BASE = "https://atlas.microsoft.com/weather"

scope, clave_grupo = leer_env()
clave = clave_dispositivo(clave_grupo, ID)
maps_key = os.environ["AZURE_MAPS_KEY"]


def consultar(ruta):
    url = f"{BASE}/{ruta}/json?api-version=1.1&query={LAT_LON}&subscription-key={maps_key}"
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.load(r)


prov = ProvisioningDeviceClient.create_from_symmetric_key(
    provisioning_host=HOST_DPS, registration_id=ID, id_scope=scope, symmetric_key=clave)
hub = prov.register().registration_state.assigned_hub
cliente = IoTHubDeviceClient.create_from_symmetric_key(symmetric_key=clave, hostname=hub, device_id=ID)
cliente.connect()
cliente.patch_twin_reported_properties({"fuenteDatos": "Azure Maps Weather (Atlas)"})

while True:
    try:
        aire = consultar("airQuality/current")["results"][0]
        clima = consultar("currentConditions")["results"][0]
        pm25 = next((p["concentration"]["value"] for p in aire.get("pollutants", []) if p["type"] == "PM2.5"), None)
        datos = {
            "pm25": pm25,
            "aqi": aire["globalIndex"],
            "humedadRelativa": clima["relativeHumidity"],
            "horaFuente": aire["dateTime"],
        }
        msg = Message(json.dumps(datos))
        msg.content_type = "application/json"
        msg.content_encoding = "utf-8"
        cliente.send_message(msg)
        print(datos, flush=True)
    except Exception as e:
        print("error", e, flush=True)
    time.sleep(INTERVALO)
