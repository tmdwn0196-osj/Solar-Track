import type { Scenario, WeatherState } from "../types/solar";

export function calculateWeather(scenario: Scenario): WeatherState {
  switch (scenario) {
    case "cloudy":
      return {
        label: "흐림",
        cloudCover: 82,
        rain: false,
        temperature: 24,
        windSpeed: 3.2,
        trackingLimited: true,
        reason: "구름량이 높아 일시적인 출력 저하 가능성이 큽니다.",
      };
    case "overheat":
      return {
        label: "고온",
        cloudCover: 12,
        rain: false,
        temperature: 36,
        windSpeed: 1.8,
        trackingLimited: false,
        reason: "기상은 맑지만 패널 온도 상승을 주의해야 합니다.",
      };
    case "shade":
      return {
        label: "맑음",
        cloudCover: 24,
        rain: false,
        temperature: 27,
        windSpeed: 2.4,
        trackingLimited: false,
        reason: "기상 조건은 안정적이며 부분 음영 가능성을 확인합니다.",
      };
    default:
      return {
        label: "맑음",
        cloudCover: 18,
        rain: false,
        temperature: 25,
        windSpeed: 2.1,
        trackingLimited: false,
        reason: "추적 동작이 가능한 안정적인 기상 조건입니다.",
      };
  }
}
