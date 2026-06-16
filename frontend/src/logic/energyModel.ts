import type { SolarHistoryPoint } from "../types/solar";

export type EnergySummary = {
  fixedWh: number;
  trackedWh: number;
  gainWh: number;
  gainRate: number;
};

export function calculateEnergySummary(history: SolarHistoryPoint[]): EnergySummary {
  if (history.length < 2) {
    return {
      fixedWh: 0,
      trackedWh: 0,
      gainWh: 0,
      gainRate: 0,
    };
  }

  let fixedWh = 0;
  let trackedWh = 0;

  for (let index = 1; index < history.length; index += 1) {
    const previous = history[index - 1];
    const current = history[index];
    const elapsedHours = getElapsedHours(previous.time, current.time);

    fixedWh += ((previous.fixedPower + current.fixedPower) / 2) * elapsedHours;
    trackedWh += ((previous.trackedPower + current.trackedPower) / 2) * elapsedHours;
  }

  const gainWh = trackedWh - fixedWh;
  const gainRate = fixedWh <= 0 ? 0 : (gainWh / fixedWh) * 100;

  return {
    fixedWh: roundEnergy(fixedWh),
    trackedWh: roundEnergy(trackedWh),
    gainWh: roundEnergy(gainWh),
    gainRate: Number(gainRate.toFixed(1)),
  };
}

function getElapsedHours(previousTime: number, currentTime: number) {
  const delta = currentTime - previousTime;
  if (delta > 0 && delta <= 1) return delta;
  return 0.1;
}

function roundEnergy(value: number) {
  return Number(value.toFixed(2));
}
