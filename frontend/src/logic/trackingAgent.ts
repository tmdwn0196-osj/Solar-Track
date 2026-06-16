import type { SolarState } from "../types/solar";

export function runTrackingStep(state: SolarState): Pick<SolarState, "panelAzimuth" | "panelElevation" | "phase"> {
  if (!state.autoTracking) {
    return {
      panelAzimuth: state.panelAzimuth,
      panelElevation: state.panelElevation,
      phase: "idle",
    };
  }

  if (state.weather.trackingLimited || state.vision.cloudDetected) {
    return {
      panelAzimuth: state.panelAzimuth,
      panelElevation: state.panelElevation,
      phase: "hold",
    };
  }

  const azimuthDiff = state.sunAzimuth - state.panelAzimuth;
  if (Math.abs(azimuthDiff) > 3) {
    return {
      panelAzimuth: clamp(state.panelAzimuth + (azimuthDiff > 0 ? 3 : -3), -90, 90),
      panelElevation: state.panelElevation,
      phase: "azimuth_align",
    };
  }

  const elevationDiff = state.sunElevation - state.panelElevation;
  if (Math.abs(elevationDiff) > 2) {
    return {
      panelAzimuth: state.panelAzimuth,
      panelElevation: clamp(state.panelElevation + (elevationDiff > 0 ? 2 : -2), 0, 70),
      phase: "elevation_align",
    };
  }

  return {
    panelAzimuth: state.panelAzimuth,
    panelElevation: state.panelElevation,
    phase: "power_verify",
  };
}

export function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value));
}
