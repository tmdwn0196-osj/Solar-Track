from __future__ import annotations

from datetime import datetime, timezone
from math import pi, sin
from typing import Any

from backend.vision_dataset import build_virtual_vision_result


LOCATIONS: dict[str, dict[str, Any]] = {
    "seoul": {
        "id": "seoul",
        "name": "Seoul",
        "latitude": 37.5665,
        "longitude": 126.978,
    },
    "busan": {
        "id": "busan",
        "name": "Busan",
        "latitude": 35.1796,
        "longitude": 129.0756,
    },
    "jeju": {
        "id": "jeju",
        "name": "Jeju",
        "latitude": 33.4996,
        "longitude": 126.5312,
    },
    "daejeon": {
        "id": "daejeon",
        "name": "Daejeon",
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
                "Cloud cover detected. Tracking correction is temporarily conservative.",
            ),
        }
    if scenario == "soiling":
        return {
            "cloudDetected": False,
            "soilingDetected": True,
            "shadeDetected": False,
            **build_virtual_vision_result(
                scenario,
                "Possible dust or soiling detected on the panel surface.",
            ),
        }
    if scenario == "shade":
        return {
            "cloudDetected": False,
            "soilingDetected": False,
            "shadeDetected": True,
            **build_virtual_vision_result(
                scenario,
                "Partial shading detected near the panel.",
            ),
        }
    return {
        "cloudDetected": False,
        "soilingDetected": False,
        "shadeDetected": False,
        **build_virtual_vision_result(scenario, "Vision inference is stable."),
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
    log_message = f"{format_time(updated['time'])} {updated.get('phaseReason') or 'State updated.'}"

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
            "phaseReason": "Auto tracking is disabled. Holding the current panel angle.",
        }

    if state["weather"]["trackingLimited"] or state["vision"]["cloudDetected"]:
        reason = (
            "Weather conditions limit tracking. Motor correction is on hold."
            if state["weather"]["trackingLimited"]
            else "Vision detected cloud cover. Angle correction is on hold."
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
            "phaseReason": f"Azimuth error is {azimuth_error:.1f} deg. Aligning azimuth first.",
        }

    if abs(elevation_error) > 2:
        return {
            "panelAzimuth": state["panelAzimuth"],
            "panelElevation": clamp(state["panelElevation"] + (2 if elevation_error > 0 else -2), 0, 70),
            **errors,
            "phase": "elevation_align",
            "phaseReason": f"Elevation error is {elevation_error:.1f} deg. Correcting elevation.",
        }

    return {
        "panelAzimuth": state["panelAzimuth"],
        "panelElevation": state["panelElevation"],
        **errors,
        "phase": "power_verify",
        "phaseReason": "Panel angle is within tolerance. Verifying power gain.",
    }


