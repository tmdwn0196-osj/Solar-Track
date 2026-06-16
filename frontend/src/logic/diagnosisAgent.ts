import type { RiskLevel, SolarState } from "../types/solar";

export function diagnoseState(state: SolarState): {
  diagnosis: string;
  action: string;
  riskLevel: RiskLevel;
} {
  if (state.scenario === "overheat" || state.panelTemp >= 65) {
    return {
      diagnosis: "패널 과열",
      action: "추적을 제한하고 통풍 상태와 패널 온도를 먼저 확인하세요.",
      riskLevel: "danger",
    };
  }

  if (state.weather.trackingLimited || state.vision.cloudDetected) {
    return {
      diagnosis: "기상 영향으로 인한 일시적 출력 저하",
      action: "구름량이 높아 추적을 보류합니다. 날씨가 안정된 뒤 발전량을 다시 비교하세요.",
      riskLevel: "warning",
    };
  }

  if (state.powerGainRate >= 5) {
    return {
      diagnosis: "추적 보정 성공",
      action: "방위각과 고도각 조정 후 발전량이 개선되었습니다.",
      riskLevel: "normal",
    };
  }

  if (state.scenario === "soiling") {
    return {
      diagnosis: "패널 오염 의심",
      action: "패널 표면을 청소한 뒤 같은 조건에서 발전량을 다시 확인하세요.",
      riskLevel: "warning",
    };
  }

  if (state.scenario === "shade") {
    return {
      diagnosis: "부분 음영 의심",
      action: "주변 구조물과 시간대별 그림자를 확인하세요.",
      riskLevel: "warning",
    };
  }

  if (state.scenario === "charging_issue") {
    return {
      diagnosis: "충전 계통 문제",
      action: "충전 컨트롤러, 배터리 연결, 배선 상태를 점검하세요.",
      riskLevel: "warning",
    };
  }

  if (state.scenario === "overload") {
    return {
      diagnosis: "부하 과다",
      action: "소비 전력을 줄이거나 배터리 방전 상태를 확인하세요.",
      riskLevel: "warning",
    };
  }

  return {
    diagnosis: "추적 상태 확인 중",
    action: "시뮬레이션을 계속 실행해 발전량 개선률을 확인하세요.",
    riskLevel: "normal",
  };
}
