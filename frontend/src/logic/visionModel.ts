import type { Scenario, VisionState } from "../types/solar";

const scenarioVisionMap: Record<
  Scenario,
  Pick<VisionState, "primaryClass" | "confidence" | "modelMode" | "detections">
> = {
  normal: {
    primaryClass: "panel_clean",
    confidence: 0.91,
    modelMode: "virtual_dataset_stub",
    detections: [
      { className: "sky_clear", confidence: 0.88 },
      { className: "panel_clean", confidence: 0.91 },
    ],
  },
  cloudy: {
    primaryClass: "sun_cloud_block",
    confidence: 0.86,
    modelMode: "virtual_dataset_stub",
    detections: [
      { className: "sky_cloudy", confidence: 0.84 },
      { className: "sun_cloud_block", confidence: 0.86 },
    ],
  },
  shade: {
    primaryClass: "panel_partial_shadow",
    confidence: 0.82,
    modelMode: "virtual_dataset_stub",
    detections: [{ className: "panel_partial_shadow", confidence: 0.82 }],
  },
  soiling: {
    primaryClass: "panel_soiling",
    confidence: 0.8,
    modelMode: "virtual_dataset_stub",
    detections: [{ className: "panel_soiling", confidence: 0.8 }],
  },
  overheat: {
    primaryClass: "panel_clean",
    confidence: 0.74,
    modelMode: "virtual_dataset_stub",
    detections: [
      { className: "sky_clear", confidence: 0.79 },
      { className: "panel_clean", confidence: 0.74 },
    ],
  },
  charging_issue: {
    primaryClass: "panel_clean",
    confidence: 0.78,
    modelMode: "virtual_dataset_stub",
    detections: [{ className: "panel_clean", confidence: 0.78 }],
  },
  overload: {
    primaryClass: "panel_clean",
    confidence: 0.77,
    modelMode: "virtual_dataset_stub",
    detections: [{ className: "panel_clean", confidence: 0.77 }],
  },
};

export function inferVirtualVision(scenario: Scenario): VisionState {
  if (scenario === "cloudy") {
    return {
      cloudDetected: true,
      soilingDetected: false,
      shadeDetected: false,
      ...scenarioVisionMap[scenario],
      note: "구름에 의한 일시적 광량 저하가 감지되었습니다.",
    };
  }

  if (scenario === "soiling") {
    return {
      cloudDetected: false,
      soilingDetected: true,
      shadeDetected: false,
      ...scenarioVisionMap[scenario],
      note: "패널 표면 오염 후보가 있습니다.",
    };
  }

  if (scenario === "shade") {
    return {
      cloudDetected: false,
      soilingDetected: false,
      shadeDetected: true,
      ...scenarioVisionMap[scenario],
      note: "부분 음영 후보가 있습니다.",
    };
  }

  return {
    cloudDetected: false,
    soilingDetected: false,
    shadeDetected: false,
    ...scenarioVisionMap[scenario],
    note: "비전 감지 결과가 안정적입니다.",
  };
}
