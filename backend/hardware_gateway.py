from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


AZIMUTH_LIMIT = (-90.0, 90.0)
ELEVATION_LIMIT = (0.0, 70.0)
MAX_PANEL_TEMP = 65.0
MAX_WIND_SPEED = 10.0
MIN_BATTERY_VOLTAGE = 11.2


def get_hardware_profile() -> dict[str, Any]:
    return {
        "controller": "ESP32",
        "mode": "simulated_gateway",
        "sensors": ["ldr_left", "ldr_right", "ldr_top", "ldr_bottom", "ina219", "ds18b20"],
        "actuators": ["azimuth_stepper", "elevation_servo"],
        "camera": "optional_esp32_cam_or_external_module",
        "limits": {
            "azimuth": {"min": AZIMUTH_LIMIT[0], "max": AZIMUTH_LIMIT[1], "unit": "deg"},
            "elevation": {"min": ELEVATION_LIMIT[0], "max": ELEVATION_LIMIT[1], "unit": "deg"},
            "panelTempMax": {"value": MAX_PANEL_TEMP, "unit": "C"},
            "windSpeedMax": {"value": MAX_WIND_SPEED, "unit": "m/s"},
            "batteryVoltageMin": {"value": MIN_BATTERY_VOLTAGE, "unit": "V"},
        },
        "safety": [
            "LLM never controls motors directly.",
            "Backend validates all requested angles before returning a command.",
            "Rain, high wind, overheating, low battery, and sensor faults force a hold command.",
        ],
    }


def evaluate_hardware_telemetry(payload: dict[str, Any]) -> dict[str, Any]:
    readings = normalize_telemetry(payload)
    safety = evaluate_safety(readings)
    command = build_hardware_command(readings, safety)

    return {
        "receivedAt": datetime.now(timezone.utc).isoformat(),
        "deviceId": readings["deviceId"],
        "accepted": safety["allowed"],
        "safety": safety,
        "command": command,
        "readings": readings,
    }


def normalize_telemetry(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "deviceId": str(payload.get("deviceId") or "esp32-demo"),
        "leftLight": to_float(payload.get("leftLight"), 0),
        "rightLight": to_float(payload.get("rightLight"), 0),
        "topLight": to_float(payload.get("topLight"), 0),
        "bottomLight": to_float(payload.get("bottomLight"), 0),
        "voltage": to_float(payload.get("voltage"), 0),
        "current": to_float(payload.get("current"), 0),
        "panelTemp": to_float(payload.get("panelTemp"), 25),
        "batteryVoltage": to_float(payload.get("batteryVoltage"), 12.0),
        "panelAzimuth": clamp(to_float(payload.get("panelAzimuth"), 0), *AZIMUTH_LIMIT),
        "panelElevation": clamp(to_float(payload.get("panelElevation"), 35), *ELEVATION_LIMIT),
        "targetAzimuth": clamp(to_float(payload.get("targetAzimuth"), 0), *AZIMUTH_LIMIT),
        "targetElevation": clamp(to_float(payload.get("targetElevation"), 35), *ELEVATION_LIMIT),
        "rain": bool(payload.get("rain", False)),
        "windSpeed": to_float(payload.get("windSpeed"), 0),
        "emergencyStop": bool(payload.get("emergencyStop", False)),
    }


def evaluate_safety(readings: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []

    if readings["emergencyStop"]:
        reasons.append("Emergency stop input is active.")
    if readings["rain"]:
        reasons.append("Rain detected; hold motor movement.")
    if readings["windSpeed"] >= MAX_WIND_SPEED:
        reasons.append("Wind speed exceeds motor movement limit.")
    if readings["panelTemp"] >= MAX_PANEL_TEMP:
        reasons.append("Panel temperature exceeds safe threshold.")
    if readings["batteryVoltage"] <= MIN_BATTERY_VOLTAGE:
        reasons.append("Battery voltage is too low for motor movement.")
    if has_sensor_fault(readings):
        reasons.append("One or more light sensor values are outside the expected range.")

    return {
        "allowed": len(reasons) == 0,
        "reasons": reasons or ["Telemetry passed safety checks."],
    }


def build_hardware_command(readings: dict[str, Any], safety: dict[str, Any]) -> dict[str, Any]:
    if not safety["allowed"]:
        return {
            "type": "hold",
            "azimuthTarget": readings["panelAzimuth"],
            "elevationTarget": readings["panelElevation"],
            "reason": "; ".join(safety["reasons"]),
        }

    return {
        "type": "move",
        "azimuthTarget": readings["targetAzimuth"],
        "elevationTarget": readings["targetElevation"],
        "azimuthDelta": round(readings["targetAzimuth"] - readings["panelAzimuth"], 2),
        "elevationDelta": round(readings["targetElevation"] - readings["panelElevation"], 2),
        "reason": "Backend safety gate approved the bounded target angles.",
    }


def has_sensor_fault(readings: dict[str, Any]) -> bool:
    for key in ("leftLight", "rightLight", "topLight", "bottomLight"):
        value = readings[key]
        if value < 0 or value > 2.5:
            return True
    return False


def to_float(value: Any, fallback: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def clamp(value: float, minimum: float, maximum: float) -> float:
    return min(maximum, max(minimum, value))
