from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.agent_graph import run_agent_graph
from backend.demo_report import build_demo_report, get_demo_scenarios
from backend.hardware_gateway import evaluate_hardware_telemetry, get_hardware_profile
from backend.models import (
    ControlCommandRequest,
    DemoReportRequest,
    HardwareTelemetryRequest,
    StateRequest,
    VisionInferRequest,
    WeatherContextRequest,
)
from backend.simulation import calculate_weather, diagnose_state, infer_vision, recalculate_state, run_tracking_step, simulate_step
from backend.vision_dataset import get_vision_dataset_summary


app = FastAPI(title="SolarTrack Agent API", version="0.11.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://localhost:5173",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "solartrack-backend", "version": "0.11.0"}


@app.post("/api/simulate/step")
def simulate_step_endpoint(request: StateRequest) -> dict[str, object]:
    return {"state": simulate_step(request.state)}


@app.post("/api/weather/context")
def weather_context(request: WeatherContextRequest) -> dict[str, object]:
    return {
        "weather": calculate_weather(
            scenario=request.scenario,
            location_id=request.locationId,
        )
    }


@app.post("/api/diagnosis")
def diagnosis(request: StateRequest) -> dict[str, object]:
    return {"diagnosis": diagnose_state(recalculate_state(request.state))}


@app.post("/api/vision/infer")
def vision_infer(request: VisionInferRequest) -> dict[str, object]:
    return {"vision": infer_vision(request.scenario)}


@app.get("/api/vision/classes")
def vision_classes() -> dict[str, object]:
    return {"visionDataset": get_vision_dataset_summary()}


@app.post("/api/control/command")
def control_command(request: ControlCommandRequest) -> dict[str, object]:
    if request.command == "track_step":
        return {"accepted": True, "command": request.command, "control": run_tracking_step(request.state)}
    if request.command == "hold":
        return {
            "accepted": True,
            "command": request.command,
            "control": {
                "panelAzimuth": request.state["panelAzimuth"],
                "panelElevation": request.state["panelElevation"],
                "phase": "hold",
                "phaseReason": "External hold command accepted.",
            },
        }
    return {"accepted": True, "command": request.command, "control": run_tracking_step(request.state)}


@app.post("/api/agent/evaluate")
def agent_evaluate(request: StateRequest) -> dict[str, object]:
    return {"agent": run_agent_graph(request.state)}


@app.get("/api/hardware/profile")
def hardware_profile() -> dict[str, object]:
    return {"hardware": get_hardware_profile()}


@app.post("/api/hardware/telemetry")
def hardware_telemetry(request: HardwareTelemetryRequest) -> dict[str, object]:
    return {"hardware": evaluate_hardware_telemetry(request.model_dump())}


@app.get("/api/demo/scenarios")
def demo_scenarios() -> dict[str, object]:
    return {"scenarios": get_demo_scenarios()}


@app.post("/api/demo/report")
def demo_report(request: DemoReportRequest) -> dict[str, object]:
    return {"report": build_demo_report(request.state)}
