from __future__ import annotations

from typing import Any, Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from backend.simulation import (
    calculate_weather,
    diagnose_state,
    infer_vision,
    recalculate_state,
    run_tracking_step,
)


Route = Literal["safety_hold", "cloud_gate", "hold_servo", "validate_sensor"]


class AgentGraphState(TypedDict, total=False):
    state: dict[str, Any]
    sensorSnapshot: dict[str, Any]
    weather: dict[str, Any]
    vision: dict[str, Any]
    beforePower: float
    afterPower: float
    powerGainRate: float
    control: dict[str, Any]
    diagnosis: dict[str, Any]
    report: str
    route: str
    trace: list[str]


def run_agent_graph(state: dict[str, Any]) -> dict[str, Any]:
    result = solar_agent_graph.invoke({"state": state, "trace": []})
    return {
        "state": result["state"],
        "sensorSnapshot": result.get("sensorSnapshot", {}),
        "weather": result.get("weather", {}),
        "vision": result.get("vision", {}),
        "control": result.get("control", {}),
        "diagnosis": result.get("diagnosis", {}),
        "report": result.get("report", ""),
        "trace": result.get("trace", []),
    }


def collect_sensor(graph_state: AgentGraphState) -> AgentGraphState:
    state = recalculate_state(graph_state["state"])
    return {
        "state": state,
        "sensorSnapshot": {
            "leftLight": state["leftLight"],
            "rightLight": state["rightLight"],
            "topLight": state["topLight"],
            "bottomLight": state["bottomLight"],
            "lightAverage": state["lightAverage"],
            "voltage": state["voltage"],
            "current": state["current"],
            "power": state["power"],
        },
        "trace": append_trace(graph_state, "collect_sensor"),
    }


def collect_weather(graph_state: AgentGraphState) -> AgentGraphState:
    state = graph_state["state"]
    weather = calculate_weather(state["scenario"], state.get("weatherLocationId", "seoul"))
    updated = recalculate_state({**state, "weather": weather})
    return {
        "state": updated,
        "weather": weather,
        "trace": append_trace(graph_state, "collect_weather"),
    }


def vision_inference(graph_state: AgentGraphState) -> AgentGraphState:
    state = graph_state["state"]
    vision = infer_vision(state["scenario"])
    updated = recalculate_state({**state, "vision": vision})
    return {
        "state": updated,
        "vision": vision,
        "trace": append_trace(graph_state, "vision_inference"),
    }


def weather_gate(graph_state: AgentGraphState) -> AgentGraphState:
    weather = graph_state["state"]["weather"]
    route = "safety_hold" if weather["rain"] or weather["windSpeed"] >= 10 else "cloud_gate"
    return {"route": route, "trace": append_trace(graph_state, "weather_gate")}


def safety_hold(graph_state: AgentGraphState) -> AgentGraphState:
    state = graph_state["state"]
    control = {
        "panelAzimuth": state["panelAzimuth"],
        "panelElevation": state["panelElevation"],
        "phase": "hold",
        "phaseReason": "Weather safety gate requested a tracking hold.",
    }
    updated = recalculate_state({**state, **control})
    return {
        "state": updated,
        "control": control,
        "trace": append_trace(graph_state, "safety_hold"),
    }


def cloud_gate(graph_state: AgentGraphState) -> AgentGraphState:
    state = graph_state["state"]
    cloud_detected = state["weather"]["cloudCover"] >= 75 or state["vision"]["cloudDetected"]
    route = "hold_servo" if cloud_detected else "validate_sensor"
    return {"route": route, "trace": append_trace(graph_state, "cloud_gate")}


def hold_servo(graph_state: AgentGraphState) -> AgentGraphState:
    state = graph_state["state"]
    control = {
        "panelAzimuth": state["panelAzimuth"],
        "panelElevation": state["panelElevation"],
        "phase": "hold",
        "phaseReason": "Cloud gate requested a servo hold to avoid unnecessary movement.",
    }
    updated = recalculate_state({**state, **control})
    return {
        "state": updated,
        "control": control,
        "trace": append_trace(graph_state, "hold_servo"),
    }


def validate_sensor(graph_state: AgentGraphState) -> AgentGraphState:
    state = graph_state["state"]
    phase_reason = (
        "Sensor values are usable for tracking."
        if state["lightAverage"] >= 0.55
        else "Light is low, but weather gate allowed a conservative validation pass."
    )
    updated = recalculate_state({**state, "phase": "weather_check", "phaseReason": phase_reason})
    return {"state": updated, "trace": append_trace(graph_state, "validate_sensor")}


def measure_before_power(graph_state: AgentGraphState) -> AgentGraphState:
    return {
        "beforePower": graph_state["state"]["trackedPower"],
        "trace": append_trace(graph_state, "measure_before_power"),
    }


def azimuth_align(graph_state: AgentGraphState) -> AgentGraphState:
    state = graph_state["state"]
    control = run_tracking_step({**state, "phase": "azimuth_align"})
    updated = recalculate_state({**state, **control})
    return {
        "state": updated,
        "control": control,
        "trace": append_trace(graph_state, "azimuth_align"),
    }


