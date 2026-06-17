/*
  SolarTrack Agent ESP32 gateway example.

  This sketch is a communication contract stub. It posts sensor telemetry to the
  FastAPI backend and expects a bounded "move" or "hold" command in response.
  Replace placeholder sensor reads and motor handlers only after bench testing.
*/

#include <HTTPClient.h>
#include <WiFi.h>

const char* WIFI_SSID = "CHANGE_ME";
const char* WIFI_PASSWORD = "CHANGE_ME";
const char* API_URL = "http://192.168.0.10:8000/api/hardware/telemetry";

void setup() {
  Serial.begin(115200);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nSolarTrack ESP32 gateway connected.");
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected. Holding motors.");
    holdMotors("wifi_disconnected");
    delay(2000);
    return;
  }

  String payload = buildTelemetryPayload();
  HTTPClient http;
  http.begin(API_URL);
  http.addHeader("Content-Type", "application/json");

  int status = http.POST(payload);
  String response = http.getString();
  http.end();

  Serial.printf("Backend status=%d response=%s\n", status, response.c_str());

  if (status < 200 || status >= 300) {
    holdMotors("backend_error");
  }

  delay(2000);
}

String buildTelemetryPayload() {
  // Placeholder values. Replace with LDR/BH1750, INA219, and DS18B20 reads.
  return "{"
    "\"deviceId\":\"esp32-demo\","
    "\"leftLight\":1.0,"
    "\"rightLight\":1.1,"
    "\"topLight\":1.2,"
    "\"bottomLight\":1.0,"
    "\"voltage\":5.1,"
    "\"current\":0.4,"
    "\"panelTemp\":32.0,"
    "\"batteryVoltage\":12.3,"
    "\"panelAzimuth\":0,"
    "\"panelElevation\":35,"
    "\"targetAzimuth\":5,"
    "\"targetElevation\":37,"
    "\"rain\":false,"
    "\"windSpeed\":2.0,"
    "\"emergencyStop\":false"
  "}";
}

void holdMotors(const char* reason) {
  // Keep motor outputs disabled until backend command parsing is implemented.
  Serial.printf("HOLD motors: %s\n", reason);
}
