import json
import time
import urllib.request

from azure.iot.device import IoTHubDeviceClient, Message, ProvisioningDeviceClient

from comun import clave_dispositivo, leer_env

ID = "meteorologia-predio-01"
INTERVALO = 600
HOST_DPS = "global.azure-devices-provisioning.net"
URL = ("https://api.open-meteo.com/v1/forecast?latitude=6.88&longitude=-73.41"
       "&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,shortwave_radiation"
       "&timezone=America%2FBogota")

scope, clave_grupo = leer_env()
clave = clave_dispositivo(clave_grupo, ID)

prov = ProvisioningDeviceClient.create_from_symmetric_key(
    provisioning_host=HOST_DPS, registration_id=ID, id_scope=scope, symmetric_key=clave)
hub = prov.register().registration_state.assigned_hub
cliente = IoTHubDeviceClient.create_from_symmetric_key(symmetric_key=clave, hostname=hub, device_id=ID)
cliente.connect()
cliente.patch_twin_reported_properties({"fuenteDatos": "Open-Meteo API (6.88, -73.41)"})

while True:
    try:
        with urllib.request.urlopen(URL, timeout=20) as r:
            actual = json.load(r)["current"]
        datos = {
            "temperatura": actual["temperature_2m"],
            "humedadRelativa": actual["relative_humidity_2m"],
            "lluvia": actual["precipitation"],
            "viento": actual["wind_speed_10m"],
            "radiacion": actual["shortwave_radiation"],
            "horaFuente": actual["time"],
        }
        msg = Message(json.dumps(datos))
        msg.content_type = "application/json"
        msg.content_encoding = "utf-8"
        cliente.send_message(msg)
        print(datos, flush=True)
    except Exception as e:
        print("error", e, flush=True)
    time.sleep(INTERVALO)
