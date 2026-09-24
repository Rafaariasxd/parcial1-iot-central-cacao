import base64
import hashlib
import hmac
import math
import os
import random
import time


def leer_env():
    return os.environ["IOTC_ID_SCOPE"], os.environ["IOTC_GROUP_KEY"]


def clave_dispositivo(clave_grupo, id_dispositivo):
    firma = hmac.new(base64.b64decode(clave_grupo), id_dispositivo.encode(), hashlib.sha256).digest()
    return base64.b64encode(firma).decode()


def hora_local():
    t = time.gmtime(time.time() - 5 * 3600)
    return t.tm_hour + t.tm_min / 60


def luz_dia(maximo):
    h = hora_local()
    if h < 6 or h > 18:
        return 0.0
    return maximo * math.sin(math.pi * (h - 6) / 12) * random.uniform(0.7, 1.0)


def ciclo_dia(minimo, maximo, pico=14.0):
    h = hora_local()
    fase = math.cos(2 * math.pi * (h - pico) / 24)
    return minimo + (maximo - minimo) * (fase + 1) / 2


class Apagon:
    def __init__(self, id_dispositivo, cada_min, dura_min):
        self.cada = cada_min * 60
        self.dura = dura_min * 60
        self.desfase = sum(id_dispositivo.encode()) * 97 % (self.cada + self.dura)

    def activo(self):
        return (time.time() + self.desfase) % (self.cada + self.dura) >= self.cada
