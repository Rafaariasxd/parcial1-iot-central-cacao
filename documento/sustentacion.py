import os

import pandas as pd
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

RAIZ = r"D:\Parcial1-IoT"
VERDE = RGBColor(0x2F, 0x6F, 0x4E)

doc = Document()
sec = doc.sections[0]
for lado in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
    setattr(sec, lado, Cm(1.8))

estilo = doc.styles["Normal"]
estilo.font.name = "Calibri"
estilo.font.size = Pt(10.5)
for nombre, tam in (("Heading 1", 15), ("Heading 2", 12)):
    h = doc.styles[nombre]
    h.font.name = "Calibri"
    h.font.size = Pt(tam)
    h.font.color.rgb = VERDE


def sombrear(celda, color):
    tc = celda._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear")
    sh.set(qn("w:color"), "auto")
    sh.set(qn("w:fill"), color)
    tc.append(sh)


def tabla(encabezados, filas, anchos=None, tam=9.5):
    t = doc.add_table(rows=1, cols=len(encabezados))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, e in enumerate(encabezados):
        c = t.rows[0].cells[i]
        r = c.paragraphs[0].add_run(e)
        r.bold = True
        r.font.size = Pt(tam)
        r.font.color.rgb = RGBColor(255, 255, 255)
        sombrear(c, "2F6F4E")
    for fila in filas:
        celdas = t.add_row().cells
        for i, v in enumerate(fila):
            celdas[i].paragraphs[0].add_run(str(v)).font.size = Pt(tam)
    if anchos:
        for fila in t.rows:
            for i, a in enumerate(anchos):
                fila.cells[i].width = Cm(a)
    doc.add_paragraph()


def parrafo(texto):
    doc.add_paragraph(texto)


def punto(texto):
    doc.add_paragraph(texto, style="List Bullet")


# Portada corta
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Hoja de sustentación – Parcial 1 IoT Central")
r.bold = True
r.font.size = Pt(19)
r.font.color.rgb = VERDE
p2 = doc.add_paragraph()
p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
r2 = p2.add_run("Granja y cultivo de cacao – San Vicente de Chucurí · Rafael Antonio Arias Monsalve")
r2.font.size = Pt(11)
doc.add_paragraph()

doc.add_heading("El escenario en tres frases", 1)
parrafo(
    "Es una finca de cacao en San Vicente de Chucurí, sin red institucional: todo sale por un módem 4G/LTE de la "
    "caseta. Son 10 dispositivos, cada uno con una forma distinta de mandar datos a Azure IoT Central, y todos "
    "comparten la app parcial1-granja-cacao (parcial1-granja-unab-rarias.azureiotcentral.com)."
)

doc.add_heading("Catálogo de dispositivos y orígenes", 1)
tabla(
    ["#", "Dispositivo", "Origen"],
    [
        ["01", "lote-cultivo-01", "Digital Twin / simulador nativo de IoT Central"],
        ["02", "lote-cultivo-02", "ESP32 en Wokwi (pendiente de conectar)"],
        ["03", "lote-cultivo-03", "Python con azure-iot-device (MQTT)"],
        ["04", "dosel-sombra-01", "Python con paho-mqtt, SAS manual"],
        ["05", "estacion-campo-01", "Node.js con azure-iot-device"],
        ["06", "meteorologia-predio-01", "API pública Open-Meteo"],
        ["07", "calidad-aire-01", "Atlas Weather / Azure Maps Weather API"],
        ["08", "secado-fermentacion-01", "Python con azure-iot-device sobre WebSockets"],
        ["09", "reservorio-riego-01", "ESP32 en Wokwi (pendiente de conectar)"],
        ["10", "perimetro-bodega-01", "REST manual: HTTPS directo al IoT Hub"],
    ],
    [1.3, 4.5, 11],
)

doc.add_heading("Dónde está corriendo cada cosa", 1)
punto("7 de los 10 orígenes corren solos, 24/7, como servicios systemd en una VM de Azure (vm-lab2-python).")
punto("lote-cultivo-01 lo genera el simulador nativo de IoT Central, no un script propio.")
punto("Los dos de Wokwi (lote-cultivo-02 y reservorio-riego-01) están escritos y compilan con PlatformIO, pero "
      "no se han corrido en vivo todavía; el código está en la carpeta wokwi/ del repositorio.")

doc.add_heading("Telemetría en vivo", 1)
resumen = pd.read_csv(os.path.join(RAIZ, "datos", "resumen_por_dia.csv"))
dias = sorted(resumen["dia"].unique())
parrafo(
    f"Hay datos en {len(dias)} días no continuos, del {dias[0][8:10]}/{dias[0][5:7]} al "
    f"{dias[-1][8:10]}/{dias[-1][5:7]} de septiembre (piden mínimo 4). Cada dispositivo tiene su propio ciclo de "
    "apagón simulado, así que en el Explorador de datos de IoT Central se ven huecos reales de desconexión, no "
    "una línea continua."
)

doc.add_heading("Cuarto de control", 1)
punto("Panel \"Cuarto de control - Finca Cacao\": conteo de flota, 7 KPI (humedad de suelo, tanque, caja, PM2.5, "
      "lluvia), 12 gráficas de línea, esquema de zonas y bloque de alertas.")
punto("2 reglas activas con envío de correo: caja de fermentación > 42 °C y bodega > 28 °C.")
punto("El panel se armó con un script (panel_api.py) que usa la API de IoT Central, no a mano tile por tile.")

doc.add_heading("Documento y repositorio", 1)
punto("Documento completo: documento/Parcial1_IoT_Central.pdf (portada, historial de versiones, plano de la finca, "
      "arquitectura, catálogo, plantillas DTDL, gráficas con análisis).")
punto("Repositorio: github.com/Rafaariasxd/parcial1-iot-central-cacao")

doc.add_heading("Si preguntan por qué falta algo", 1)
punto("¿Por qué no están los dos de Wokwi en vivo? El código ya está y compila; falta correrlo en el navegador o "
      "en VS Code el día de la sustentación.")
punto("¿Por qué calidad-aire-01 no manda datos el 28 y 29? La clave de Azure Maps Weather que compartió el "
      "profesor para el curso empezó a devolver \"401 Unauthorized\" desde ayer; no es un error del script, es la "
      "clave del curso.")
punto("¿Por qué el lote 1 se ve tan brusco en las gráficas de humedad y temperatura de suelo? Porque usa el "
      "simulador nativo de IoT Central, que genera valores al azar en todo el rango permitido; el lote 3, que "
      "corre el script propio, se mueve en un rango realista.")

doc.add_heading("Para correr algo en vivo", 1)
parrafo(
    "Desde D:\\Parcial1-IoT\\scripts, con IOTC_ID_SCOPE e IOTC_GROUP_KEY como variables de entorno "
    "(están en .secrets\\iotc.env): python lote03_python_sdk.py conecta un dispositivo nuevo y en IoT Central se "
    "ve pasar de Registrado a Conectado en segundos."
)

doc.save(os.path.join(RAIZ, "documento", "Sustentacion_Parcial1_IoT.docx"))
print("listo")
