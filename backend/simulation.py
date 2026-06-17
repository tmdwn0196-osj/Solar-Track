from __future__ import annotations

from datetime import datetime, timezone
from math import pi, sin
from typing import Any

from backend.vision_dataset import build_virtual_vision_result


LOCATIONS: dict[str, dict[str, Any]] = {
    "seoul": {
        "id": "seoul",
        "name": "서울",
        "latitude": 37.5665,
        "longitude": 126.978,
    },
    "busan": {
        "id": "busan",
        "name": "부산",
        "latitude": 35.1796,
        "longitude": 129.0756,
    },
    "jeju": {
        "id": "jeju",
        "name": "제주",
        "latitude": 33.4996,
        "longitude": 126.5312,
    },
    "daejeon": {
        "id": "daejeon",
        "name": "대전",
        "latitude": 36.3504,
        "longitude": 127.3845,
    },
}


SCENARIO_WEATHER: dict[str, dict[str, Any]] = {
    "normal": {"cloudCover": 18, "rain": False, "temperature": 25, "windSpeed": 2.1},
    "cloudy": {"cloudCover": 82, "rain": False, "temperature": 24, "windSpeed": 3.2},
    "shade": {"cloudCover": 24, "rain": False, "temperature": 27, "windSpeed": 2.4},
    "soiling": {"cloudCover": 20, "rain": False, "temperature": 26, "windSpeed": 2.0},
    "overheat": {"cloudCover": 12, "rain": False, "temperature": 36, "windSpeed": 1.8},
    "charging_issue": {"cloudCover": 22, "rain": False, "temperature": 25, "windSpeed": 2.2},
    "overload": {"cloudCover": 18, "rain": False, "temperature": 25, "windSpeed": 2.1},
}


def calculate_weather(scenario: str, location_id: str = "seoul", source: str = "scenario") -> dict[str, Any]:
    location = LOCATIONS.get(location_id, LOCATIONS["seoul"])
    values = dict(SCENARIO_WEATHER[scenario])

    if scenario == "cloudy":
        values["cloudCover"] = max(values["cloudCover"], 82)
    if scenario == "overheat":
        values["temperature"] = max(values["temperature"], 36)
        values["windSpeed"] = min(values["windSpeed"], 2.4)

    tracking_limited = values["rain"] or values["cloudCover"] >= 75 or values["windSpeed"] >= 10

    return {
        "label": get_weather_label(values),
        "cloudCover": round(values["cloudCover"]),
        "rain": values["rain"],
        "temperature": round(values["temperature"], 1),
        "windSpeed": round(values["windSpeed"], 1),
        "trackingLimited": tracking_limited,
        "reason": get_weather_reason(values, tracking_limited),
        "locationName": location["name"],
        "source": source,
        "collectedAt": datetime.now(timezone.utc).isoformat(),
        "agentNote": get_agent_note(source, location["name"], scenario, tracking_limited),
    }


def infer_vision(scenario: str) -> dict[str, Any]:
    if scenario == "cloudy":
        return {
            "cloudDetected": True,
            "soilingDetected": False,
            "shadeDetected": False,
            **build_virtual_vision_result(
                scenario,
                "구름으로 인한 일시적 광량 저하가 감지되었습니다.",
            ),
        }
    if scenario == "soiling":
        return {
            "cloudDetected": False,
            "soilingDetected": True,
            "shadeDetected": False,
            **build_virtual_vision_result(
                scenario,
                "패널 표면 오염 후보가 감지되었습니다.",
            ),
        }
    if scenario == "shade":
        return {
            "cloudDetected": False,
            "soilingDetected": False,
            "shadeDetected": True,
            **build_virtual_vision_result(
                scenario,
                "패널 주변 부분 음영 후보가 감지되었습니다.",
            ),
        }
    return {
        "cloudDetected": False,
        "soilingDetected": False,
        "shadeDetected": False,
        **build_virtual_vision_result(scenario, "비전 감지 결과가 안정적입니다."),
    }


