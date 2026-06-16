import { Minus, Pause, Play, Plus, RotateCcw, SlidersHorizontal } from "lucide-react";
import { scenarios } from "../data/scenarios";
import type { Scenario } from "../types/solar";

type ControlPanelProps = {
  running: boolean;
  autoTracking: boolean;
  scenario: Scenario;
  onStart: () => void;
  onPause: () => void;
  onReset: () => void;
  onScenarioChange: (scenario: Scenario) => void;
  onAutoTrackingChange: (enabled: boolean) => void;
  onManualAdjust: (field: "azimuth" | "elevation", amount: number) => void;
};

export function ControlPanel({
  running,
  autoTracking,
  scenario,
  onStart,
  onPause,
  onReset,
  onScenarioChange,
  onAutoTrackingChange,
  onManualAdjust,
}: ControlPanelProps) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <SlidersHorizontal size={18} />
        <h2>제어</h2>
      </div>

      <div className="button-row">
        <button type="button" onClick={running ? onPause : onStart}>
          {running ? <Pause size={17} /> : <Play size={17} />}
          {running ? "정지" : "시작"}
        </button>
        <button type="button" className="secondary" onClick={onReset}>
          <RotateCcw size={17} />
          초기화
        </button>
      </div>

      <label className="toggle">
        <input
          type="checkbox"
          checked={autoTracking}
          onChange={(event) => onAutoTrackingChange(event.target.checked)}
        />
        <span>자동 추적</span>
      </label>

      <div className="control-group">
        <span>시나리오</span>
        <select
          value={scenario}
          onChange={(event) => onScenarioChange(event.target.value as Scenario)}
        >
          {scenarios.map((item) => (
            <option key={item.value} value={item.value}>
              {item.label}
            </option>
          ))}
        </select>
        <p>{scenarios.find((item) => item.value === scenario)?.description}</p>
      </div>

      <div className="manual-grid">
        <span>방위각</span>
        <button type="button" className="icon-button" aria-label="방위각 감소" onClick={() => onManualAdjust("azimuth", -5)}>
          <Minus size={16} />
        </button>
        <button type="button" className="icon-button" aria-label="방위각 증가" onClick={() => onManualAdjust("azimuth", 5)}>
          <Plus size={16} />
        </button>
        <span>고도각</span>
        <button type="button" className="icon-button" aria-label="고도각 감소" onClick={() => onManualAdjust("elevation", -5)}>
          <Minus size={16} />
        </button>
        <button type="button" className="icon-button" aria-label="고도각 증가" onClick={() => onManualAdjust("elevation", 5)}>
          <Plus size={16} />
        </button>
      </div>
    </section>
  );
}
