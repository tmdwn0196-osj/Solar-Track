import { defaultWeatherLocation } from "../data/weatherLocations";
import type { Scenario, WeatherLocation, WeatherSource, WeatherState } from "../types/solar";

type WeatherValues = {
  cloudCover: number;
  rain: boolean;
  temperature: number;
  windSpeed: number;
};

const scenarioWeather: Record<Scenario, WeatherValues> = {
  normal: { cloudCover: 18, rain: false, temperature: 25, windSpeed: 2.1 },
  cloudy: { cloudCover: 82, rain: false, temperature: 24, windSpeed: 3.2 },
  shade: { cloudCover: 24, rain: false, temperature: 27, windSpeed: 2.4 },
  soiling: { cloudCover: 20, rain: false, temperature: 26, windSpeed: 2.0 },
  overheat: { cloudCover: 12, rain: false, temperature: 36, windSpeed: 1.8 },
  charging_issue: { cloudCover: 22, rain: false, temperature: 25, windSpeed: 2.2 },
  overload: { cloudCover: 18, rain: false, temperature: 25, windSpeed: 2.1 },
};

export function calculateWeather(
  scenario: Scenario,
  location: WeatherLocation = defaultWeatherLocation,
  source: WeatherSource = "scenario",
): WeatherState {
  return buildWeatherState({
    values: scenarioWeather[scenario],
    scenario,
    location,
    source,
    collectedAt: source === "fallback" ? "대체 기상 데이터 사용" : "시나리오 기준",
  });
}

function buildWeatherState({
  values,
  scenario,
  location,
  source,
  collectedAt,
}: {
  values: WeatherValues;
  scenario: Scenario;
  location: WeatherLocation;
  source: WeatherSource;
  collectedAt: string;
}): WeatherState {
  const adjustedValues = applyScenarioWeather(values, scenario);
  const trackingLimited =
    adjustedValues.rain || adjustedValues.cloudCover >= 75 || adjustedValues.windSpeed >= 10;

  return {
    label: getWeatherLabel(adjustedValues),
    cloudCover: Math.round(adjustedValues.cloudCover),
    rain: adjustedValues.rain,
    temperature: Number(adjustedValues.temperature.toFixed(1)),
    windSpeed: Number(adjustedValues.windSpeed.toFixed(1)),
    trackingLimited,
    reason: getWeatherReason(adjustedValues, trackingLimited),
    locationName: location.name,
    source,
    collectedAt,
    agentNote: getAgentNote(source, location, scenario, trackingLimited),
  };
}

function applyScenarioWeather(values: WeatherValues, scenario: Scenario): WeatherValues {
  if (scenario === "cloudy") {
    return { ...values, cloudCover: Math.max(values.cloudCover, 82) };
  }

  if (scenario === "overheat") {
    return { ...values, temperature: Math.max(values.temperature, 36), windSpeed: Math.min(values.windSpeed, 2.4) };
  }

  return values;
}

function getWeatherLabel(values: WeatherValues) {
  if (values.rain) return "비";
  if (values.cloudCover >= 75) return "흐림";
  if (values.temperature >= 34) return "고온";
  if (values.cloudCover >= 45) return "구름 많음";
  return "맑음";
}

function getWeatherReason(values: WeatherValues, trackingLimited: boolean) {
  if (values.rain) return "강수가 감지되어 발전기와 장비 보호를 위해 추적을 보류합니다.";
  if (values.windSpeed >= 10) return "풍속이 높아 패널 각도 변경을 보수적으로 판단합니다.";
  if (values.cloudCover >= 75) return "구름량이 높아 일시적인 출력 저하 가능성이 큽니다.";
  if (values.temperature >= 34) return "기온이 높아 패널 온도 상승과 효율 저하를 함께 확인합니다.";
  if (trackingLimited) return "기상 조건이 추적 보류 기준에 가깝습니다.";
  return "추적 동작이 가능한 안정적인 기상 조건입니다.";
}

function getAgentNote(
  source: WeatherSource,
  location: WeatherLocation,
  scenario: Scenario,
  trackingLimited: boolean,
) {
  const sourceText =
    source === "kma-kim"
      ? "기상청 API 허브 KIM 예측"
      : source === "fallback"
        ? "대체 기상 데이터"
        : "시나리오 기준값";
  const decision = trackingLimited ? "모터 보정은 보류 후보로 표시합니다." : "추적 보정을 계속 허용합니다.";
  const scenarioText = scenario === "cloudy" || scenario === "overheat" ? " 시나리오 조건도 함께 반영했습니다." : "";
  const fallbackText = source === "fallback" ? " 기상청 KIM 데이터를 사용할 수 없어 대체 기상 데이터를 사용합니다." : "";

  return `${location.name} 위치의 ${sourceText}을 에이전트 판단 보조 데이터로 사용합니다.${fallbackText} ${decision}${scenarioText}`;
}