def simulate_step(state: dict[str, Any]) -> dict[str, Any]:
    next_time = 6 if state["time"] >= 18 else round(state["time"] + 0.1, 1)
    prepared = recalculate_state({**state, "time": next_time, "phase": "weather_check"})
    tracking = run_tracking_step(prepared)
    updated = recalculate_state({**prepared, **tracking})

    history = [
        *updated.get("history", []),
        {
            "time": updated["time"],
            "fixedPower": updated["fixedPower"],
            "trackedPower": updated["trackedPower"],
        },
    ][-60:]
    log_message = f"{format_time(updated['time'])} {updated.get('phaseReason') or '상태를 갱신했습니다.'}"

    return {
        **updated,
        "history": history,
        "logs": append_log(updated.get("logs", []), log_message),
    }


def recalculate_state(state: dict[str, Any]) -> dict[str, Any]:
    scenario = state["scenario"]
    weather = state.get("weather") or calculate_weather(scenario, state.get("weatherLocationId", "seoul"))
    vision = infer_vision(scenario)
    sun = calculate_sun_position(state["time"])
    panel_temp = 68 if scenario == "overheat" else weather["temperature"] + 5
    errors = calculate_angle_errors(
        sun["sunAzimuth"],
        sun["sunElevation"],
        state["panelAzimuth"],
        state["panelElevation"],
    )
    sensors = calculate_virtual_sensors(
        sun["sunAzimuth"],
        sun["sunElevation"],
        state["panelAzimuth"],
        state["panelElevation"],
        scenario,
    )
    tracked = calculate_power(
        sun["sunAzimuth"],
        sun["sunElevation"],
        state["panelAzimuth"],
        state["panelElevation"],
        panel_temp,
        scenario,
        weather,
    )
    fixed = calculate_power(
        sun["sunAzimuth"],
        sun["sunElevation"],
        0,
        35,
        panel_temp,
        scenario,
        weather,
    )
    next_state = {
        **state,
        **sun,
        **errors,
        **sensors,
        "weather": weather,
        "vision": vision,
        "panelTemp": panel_temp,
        "voltage": tracked["voltage"],
        "current": tracked["current"],
        "power": tracked["power"],
        "fixedPower": fixed["power"],
        "trackedPower": tracked["power"],
        "powerGainRate": calculate_power_gain(fixed["power"], tracked["power"]),
        "powerBreakdown": tracked["powerBreakdown"],
        "batteryVoltage": 12.0 if scenario == "charging_issue" else round(12.1 + tracked["power"] / 35, 3),
    }

    return {**next_state, **diagnose_state(next_state)}


def run_tracking_step(state: dict[str, Any]) -> dict[str, Any]:
    errors = calculate_angle_errors(
        state["sunAzimuth"],
        state["sunElevation"],
        state["panelAzimuth"],
        state["panelElevation"],
    )
    azimuth_error = errors["azimuthError"]
    elevation_error = errors["elevationError"]

    if not state["autoTracking"]:
        return {
            "panelAzimuth": state["panelAzimuth"],
            "panelElevation": state["panelElevation"],
            **errors,
            "phase": "idle",
            "phaseReason": "자동 추적이 꺼져 있어 현재 패널 각도를 유지합니다.",
        }

    if state["weather"]["trackingLimited"] or state["vision"]["cloudDetected"]:
        reason = (
            "기상 조건으로 인해 추적을 보류합니다."
            if state["weather"]["trackingLimited"]
            else "비전 결과에서 구름이 감지되어 각도 보정을 보류합니다."
        )
        return {
            "panelAzimuth": state["panelAzimuth"],
            "panelElevation": state["panelElevation"],
            **errors,
            "phase": "hold",
            "phaseReason": reason,
        }

    if abs(azimuth_error) > 3:
        return {
            "panelAzimuth": clamp(state["panelAzimuth"] + (3 if azimuth_error > 0 else -3), -90, 90),
            "panelElevation": state["panelElevation"],
            **errors,
            "phase": "azimuth_align",
            "phaseReason": f"방위각 오차가 {azimuth_error:.1f}°라서 방위각을 먼저 정렬합니다.",
        }

    if abs(elevation_error) > 2:
        return {
            "panelAzimuth": state["panelAzimuth"],
            "panelElevation": clamp(state["panelElevation"] + (2 if elevation_error > 0 else -2), 0, 70),
            **errors,
            "phase": "elevation_align",
            "phaseReason": f"고도각 오차 {elevation_error:.1f}°를 보정합니다.",
        }

    return {
        "panelAzimuth": state["panelAzimuth"],
        "panelElevation": state["panelElevation"],
        **errors,
        "phase": "power_verify",
        "phaseReason": "패널 각도가 허용 범위에 들어와 발전량 개선률을 검증합니다.",
    }


