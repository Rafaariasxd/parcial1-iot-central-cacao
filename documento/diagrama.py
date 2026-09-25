import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(figsize=(15, 8), dpi=150)
ax.set_xlim(0, 15)
ax.set_ylim(0, 8)
ax.axis("off")

CELESTE, AZUL, GRIS = "#a9e3ee", "#2b6fb0", "#f4f4f4"


def marco(x, y, w, h, fondo="#ffffff", borde="#8aa0c8", lw=1.2, r=0.12):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.02,rounding_size={r}", fc=fondo, ec=borde, lw=lw))


def etiqueta(x, y, w, t, fondo=CELESTE, size=7.5):
    marco(x, y, w, 0.34, fondo, "#5aa9bd", 1, 0.1)
    ax.text(x + w / 2, y + 0.17, t, ha="center", va="center", fontsize=size, fontweight="bold")


def texto(x, y, t, size=7, bold=False, color="#111111"):
    ax.text(x, y, t, ha="center", va="center", fontsize=size, fontweight="bold" if bold else "normal", color=color, linespacing=1.15)


def flecha(x1, y1, x2, y2, color="#555555", ls="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=11, lw=1.2, color=color, linestyle=ls))


etiqueta(0.1, 7.5, 2.5, "Dispositivos IoT")
marco(0.1, 0.5, 2.5, 6.95, GRIS, "#7a9bd1")
grupos = [
    (4.15, 7.15, "Nodos de campo (Wi-Fi)", ["lote-cultivo-01/02/03", "dosel-sombra-01", "estacion-campo-01", "reservorio-riego-01"]),
    (2.45, 3.95, "Caseta y bodega (Ethernet)", ["secado-fermentacion-01", "perimetro-bodega-01"]),
    (0.7, 2.25, "APIs por Internet directo", ["meteorologia-predio-01", "calidad-aire-01"]),
]
for base, tope, titulo, items in grupos:
    marco(0.22, base, 2.26, tope - base, "#ffffff", "#8aa0c8", 1, 0.08)
    texto(1.35, tope - 0.28, titulo, 6.8, True)
    for i, it in enumerate(items):
        texto(1.35, tope - 0.75 - i * 0.55, it, 6.6)

etiqueta(3.0, 7.5, 2.0, "Red y conexiones")
marco(3.0, 0.5, 2.0, 6.95, "#ffffff", "#7a9bd1")
texto(4.0, 6.5, "Conexion Wi-Fi\ninalambrica", 7, True)
texto(4.0, 3.3, "Conexion\nEthernet", 7, True)
texto(4.0, 1.5, "Conexion HTTPS\na Internet", 7, True)
marco(3.25, 4.4, 1.5, 0.75, "#eef3fb", "#8aa0c8", 1, 0.08)
texto(4.0, 4.78, "Gateway / Router\nmodem 4G-LTE", 7, True, AZUL)
flecha(2.48, 5.6, 3.25, 4.95)
flecha(2.48, 3.2, 3.25, 4.6)
flecha(2.48, 1.5, 3.0, 1.5, "#4fae7a", "--")

etiqueta(5.35, 5.25, 0.95, "Conexion", "#dfe9fb")
flecha(4.75, 4.98, 6.45, 4.98, AZUL)
etiqueta(5.35, 4.0, 0.95, "Trabajos", "#dfe9fb")
flecha(6.45, 4.55, 4.75, 4.55, AZUL)

etiqueta(6.45, 7.5, 6.6, "Azure IoT Central")
marco(6.45, 0.5, 6.6, 6.95, "#ffffff", "#7a9bd1")

marco(6.6, 3.0, 1.35, 4.0, "#f2f6fb", "#8aa0c8", 1, 0.08)
etiqueta(6.63, 6.6, 1.29, "Ingestion", "#dfe9fb", 6.5)
texto(7.27, 5.55, "Azure IoT Hub", 7, True)
texto(7.27, 4.1, "Device\nProvisioning\nService", 7, True)

for y, t, s in [(6.2, "Hot Path", "Azure Stream\nAnalytics"), (4.95, "Warm Path", "Azure Data\nExplorer"), (3.5, "Cold Path", "SQL DB\nCosmos DB")]:
    marco(8.1, y - 0.3, 1.2, 1.15, "#f2f6fb", "#8aa0c8", 1, 0.08)
    etiqueta(8.13, y + 0.5, 1.14, t, "#dfe9fb", 6.5)
    texto(8.7, y + 0.1, s, 6.8, True)

marco(9.5, 2.2, 3.4, 4.85, "#f2f6fb", "#8aa0c8", 1, 0.1)
etiqueta(9.7, 6.65, 3.0, "Experiencia web de administracion", CELESTE, 6.8)
cols = [
    (9.6, "Administrar los\ndispositivos", ["Ver datos sin\nprocesar", "Estado de\nconectividad", "Modelado de\ndispositivos", "Trabajos"]),
    (10.75, "Visualizacion y\nanalisis de datos", ["Dashboards", "Analitica de\ndatos", "Reglas"]),
    (11.9, "Asegurar los\ndatos y los\ndispositivos", ["Gestion de\nusuarios", "Organizaciones"]),
]
for x, tit, items in cols:
    marco(x, 2.35, 1.05, 4.15, "#ffffff", "#8aa0c8", 1, 0.08)
    texto(x + 0.525, 6.05, tit, 6.3, True)
    for i, it in enumerate(items):
        marco(x + 0.08, 4.95 - i * 0.68, 0.89, 0.55, "#e6f3fb", "#5aa9bd", 0.8, 0.06)
        texto(x + 0.525, 5.22 - i * 0.68, it, 5.6)

marco(6.6, 0.65, 6.3, 1.35, "#aee6ec", "#5aa9bd", 1, 0.08)
texto(9.75, 1.78, "Basado en los servicios PaaS administrados", 7, True)
for i, t in enumerate(["Alta\ndisponibilidad", "Escalabilidad\nelastica", "Recuperacion\nante desastres"]):
    marco(6.8 + i * 2.05, 0.8, 1.85, 0.7, "#1d78b5", "#1d78b5", 1, 0.08)
    texto(6.8 + i * 2.05 + 0.925, 1.15, t, 6.6, True, "#ffffff")

etiqueta(13.45, 7.5, 1.45, "Integracion empresarial", CELESTE, 6.3)
marco(13.45, 0.5, 1.45, 6.95, GRIS, "#7a9bd1")
texto(14.17, 5.9, "Azure Maps\n(Atlas Weather)", 7, True)
texto(14.17, 4.2, "Correo\nelectronico", 7, True)
texto(14.17, 2.5, "Panel y\nreglas de\nalerta", 7, True)
flecha(13.45, 5.8, 12.95, 5.8, AZUL)
texto(13.2, 6.05, "Consultar", 6, True, AZUL)
flecha(12.95, 4.2, 13.45, 4.2, AZUL)
texto(13.2, 4.5, "Disparar\nalertas", 6, True, AZUL)

plt.tight_layout()
plt.savefig("diagrama_arquitectura.png")
