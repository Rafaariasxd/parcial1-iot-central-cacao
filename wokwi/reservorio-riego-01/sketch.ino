#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include "mbedtls/md.h"
#include "mbedtls/base64.h"
#include "secrets.h"

#define TRIG_PIN 5
#define ECHO_PIN 18
#define RELE_PIN 2
#define FLUJO_PIN 34
#define ALTURA_TANQUE_CM 100.0

WiFiClientSecure tls;
PubSubClient mqtt(tls);
float nivelTanqueMin = 20.0;
bool bombaActiva = false;
unsigned long bombaFin = 0;

const char* WIFI_SSID = "Wokwi-GUEST";
const char* WIFI_PASS = "";
const char* DPS_HOST  = "global.azure-devices-provisioning.net";

String hubHost;
unsigned long lastSend = 0;
String dpsTopic, dpsPayload;
bool dpsGot = false;

void reportProperty(const char* name, const String& jsonValue) {
  String out = String("{\"") + name + "\":" + jsonValue + "}";
  mqtt.publish("$iothub/twin/PATCH/properties/reported/?$rid=10", out.c_str());
}

void onConnected() {
  reportProperty("bombaActiva", bombaActiva ? "true" : "false");
  reportProperty("nivelTanqueMin", String(nivelTanqueMin, 1));
}

float leerNivel() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  long dur = pulseIn(ECHO_PIN, HIGH, 30000);
  if (dur == 0) return NAN;
  float distancia = dur * 0.0343 / 2.0;
  float nivel = (1.0 - distancia / ALTURA_TANQUE_CM) * 100.0;
  return constrain(nivel, 0.0, 100.0);
}

String urlEncode(const String& s) {
  String out;
  const char* hex = "0123456789ABCDEF";
  for (size_t i = 0; i < s.length(); i++) {
    char c = s[i];
    if (isalnum(c) || c == '-' || c == '_' || c == '.' || c == '~') out += c;
    else { out += '%'; out += hex[(c >> 4) & 0xF]; out += hex[c & 0xF]; }
  }
  return out;
}

String hmacSha256Base64(const String& keyB64, const String& msg) {
  unsigned char key[64]; size_t keyLen = 0;
  mbedtls_base64_decode(key, sizeof(key), &keyLen, (const unsigned char*)keyB64.c_str(), keyB64.length());
  unsigned char mac[32];
  mbedtls_md_hmac(mbedtls_md_info_from_type(MBEDTLS_MD_SHA256), key, keyLen,
                  (const unsigned char*)msg.c_str(), msg.length(), mac);
  unsigned char b64[64]; size_t b64Len = 0;
  mbedtls_base64_encode(b64, sizeof(b64), &b64Len, mac, sizeof(mac));
  return String((char*)b64).substring(0, b64Len);
}

String makeSas(const String& resource, const char* keyB64, const char* policy = nullptr) {
  uint32_t expiry = (uint32_t)time(nullptr) + 3600;
  String enc = urlEncode(resource);
  String sig = urlEncode(hmacSha256Base64(keyB64, enc + "\n" + String(expiry)));
  String tok = "SharedAccessSignature sr=" + enc + "&sig=" + sig + "&se=" + String(expiry);
  if (policy) tok += String("&skn=") + policy;
  return tok;
}
void onMessage(char* topic, byte* payload, unsigned int len) {
  String t(topic), p;
  for (unsigned int i = 0; i < len; i++) p += (char)payload[i];
  if (t.startsWith("$dps/registrations/res/")) {
    dpsTopic = t; dpsPayload = p; dpsGot = true;
    return;
  }
  if (t.startsWith("$iothub/methods/POST/")) {
    int nameStart = String("$iothub/methods/POST/").length();
    String name = t.substring(nameStart, t.indexOf('/', nameStart));
    String rid = t.substring(t.indexOf("$rid=") + 5);
    int status = 404;
    String resp = "{\"error\":\"comando desconocido\"}";
    if (name == "activarBomba") {
      JsonDocument doc;
      deserializeJson(doc, p);
      int minutos = doc["duracionMin"] | 1;
      bombaActiva = true;
      bombaFin = millis() + (unsigned long)minutos * 60000UL;
      digitalWrite(RELE_PIN, HIGH);
      Serial.printf("[CMD] activarBomba %d min\n", minutos);
      status = 200;
      resp = "{\"resultado\":\"bomba encendida " + String(minutos) + " min\"}";
      reportProperty("bombaActiva", "true");
    }
    mqtt.publish(("$iothub/methods/res/" + String(status) + "/?$rid=" + rid).c_str(), resp.c_str());
    return;
  }
  if (t.startsWith("$iothub/twin/PATCH/properties/desired/")) {
    JsonDocument doc;
    if (!deserializeJson(doc, p) && doc["nivelTanqueMin"].is<float>()) {
      nivelTanqueMin = doc["nivelTanqueMin"];
      Serial.printf("[PROP] nivelTanqueMin = %.1f\n", nivelTanqueMin);
      JsonDocument ack;
      ack["nivelTanqueMin"]["value"] = nivelTanqueMin;
      ack["nivelTanqueMin"]["ac"] = 200;
      ack["nivelTanqueMin"]["ad"] = "completed";
      ack["nivelTanqueMin"]["av"] = doc["$version"];
      String out; serializeJson(ack, out);
      mqtt.publish("$iothub/twin/PATCH/properties/reported/?$rid=20", out.c_str());
    }
  }
}