def diagnose_state(state: dict[str, Any]) -> dict[str, Any]:
    if state["phase"] == "idle":
        return {
            "diagnosis": "시뮬레이션 대기",
            "action": "시작 버튼을 눌러 태양 추적 흐름을 확인하세요.",
            "riskLevel": "normal",
            "diagnosisReasons": ["아직 추적 루프가 실행되지 않았습니다."],
        }
    if state["scenario"] == "overheat" or state["panelTemp"] >= 65:
        return {
            "diagnosis": "패널 과열",
            "action": "추적을 제한하고 패널 통풍 상태를 먼저 확인하세요.",
            "riskLevel": "danger",
            "diagnosisReasons": [
                f"패널 온도 {state['panelTemp']:.1f} °C",
                "고온은 효율 저하와 안전 보류 조건이 될 수 있습니다.",
            ],
        }
    if state["weather"]["trackingLimited"] or state["vision"]["cloudDetected"]:
        return {
            "diagnosis": "기상 영향으로 인한 일시적 출력 저하",
            "action": "광량이 불안정한 동안 추적을 보류하고, 이후 발전량을 다시 비교하세요.",
            "riskLevel": "warning",
            "diagnosisReasons": [
                f"구름량 {state['weather']['cloudCover']}%",
                "비전 또는 기상 정보가 불안정한 광량을 나타냅니다.",
            ],
        }
    if state["lightAverage"] < 0.55:
        return {
            "diagnosis": "광량 부족",
            "action": "광량이 회복된 뒤 추적 성능을 판단하세요.",
            "riskLevel": "warning",
            "diagnosisReasons": [
                f"평균 조도 {state['lightAverage']:.2f}",
                "신뢰할 만한 발전량 비교를 하기에는 센서 평균값이 낮습니다.",
            ],
        }
    if state["phase"] == "power_verify" and state["powerGainRate"] >= 5:
        return {
            "diagnosis": "추적 보정 성공",
            "action": "패널 정렬 후 고정식 대비 출력이 개선되었습니다.",
            "riskLevel": "normal",
            "diagnosisReasons": [
                f"발전량 개선률 {state['powerGainRate']:.1f}%",
                "추적식 출력이 고정식보다 5% 이상 높습니다.",
            ],
        }
    if state["vision"]["soilingDetected"] or state["scenario"] == "soiling":
        return {
            "diagnosis": "패널 오염 의심",
            "action": "패널 표면을 청소한 뒤 비슷한 기상 조건에서 출력을 다시 비교하세요.",
            "riskLevel": "warning",
            "diagnosisReasons": [
                "비전 결과에서 표면 오염 후보가 감지되었습니다.",
                f"시나리오 계수 {state['powerBreakdown']['scenarioFactor']:.2f}",
            ],
        }
    if state["vision"]["shadeDetected"] or state["scenario"] == "shade":
        return {
            "diagnosis": "부분 음영 의심",
            "action": "주변 구조물과 시간대별 그림자 패턴을 확인하세요.",
            "riskLevel": "warning",
            "diagnosisReasons": [
                "비전 결과에서 부분 음영 후보가 감지되었습니다.",
                f"평균 조도 {state['lightAverage']:.2f}",
            ],
        }
    if state["scenario"] == "charging_issue":
        return {
            "diagnosis": "충전 계통 문제",
            "action": "충전 컨트롤러, 배터리 연결, 배선 상태를 점검하세요.",
            "riskLevel": "warning",
            "diagnosisReasons": [
                f"추적식 발전량 {state['trackedPower']:.2f} W",
                f"배터리 전압 {state['batteryVoltage']:.1f} V",
            ],
        }
    if state["scenario"] == "overload":
        return {
            "diagnosis": "부하 과다",
            "action": "소비 전력을 줄이거나 배터리 방전 상태를 확인하세요.",
            "riskLevel": "warning",
            "diagnosisReasons": [
                "현재 발전량보다 부하가 큰 상황으로 가정됩니다.",
                f"추적식 발전량 {state['trackedPower']:.2f} W",
            ],
        }
    if state["phase"] in {"azimuth_align", "elevation_align", "weather_check"}:
        return {
            "diagnosis": "순차제어 진행 중",
            "action": "방위각과 고도각 정렬을 계속한 뒤 발전량을 검증하세요.",
            "riskLevel": "normal",
            "diagnosisReasons": [
                f"방위각 오차 {state['azimuthError']:.1f}°",
                f"고도각 오차 {state['elevationError']:.1f}°",
            ],
        }

    return {
        "diagnosis": "추적 상태 확인 중",
        "action": "시뮬레이션을 계속 실행해 비교 데이터를 더 수집하세요.",
        "riskLevel": "normal",
        "diagnosisReasons": [
            f"발전량 개선률 {state['powerGainRate']:.1f}%",
            "추가 시뮬레이션 샘플이 필요합니다.",
        ],
    }


