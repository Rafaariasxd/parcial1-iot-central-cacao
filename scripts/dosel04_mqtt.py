import base64
import hashlib
import hmac
import json
import random
import ssl
import time
import urllib.parse

import paho.mqtt.client as mqtt

from comun import Apagon, ciclo_dia, clave_dispositivo, leer_env, luz_dia

ID = "dosel-sombra-01"
INTERVALO = 45
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


def cliente_tls():
    c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=ID, protocol=mqtt.MQTTv311)
    c.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS_CLIENT)
    return c


def registrar():
    recibido = {}
    c = cliente_tls()
    c.username_pw_set(f"{scope}/registrations/{ID}/api-version=2019-03-31", sas(f"{scope}/registrations/{ID}", "registration"))
    c.on_message = lambda cl, ud, m: recibido.update(cuerpo=m.payload.decode())
    c.connect(HOST_DPS, 8883, keepalive=60)
    c.loop_start()
    c.subscribe("$dps/registrations/res/#", qos=1)
    time.sleep(1)
    c.publish("$dps/registrations/PUT/iotdps-register/?$rid=1", json.dumps({"registrationId": ID}), qos=1)
    hub = None
    for _ in range(30):
        time.sleep(1)
        if "cuerpo" not in recibido:
            continue
        doc = json.loads(recibido.pop("cuerpo"))
        if doc.get("status") == "assigned":
            hub = doc["registrationState"]["assignedHub"]
            break
        c.publish(f"$dps/registrations/GET/iotdps-get-operationstatus/?$rid=2&operationId={doc['operationId']}", "", qos=1)
    c.loop_stop()
    c.disconnect()
    return hub


hub = registrar()
apagon = Apagon(ID, 300, 40)
topico = f"devices/{ID}/messages/events/"
c = None
conectado_desde = 0.0

while True:
    if c is not None and time.time() - conectado_desde > 3000:
        c.loop_stop()
        c.disconnect()
        c = None
    if apagon.activo():
        if c is not None:
            c.loop_stop()
            c.disconnect()
            c = None
            print("desconectado", flush=True)
        time.sleep(20)
        continue
    if c is None:
        c = cliente_tls()
        c.username_pw_set(f"{hub}/{ID}/?api-version=2021-04-12", sas(f"{hub}/devices/{ID}"))
        c.reconnect_delay_set(min_delay=1, max_delay=10)
        c.connect(hub, 8883, keepalive=30)
        c.loop_start()
        conectado_desde = time.time()
        print("conectado", flush=True)
    datos = {
        "temperatura": round(ciclo_dia(21.5, 28.5) + random.uniform(-0.4, 0.4), 2),
        "humedadRelativa": round(ciclo_dia(92, 68, pico=14.0) + random.uniform(-1.5, 1.5), 1),
        "iluminancia": round(luz_dia(9000), 1),
    }
    c.publish(topico, json.dumps(datos), qos=1)
    print(datos, flush=True)
    time.sleep(INTERVALO)
