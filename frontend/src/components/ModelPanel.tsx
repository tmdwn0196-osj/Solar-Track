import { Calculator } from "lucide-react";
import type { PowerBreakdown } from "../types/solar";
import { Metric } from "./Metric";

export function ModelPanel({ powerBreakdown }: { powerBreakdown: PowerBreakdown }) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <Calculator size={18} />
        <h2>계산 모델</h2>
      </div>
      <p className="formula">
        발전량 = 최대출력 × 태양광 계수 × 각도 일치율 × 시나리오 계수 × 온도 계수 × 기상 계수
      </p>
      <div className="metric-grid">
        <Metric label="최대출력" value={`${powerBreakdown.maxPower.toFixed(0)} W`} />
        <Metric label="태양광 계수" value={powerBreakdown.sunFactor.toFixed(2)} />
        <Metric label="각도 일치율" value={powerBreakdown.angleFactor.toFixed(2)} />
        <Metric label="시나리오 계수" value={powerBreakdown.scenarioFactor.toFixed(2)} />
        <Metric label="온도 계수" value={powerBreakdown.tempFactor.toFixed(2)} />
        <Metric label="기상 계수" value={powerBreakdown.weatherFactor.toFixed(2)} />
      </div>
    </section>
  );
}
