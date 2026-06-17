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


class ControlCommandRequest(BaseModel):
    state: dict[str, Any]
    command: Literal["track_step", "hold", "validate"]
