import type { DiagnosisResult, SolarState } from "../types/solar";

export function diagnoseState(state: SolarState): DiagnosisResult {
  if (state.phase === "idle") {
    return {
      diagnosis: "시뮬레이션 대기",
      action: "시작 버튼을 눌러 순차제어 흐름을 확인하세요.",
      riskLevel: "normal",
      diagnosisReasons: ["아직 추적 루프가 실행되지 않았습니다."],
    };
  }

  if (state.scenario === "overheat" || state.panelTemp >= 65) {
    return {
      diagnosis: "패널 과열",
      action: "추적을 제한하고 통풍 상태와 패널 온도를 먼저 확인하세요.",
      riskLevel: "danger",
      diagnosisReasons: [
        `패널 온도 ${state.panelTemp.toFixed(1)} °C`,
        "고온 상태에서는 발전 효율이 낮아지고 안전 제한이 필요합니다.",
      ],
    };
  }

  if (state.weather.trackingLimited || state.vision.cloudDetected) {
    return {
      diagnosis: "기상 영향으로 인한 일시적 출력 저하",
      action: "구름량이 높아 추적을 보류합니다. 날씨가 안정된 뒤 발전량을 다시 비교하세요.",
      riskLevel: "warning",
      diagnosisReasons: [
        `구름량 ${state.weather.cloudCover}%`,
        state.vision.cloudDetected ? "Vision 결과에서 구름이 감지되었습니다." : state.weather.reason,
      ],
    };
  }

  if (state.lightAverage < 0.55) {
    return {
      diagnosis: "광량 부족",
      action: "일시적인 흐림 또는 시간대 영향일 수 있으므로 광량이 회복된 뒤 다시 비교하세요.",
      riskLevel: "warning",
      diagnosisReasons: [
        `평균 조도 ${state.lightAverage.toFixed(2)}`,
        "센서 평균 조도가 낮아 충분한 일사가 들어오지 않습니다.",
      ],
    };
  }

  if (state.phase === "power_verify" && state.powerGainRate >= 5) {
    return {
      diagnosis: "추적 보정 성공",
      action: "방위각과 고도각 조정 후 발전량이 개선되었습니다.",
      riskLevel: "normal",
      diagnosisReasons: [
        `발전량 개선률 ${state.powerGainRate.toFixed(1)}%`,
        "고정식 대비 추적식 발전량이 5% 이상 높습니다.",
      ],
    };
  }

  if (state.vision.soilingDetected || state.scenario === "soiling") {
    return {
      diagnosis: "패널 오염 의심",
      action: "패널 표면을 청소한 뒤 같은 조건에서 발전량을 다시 확인하세요.",
      riskLevel: "warning",
      diagnosisReasons: [
        "Vision 결과에서 오염 후보가 감지되었습니다.",
        `시나리오 계수 ${state.powerBreakdown.scenarioFactor.toFixed(2)}`,
      ],
    };
  }

  if (state.vision.shadeDetected || state.scenario === "shade") {
    return {
      diagnosis: "부분 음영 의심",
      action: "주변 구조물과 시간대별 그림자를 확인하세요.",
      riskLevel: "warning",
      diagnosisReasons: [
        "Vision 결과에서 부분 음영 후보가 감지되었습니다.",
        `평균 조도 ${state.lightAverage.toFixed(2)}`,
      ],
    };
  }

  if (state.scenario === "charging_issue") {
    return {
      diagnosis: "충전 계통 문제",
      action: "충전 컨트롤러, 배터리 연결, 배선 상태를 점검하세요.",
      riskLevel: "warning",
      diagnosisReasons: [
        `추적식 발전량 ${state.trackedPower.toFixed(2)} W`,
        `배터리 전압 ${state.batteryVoltage.toFixed(1)} V`,
      ],
    };
  }

  if (state.scenario === "overload") {
    return {
      diagnosis: "부하 과다",
      action: "소비 전력을 줄이거나 배터리 방전 상태를 확인하세요.",
      riskLevel: "warning",
      diagnosisReasons: [
        "부하가 발전량보다 큰 상황으로 가정되었습니다.",
        `추적식 발전량 ${state.trackedPower.toFixed(2)} W`,
      ],
    };
  }

  if (state.phase === "azimuth_align" || state.phase === "elevation_align" || state.phase === "weather_check") {
    return {
      diagnosis: "순차제어 진행 중",
      action: "방위각 정렬을 먼저 끝낸 뒤 고도각 정렬과 발전량 검증을 진행합니다.",
      riskLevel: "normal",
      diagnosisReasons: [
        `방위각 오차 ${state.azimuthError.toFixed(1)}도`,
        `고도각 오차 ${state.elevationError.toFixed(1)}도`,
      ],
    };
  }

  return {
    diagnosis: "추적 상태 확인 중",
    action: "시뮬레이션을 계속 실행해 발전량 개선률을 확인하세요.",
    riskLevel: "normal",
    diagnosisReasons: [
      `발전량 개선률 ${state.powerGainRate.toFixed(1)}%`,
      "추가 시뮬레이션 데이터가 필요합니다.",
    ],
  };
}
