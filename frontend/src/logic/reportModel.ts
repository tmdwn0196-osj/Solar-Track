import type { Scenario, SolarState } from "../types/solar";

const scenarioTitles: Record<Scenario, string> = {
  normal: "정상 추적",
  cloudy: "흐림과 구름 가림",
  shade: "부분 음영",
  soiling: "패널 오염",
  overheat: "패널 과열",
  charging_issue: "충전 계통 문제",
  overload: "부하 과다",
};

const scenarioTalkingPoints: Record<Scenario, string> = {
  normal: "방위각과 고도각을 순차적으로 맞춘 뒤 발전량 개선률을 확인합니다.",
  cloudy: "출력 저하를 각도 문제가 아니라 기상 영향으로 분류하고 모터 동작을 보류합니다.",
  shade: "부분 음영 후보를 Vision 결과로 확인하고 주변 장애물 점검을 추천합니다.",
  soiling: "각도 정렬 후에도 출력이 낮으면 패널 표면 청소와 재측정을 추천합니다.",
  overheat: "과열 상황에서는 발전 효율보다 안전 확인과 통풍 점검을 우선합니다.",
  charging_issue: "패널 출력과 배터리 반응이 맞지 않으면 충전 컨트롤러와 배선을 점검합니다.",
  overload: "발전량보다 부하가 큰 상황을 경고하고 부하 조정을 안내합니다.",
};

export function buildDemoReport(state: SolarState) {
  return {
    title: scenarioTitles[state.scenario],
    summary: `${scenarioTitles[state.scenario]} 시나리오에서 추적식 ${state.trackedPower.toFixed(2)} W, 고정식 ${state.fixedPower.toFixed(2)} W를 비교합니다.`,
    talkingPoint: scenarioTalkingPoints[state.scenario],
    script: [
      `현재 시간은 ${formatTime(state.time)}이고 패널은 방위각 ${state.panelAzimuth.toFixed(1)}도, 고도각 ${state.panelElevation.toFixed(1)}도입니다.`,
      `발전량 개선률은 ${state.powerGainRate.toFixed(1)}%이며 위험도는 ${state.riskLevel}입니다.`,
      `에이전트 진단은 '${state.diagnosis}'입니다.`,
      `추천 조치는 '${state.action}'입니다.`,
    ],
  };
}

function formatTime(time: number) {
  const hour = Math.floor(time);
  const minute = Math.round((time - hour) * 60);
  return `${String(hour).padStart(2, "0")}:${String(minute).padStart(2, "0")}`;
}
