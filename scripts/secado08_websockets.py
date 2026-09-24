import json
import random
import time

from azure.iot.device import IoTHubDeviceClient, Message, ProvisioningDeviceClient

from comun import Apagon, clave_dispositivo, leer_env

ID = "secado-fermentacion-01"
INTERVALO = 120
HOST_DPS = "global.azure-devices-provisioning.net"

scope, clave_grupo = leer_env()
clave = clave_dispositivo(clave_grupo, ID)

prov = ProvisioningDeviceClient.create_from_symmetric_key(
    provisioning_host=HOST_DPS, registration_id=ID, id_scope=scope, symmetric_key=clave, websockets=True)
hub = prov.register().registration_state.assigned_hub
cliente = IoTHubDeviceClient.create_from_symmetric_key(symmetric_key=clave, hostname=hub, device_id=ID, websockets=True)
cliente.connect()
cliente.patch_twin_reported_properties({"loteEnProceso": "F-2026-09"})

apagon = Apagon(ID, 200, 30)
conectado = True
inicio = time.time()

while True:
    if apagon.activo():
        if conectado:
            cliente.disconnect()
            conectado = False
            print("desconectado", flush=True)
        time.sleep(20)
        continue
    if not conectado:
        cliente.connect()
        conectado = True
        print("reconectado", flush=True)
    dias = (time.time() - inicio) / 86400
    datos = {
        "temperaturaCaja": round(min(48.0, 31 + dias * 2.5) + random.uniform(-0.6, 0.6), 2),
        "humedadRelativa": round(random.uniform(74, 86), 1),
        "masaEstimada": round(max(95.0, 180 - dias * 4) + random.uniform(-0.3, 0.3), 2),
    }
    msg = Message(json.dumps(datos))
    msg.content_type = "application/json"
    msg.content_encoding = "utf-8"
    cliente.send_message(msg)
    print(datos, flush=True)
    time.sleep(INTERVALO)
