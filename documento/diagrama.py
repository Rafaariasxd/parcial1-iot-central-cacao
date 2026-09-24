import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(figsize=(13, 7.2), dpi=150)
ax.set_xlim(0, 13)
ax.set_ylim(0, 7.2)
ax.axis("off")

VERDE, CAFE, AZUL, GRIS = "#2f6f4e", "#8b5a2b", "#2b5c8a", "#f2efe8"


def caja(x, y, w, h, texto, fondo="#ffffff", borde="#444444", size=8.5, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fondo, ec=borde, lw=1.2))
    ax.text(x + w / 2, y + h / 2, texto, ha="center", va="center", fontsize=size, fontweight="bold" if bold else "normal")


def flecha(x1, y1, x2, y2, color="#555555"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=11, lw=1.1, color=color))


ax.text(0.1, 7.0, "Finca de cacao - San Vicente de Chucuri: arquitectura del escenario IoT", fontsize=12, fontweight="bold", va="center")

ax.add_patch(FancyBboxPatch((0.1, 0.4), 4.9, 6.2, boxstyle="round,pad=0.02,rounding_size=0.1", fc=GRIS, ec=VERDE, lw=1.5))
ax.text(2.55, 6.35, "Campo y bodega (10 dispositivos, 10 origenes)", ha="center", fontsize=9, fontweight="bold", color=VERDE)

origenes = [
    ("lote-cultivo-01", "Digital Twin / simulador nativo"),
    ("lote-cultivo-02", "ESP32 en Wokwi"),
    ("lote-cultivo-03", "Python SDK (MQTT)"),
    ("dosel-sombra-01", "Python, MQTT explicito (paho)"),
    ("estacion-campo-01", "Node.js SDK"),
    ("meteorologia-predio-01", "API publica Open-Meteo"),
    ("calidad-aire-01", "Atlas Weather (Azure Maps)"),
    ("secado-fermentacion-01", "Python SDK sobre WebSockets"),
    ("reservorio-riego-01", "ESP32 en Wokwi (rele + ultrasonido)"),
    ("perimetro-bodega-01", "REST manual (HTTPS)"),
]
for i, (dev, org) in enumerate(origenes):
    y = 5.75 - i * 0.55
    caja(0.25, y, 4.6, 0.46, f"{dev}  |  {org}", size=7.6)

caja(5.6, 5.3, 2.0, 0.9, "DPS\nglobal.azure-devices-\nprovisioning.net", "#e7eef7", AZUL, 7.8)
caja(5.6, 3.55, 2.0, 0.9, "IoT Hub\n(MQTT 8883, WSS 443,\nHTTPS)", "#e7eef7", AZUL, 7.8)
caja(5.6, 1.8, 2.0, 0.9, "Ingesta de\ntelemetria y\npropiedades", "#e7eef7", AZUL, 7.8)
flecha(5.0, 4.6, 5.6, 5.7)
flecha(6.6, 5.3, 6.6, 4.45)
flecha(5.0, 3.6, 5.6, 4.0)
flecha(6.6, 3.55, 6.6, 2.7)

ax.add_patch(FancyBboxPatch((8.2, 0.4), 4.7, 6.2, boxstyle="round,pad=0.02,rounding_size=0.1", fc="#fbf6ee", ec=CAFE, lw=1.5))
ax.text(10.55, 6.35, "Azure IoT Central (parcial1-granja-cacao)", ha="center", fontsize=9, fontweight="bold", color=CAFE)
caja(8.45, 5.2, 4.2, 0.8, "8 plantillas DTDL: Cultivo, Dosel, Estacion, Meteorologia,\nCalidad de aire, Proceso, Riego, Perimetro", "#ffffff", CAFE, 7.6)
caja(8.45, 4.0, 4.2, 0.8, "Grupos de dispositivos y estado de flota\n(Conectado / Desconectado / Sin asociar)", "#ffffff", CAFE, 7.6)
caja(8.45, 2.8, 4.2, 0.8, "Panel Cuarto de control: KPIs, 12 graficas,\nconteo de flota", "#ffffff", CAFE, 7.6)
caja(8.45, 1.6, 4.2, 0.8, "Reglas: caja de fermentacion > 42 C,\nbodega > 28 C", "#ffffff", CAFE, 7.6)
caja(8.45, 0.6, 4.2, 0.7, "Alertas por correo", "#ffffff", CAFE, 7.6)
flecha(7.6, 2.25, 8.2, 3.2)
flecha(10.55, 1.6, 10.55, 1.3)

caja(5.6, 0.5, 2.0, 0.75, "VM Azure (Ubuntu)\n7 servicios systemd", "#e9f3ec", VERDE, 7.6)
ax.text(6.6, 1.42, "genera 7 de los origenes", ha="center", fontsize=6.8, color=VERDE)
plt.tight_layout()
plt.savefig("diagrama_arquitectura.png")
