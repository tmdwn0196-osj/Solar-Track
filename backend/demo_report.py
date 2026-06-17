from __future__ import annotations

from typing import Any

from backend.agent_graph import run_agent_graph
from backend.simulation import recalculate_state


DEMO_SCENARIOS: list[dict[str, str]] = [
    {
        "id": "normal_tracking",
        "scenario": "normal",
        "title": "정상 추적",
        "goal": "맑은 날 순차제어로 고정식 대비 발전량이 개선되는지 보여준다.",
        "talkingPoint": "방위각을 먼저 맞추고 고도각을 보정한 뒤 발전량 개선률을 확인한다.",
    },
    {
        "id": "cloudy_weather",
        "scenario": "cloudy",
        "title": "흐림과 구름 가림",
        "goal": "구름 조건에서 불필요한 모터 동작을 보류하는 판단을 보여준다.",
        "talkingPoint": "출력 저하는 각도 문제가 아니라 기상 영향으로 분류한다.",
    },
    {
        "id": "partial_shade",
        "scenario": "shade",
        "title": "부분 음영",
        "goal": "패널 일부가 가려졌을 때 Vision 결과가 진단을 보완하는지 보여준다.",
        "talkingPoint": "주변 장애물과 시간대별 그림자 확인이 조치로 제시된다.",
    },
    {
        "id": "panel_soiling",
        "scenario": "soiling",
        "title": "패널 오염",
        "goal": "각도 정렬 후에도 출력이 낮을 때 패널 표면 문제를 진단한다.",
        "talkingPoint": "청소 후 같은 조건에서 재측정하라는 조치가 핵심이다.",
    },
    {
        "id": "panel_overheat",
        "scenario": "overheat",
        "title": "패널 과열",
        "goal": "온도 상승이 발전 효율과 위험도에 반영되는지 보여준다.",
        "talkingPoint": "과열 상태에서는 추적보다 안전 확인과 통풍 점검이 우선이다.",
    },
    {
        "id": "charging_issue",
        "scenario": "charging_issue",
        "title": "충전 계통 문제",
        "goal": "패널 출력과 배터리 반응이 맞지 않을 때 계통 문제를 진단한다.",
        "talkingPoint": "충전 컨트롤러, 배선, 배터리 연결 확인을 추천한다.",
    },
    {
        "id": "overload",
        "scenario": "overload",
        "title": "부하 과다",
        "goal": "발전량보다 부하가 큰 상황을 경고로 설명한다.",
        "talkingPoint": "부하를 줄이거나 배터리 방전 상태를 점검한다.",
    },
]


def get_demo_scenarios() -> list[dict[str, str]]:
    return DEMO_SCENARIOS


def build_demo_report(state: dict[str, Any]) -> dict[str, Any]:
    calculated = recalculate_state(state)
    agent = run_agent_graph(calculated)
    scenario = find_scenario(calculated["scenario"])
    metrics = {
        "time": calculated["time"],
        "fixedPower": calculated["fixedPower"],
        "trackedPower": calculated["trackedPower"],
        "powerGainRate": calculated["powerGainRate"],
        "panelTemp": calculated["panelTemp"],
        "batteryVoltage": calculated["batteryVoltage"],
        "riskLevel": calculated["riskLevel"],
    }
    summary = (
        f"{scenario['title']} 시나리오에서 추적식 발전량은 "
        f"{calculated['trackedPower']:.2f} W, 고정식 발전량은 {calculated['fixedPower']:.2f} W다. "
        f"현재 개선률은 {calculated['powerGainRate']:.1f}%이며 에이전트 판단은 "
        f"{calculated['diagnosis']}이다."
    )

    return {
        "scenario": scenario,
        "summary": summary,
        "metrics": metrics,
        "diagnosis": {
            "title": calculated["diagnosis"],
            "action": calculated["action"],
            "riskLevel": calculated["riskLevel"],
            "reasons": calculated["diagnosisReasons"],
        },
        "vision": calculated["vision"],
        "weather": calculated["weather"],
        "agentTrace": agent["trace"],
        "presentationScript": build_presentation_script(calculated, scenario),
    }


def find_scenario(scenario: str) -> dict[str, str]:
    for item in DEMO_SCENARIOS:
        if item["scenario"] == scenario:
            return item
    return DEMO_SCENARIOS[0]


def build_presentation_script(state: dict[str, Any], scenario: dict[str, str]) -> list[str]:
    return [
        f"이 장면은 {scenario['title']} 시나리오입니다.",
        scenario["talkingPoint"],
        (
            f"현재 패널 각도는 방위각 {state['panelAzimuth']:.1f}도, "
            f"고도각 {state['panelElevation']:.1f}도입니다."
        ),
        (
            f"고정식 {state['fixedPower']:.2f} W와 추적식 {state['trackedPower']:.2f} W를 비교해 "
            f"{state['powerGainRate']:.1f}% 개선률을 계산합니다."
        ),
        f"에이전트 진단은 '{state['diagnosis']}'이며 추천 조치는 '{state['action']}'입니다.",
    ]
