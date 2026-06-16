import { CloudSun } from "lucide-react";
import { Metric } from "./Metric";
import type { WeatherState } from "../types/solar";

const sourceLabels: Record<WeatherState["source"], string> = {
  scenario: "시나리오",
  "open-meteo": "Open-Meteo",
  fallback: "대체값",
};

export function WeatherPanel({ weather }: { weather: WeatherState }) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <CloudSun size={18} />
        <h2>기상 Agent</h2>
      </div>
      <div className="metric-grid">
        <Metric label="위치" value={weather.locationName} />
        <Metric label="출처" value={sourceLabels[weather.source]} tone={weather.source === "fallback" ? "warn" : "good"} />
        <Metric label="상태" value={weather.label} tone={weather.trackingLimited ? "warn" : "good"} />
        <Metric label="구름량" value={`${weather.cloudCover}%`} />
        <Metric label="강수" value={weather.rain ? "있음" : "없음"} tone={weather.rain ? "warn" : "default"} />
        <Metric label="풍속" value={`${weather.windSpeed.toFixed(1)} m/s`} />
      </div>
      <p className="panel-note">{weather.reason}</p>
      <p className="panel-note">{weather.agentNote}</p>
      <p className="panel-note">수집 시각: {weather.collectedAt}</p>
    </section>
  );
}
