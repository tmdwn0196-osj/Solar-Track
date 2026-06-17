from __future__ import annotations

from typing import Any


VISION_CLASSES: list[dict[str, str]] = [
    {
        "name": "sky_clear",
        "type": "classification",
        "description": "맑고 안정적인 일사 조건입니다.",
    },
    {
        "name": "sky_cloudy",
        "type": "classification",
        "description": "구름으로 인해 일사량이 낮아질 수 있는 조건입니다.",
    },
    {
        "name": "sun_cloud_block",
        "type": "detection",
        "description": "태양이 구름에 일시적으로 가려진 상태입니다.",
    },
    {
        "name": "panel_clean",
        "type": "classification",
        "description": "패널 표면이 시각적으로 깨끗한 상태입니다.",
    },
    {
        "name": "panel_soiling",
        "type": "detection",
        "description": "패널 표면에 먼지, 오염, 잔여물이 보이는 상태입니다.",
    },
    {
        "name": "panel_partial_shadow",
        "type": "detection",
        "description": "패널 일부 영역이 그림자로 가려진 상태입니다.",
    },
    {
        "name": "panel_foreign_object",
        "type": "detection",
        "description": "패널 위에 낙엽, 이물질, 기타 물체가 있는 상태입니다.",
    },
    {
        "name": "panel_damage",
        "type": "detection",
        "description": "균열, 탄 흔적 등 패널 손상 후보가 보이는 상태입니다.",
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
        "modelMode": "가상 데이터셋",
        "note": note,
    }


def get_vision_dataset_summary() -> dict[str, Any]:
    return {
        "classes": VISION_CLASSES,
        "datasetRoot": "datasets",
        "imageFolders": ["datasets/images/raw", "datasets/images/train", "datasets/images/val"],
        "labelFolders": ["datasets/labels/classification", "datasets/labels/detection"],
        "sampleManifest": "datasets/sample_manifest.csv",
        "trainingStatus": "학습 전",
        "reason": "v09 단계에서는 데이터셋 구조와 가상 추론 메타데이터만 정의합니다.",
    }