def diagnose_state(state: dict[str, Any]) -> dict[str, Any]:
    if state["phase"] == "idle":
        return {
            "diagnosis": "Simulation idle",
            "action": "Start the loop to verify the solar tracking flow.",
            "riskLevel": "normal",
            "diagnosisReasons": ["The tracking loop has not run yet."],
        }
    if state["scenario"] == "overheat" or state["panelTemp"] >= 65:
        return {
            "diagnosis": "Panel overheating",
            "action": "Limit tracking and inspect panel ventilation before continuing.",
            "riskLevel": "danger",
            "diagnosisReasons": [
                f"Panel temperature is {state['panelTemp']:.1f} C.",
                "High temperature reduces efficiency and may require a safety hold.",
            ],
        }
    if state["weather"]["trackingLimited"] or state["vision"]["cloudDetected"]:
        return {
            "diagnosis": "Temporary output loss from weather",
            "action": "Hold tracking while irradiance is unstable, then compare output again.",
            "riskLevel": "warning",
            "diagnosisReasons": [
                f"Cloud cover is {state['weather']['cloudCover']}%.",
                "Vision or weather context indicates unstable irradiance.",
            ],
        }
    if state["lightAverage"] < 0.55:
        return {
            "diagnosis": "Low irradiance",
            "action": "Wait for irradiance recovery before judging tracker performance.",
            "riskLevel": "warning",
            "diagnosisReasons": [
                f"Average light sensor value is {state['lightAverage']:.2f}.",
                "The sensor average is too low for reliable power comparison.",
            ],
        }
    if state["phase"] == "power_verify" and state["powerGainRate"] >= 5:
        return {
            "diagnosis": "Tracking correction succeeded",
            "action": "Panel alignment improved output compared with the fixed panel.",
            "riskLevel": "normal",
            "diagnosisReasons": [
                f"Power gain is {state['powerGainRate']:.1f}%.",
                "Tracked output is at least 5% above fixed output.",
            ],
        }
    if state["vision"]["soilingDetected"] or state["scenario"] == "soiling":
        return {
            "diagnosis": "Possible panel soiling",
            "action": "Clean the panel surface and compare output under similar weather.",
            "riskLevel": "warning",
            "diagnosisReasons": [
                "Vision flagged possible surface soiling.",
                f"Scenario factor is {state['powerBreakdown']['scenarioFactor']:.2f}.",
            ],
        }
    if state["vision"]["shadeDetected"] or state["scenario"] == "shade":
        return {
            "diagnosis": "Possible partial shading",
            "action": "Inspect surrounding structures and time-based shadow patterns.",
            "riskLevel": "warning",
            "diagnosisReasons": [
                "Vision flagged possible partial shading.",
                f"Average light sensor value is {state['lightAverage']:.2f}.",
            ],
        }
    if state["scenario"] == "charging_issue":
        return {
            "diagnosis": "Charging system issue",
            "action": "Inspect the charge controller, battery connection, and wiring.",
            "riskLevel": "warning",
            "diagnosisReasons": [
                f"Tracked power is {state['trackedPower']:.2f} W.",
                f"Battery voltage is {state['batteryVoltage']:.1f} V.",
            ],
        }
    if state["scenario"] == "overload":
        return {
            "diagnosis": "Load exceeds expected output",
            "action": "Reduce device load or inspect battery discharge state.",
            "riskLevel": "warning",
            "diagnosisReasons": [
                "The load is assumed to exceed current generation.",
                f"Tracked power is {state['trackedPower']:.2f} W.",
            ],
        }
    if state["phase"] in {"azimuth_align", "elevation_align", "weather_check"}:
        return {
            "diagnosis": "Sequential tracking in progress",
            "action": "Continue azimuth and elevation alignment, then verify power.",
            "riskLevel": "normal",
            "diagnosisReasons": [
                f"Azimuth error is {state['azimuthError']:.1f} deg.",
                f"Elevation error is {state['elevationError']:.1f} deg.",
            ],
        }

    return {
        "diagnosis": "Tracking state under observation",
        "action": "Keep the simulation running to gather more comparison data.",
        "riskLevel": "normal",
        "diagnosisReasons": [
            f"Power gain is {state['powerGainRate']:.1f}%.",
            "More simulation samples are required.",
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
        return "Rain"
    if values["cloudCover"] >= 75:
        return "Cloudy"
    if values["temperature"] >= 34:
        return "Hot"
    if values["cloudCover"] >= 45:
        return "Partly cloudy"
    return "Clear"


def get_weather_reason(values: dict[str, Any], tracking_limited: bool) -> str:
    if values["rain"]:
        return "Rain detected. Protecting equipment takes priority over tracking."
    if values["windSpeed"] >= 10:
        return "Wind speed is high, so panel movement is limited."
    if values["cloudCover"] >= 75:
        return "Cloud cover is high and temporary output loss is expected."
    if values["temperature"] >= 34:
        return "High ambient temperature may increase panel temperature."
    if tracking_limited:
        return "Weather is close to the tracking hold threshold."
    return "Weather is stable enough for tracking."


def get_agent_note(source: str, location_name: str, scenario: str, tracking_limited: bool) -> str:
    source_text = "scenario baseline" if source == "scenario" else source
    decision = "holding motor correction" if tracking_limited else "allowing tracking correction"
    scenario_text = " Scenario constraints are reflected." if scenario in {"cloudy", "overheat"} else ""
    return f"{location_name} weather from {source_text}; agent is {decision}.{scenario_text}"


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
