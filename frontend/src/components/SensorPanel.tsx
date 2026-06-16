import { Activity } from "lucide-react";
import { Metric } from "./Metric";
import type { SolarState } from "../types/solar";

export function SensorPanel({ state }: { state: SolarState }) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <Activity size={18} />
        <h2>센서</h2>
      </div>
      <div className="metric-grid">
        <Metric label="좌측 조도" value={state.leftLight.toFixed(2)} />
        <Metric label="우측 조도" value={state.rightLight.toFixed(2)} />
        <Metric label="상단 조도" value={state.topLight.toFixed(2)} />
        <Metric label="하단 조도" value={state.bottomLight.toFixed(2)} />
        <Metric label="전압" value={`${state.voltage.toFixed(2)} V`} />
        <Metric label="전류" value={`${state.current.toFixed(2)} A`} />
        <Metric label="패널 온도" value={`${state.panelTemp.toFixed(1)} °C`} tone={state.panelTemp >= 65 ? "danger" : "default"} />
        <Metric label="배터리" value={`${state.batteryVoltage.toFixed(1)} V`} />
      </div>
    </section>
  );
}