def calculate_sun_position(time: float) -> dict[str, float]:
    clamped_time = max(6, min(18, time))
    sun_azimuth = ((clamped_time - 12) / 6) * 90
    normalized_elevation = sin(((clamped_time - 6) / 12) * pi)
    sun_elevation = max(0, normalized_elevation * 70)
    return {"sunAzimuth": round(sun_azimuth, 1), "sunElevation": round(sun_elevation, 1)}


def calculate_virtual_sensors(
    sun_azimuth: float,
    sun_elevation: float,
    panel_azimuth: float,
    panel_elevation: float,
    scenario: str,
) -> dict[str, float]:
    azimuth_diff = sun_azimuth - panel_azimuth
    elevation_diff = sun_elevation - panel_elevation
    base_light = get_light_factor(scenario)
    left_light = round(base_light + max(0, -azimuth_diff) / 100, 2)
    right_light = round(base_light + max(0, azimuth_diff) / 100, 2)
    top_light = round(base_light + max(0, elevation_diff) / 100, 2)
    bottom_light = round(base_light + max(0, -elevation_diff) / 100, 2)
    return {
        "leftLight": left_light,
        "rightLight": right_light,
        "topLight": top_light,
        "bottomLight": bottom_light,
        "lightAverage": round((left_light + right_light + top_light + bottom_light) / 4, 2),
    }


def calculate_power(
    sun_azimuth: float,
    sun_elevation: float,
    panel_azimuth: float,
    panel_elevation: float,
    panel_temp: float,
    scenario: str,
    weather: dict[str, Any],
) -> dict[str, Any]:
    max_power = 10
    azimuth_error = abs(sun_azimuth - panel_azimuth)
    elevation_error = abs(sun_elevation - panel_elevation)
    angle_factor = max(0, 1 - (azimuth_error + elevation_error) / 140)
    sun_factor = max(0, sun_elevation / 70)
    scenario_factor = get_scenario_factor(scenario)
    temp_factor = get_temp_factor(panel_temp)
    weather_factor = get_weather_factor(weather)
    power = max_power * sun_factor * angle_factor * scenario_factor * temp_factor * weather_factor
    voltage = 6 * max(0.42, sun_factor)
    current = power / voltage if voltage > 0 else 0
    return {
        "power": round(power, 2),
        "voltage": round(voltage, 2),
        "current": round(current, 2),
        "powerBreakdown": {
            "maxPower": max_power,
            "sunFactor": round(sun_factor, 2),
            "angleFactor": round(angle_factor, 2),
            "scenarioFactor": round(scenario_factor, 2),
            "tempFactor": round(temp_factor, 2),
            "weatherFactor": round(weather_factor, 2),
        },
    }


