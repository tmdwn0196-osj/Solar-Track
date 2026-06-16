import type { Scenario } from "../types/solar";

type SensorInput = {
  sunAzimuth: number;
  sunElevation: number;
  panelAzimuth: number;
  panelElevation: number;
  scenario: Scenario;
};

function getLightFactor(scenario: Scenario) {
  if (scenario === "cloudy") return 0.45;
  if (scenario === "shade") return 0.58;
  if (scenario === "soiling") return 0.72;
  return 1;
}

export function calculateVirtualSensors(input: SensorInput) {
  const azimuthDiff = input.sunAzimuth - input.panelAzimuth;
  const elevationDiff = input.sunElevation - input.panelElevation;
  const baseLight = getLightFactor(input.scenario);

  const leftLight = Number((baseLight + Math.max(0, -azimuthDiff) / 100).toFixed(2));
  const rightLight = Number((baseLight + Math.max(0, azimuthDiff) / 100).toFixed(2));
  const topLight = Number((baseLight + Math.max(0, elevationDiff) / 100).toFixed(2));
  const bottomLight = Number((baseLight + Math.max(0, -elevationDiff) / 100).toFixed(2));

  return {
    leftLight,
    rightLight,
    topLight,
    bottomLight,
    lightAverage: Number(((leftLight + rightLight + topLight + bottomLight) / 4).toFixed(2)),
  };
}
