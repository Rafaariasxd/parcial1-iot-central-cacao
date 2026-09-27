import numpy as np
from PIL import Image, ImageDraw, ImageFont

VERDE_BG = (28, 43, 30)
NARANJA = (230, 167, 51)
CAFE = (122, 74, 30)
CAFE2 = (94, 56, 22)
VERDE1 = (95, 174, 102)
VERDE2 = (63, 138, 74)
VERDE3 = (44, 105, 56)
AZUL = (74, 138, 186)
AZUL2 = (52, 104, 150)
GRIS = (150, 150, 150)
GRIS2 = (110, 110, 110)
ROJO = (192, 67, 42)
CREMA = (222, 196, 150)
BLANCO = (235, 235, 235)
NEGRO = (30, 30, 30)
AMARILLO = (240, 205, 90)

N = 16


def lienzo():
    a = np.zeros((N, N, 3), dtype=np.uint8)
    a[:, :] = VERDE_BG
    return a


def cuadro(a, x0, y0, x1, y1, c):
    a[y0:y1, x0:x1] = c


def circulo(a, cx, cy, r, c):
    for y in range(N):
        for x in range(N):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                a[y, x] = c


def cultivo():
    a = lienzo()
    cuadro(a, 2, 11, 14, 15, CAFE2)
    for x in (5, 8, 11):
        cuadro(a, x, 7, x + 1, 11, VERDE3)
    circulo(a, 5, 6, 2, VERDE2)
    circulo(a, 8, 4, 2, VERDE1)
    circulo(a, 11, 6, 2, VERDE2)
    return a


def dosel():
    a = lienzo()
    circulo(a, 8, 6, 6, VERDE3)
    circulo(a, 8, 6, 4, VERDE2)
    circulo(a, 6, 5, 2, VERDE1)
    cuadro(a, 7, 12, 9, 15, CAFE)
    return a


def estacion():
    a = lienzo()
    cuadro(a, 7, 3, 9, 13, GRIS)
    cuadro(a, 9, 3, 13, 6, ROJO)
    circulo(a, 4, 9, 2, AZUL)
    circulo(a, 4, 12, 2, AZUL2)
    return a


def meteo():
    a = lienzo()
    circulo(a, 6, 5, 3, AMARILLO)
    circulo(a, 8, 9, 4, BLANCO)
    circulo(a, 11, 8, 3, GRIS)
    cuadro(a, 5, 9, 12, 12, BLANCO)
    return a


def aire():
    a = lienzo()
    for i, y in enumerate((4, 7, 10)):
        cuadro(a, 2 + i, y, 12 - i, y + 2, GRIS if i % 2 == 0 else GRIS2)
    circulo(a, 12, 12, 2, VERDE1)
    return a


def proceso():
    a = lienzo()
    cuadro(a, 5, 3, 11, 5, GRIS2)
    cuadro(a, 4, 5, 12, 14, CREMA)
    cuadro(a, 4, 5, 12, 6, CAFE)
    cuadro(a, 7, 8, 9, 12, ROJO)
    return a


def riego():
    a = lienzo()
    for y in range(N):
        for x in range(N):
            if 4 <= y <= 12:
                dx = x - 8
                w = 3 + (y - 4) * 0.4
                if abs(dx) <= w and y >= 4:
                    a[y, x] = AZUL
    circulo(a, 6, 8, 1, AZUL2)
    return a


def perimetro():
    a = lienzo()
    cuadro(a, 4, 2, 12, 14, CAFE2)
    cuadro(a, 5, 3, 11, 13, CREMA)
    cuadro(a, 9, 7, 10, 8, CAFE)
    return a


ICONOS = [
    ("NodoCultivo", cultivo),
    ("NodoDoselSombra", dosel),
    ("NodoEstacionCampo", estacion),
    ("NodoMeteorologia", meteo),
    ("NodoCalidadAire", aire),
    ("NodoProceso", proceso),
    ("NodoRiego", riego),
    ("NodoPerimetro", perimetro),
]

ESCALA = 10
PAD = 14
CELDA = N * ESCALA
ANCHO = CELDA * len(ICONOS) + PAD * (len(ICONOS) + 1)
ALTO = CELDA + PAD * 2 + 26

lienzo_final = Image.new("RGB", (ANCHO, ALTO), (255, 255, 255))
draw = ImageDraw.Draw(lienzo_final)
try:
    fuente = ImageFont.truetype("arialbd.ttf", 13)
except Exception:
    fuente = ImageFont.load_default()

for i, (nombre, fn) in enumerate(ICONOS):
    arr = fn()
    im = Image.fromarray(arr, "RGB").resize((CELDA, CELDA), Image.NEAREST)
    x = PAD + i * (CELDA + PAD)
    lienzo_final.paste(im, (x, PAD))
    bbox = draw.textbbox((0, 0), nombre, font=fuente)
    tw = bbox[2] - bbox[0]
    draw.text((x + CELDA / 2 - tw / 2, PAD + CELDA + 6), nombre, fill=(40, 40, 40), font=fuente)

lienzo_final.save("iconos_dispositivos.png")
print("ok", lienzo_final.size)
