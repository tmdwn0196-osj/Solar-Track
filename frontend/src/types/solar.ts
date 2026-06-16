export type Scenario =
  | "normal"
  | "cloudy"
  | "shade"
  | "soiling"
  | "overheat"
  | "charging_issue"
  | "overload";

export type RiskLevel = "normal" | "warning" | "danger";

export type WeatherSource = "scenario" | "open-meteo" | "fallback";

export type WeatherLocation = {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  note: string;
};

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
  locationName: string;
  source: WeatherSource;
  collectedAt: string;
  agentNote: string;
};

export type VisionState = {
  cloudDetected: boolean;
  soilingDetected: boolean;
  shadeDetected: boolean;
  note: string;
};

export type PowerBreakdown = {
  maxPower: number;
  sunFactor: number;
  angleFactor: number;
  scenarioFactor: number;
  tempFactor: number;
  weatherFactor: number;
};

export type DiagnosisResult = {
  diagnosis: string;
  action: string;
  riskLevel: RiskLevel;
  diagnosisReasons: string[];
};

export type SolarHistoryPoint = {
  time: number;
  fixedPower: number;
  trackedPower: number;
};

export type SolarState = {
  time: number;
  running: boolean;
  autoTracking: boolean;
  sunAzimuth: number;
  sunElevation: number;
  panelAzimuth: number;
  panelElevation: number;
  azimuthError: number;
  elevationError: number;
  leftLight: number;
  rightLight: number;
  topLight: number;
  bottomLight: number;
  lightAverage: number;
  voltage: number;
  current: number;
  power: number;
  fixedPower: number;
  trackedPower: number;
  powerGainRate: number;
  powerBreakdown: PowerBreakdown;
  panelTemp: number;
  batteryVoltage: number;
  scenario: Scenario;
  weatherLocationId: string;
  phase: AgentPhase;
  phaseReason: string;
  diagnosis: string;
  action: string;
  riskLevel: RiskLevel;
  diagnosisReasons: string[];
  weather: WeatherState;
  vision: VisionState;
  history: SolarHistoryPoint[];
  logs: string[];
};
