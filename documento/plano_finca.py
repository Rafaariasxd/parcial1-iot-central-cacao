import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, Polygon
from matplotlib.path import Path
from matplotlib.patches import PathPatch

rng = np.random.default_rng(7)

PAL = {
    "bg": (20, 33, 22),
    "pasto1": (86, 107, 52),
    "pasto2": (98, 121, 58),
    "pasto3": (74, 93, 44),
    "surco": (108, 82, 46),
    "surco2": (92, 68, 38),
    "cerca": (156, 112, 61),
    "cerca_sombra": (110, 78, 42),
    "sendero": (208, 178, 110),
    "sendero2": (184, 152, 88),
    "sendero3": (162, 132, 74),
    "lote": (231, 168, 52),
    "lote_sombra": (188, 130, 36),
    "hoja1": (108, 186, 111),
    "hoja2": (72, 150, 84),
    "hoja3": (48, 116, 63),
    "hoja_luz": (150, 210, 140),
    "tronco": (94, 60, 30),
    "techo": (168, 84, 52),
    "techo_sombra": (132, 58, 36),
    "techo_luz": (196, 108, 68),
    "pared": (232, 210, 168),
    "pared_sombra": (206, 180, 136),
    "puerta": (94, 58, 30),
    "ventana": (140, 196, 212),
    "agua": (86, 154, 202),
    "agua_luz": (140, 200, 232),
    "agua_sombra": (58, 112, 158),
    "gris": (168, 168, 168),
    "gris2": (120, 120, 120),
    "rojo": (206, 79, 52),
    "blanco": (244, 240, 224),
}

W, H = 96, 66
img = np.zeros((H, W, 3), dtype=np.uint8)
img[:, :] = PAL["bg"]


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        img[y, x] = PAL[c]


def rect(x0, y0, x1, y1, c):
    img[max(y0, 0):max(y1, 0), max(x0, 0):max(x1, 0)] = PAL[c]


def textura(x0, y0, x1, y1, base, variantes, densidad=0.18):
    rect(x0, y0, x1, y1, base)
    for y in range(y0, y1):
        for x in range(x0, x1):
            if rng.random() < densidad:
                img[y, x] = PAL[rng.choice(variantes)]


def cerca(x0, y0, x1, y1):
    for x in range(x0, x1, 3):
        img[y0, x] = PAL["cerca"]
        if y0 + 1 < H:
            img[y0 + 1, x] = PAL["cerca_sombra"]
    for y in range(y0, y1, 1):
        img[y, x0] = PAL["cerca"] if y % 2 == 0 else PAL["cerca_sombra"]
        img[y, x1 - 1] = PAL["cerca"] if y % 2 == 0 else PAL["cerca_sombra"]


def cacao(cx, cy):
    rect(cx - 1, cy + 2, cx + 2, cy + 4, "tronco")
    for dx, dy, c in [(-2, -2, "hoja3"), (2, -2, "hoja3"), (0, -3, "hoja2"), (-1, 0, "hoja2"), (1, 0, "hoja1"), (0, -1, "hoja_luz")]:
        img[max(cy + dy, 0):cy + dy + 2, max(cx + dx, 0):cx + dx + 2] = PAL[c]


def lote_cultivo(x0, y0, x1, y1, filas=3):
    textura(x0, y0, x1, y1, "surco", ["surco2"], 0.22)
    paso_y = (y1 - y0) // filas
    for fy in range(filas):
        yy = y0 + paso_y * fy + paso_y // 2
        for xx in range(x0 + 3, x1 - 2, 5):
            cacao(xx, yy)


def techo_triangular(x0, y0, w, alto, base="techo"):
    mitad = w // 2
    for i in range(alto):
        anchoy = int((i + 1) / alto * mitad) + 1
        y = y0 + i
        c = "techo_luz" if i == 0 else ("techo_sombra" if i == alto - 1 else base)
        rect(x0 + mitad - anchoy, y, x0 + mitad + anchoy, y + 1, c)


