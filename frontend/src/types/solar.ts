export type Scenario =
  | "normal"
  | "cloudy"
  | "shade"
  | "soiling"
  | "overheat"
  | "charging_issue"
  | "overload";

export type RiskLevel = "normal" | "warning" | "danger";

export type AgentPhase =
  | "idle"
  | "weather_check"
  | "azimuth_align"
  | "elevation_align"
  | "power_verify"
  | "hold"
  | "diagnosis";

export type WeatherState = {
  label: string;
  cloudCover: number;
  rain: boolean;
  temperature: number;
  windSpeed: number;
  trackingLimited: boolean;
  reason: string;
};

export type VisionState = {
  cloudDetected: boolean;
  soilingDetected: boolean;
  shadeDetected: boolean;
  note: string;
};

export type SolarState = {
  time: number;
  running: boolean;
  autoTracking: boolean;
  sunAzimuth: number;
  sunElevation: number;
  panelAzimuth: number;
  panelElevation: number;
  leftLight: number;
  rightLight: number;
  topLight: number;
  bottomLight: number;
  voltage: number;
  current: number;
  power: number;
  fixedPower: number;
  trackedPower: number;
  powerGainRate: number;
  panelTemp: number;
  batteryVoltage: number;
  scenario: Scenario;
  phase: AgentPhase;
  diagnosis: string;
  action: string;
  riskLevel: RiskLevel;
  weather: WeatherState;
  vision: VisionState;
  history: { time: number; fixedPower: number; trackedPower: number }[];
  logs: string[];
};
