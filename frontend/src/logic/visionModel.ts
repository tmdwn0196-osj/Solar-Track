import type { Scenario, VisionState } from "../types/solar";

export function inferVirtualVision(scenario: Scenario): VisionState {
  if (scenario === "cloudy") {
    return {
      cloudDetected: true,
      soilingDetected: false,
      shadeDetected: false,
      note: "구름에 의한 일시적 광량 저하가 감지되었습니다.",
    };
  }

  if (scenario === "soiling") {
    return {
      cloudDetected: false,
      soilingDetected: true,
      shadeDetected: false,
      note: "패널 표면 오염 후보가 있습니다.",
    };
  }

  if (scenario === "shade") {
    return {
      cloudDetected: false,
      soilingDetected: false,
      shadeDetected: true,
      note: "부분 음영 후보가 있습니다.",
    };
  }

  return {
    cloudDetected: false,
    soilingDetected: false,
    shadeDetected: false,
    note: "비전 감지 결과가 안정적입니다.",
  };
}