def casa(x0, y0, w, h, alto_techo=4, techo="techo", con_chimenea=False):
    techo_triangular(x0 - 1, y0, w + 2, alto_techo, techo)
    y_pared = y0 + alto_techo
    rect(x0, y_pared, x0 + w, y_pared + h, "pared")
    rect(x0, y_pared + h - 1, x0 + w, y_pared + h, "pared_sombra")
    for wx in (x0 + 2, x0 + w - 4):
        rect(wx, y_pared + 2, wx + 2, y_pared + 4, "ventana")
    rect(x0 + w // 2 - 1, y_pared + h - 4, x0 + w // 2 + 1, y_pared + h, "puerta")
    if con_chimenea:
        rect(x0 + w - 3, y0 - 3, x0 + w - 1, y0 + 1, "gris2")


def tanque(x0, y0, w, h):
    rect(x0, y0, x0 + w, y0 + h, "agua_sombra")
    rect(x0 + 1, y0 + 1, x0 + w - 1, y0 + h - 1, "agua")
    rect(x0 + 1, y0 + 1, x0 + w - 1, y0 + 3, "agua_luz")
    rect(x0, y0 - 1, x0 + w, y0, "gris2")


def antena(x, y0, alto):
    for i in range(alto):
        img[y0 - i, x] = PAL["gris2"] if i % 2 else PAL["gris"]
    img[y0 - alto, x] = PAL["rojo"]


# fondo general: pasto con textura suave en todo el predio
rect(1, 1, W - 1, H - 1, "pasto1")
textura(1, 1, W - 1, H - 1, "pasto1", ["pasto2", "pasto3"], 0.10)

# senderos principales (cruz)
rect(1, 30, W - 1, 34, "sendero")
rect(1, 31, W - 1, 32, "sendero2")
rect(46, 1, 50, H - 1, "sendero")
rect(47, 1, 48, H - 1, "sendero2")
for x in range(1, W - 1, 4):
    img[30, x] = PAL["sendero3"]
    img[33, x] = PAL["sendero3"]

# cercas alrededor de los tres lotes (occidente)
cerca(2, 3, 44, 15)
cerca(2, 18, 44, 29)
cerca(2, 35, 44, 47)
lote_cultivo(3, 4, 43, 14, filas=2)
lote_cultivo(3, 19, 43, 28, filas=2)
lote_cultivo(3, 36, 43, 46, filas=2)

# dosel de sombra: arboleda cerca del cruce, sobre el lote 2
copas = [(58, 20), (63, 18), (68, 21), (61, 25), (66, 26), (71, 24)]
for cx, cy in copas:
    for dy, dx, r, c in [(0, 0, 4, "hoja3")]:
        pass
for cx, cy in copas:
    for r, c in [(4, "hoja3"), (3, "hoja2"), (2, "hoja1")]:
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    px(xx, yy, c)
    px(cx - 1, cy - 1, "hoja_luz")
    rect(cx - 1, cy + 4, cx + 1, cy + 6, "tronco")

# estacion de campo, junto al cruce
antena(51, 28, 6)
rect(50, 28, 53, 30, "gris2")

# caseta central (modem, reservorio y riego) - nororiente
casa(60, 6, 14, 8, alto_techo=5, techo="techo", con_chimenea=False)
antena(74, 9, 5)
tanque(80, 10, 7, 9)

# bodega (secado, fermentacion, perimetro) - suroriente
casa(60, 42, 17, 10, alto_techo=5, techo="techo_sombra", con_chimenea=True)
rect(58, 41, 80, 42, "gris2")

# cerca perimetral general del predio
for x in range(1, W - 1):
    if img[1, x].tolist() == list(PAL["pasto1"]) or True:
        pass

Image = __import__("PIL.Image", fromlist=["Image"])
im_full = Image.fromarray(img, "RGB").resize((W * 9, H * 9), Image.NEAREST)
im_full.save("plano_finca_base.png")

PINES = [
    ("1", "lote-cultivo-01", 23, 9),
    ("2", "lote-cultivo-02", 23, 23),
    ("3", "lote-cultivo-03", 23, 41),
    ("4", "dosel-sombra-01", 64, 22),
    ("5", "estacion-campo-01", 51.5, 27),
    ("6", "meteorologia-predio-01", 67, 10),
    ("7", "calidad-aire-01", 76, 12),
    ("8", "secado-fermentacion-01", 68, 42),
    ("9", "reservorio-riego-01", 83.5, 9),
    ("10", "perimetro-bodega-01", 68, 51),
]

fig, ax = plt.subplots(figsize=(12, 8.6), dpi=170)
ax.imshow(im_full, extent=[0, W, H, 0], interpolation="nearest")

for num, nombre, x, y in PINES:
    y_pin = y - 5.2
    ax.plot([x, x], [y_pin + 2.0, y - 1.1], color="#2b2118", lw=1.3, zorder=5, solid_capstyle="round")
    ax.add_patch(FancyBboxPatch((x - 2.0, y_pin - 1.9), 4.0, 3.8, boxstyle="round,pad=0.02,rounding_size=1.2",
                                 fc="#f4ecd6", ec="#3a2c1c", lw=1.15, zorder=6))
    ax.text(x, y_pin + 0.05, num, ha="center", va="center", fontsize=9.5, fontweight="bold", color="#3a2c1c", zorder=7)
    ax.add_patch(plt.Circle((x, y), 0.55, facecolor="#3a2c1c", edgecolor="none", zorder=4, alpha=0.55))

ax.set_xlim(0, W)
ax.set_ylim(H, -6)
ax.axis("off")
fig.patch.set_facecolor("white")
ax.set_title("Plano de la finca de cacao – San Vicente de Chucurí", fontsize=14, fontweight="bold", color="#2f6f4e", pad=10)
fig.tight_layout()
fig.savefig("plano_finca.png", facecolor="white")
print("ok")
