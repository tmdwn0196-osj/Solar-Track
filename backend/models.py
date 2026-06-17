from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


Scenario = Literal[
    "normal",
    "cloudy",
    "shade",
    "soiling",
    "overheat",
    "charging_issue",
    "overload",
]


class WeatherContextRequest(BaseModel):
    scenario: Scenario
    locationId: str = Field(default="seoul")


class VisionInferRequest(BaseModel):
    scenario: Scenario


class StateRequest(BaseModel):
    state: dict[str, Any]


class DemoReportRequest(BaseModel):
    state: dict[str, Any]


class ControlCommandRequest(BaseModel):
    state: dict[str, Any]
    command: Literal["track_step", "hold", "validate"]


class HardwareTelemetryRequest(BaseModel):
    deviceId: str = Field(default="esp32-demo")
    leftLight: float
    rightLight: float
    topLight: float
    bottomLight: float
    voltage: float
    current: float
    panelTemp: float
    batteryVoltage: float
    panelAzimuth: float
    panelElevation: float
    targetAzimuth: float
    targetElevation: float
    rain: bool = Field(default=False)
    windSpeed: float = Field(default=0)
    emergencyStop: bool = Field(default=False)
