import { LayoutDashboard } from "lucide-react";
import { calculateEnergySummary } from "../logic/energyModel";
import type { SolarState } from "../types/solar";
import { Metric } from "./Metric";

const riskLabels: Record<SolarState["riskLevel"], string> = {
  normal: "정상",
  warning: "주의",
  danger: "위험",
};

const phaseLabels: Record<SolarState["phase"], string> = {
  idle: "대기",
  weather_check: "기상 확인",
  azimuth_align: "방위각 정렬",
  elevation_align: "고도각 정렬",
  power_verify: "발전량 검증",
  hold: "추적 보류",
  diagnosis: "진단",
};

export function DashboardPanel({ state }: { state: SolarState }) {
  const energy = calculateEnergySummary(state.history);
  const riskTone = state.riskLevel === "danger" ? "danger" : state.riskLevel === "warning" ? "warn" : "good";

  return (
    <section className="panel dashboard-panel">
      <div className="panel-heading">
        <LayoutDashboard size={18} />
        <h2>대시보드</h2>
      </div>
      <div className="dashboard-grid">
        <Metric label="운전 상태" value={state.running ? "실행 중" : "정지"} tone={state.running ? "good" : "default"} />
        <Metric label="에이전트 단계" value={phaseLabels[state.phase]} tone={state.phase === "hold" ? "warn" : "default"} />
        <Metric label="위험도" value={riskLabels[state.riskLevel]} tone={riskTone} />
        <Metric
          label="현재 개선률"
          value={`${state.powerGainRate.toFixed(1)}%`}
          tone={state.powerGainRate >= 5 ? "good" : "default"}
        />
        <Metric label="누적 개선량" value={`${energy.gainWh.toFixed(2)} Wh`} tone={energy.gainWh > 0 ? "good" : "default"} />
        <Metric label="기상 계수" value={state.powerBreakdown.weatherFactor.toFixed(2)} tone={state.weather.trackingLimited ? "warn" : "good"} />
      </div>
    </section>
  );
}