def calculate_power_gain(fixed_power: float, tracked_power: float) -> float:
    if fixed_power <= 0:
        return 0
    return round(((tracked_power - fixed_power) / fixed_power) * 100, 1)


def calculate_angle_errors(
    sun_azimuth: float,
    sun_elevation: float,
    panel_azimuth: float,
    panel_elevation: float,
) -> dict[str, float]:
    return {
        "azimuthError": round(sun_azimuth - panel_azimuth, 1),
        "elevationError": round(sun_elevation - panel_elevation, 1),
    }


def get_light_factor(scenario: str) -> float:
    if scenario == "cloudy":
        return 0.45
    if scenario == "shade":
        return 0.58
    if scenario == "soiling":
        return 0.72
    return 1


def get_scenario_factor(scenario: str) -> float:
    if scenario == "cloudy":
        return 0.52
    if scenario == "shade":
        return 0.58
    if scenario == "soiling":
        return 0.72
    if scenario == "overheat":
        return 0.92
    return 1


def get_temp_factor(panel_temp: float) -> float:
    if panel_temp <= 45:
        return 1
    return max(0.6, 1 - (panel_temp - 45) * 0.012)


def get_weather_factor(weather: dict[str, Any]) -> float:
    if weather["rain"]:
        return 0.35
    return max(0.42, 1 - weather["cloudCover"] / 180)


def get_weather_label(values: dict[str, Any]) -> str:
    if values["rain"]:
        return "비"
    if values["cloudCover"] >= 75:
        return "흐림"
    if values["temperature"] >= 34:
        return "고온"
    if values["cloudCover"] >= 45:
        return "구름 많음"
    return "맑음"


def get_weather_reason(values: dict[str, Any], tracking_limited: bool) -> str:
    if values["rain"]:
        return "강수가 감지되어 추적보다 장비 보호를 우선합니다."
    if values["windSpeed"] >= 10:
        return "풍속이 높아 패널 움직임을 제한합니다."
    if values["cloudCover"] >= 75:
        return "구름량이 높아 일시적인 출력 저하가 예상됩니다."
    if values["temperature"] >= 34:
        return "높은 외기 온도가 패널 온도를 올릴 수 있습니다."
    if tracking_limited:
        return "기상 조건이 추적 보류 기준에 가깝습니다."
    return "추적 가능한 안정적인 기상 조건입니다."


def get_agent_note(source: str, location_name: str, scenario: str, tracking_limited: bool) -> str:
    source_text = "시나리오 기준값" if source == "scenario" else source
    decision = "모터 보정을 보류합니다" if tracking_limited else "추적 보정을 허용합니다"
    scenario_text = " 시나리오 조건도 반영했습니다." if scenario in {"cloudy", "overheat"} else ""
    return f"{location_name} 기상 데이터 출처는 {source_text}이며, 에이전트는 {decision}.{scenario_text}"


def append_log(logs: list[str], message: str) -> list[str]:
    if logs and logs[-1] == message:
        return logs
    return [*logs, message][-40:]


def format_time(time: float) -> str:
    hour = int(time)
    minute = round((time - hour) * 60)
    return f"{hour:02d}:{minute:02d}"


def clamp(value: float, minimum: float, maximum: float) -> float:
    return min(maximum, max(minimum, value))
