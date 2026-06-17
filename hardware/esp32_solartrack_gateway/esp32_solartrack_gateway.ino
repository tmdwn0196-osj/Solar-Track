/*
  SolarTrack Agent ESP32 gateway.

  Required Arduino libraries:
  - ArduinoJson
  - Adafruit INA219
  - OneWire
  - DallasTemperature
  - ESP32Servo
  - AccelStepper

  Safety model:
  - Backend returns a bounded "move" or "hold" command.
  - Emergency stop, limit switches, Wi-Fi failure, backend failure, and invalid
    responses disable motor outputs.
*/

#include <ArduinoJson.h>
#include <HTTPClient.h>
#include <WiFi.h>
#include <Wire.h>
#include <Adafruit_INA219.h>
#include <AccelStepper.h>
#include <DallasTemperature.h>
#include <ESP32Servo.h>
#include <OneWire.h>
#include <math.h>

const char* WIFI_SSID = "CHANGE_ME";
const char* WIFI_PASSWORD = "CHANGE_ME";
const char* API_URL = "http://192.168.0.10:8000/api/hardware/telemetry";

constexpr int PIN_LDR_LEFT = 34;
constexpr int PIN_LDR_RIGHT = 35;
constexpr int PIN_LDR_TOP = 32;
constexpr int PIN_LDR_BOTTOM = 33;
constexpr int PIN_WIND_ANALOG = 39;
constexpr int PIN_ONEWIRE = 4;
constexpr int PIN_SERVO_ELEVATION = 18;
constexpr int PIN_STEPPER_STEP = 26;
constexpr int PIN_STEPPER_DIR = 27;
constexpr int PIN_STEPPER_ENABLE = 25;
constexpr int PIN_LIMIT_AZ_MIN = 13;
constexpr int PIN_LIMIT_AZ_MAX = 14;
constexpr int PIN_LIMIT_EL_MIN = 16;
constexpr int PIN_LIMIT_EL_MAX = 17;
constexpr int PIN_EMERGENCY_STOP = 23;
constexpr int PIN_RAIN = 19;

constexpr float AZIMUTH_MIN = -90.0f;
constexpr float AZIMUTH_MAX = 90.0f;
constexpr float ELEVATION_MIN = 0.0f;
constexpr float ELEVATION_MAX = 70.0f;
constexpr float AZIMUTH_STEPS_PER_DEGREE = 8.8889f;  // 200 steps/rev, 16x microstep, 360 deg.
constexpr unsigned long LOOP_INTERVAL_MS = 2000;

Adafruit_INA219 ina219;
OneWire oneWire(PIN_ONEWIRE);
DallasTemperature panelTempSensor(&oneWire);
Servo elevationServo;
AccelStepper azimuthStepper(AccelStepper::DRIVER, PIN_STEPPER_STEP, PIN_STEPPER_DIR);

float panelAzimuth = 0.0f;
float panelElevation = 35.0f;
float targetAzimuth = 0.0f;
float targetElevation = 35.0f;
unsigned long lastLoopAt = 0;
bool ina219Ready = false;

struct Telemetry {
  float leftLight;
  float rightLight;
  float topLight;
  float bottomLight;
  float voltage;
  float current;
  float panelTemp;
  float batteryVoltage;
  bool rain;
  float windSpeed;
  bool emergencyStop;
};

void setup() {
  Serial.begin(115200);

  pinMode(PIN_STEPPER_ENABLE, OUTPUT);
  pinMode(PIN_LIMIT_AZ_MIN, INPUT_PULLUP);
  pinMode(PIN_LIMIT_AZ_MAX, INPUT_PULLUP);
  pinMode(PIN_LIMIT_EL_MIN, INPUT_PULLUP);
  pinMode(PIN_LIMIT_EL_MAX, INPUT_PULLUP);
  pinMode(PIN_EMERGENCY_STOP, INPUT_PULLUP);
  pinMode(PIN_RAIN, INPUT_PULLUP);
  disableMotors();

  Wire.begin(21, 22);
  ina219Ready = ina219.begin();
  panelTempSensor.begin();

  elevationServo.setPeriodHertz(50);
  elevationServo.attach(PIN_SERVO_ELEVATION, 500, 2400);
  elevationServo.write(elevationToServoAngle(panelElevation));

  azimuthStepper.setMaxSpeed(700);
  azimuthStepper.setAcceleration(250);
  azimuthStepper.setCurrentPosition(azimuthToSteps(panelAzimuth));

  connectWiFi();
}

void loop() {
  azimuthStepper.run();

  if (millis() - lastLoopAt < LOOP_INTERVAL_MS) {
    return;
  }
  lastLoopAt = millis();

  if (isEmergencyStopActive()) {
    holdMotors("emergency_stop");
    return;
  }

  if (WiFi.status() != WL_CONNECTED) {
    holdMotors("wifi_disconnected");
    connectWiFi();
    return;
  }

  Telemetry telemetry = readTelemetry();
  String payload = buildTelemetryPayload(telemetry);
  String response;

  int status = postTelemetry(payload, response);
  Serial.printf("Backend status=%d response=%s\n", status, response.c_str());

  if (status < 200 || status >= 300) {
    holdMotors("backend_error");
    return;
  }

  applyBackendCommand(response);
}

