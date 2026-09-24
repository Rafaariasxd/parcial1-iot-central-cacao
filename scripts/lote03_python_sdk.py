import json
import random
import time

from azure.iot.device import IoTHubDeviceClient, Message, ProvisioningDeviceClient

from comun import Apagon, clave_dispositivo, leer_env, luz_dia

ID = "lote-cultivo-03"
INTERVALO = 60
HOST_DPS = "global.azure-devices-provisioning.net"

scope, clave_grupo = leer_env()
clave = clave_dispositivo(clave_grupo, ID)

prov = ProvisioningDeviceClient.create_from_symmetric_key(
    provisioning_host=HOST_DPS, registration_id=ID, id_scope=scope, symmetric_key=clave)
hub = prov.register().registration_state.assigned_hub
cliente = IoTHubDeviceClient.create_from_symmetric_key(symmetric_key=clave, hostname=hub, device_id=ID)
cliente.connect()
cliente.patch_twin_reported_properties({"loteId": "L3", "intervaloMuestreoSeg": INTERVALO})

apagon = Apagon(ID, 240, 25)
humedad = 34.0
conectado = True

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
    humedad = min(45.0, max(22.0, humedad - random.uniform(0.0, 0.25) + (random.uniform(3, 6) if random.random() < 0.02 else 0)))
    datos = {
        "humedadSuelo": round(humedad, 2),
        "iluminanciaPAR": round(luz_dia(18000), 1),
    }
    msg = Message(json.dumps(datos))
    msg.content_type = "application/json"
    msg.content_encoding = "utf-8"
    cliente.send_message(msg)
    print(datos, flush=True)
    time.sleep(INTERVALO)
