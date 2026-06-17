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
            "LLM은 모터를 직접 제어하지 않습니다.",
            "백엔드는 명령을 반환하기 전에 모든 목표 각도를 검증합니다.",
            "강수, 강풍, 과열, 저전압, 센서 이상이 있으면 보류 명령을 반환합니다.",
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
        reasons.append("비상 정지 입력이 활성화되었습니다.")
    if readings["rain"]:
        reasons.append("강수가 감지되어 모터 동작을 보류합니다.")
    if readings["windSpeed"] >= MAX_WIND_SPEED:
        reasons.append("풍속이 모터 동작 제한값을 초과했습니다.")
    if readings["panelTemp"] >= MAX_PANEL_TEMP:
        reasons.append("패널 온도가 안전 기준을 초과했습니다.")
    if readings["batteryVoltage"] <= MIN_BATTERY_VOLTAGE:
        reasons.append("배터리 전압이 모터 동작 기준보다 낮습니다.")
    if has_sensor_fault(readings):
        reasons.append("하나 이상의 조도 센서 값이 예상 범위를 벗어났습니다.")

    return {
        "allowed": len(reasons) == 0,
        "reasons": reasons or ["텔레메트리가 안전 검사를 통과했습니다."],
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
        "reason": "백엔드 안전 게이트가 제한 범위 내 목표 각도를 승인했습니다.",
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
