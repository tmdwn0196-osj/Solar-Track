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

  return {
    leftLight: Number((baseLight + Math.max(0, -azimuthDiff) / 100).toFixed(2)),
    rightLight: Number((baseLight + Math.max(0, azimuthDiff) / 100).toFixed(2)),
    topLight: Number((baseLight + Math.max(0, elevationDiff) / 100).toFixed(2)),
    bottomLight: Number((baseLight + Math.max(0, -elevationDiff) / 100).toFixed(2)),
  };
}
