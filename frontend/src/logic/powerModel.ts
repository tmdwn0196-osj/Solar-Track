import type { PowerBreakdown, Scenario, WeatherState } from "../types/solar";

type PowerInput = {
  sunAzimuth: number;
  sunElevation: number;
  panelAzimuth: number;
  panelElevation: number;
  panelTemp: number;
  scenario: Scenario;
  weather: WeatherState;
};

function getScenarioFactor(scenario: Scenario) {
  if (scenario === "cloudy") return 0.52;
  if (scenario === "shade") return 0.58;
  if (scenario === "soiling") return 0.72;
  if (scenario === "overheat") return 0.92;
  return 1;
}

function getTempFactor(panelTemp: number) {
  if (panelTemp <= 45) return 1;
  return Math.max(0.6, 1 - (panelTemp - 45) * 0.012);
}

function getWeatherFactor(weather: WeatherState) {
  if (weather.rain) return 0.35;
  return Math.max(0.42, 1 - weather.cloudCover / 180);
}

export function calculatePower(input: PowerInput) {
  const maxPower = 10;
  const azimuthError = Math.abs(input.sunAzimuth - input.panelAzimuth);
  const elevationError = Math.abs(input.sunElevation - input.panelElevation);
  const angleFactor = Math.max(0, 1 - (azimuthError + elevationError) / 140);
  const sunFactor = Math.max(0, input.sunElevation / 70);
  const scenarioFactor = getScenarioFactor(input.scenario);
  const tempFactor = getTempFactor(input.panelTemp);
  const weatherFactor = getWeatherFactor(input.weather);
  const powerBreakdown: PowerBreakdown = {
    maxPower,
    sunFactor: roundFactor(sunFactor),
    angleFactor: roundFactor(angleFactor),
    scenarioFactor: roundFactor(scenarioFactor),
    tempFactor: roundFactor(tempFactor),
    weatherFactor: roundFactor(weatherFactor),
  };
  const power =
    maxPower *
    sunFactor *
    angleFactor *
    scenarioFactor *
    tempFactor *
    weatherFactor;
  const voltage = 6 * Math.max(0.42, sunFactor);
  const current = voltage > 0 ? power / voltage : 0;

  return {
    power: Number(power.toFixed(2)),
    voltage: Number(voltage.toFixed(2)),
    current: Number(current.toFixed(2)),
    powerBreakdown,
  };
}

export function calculatePowerGain(fixedPower: number, trackedPower: number) {
  if (fixedPower <= 0) return 0;
  return Number((((trackedPower - fixedPower) / fixedPower) * 100).toFixed(1));
}

function roundFactor(value: number) {
  return Number(value.toFixed(2));
}
