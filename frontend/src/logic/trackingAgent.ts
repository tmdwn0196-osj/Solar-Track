import type { SolarState } from "../types/solar";

type TrackingStep = Pick<
  SolarState,
  "panelAzimuth" | "panelElevation" | "phase" | "phaseReason" | "azimuthError" | "elevationError"
>;

export function runTrackingStep(state: SolarState): TrackingStep {
  const { azimuthError, elevationError } = calculateAngleErrors(state);

  if (!state.autoTracking) {
    return {
      panelAzimuth: state.panelAzimuth,
      panelElevation: state.panelElevation,
      azimuthError,
      elevationError,
      phase: "idle",
      phaseReason: "자동 추적이 꺼져 있어 현재 패널 각도를 유지합니다.",
    };
  }

  if (state.weather.trackingLimited || state.vision.cloudDetected) {
    return {
      panelAzimuth: state.panelAzimuth,
      panelElevation: state.panelElevation,
      azimuthError,
      elevationError,
      phase: "hold",
      phaseReason: state.weather.trackingLimited
        ? "기상 조건으로 인한 일시적 출력 저하 가능성이 있어 모터 동작을 보류합니다."
        : "비전 결과에서 구름이 감지되어 각도 보정을 보류합니다.",
    };
  }

  if (Math.abs(azimuthError) > 3) {
    return {
      panelAzimuth: clamp(state.panelAzimuth + (azimuthError > 0 ? 3 : -3), -90, 90),
      panelElevation: state.panelElevation,
      azimuthError,
      elevationError,
      phase: "azimuth_align",
      phaseReason: `태양 방위각 차이가 ${azimuthError.toFixed(1)}°라서 방위각을 먼저 정렬합니다.`,
    };
  }

  if (Math.abs(elevationError) > 2) {
    return {
      panelAzimuth: state.panelAzimuth,
      panelElevation: clamp(state.panelElevation + (elevationError > 0 ? 2 : -2), 0, 70),
      azimuthError,
      elevationError,
      phase: "elevation_align",
      phaseReason: `방위각 정렬 후 남은 고도각 차이 ${elevationError.toFixed(1)}°를 보정합니다.`,
    };
  }

  return {
    panelAzimuth: state.panelAzimuth,
    panelElevation: state.panelElevation,
    azimuthError,
    elevationError,
    phase: "power_verify",
    phaseReason: "방위각과 고도각이 허용 범위에 들어와 발전량 개선률을 검증합니다.",
  };
}

export function calculateAngleErrors(state: Pick<SolarState, "sunAzimuth" | "sunElevation" | "panelAzimuth" | "panelElevation">) {
  return {
    azimuthError: Number((state.sunAzimuth - state.panelAzimuth).toFixed(1)),
    elevationError: Number((state.sunElevation - state.panelElevation).toFixed(1)),
  };
}

export function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value));
}
