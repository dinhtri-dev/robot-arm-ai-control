#include <WiFi.h>
#if __has_include("config.local.h")
#include "config.local.h"
#endif
#include "config.example.h"
#include <WebServer.h>
#include "web_page.h"
#include <HardwareSerial.h>

/* ================= WIFI ================= */
const char* ssid = YEAR2_WIFI_SSID;
const char* password = YEAR2_WIFI_PASSWORD;
/* ================= UART TO UNO ================= */
// ESP32-C3 RX nhận từ UNO TX
// ESP32-C3 TX gửi sang UNO RX
#define ESP_RX_PIN 20
#define ESP_TX_PIN 21

#define UNO_BAUD 115200

HardwareSerial UnoSerial(1);
WebServer server(80);

/* ================= DATA FROM UNO ================= */
String unoRxLine = "";

String lastUnoLine   = "Chua co du lieu tu Uno";
String lastEncLine   = "Chua co du lieu AS5600";
String lastAngleLine = "A,0,0,0";
String lastCmdSent   = "None";

unsigned long lastUnoDataMs = 0;

/* ================= JSON ESCAPE ================= */
String jsonEscape(String s) {
  s.replace("\\", "\\\\");
  s.replace("\"", "\\\"");
  s.replace("\n", "\\n");
  s.replace("\r", "");
  return s;
}

/* ================= SEND TO UNO ================= */
void sendGcode(String cmd) {
  UnoSerial.print(cmd);
  UnoSerial.print('\n');

  lastCmdSent = cmd;

  Serial.print("Send G-code to UNO: ");
  Serial.println(cmd);
}

void sendKey(char c) {
  UnoSerial.write(c);

  lastCmdSent = String(c);

  Serial.print("Send key to UNO: ");
  Serial.println(c);
}

/* ================= READ FROM UNO ================= */
void readUnoSerial() {
  while (UnoSerial.available() > 0) {
    char c = UnoSerial.read();

    if (c == '\n' || c == '\r') {
      if (unoRxLine.length() > 0) {
        lastUnoLine = unoRxLine;
        lastUnoDataMs = millis();

        Serial.print("UNO >> ");
        Serial.println(unoRxLine);

        // Dòng encoder chi tiết từ Uno
        if (unoRxLine.startsWith("ENC")) {
          lastEncLine = unoRxLine;
        }

        // Dòng góc dành cho Unity:
        // A,baseDeg,lowDeg,highDeg
        if (unoRxLine.startsWith("A,")) {
          lastAngleLine = unoRxLine;
        }

        unoRxLine = "";
      }
    } else {
      if (unoRxLine.length() < 300) {
        unoRxLine += c;
      } else {
        unoRxLine = "";
      }
    }
  }
}

/* ================= HTML PAGE ================= */
String htmlPage() {
  String page = YEAR2_WEB_PAGE;

  return page;
}

/* ================= WEB HANDLERS ================= */
void handleRoot() {
  server.send(200, "text/html", htmlPage());
}

void handleGcode() {
  if (!YEAR2_ENABLE_REMOTE_CONTROL) {
    server.send(503, "text/plain", "Remote control disabled in source archive");
    return;
  }
  if (server.hasArg("line")) {
    String line = server.arg("line");
    sendGcode(line);
    server.send(200, "text/plain", "OK: " + line);
  } else {
    server.send(400, "text/plain", "Missing line");
  }
}

void handleKey() {
  if (!YEAR2_ENABLE_REMOTE_CONTROL) {
    server.send(503, "text/plain", "Remote control disabled in source archive");
    return;
  }
  String val = "";

  if (server.hasArg("val")) {
    val = server.arg("val");
  } else if (server.hasArg("key")) {
    val = server.arg("key");
  }

  if (val.length() > 0) {
    char c = val.charAt(0);

    if (
      c == 'w' || c == 's' ||
      c == 'q' || c == 'e' ||
      c == 'a' || c == 'd' ||
      c == 'x' || c == 'o' || c == 'p' || c == ' '
    ) {
      sendKey(c);
      server.send(200, "text/plain", "OK KEY: " + String(c));
      return;
    }
  }

  server.send(400, "text/plain", "Missing key");
}


void handleCmd() {
  if (!YEAR2_ENABLE_REMOTE_CONTROL) {
    server.send(503, "text/plain", "Remote control disabled in source archive");
    return;
  }
  String val = "";

  if (server.hasArg("key")) {
    val = server.arg("key");
  } else if (server.hasArg("val")) {
    val = server.arg("val");
  }

  if (val.length() > 0) {
    char c = val.charAt(0);

    if (
      c == 'w' || c == 's' ||
      c == 'q' || c == 'e' ||
      c == 'a' || c == 'd' ||
      c == 'x' || c == 'o' || c == 'p' || c == ' '
    ) {
      sendKey(c);
      server.send(200, "text/plain", "OK CMD: " + String(c));
      return;
    }
  }

  server.send(400, "text/plain", "Missing key");
}

void handleStatus() {
  String json = "{";
  json += "\"encoder\":\"" + jsonEscape(lastEncLine) + "\",";
  json += "\"angle\":\"" + jsonEscape(lastAngleLine) + "\",";
  json += "\"uno\":\"" + jsonEscape(lastUnoLine) + "\",";
  json += "\"cmd\":\"" + jsonEscape(lastCmdSent) + "\",";
  json += "\"age_ms\":" + String(millis() - lastUnoDataMs);
  json += "}";

  server.send(200, "application/json", json);
}

/* ================= SETUP ================= */
void setup() {
  Serial.begin(115200);
  delay(1000);

  UnoSerial.begin(UNO_BAUD, SERIAL_8N1, ESP_RX_PIN, ESP_TX_PIN);

  WiFi.mode(WIFI_STA);
  if (!YEAR2_ENABLE_REMOTE_CONTROL) {
    Serial.println("Wi-Fi/HTTP disabled in source archive");
    return;
  }
  WiFi.begin(ssid, password);

  WiFi.setTxPower(WIFI_POWER_8_5dBm);

  Serial.print("Dang ket noi WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("WiFi OK");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());

  server.on("/", handleRoot);
  server.on("/gcode", HTTP_POST, handleGcode);
  server.on("/key", HTTP_POST, handleKey);
  server.on("/cmd", HTTP_POST, handleCmd);
  server.on("/status", handleStatus);

  server.begin();
  Serial.println("Web server started");
}

/* ================= LOOP ================= */
void loop() {
  if (YEAR2_ENABLE_REMOTE_CONTROL) server.handleClient();
  readUnoSerial();
}