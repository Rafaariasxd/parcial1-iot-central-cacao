import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from matplotlib.patches import Circle, FancyBboxPatch

PAL = {
    "bg": (28, 43, 30),
    "campo1": (74, 61, 34),
    "campo2": (94, 78, 42),
    "sendero": (196, 164, 94),
    "sendero2": (168, 138, 74),
    "lote": (230, 167, 51),
    "lote_borde": (122, 74, 30),
    "hoja1": (95, 174, 102),
    "hoja2": (63, 138, 74),
    "hoja3": (44, 105, 56),
    "techo": (122, 74, 30),
    "techo2": (94, 56, 22),
    "pared": (222, 196, 150),
    "pared2": (196, 168, 118),
    "puerta": (74, 48, 24),
    "agua": (74, 138, 186),
    "agua2": (52, 104, 150),
    "gris": (150, 150, 150),
    "gris2": (110, 110, 110),
    "rojo": (192, 67, 42),
}

W, H = 64, 44
img = np.zeros((H, W, 3), dtype=np.uint8)
img[:, :] = PAL["bg"]


def rect(x0, y0, x1, y1, color):
    img[y0:y1, x0:x1] = PAL[color]


def arbol(cx, cy, r=2, copa="hoja2", tronco="lote_borde"):
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if 0 <= y < H and 0 <= x < W and (x - cx) ** 2 + (y - cy) ** 2 <= r * r + 1:
                img[y, x] = PAL[copa]
    if 0 <= cy + r < H:
        img[cy + r, cx] = PAL[tronco]


def lote_cultivo(x0, y0, x1, y1):
    rect(x0, y0, x1, y1, "campo1")
    for yy in range(y0 + 1, y1 - 1, 3):
        for xx in range(x0 + 1, x1 - 1, 3):
            arbol(xx, yy, 1, "lote", "lote_borde")


def casa(x0, y0, w, h, techo="techo", pared="pared"):
    rect(x0, y0, x0 + w, y0 + 2, techo)
    rect(x0 - 1, y0 - 1, x0 + w + 1, y0, "techo2")
    rect(x0, y0 + 2, x0 + w, y0 + h, pared)
    img[y0 + h - 3:y0 + h - 1, x0 + w // 2 - 1:x0 + w // 2 + 1] = PAL["puerta"]


rect(2, 2, 62, 42, "campo2")
rect(2, 20, 62, 23, "sendero")
rect(30, 2, 33, 42, "sendero")
rect(2, 20, 62, 21, "sendero2")
rect(30, 2, 31, 42, "sendero2")

lote_cultivo(4, 4, 28, 12)
lote_cultivo(4, 15, 28, 19)
lote_cultivo(4, 24, 28, 32)

for cx, cy in [(35, 16), (38, 15), (41, 17), (35, 19), (39, 20)]:
    arbol(cx, cy, 2, "hoja3", "lote_borde")
for cx, cy in [(35, 16), (38, 15), (41, 17), (35, 19), (39, 20)]:
    arbol(cx, cy, 1, "hoja1", "lote_borde")

img[19, 31] = PAL["gris"]
img[18, 31] = PAL["gris2"]
img[17, 31] = PAL["rojo"]

casa(46, 8, 9, 8)
rect(58, 10, 61, 15, "agua")
rect(58, 10, 61, 11, "agua2")
img[7, 50] = PAL["gris2"]
img[6, 50] = PAL["gris"]

casa(44, 27, 12, 9, "techo2", "pared2")
rect(43, 26, 57, 27, "gris2")

PINES = [
    ("1", "lote-cultivo-01", 16, 8, "#e6a733"),
    ("2", "lote-cultivo-02", 16, 17, "#e6a733"),
    ("3", "lote-cultivo-03", 16, 28, "#e6a733"),
    ("4", "dosel-sombra-01", 38, 17, "#5fae66"),
    ("5", "estacion-campo-01", 31, 20, "#c0432a"),
    ("6", "meteorologia-predio-01", 50, 5, "#4a8aba"),
    ("7", "calidad-aire-01", 55, 5, "#b7b7b7"),
    ("8", "secado-fermentacion-01", 50, 30, "#7a4a1e"),
    ("9", "reservorio-riego-01", 59.5, 12.5, "#4a8aba"),
    ("10", "perimetro-bodega-01", 50, 35, "#c0432a"),
]

fig, ax = plt.subplots(figsize=(11, 8), dpi=170)
ax.imshow(img, extent=[0, W, H, 0], interpolation="nearest")
for num, nombre, x, y, color in PINES:
    ax.add_patch(Circle((x, y), 1.35, facecolor=color, edgecolor="white", linewidth=1.1, zorder=5))
    ax.text(x, y, num, ha="center", va="center", fontsize=8.5, fontweight="bold", color="#1c1c1c", zorder=6)
ax.set_xlim(0, W)
ax.set_ylim(H, 0)
ax.axis("off")
ax.set_title("Plano de la finca de cacao - San Vicente de Chucuri", fontsize=13, fontweight="bold", color="#2f6f4e", pad=12)
fig.tight_layout()
fig.savefig("plano_finca.png", facecolor="white")
print("ok")
