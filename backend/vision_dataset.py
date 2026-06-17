from __future__ import annotations

from typing import Any


VISION_CLASSES: list[dict[str, str]] = [
    {
        "name": "sky_clear",
        "type": "classification",
        "description": "Clear sky with stable sunlight.",
    },
    {
        "name": "sky_cloudy",
        "type": "classification",
        "description": "Cloudy sky likely to reduce irradiance.",
    },
    {
        "name": "sun_cloud_block",
        "type": "detection",
        "description": "Sun is temporarily blocked by cloud.",
    },
    {
        "name": "panel_clean",
        "type": "classification",
        "description": "Panel surface is visually clean.",
    },
    {
        "name": "panel_soiling",
        "type": "detection",
        "description": "Dust, dirt, or residue is visible on panel surface.",
    },
    {
        "name": "panel_partial_shadow",
        "type": "detection",
        "description": "Partial shadow covers one or more panel areas.",
    },
    {
        "name": "panel_foreign_object",
        "type": "detection",
        "description": "Leaf, debris, or other object is on the panel.",
    },
    {
        "name": "panel_damage",
        "type": "detection",
        "description": "Crack, burn mark, or other panel damage candidate.",
    },
]


SCENARIO_VISION_MAP: dict[str, dict[str, Any]] = {
    "normal": {
        "primaryClass": "panel_clean",
        "confidence": 0.91,
        "detections": [
            {"className": "sky_clear", "confidence": 0.88},
            {"className": "panel_clean", "confidence": 0.91},
        ],
    },
    "cloudy": {
        "primaryClass": "sun_cloud_block",
        "confidence": 0.86,
        "detections": [
            {"className": "sky_cloudy", "confidence": 0.84},
            {"className": "sun_cloud_block", "confidence": 0.86},
        ],
    },
    "shade": {
        "primaryClass": "panel_partial_shadow",
        "confidence": 0.82,
        "detections": [
            {"className": "panel_partial_shadow", "confidence": 0.82},
        ],
    },
    "soiling": {
        "primaryClass": "panel_soiling",
        "confidence": 0.8,
        "detections": [
            {"className": "panel_soiling", "confidence": 0.8},
        ],
    },
    "overheat": {
        "primaryClass": "panel_clean",
        "confidence": 0.74,
        "detections": [
            {"className": "sky_clear", "confidence": 0.79},
            {"className": "panel_clean", "confidence": 0.74},
        ],
    },
    "charging_issue": {
        "primaryClass": "panel_clean",
        "confidence": 0.78,
        "detections": [
            {"className": "panel_clean", "confidence": 0.78},
        ],
    },
    "overload": {
        "primaryClass": "panel_clean",
        "confidence": 0.77,
        "detections": [
            {"className": "panel_clean", "confidence": 0.77},
        ],
    },
}


def build_virtual_vision_result(scenario: str, note: str) -> dict[str, Any]:
    mapped = SCENARIO_VISION_MAP.get(scenario, SCENARIO_VISION_MAP["normal"])
    return {
        **mapped,
        "modelMode": "virtual_dataset_stub",
        "note": note,
    }


def get_vision_dataset_summary() -> dict[str, Any]:
    return {
        "classes": VISION_CLASSES,
        "datasetRoot": "datasets",
        "imageFolders": ["datasets/images/raw", "datasets/images/train", "datasets/images/val"],
        "labelFolders": ["datasets/labels/classification", "datasets/labels/detection"],
        "sampleManifest": "datasets/sample_manifest.csv",
        "trainingStatus": "not_started",
        "reason": "v09 only defines dataset structure and virtual inference metadata.",
    }
