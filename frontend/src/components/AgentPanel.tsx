import { Bot } from "lucide-react";
import type { SolarState } from "../types/solar";

const phaseLabels: Record<SolarState["phase"], string> = {
  idle: "대기",
  weather_check: "기상 확인",
  azimuth_align: "방위각 정렬",
  elevation_align: "고도각 정렬",
  power_verify: "발전량 검증",
  hold: "추적 보류",
  diagnosis: "진단",
};

const riskLabels: Record<SolarState["riskLevel"], string> = {
  normal: "정상",
  warning: "주의",
  danger: "위험",
};

export function AgentPanel({ state }: { state: SolarState }) {
  return (
    <section className={`panel agent-panel risk-${state.riskLevel}`}>
      <div className="panel-heading">
        <Bot size={18} />
        <h2>에이전트</h2>
        <span className={`risk-badge risk-badge-${state.riskLevel}`}>{riskLabels[state.riskLevel]}</span>
      </div>
      <dl className="agent-list">
        <div>
          <dt>현재 단계</dt>
          <dd>{phaseLabels[state.phase]}</dd>
        </div>
        <div>
          <dt>단계 사유</dt>
          <dd>{state.phaseReason}</dd>
        </div>
        <div>
          <dt>정렬 오차</dt>
          <dd>
            방위각 {state.azimuthError.toFixed(1)}°, 고도각 {state.elevationError.toFixed(1)}°
          </dd>
        </div>
        <div>
          <dt>진단</dt>
          <dd>{state.diagnosis}</dd>
        </div>
        <div>
          <dt>진단 근거</dt>
          <dd>
            <ul className="reason-list">
              {state.diagnosisReasons.map((reason) => (
                <li key={reason}>{reason}</li>
              ))}
            </ul>
          </dd>
        </div>
        <div>
          <dt>조치</dt>
          <dd>{state.action}</dd>
        </div>
      </dl>
    </section>
  );
}