Telemetry readTelemetry() {
  panelTempSensor.requestTemperatures();

  float busVoltage = ina219Ready ? ina219.getBusVoltage_V() : 0.0f;
  float currentA = ina219Ready ? ina219.getCurrent_mA() / 1000.0f : 0.0f;

  return {
    readLdr(PIN_LDR_LEFT),
    readLdr(PIN_LDR_RIGHT),
    readLdr(PIN_LDR_TOP),
    readLdr(PIN_LDR_BOTTOM),
    busVoltage,
    currentA,
    normalizeTemperature(panelTempSensor.getTempCByIndex(0)),
    busVoltage,
    digitalRead(PIN_RAIN) == LOW,
    readWindSpeed(),
    isEmergencyStopActive(),
  };
}

String buildTelemetryPayload(const Telemetry& telemetry) {
  StaticJsonDocument<768> doc;
  doc["deviceId"] = "esp32-solartrack-01";
  doc["leftLight"] = telemetry.leftLight;
  doc["rightLight"] = telemetry.rightLight;
  doc["topLight"] = telemetry.topLight;
  doc["bottomLight"] = telemetry.bottomLight;
  doc["voltage"] = telemetry.voltage;
  doc["current"] = telemetry.current;
  doc["panelTemp"] = telemetry.panelTemp;
  doc["batteryVoltage"] = telemetry.batteryVoltage;
  doc["panelAzimuth"] = panelAzimuth;
  doc["panelElevation"] = panelElevation;
  doc["targetAzimuth"] = targetAzimuth;
  doc["targetElevation"] = targetElevation;
  doc["rain"] = telemetry.rain;
  doc["windSpeed"] = telemetry.windSpeed;
  doc["emergencyStop"] = telemetry.emergencyStop;

  String payload;
  serializeJson(doc, payload);
  return payload;
}

int postTelemetry(const String& payload, String& response) {
  HTTPClient http;
  http.begin(API_URL);
  http.addHeader("Content-Type", "application/json");
  int status = http.POST(payload);
  response = http.getString();
  http.end();
  return status;
}

void applyBackendCommand(const String& response) {
  StaticJsonDocument<1024> doc;
  DeserializationError error = deserializeJson(doc, response);
  if (error) {
    holdMotors("invalid_json");
    return;
  }

  JsonObject command = doc["hardware"]["command"];
  const char* type = command["type"] | "hold";
  const char* reason = command["reason"] | "no_reason";

  if (strcmp(type, "move") != 0) {
    holdMotors(reason);
    return;
  }

  float nextAzimuth = command["azimuthTarget"] | panelAzimuth;
  float nextElevation = command["elevationTarget"] | panelElevation;
  moveToTargets(nextAzimuth, nextElevation);
}

void moveToTargets(float nextAzimuth, float nextElevation) {
  nextAzimuth = constrain(nextAzimuth, AZIMUTH_MIN, AZIMUTH_MAX);
  nextElevation = constrain(nextElevation, ELEVATION_MIN, ELEVATION_MAX);

  if ((nextAzimuth < panelAzimuth && isLimitActive(PIN_LIMIT_AZ_MIN)) ||
      (nextAzimuth > panelAzimuth && isLimitActive(PIN_LIMIT_AZ_MAX)) ||
      (nextElevation < panelElevation && isLimitActive(PIN_LIMIT_EL_MIN)) ||
      (nextElevation > panelElevation && isLimitActive(PIN_LIMIT_EL_MAX))) {
    holdMotors("limit_switch_active");
    return;
  }

  enableMotors();
  targetAzimuth = nextAzimuth;
  targetElevation = nextElevation;
  panelAzimuth = nextAzimuth;
  panelElevation = nextElevation;

  azimuthStepper.moveTo(azimuthToSteps(targetAzimuth));
  elevationServo.write(elevationToServoAngle(targetElevation));
}

void holdMotors(const char* reason) {
  disableMotors();
  Serial.printf("HOLD motors: %s\n", reason);
}

void connectWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start < 15000) {
    delay(500);
    Serial.print(".");
  }
  Serial.println(WiFi.status() == WL_CONNECTED ? "\nWi-Fi connected." : "\nWi-Fi connection failed.");
}

float readLdr(int pin) {
  int raw = analogRead(pin);
  return constrain(raw / 4095.0f * 2.5f, 0.0f, 2.5f);
}

float readWindSpeed() {
  int raw = analogRead(PIN_WIND_ANALOG);
  return raw <= 16 ? 0.0f : raw / 4095.0f * 30.0f;
}

float normalizeTemperature(float value) {
  return value <= -100.0f ? 25.0f : value;
}

bool isEmergencyStopActive() {
  return digitalRead(PIN_EMERGENCY_STOP) == LOW;
}

bool isLimitActive(int pin) {
  return digitalRead(pin) == LOW;
}

void enableMotors() {
  digitalWrite(PIN_STEPPER_ENABLE, LOW);
}

void disableMotors() {
  digitalWrite(PIN_STEPPER_ENABLE, HIGH);
}

long azimuthToSteps(float azimuth) {
  return lround(azimuth * AZIMUTH_STEPS_PER_DEGREE);
}

int elevationToServoAngle(float elevation) {
  return constrain(lround(mapFloat(elevation, ELEVATION_MIN, ELEVATION_MAX, 20.0f, 160.0f)), 20, 160);
}

float mapFloat(float value, float inMin, float inMax, float outMin, float outMax) {
  return (value - inMin) * (outMax - outMin) / (inMax - inMin) + outMin;
}
