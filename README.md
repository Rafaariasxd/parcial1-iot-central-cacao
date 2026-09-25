# Parcial 1 - IoT Central: Granja y cultivo de cacao

IoT + Cloud + Sistemas Distribuidos · UNAB · 2026-II

Escenario elegido: **5.3 Granja y cultivo de cacao** (sección 5 del enunciado). Flota heterogénea de 10 dispositivos,
cada uno con un origen de envío distinto hacia Azure IoT Central, visible durante una ventana de 4 días no continuos.

## Por qué este escenario

- Indispensables del enunciado ya cubiertos con sentido: humedad de suelo (Lotes 1-3) y un nodo meteorológico
  explícito (Nodo Meteorología, alimentado con datos reales).
- Conectividad justificada: predio rural sin cobertura de campus, salida a Internet por módem 4G/LTE en la caseta
  central de la finca; todos los nodos de campo se conectan por Wi-Fi local a ese módem, no hay red institucional.
- Aprovecha lo ya construido en el Laboratorio 1 (humedad de suelo, nivel de tanque, comando de riego) para el
  nodo de Reservorio/Riego, y el código de MQTT explícito y del SDK de los Laboratorios 2 y 3 para dos de los
  orígenes obligatorios.

## Catálogo de dispositivos (10 filas, 10 orígenes distinguibles)

| # | Dispositivo | Plantilla | Variables | Origen de envío | Sensor / fuente de referencia |
|---|---|---|---|---|---|
| 01 | Lote de cultivo 1 | NodoCultivo | humedad suelo, temp. suelo, EC | Digital Twin / simulador nativo | Sensor capacitivo de humedad de suelo v2.0; DS18B20 (temp., -55…125 °C); sensor EC de suelo (0-20 mS/cm) |
| 02 | Lote de cultivo 2 | NodoCultivo | humedad suelo, temp. canopy | Wokwi (ESP32 + DHT22 + sensor de humedad) | Sensor capacitivo de humedad de suelo v2.0; DHT22 (-40…80 °C, ±0.5 °C) |
| 03 | Lote de cultivo 3 | NodoCultivo | humedad suelo, iluminancia PAR | Python (azure-iot-device, MQTT vía SDK) | Sensor capacitivo de humedad de suelo v2.0; BH1750 (1-65535 lux, aprox. de PAR) |
| 04 | Dosel / sombra | NodoDoselSombra | temp., HR bajo dosel, lux | MQTT explícito (paho, SAS manual) | DHT22; BH1750 |
| 05 | Estación de campo | NodoEstacionCampo | lluvia, humedad foliar | Node.js (azure-iot-device, MQTT) | Pluviómetro de cubeta basculante (tipping bucket, 0.2 mm/pulso); sensor resistivo de humedad foliar |
| 06 | Meteorología del predio | NodoMeteorologia | temp., HR, lluvia, viento, radiación | API pública (Open-Meteo) | Open-Meteo API (sin autenticación), coordenadas del predio |
| 07 | Calidad de aire rural | NodoCalidadAire | PM2.5, HR, AQI | Atlas Weather (Azure Maps Weather API) | Azure Maps Weather / Air Quality REST API (suscripción del curso) |
| 08 | Secado / fermentación | NodoProceso | temp. caja, HR, masa | Python (azure-iot-device, MQTT sobre WebSockets) | DS18B20; DHT22; celda de carga + HX711 (0-5 kg) |
| 09 | Reservorio / riego | NodoRiego | nivel tanque, caudal, bomba on/off | Wokwi (ESP32 + ultrasónico + relé) | Ultrasónico JSN-SR04T (20-600 cm); sensor de flujo YF-S201 (1-30 L/min); relé para la bomba |
| 10 | Perímetro / bodega | NodoPerimetro | puerta, movimiento, temp. bodega | REST manual (HTTPS directo a IoT Hub, sin SDK) | Contacto magnético de puerta; PIR HC-SR501; DS18B20 |

Los 4 orígenes obligatorios del enunciado están presentes (Digital Twin, Wokwi, Python, API pública), más Atlas
Weather. El resto (Node.js, MQTT explícito, MQTT sobre WebSockets, REST manual) son orígenes de la lista abierta,
justificados porque cada uno usa un código o protocolo de envío distinto de los demás.

## Arquitectura de referencia (borrador)

```
[Lotes 1-3, Dosel, Estación, Riego, Perímetro]  --Wi-Fi local-->  [Módem 4G/LTE de la finca]  --Internet-->
                                                                            |
   [Nodo Meteorología <- Open-Meteo]  --Internet directo-->                |
   [Nodo Calidad de Aire <- Azure Maps Weather]  --Internet directo-->     |
                                                                            v
                                                              Azure IoT Central (MQTT/TLS 8883,
                                                              DPS + Device Templates + Rules + Views)
```

Los nodos físicos de campo (nativo, Wokwi, MQTT, Node.js, WebSockets, REST manual) comparten el módem 4G/LTE de la
finca. Los dos puentes de API (meteorología y calidad de aire) corren en un portátil/VM con salida a Internet
propia, sin pasar por el módem de campo.

## Estado actual

- Escenario elegido y catálogo de 10 orígenes (`README`, `documento/`).
- 8 plantillas DTDL en `modelo/`, publicadas en la aplicación de IoT Central.
- Los 10 dispositivos creados y asignados a su plantilla.
- 8 orígenes enviando: simulador nativo, Python SDK, MQTT explícito, Node.js, Open-Meteo, Atlas Weather (Azure Maps),
  Python sobre WebSockets y REST manual. Los scripts están en `scripts/` y corren como servicios en una VM.
- Panel `Cuarto de control - Finca Cacao` creado con `scripts/panel_api.py` (KPIs, gráficas, conteo de flota, zonas y alertas).
- Dos reglas con correo: caja de fermentación mayor a 42 °C y bodega mayor a 28 °C.
- Telemetría de los días 22, 23 y 24 de septiembre exportada en `datos/` (`scripts/exportar_datos.py`) con gráficas
  en `evidencias/graficas/` (`scripts/graficas.py`).
- Proyectos de Wokwi de `lote-cultivo-02` y `reservorio-riego-01` en `wokwi/`. El archivo `secrets.h` no se sube:
  se copia desde `secrets.h.example` con el identificador del dispositivo y su clave derivada.
- Documento del parcial en `documento/`.

Pendiente: conectar los dos ESP32 de Wokwi, capturas del panel, cuarto día de telemetría y sustentación.

## Cómo correr un origen

Las variables `IOTC_ID_SCOPE` e `IOTC_GROUP_KEY` se leen del entorno. La clave de cada dispositivo se deriva con
HMAC-SHA256 de su identificador (`scripts/comun.py`). Ejemplo:

    cd scripts
    python lote03_python_sdk.py
