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
        "phaseReason": "기상 안전 게이트가 추적 보류를 요청했습니다.",
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
        "phaseReason": "구름 감지 게이트가 불필요한 모터 동작을 막기 위해 서보 보류를 요청했습니다.",
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
        "센서 값은 추적에 사용할 수 있습니다."
        if state["lightAverage"] >= 0.55
        else "광량은 낮지만 기상 게이트가 보수적인 검증을 허용했습니다."
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
        reasons.append("기상 조건상 추적을 제한해야 합니다.")
    if state["vision"]["soilingDetected"] or state["vision"]["shadeDetected"]:
        reasons.append("비전 결과가 패널 측 출력 저하 원인을 나타냅니다.")
    if state["lightAverage"] < 0.55:
        reasons.append("조도 센서 평균값이 낮습니다.")

    if not reasons:
        reasons.append("센서, 비전, 기상 신호가 추적 가능한 범위에서 일관됩니다.")

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
        f"{state['diagnosis']} | 조치={state['action']} | "
        f"위험도={state['riskLevel']} | 발전량 개선률={state['powerGainRate']:.1f}%"
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