def elevation_align(graph_state: AgentGraphState) -> AgentGraphState:
    state = graph_state["state"]
    control = run_tracking_step(state)
    updated = recalculate_state({**state, **control})
    return {
        "state": updated,
        "control": control,
        "trace": append_trace(graph_state, "elevation_align"),
    }


def measure_after_power(graph_state: AgentGraphState) -> AgentGraphState:
    return {
        "afterPower": graph_state["state"]["trackedPower"],
        "trace": append_trace(graph_state, "measure_after_power"),
    }


def verify_power_gain(graph_state: AgentGraphState) -> AgentGraphState:
    state = graph_state["state"]
    before_power = graph_state.get("beforePower", state["fixedPower"])
    after_power = graph_state.get("afterPower", state["trackedPower"])
    power_gain_rate = 0 if before_power <= 0 else round(((after_power - before_power) / before_power) * 100, 1)
    return {
        "powerGainRate": power_gain_rate,
        "trace": append_trace(graph_state, "verify_power_gain"),
    }


def fuse_sensor_vision_weather(graph_state: AgentGraphState) -> AgentGraphState:
    state = graph_state["state"]
    reasons: list[str] = []

    if state["weather"]["trackingLimited"]:
        reasons.append("Weather suggests tracking should be limited.")
    if state["vision"]["soilingDetected"] or state["vision"]["shadeDetected"]:
        reasons.append("Vision suggests a panel-side output loss cause.")
    if state["lightAverage"] < 0.55:
        reasons.append("Light sensor average is low.")

    if not reasons:
        reasons.append("Sensor, vision, and weather signals are consistent enough for tracking.")

    fused = {
        **state,
        "phaseReason": " ".join(reasons),
    }
    return {
        "state": fused,
        "trace": append_trace(graph_state, "fuse_sensor_vision_weather"),
    }


def diagnose_fault(graph_state: AgentGraphState) -> AgentGraphState:
    state = recalculate_state(graph_state["state"])
    diagnosis = diagnose_state(state)
    return {
        "state": {**state, **diagnosis},
        "diagnosis": diagnosis,
        "trace": append_trace(graph_state, "diagnose_fault"),
    }


def generate_report(graph_state: AgentGraphState) -> AgentGraphState:
    state = graph_state["state"]
    report = (
        f"{state['diagnosis']} | action={state['action']} | "
        f"risk={state['riskLevel']} | powerGain={state['powerGainRate']:.1f}%"
    )
    return {
        "report": report,
        "trace": append_trace(graph_state, "generate_report"),
    }


def route_weather(graph_state: AgentGraphState) -> Route:
    return graph_state["route"]  # type: ignore[return-value]


def route_cloud(graph_state: AgentGraphState) -> Route:
    return graph_state["route"]  # type: ignore[return-value]


def append_trace(graph_state: AgentGraphState, node_name: str) -> list[str]:
    return [*graph_state.get("trace", []), node_name]


def build_solar_agent_graph():
    graph = StateGraph(AgentGraphState)
    graph.add_node("collect_sensor", collect_sensor)
    graph.add_node("collect_weather", collect_weather)
    graph.add_node("vision_inference", vision_inference)
    graph.add_node("weather_gate", weather_gate)
    graph.add_node("safety_hold", safety_hold)
    graph.add_node("cloud_gate", cloud_gate)
    graph.add_node("hold_servo", hold_servo)
    graph.add_node("validate_sensor", validate_sensor)
    graph.add_node("measure_before_power", measure_before_power)
    graph.add_node("azimuth_align", azimuth_align)
    graph.add_node("elevation_align", elevation_align)
    graph.add_node("measure_after_power", measure_after_power)
    graph.add_node("verify_power_gain", verify_power_gain)
    graph.add_node("fuse_sensor_vision_weather", fuse_sensor_vision_weather)
    graph.add_node("diagnose_fault", diagnose_fault)
    graph.add_node("generate_report", generate_report)

    graph.add_edge(START, "collect_sensor")
    graph.add_edge("collect_sensor", "collect_weather")
    graph.add_edge("collect_weather", "vision_inference")
    graph.add_edge("vision_inference", "weather_gate")
    graph.add_conditional_edges(
        "weather_gate",
        route_weather,
        {
            "safety_hold": "safety_hold",
            "cloud_gate": "cloud_gate",
        },
    )
    graph.add_edge("safety_hold", "diagnose_fault")
    graph.add_conditional_edges(
        "cloud_gate",
        route_cloud,
        {
            "hold_servo": "hold_servo",
            "validate_sensor": "validate_sensor",
        },
    )
    graph.add_edge("hold_servo", "diagnose_fault")
    graph.add_edge("validate_sensor", "measure_before_power")
    graph.add_edge("measure_before_power", "azimuth_align")
    graph.add_edge("azimuth_align", "elevation_align")
    graph.add_edge("elevation_align", "measure_after_power")
    graph.add_edge("measure_after_power", "verify_power_gain")
    graph.add_edge("verify_power_gain", "fuse_sensor_vision_weather")
    graph.add_edge("fuse_sensor_vision_weather", "diagnose_fault")
    graph.add_edge("diagnose_fault", "generate_report")
    graph.add_edge("generate_report", END)
    return graph.compile()


solar_agent_graph = build_solar_agent_graph()