bool waitDps(unsigned long ms) {
  unsigned long t0 = millis();
  while (millis() - t0 < ms) { mqtt.loop(); if (dpsGot) return true; delay(50); }
  return false;
}

bool provision() {
  String regId = IOTC_DEVICE_ID;
  String user = String(IOTC_ID_SCOPE) + "/registrations/" + regId + "/api-version=2019-03-31";
  String pass = makeSas(String(IOTC_ID_SCOPE) + "/registrations/" + regId, IOTC_DEVICE_KEY, "registration");

  mqtt.setServer(DPS_HOST, 8883);
  if (!mqtt.connect(regId.c_str(), user.c_str(), pass.c_str())) {
    Serial.printf("[DPS] fallo MQTT rc=%d\n", mqtt.state());
    return false;
  }
  mqtt.subscribe("$dps/registrations/res/#");
  dpsGot = false;
  mqtt.publish("$dps/registrations/PUT/iotdps-register/?$rid=1", ("{\"registrationId\":\"" + regId + "\"}").c_str());

  for (int i = 0; i < 20; i++) {
    if (!waitDps(8000)) continue;
    dpsGot = false;
    JsonDocument doc;
    deserializeJson(doc, dpsPayload);
    String status = doc["status"] | "";
    if (status == "assigned") {
      hubHost = doc["registrationState"]["assignedHub"].as<String>();
      Serial.println("[DPS] asignado a " + hubHost);
      mqtt.disconnect();
      return true;
    }
    String op = doc["operationId"] | "";
    delay(3000);
    mqtt.publish(("$dps/registrations/GET/iotdps-get-operationstatus/?$rid=2&operationId=" + urlEncode(op)).c_str(), "");
  }
  mqtt.disconnect();
  return false;
}
bool connectHub() {
  String id = IOTC_DEVICE_ID;
  String user = hubHost + "/" + id + "/?api-version=2021-04-12";
  String pass = makeSas(hubHost + "/devices/" + id, IOTC_DEVICE_KEY);
  mqtt.setServer(hubHost.c_str(), 8883);
  if (!mqtt.connect(id.c_str(), user.c_str(), pass.c_str())) {
    Serial.printf("[HUB] fallo MQTT rc=%d\n", mqtt.state());
    return false;
  }
  mqtt.subscribe("$iothub/methods/POST/#");
  mqtt.subscribe("$iothub/twin/PATCH/properties/desired/#");
  onConnected();
  Serial.println("[HUB] conectado a IoT Central");
  return true;
}

void connectWifi() {
  Serial.print("WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASS, 6);
  while (WiFi.status() != WL_CONNECTED) { delay(250); Serial.print("."); }
  Serial.println(" OK");
  configTime(0, 0, "pool.ntp.org", "time.google.com");
  while (time(nullptr) < 1700000000) { delay(200); }
}

void setup() {
  Serial.begin(115200);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(RELE_PIN, OUTPUT);
  connectWifi();
  tls.setInsecure();
  mqtt.setBufferSize(1024);
  mqtt.setCallback(onMessage);
  while (!provision()) { Serial.println("[DPS] reintentando..."); delay(5000); }
}

void loop() {
  if (!mqtt.connected() && !connectHub()) { delay(5000); return; }
  mqtt.loop();
  if (bombaActiva && (long)(millis() - bombaFin) >= 0) {
    bombaActiva = false;
    digitalWrite(RELE_PIN, LOW);
    reportProperty("bombaActiva", "false");
    Serial.println("[BOMBA] apagada");
  }
  if (millis() - lastSend >= 30000) {
    lastSend = millis();
    float nivel = leerNivel();
    if (isnan(nivel)) { Serial.println("[US] sin eco"); return; }
    float caudal = bombaActiva ? analogRead(FLUJO_PIN) * 30.0 / 4095.0 : 0.0;
    JsonDocument doc;
    doc["nivelTanque"] = round(nivel * 10) / 10.0;
    doc["caudal"] = round(caudal * 10) / 10.0;
    String out; serializeJson(doc, out);
    mqtt.publish("devices/" IOTC_DEVICE_ID "/messages/events/", out.c_str());
    Serial.println("[TEL] " + out);
  }
}
