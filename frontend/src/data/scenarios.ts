import type { Scenario } from "../types/solar";

export const scenarios: {
  value: Scenario;
  label: string;
  description: string;
}[] = [
  {
    value: "normal",
    label: "정상",
    description: "맑고 안정적인 발전 조건",
  },
  {
    value: "cloudy",
    label: "흐림",
    description: "구름량이 많아 전체 광량이 낮은 상황",
  },
  {
    value: "shade",
    label: "부분 음영",
    description: "패널 일부가 주변 구조물이나 그림자에 가려진 상황",
  },
  {
    value: "soiling",
    label: "패널 오염",
    description: "먼지나 물자국으로 출력이 낮아지는 상황",
  },
  {
    value: "overheat",
    label: "패널 과열",
    description: "패널 온도가 높아 효율이 떨어지는 상황",
  },
  {
    value: "charging_issue",
    label: "충전 문제",
    description: "패널 출력은 있지만 배터리 반응이 낮은 상황",
  },
  {
    value: "overload",
    label: "부하 과다",
    description: "소비 전력이 발전량보다 큰 상황",
  },
];
