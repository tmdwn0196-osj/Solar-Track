import { LineChart } from "lucide-react";
import { calculateEnergySummary } from "../logic/energyModel";
import type { SolarState } from "../types/solar";
import { Metric } from "./Metric";

export function PowerChart({ state }: { state: SolarState }) {
  const points = state.history.slice(-30);
  const energy = calculateEnergySummary(state.history);
  const maxPower = Math.max(10, ...points.flatMap((point) => [point.fixedPower, point.trackedPower]));
  const chartWidth = 360;
  const chartHeight = 140;
  const buildPath = (key: "fixedPower" | "trackedPower") =>
    (points.length === 1 ? [points[0], points[0]] : points)
      .map((point, index, pathPoints) => {
        const x = pathPoints.length <= 1 ? 0 : (index / (pathPoints.length - 1)) * chartWidth;
        const y = chartHeight - (point[key] / maxPower) * chartHeight;
        return `${index === 0 ? "M" : "L"} ${x.toFixed(1)} ${y.toFixed(1)}`;
      })
      .join(" ");

  return (
    <section className="panel chart-panel">
      <div className="panel-heading">
        <LineChart size={18} />
        <h2>발전량</h2>
      </div>
      <div className="power-summary">
        <Metric label="고정식" value={`${state.fixedPower.toFixed(2)} W`} />
        <Metric label="추적식" value={`${state.trackedPower.toFixed(2)} W`} tone="good" />
        <Metric
          label="개선률"
          value={`${state.powerGainRate.toFixed(1)}%`}
          tone={state.powerGainRate >= 5 ? "good" : "default"}
        />
      </div>
      <svg className="power-graph" viewBox={`0 0 ${chartWidth} ${chartHeight}`} role="img" aria-label="발전량 그래프">
        <path className="grid-line" d="M0 35 H360 M0 70 H360 M0 105 H360" />
        <path className="fixed-line" d={buildPath("fixedPower")} />
        <path className="tracked-line" d={buildPath("trackedPower")} />
      </svg>
      <div className="legend">
        <span><i className="fixed-dot" />고정식</span>
        <span><i className="tracked-dot" />추적식</span>
      </div>
      <div className="energy-summary">
        <span>누적 고정식 {energy.fixedWh.toFixed(2)} Wh</span>
        <span>누적 추적식 {energy.trackedWh.toFixed(2)} Wh</span>
        <span>누적 개선률 {energy.gainRate.toFixed(1)}%</span>
      </div>
    </section>
  );
}
