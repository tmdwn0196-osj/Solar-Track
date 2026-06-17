import { Minus, Pause, Play, Plus, RotateCcw, SlidersHorizontal } from "lucide-react";
import { scenarios } from "../data/scenarios";
import { weatherLocations } from "../data/weatherLocations";
import type { Scenario, WeatherMode } from "../types/solar";

type ControlPanelProps = {
  running: boolean;
  autoTracking: boolean;
  scenario: Scenario;
  weatherLocationId: string;
  weatherMode: WeatherMode;
  onStart: () => void;
  onPause: () => void;
  onReset: () => void;
  onScenarioChange: (scenario: Scenario) => void;
  onWeatherLocationChange: (locationId: string) => void;
  onWeatherModeChange: (mode: WeatherMode) => void;
  onAutoTrackingChange: (enabled: boolean) => void;
  onManualAdjust: (field: "azimuth" | "elevation", amount: number) => void;
};

export function ControlPanel({
  running,
  autoTracking,
  scenario,
  weatherLocationId,
  weatherMode,
  onStart,
  onPause,
  onReset,
  onScenarioChange,
  onWeatherLocationChange,
  onWeatherModeChange,
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
        <select value={scenario} onChange={(event) => onScenarioChange(event.target.value as Scenario)}>
          {scenarios.map((item) => (
            <option key={item.value} value={item.value}>
              {item.label}
            </option>
          ))}
        </select>
        <p>{scenarios.find((item) => item.value === scenario)?.description}</p>
      </div>

      <div className="control-group">
        <span>기상 위치</span>
        <select value={weatherLocationId} onChange={(event) => onWeatherLocationChange(event.target.value)}>
          {weatherLocations.map((location) => (
            <option key={location.id} value={location.id}>
              {location.name}
            </option>
          ))}
        </select>
        <p>{weatherLocations.find((location) => location.id === weatherLocationId)?.note}</p>
      </div>

      <div className="control-group">
        <span>기상 모드</span>
        <select value={weatherMode} onChange={(event) => onWeatherModeChange(event.target.value as WeatherMode)}>
          <option value="kma-kim">기상청 KIM</option>
          <option value="scenario">시나리오 기반</option>
        </select>
        <p>
          {weatherMode === "kma-kim"
            ? "KIM 예측 온도를 우선 반영하고, 미연동 변수는 시나리오 값을 함께 사용합니다."
            : "외부 기상 API 없이 선택한 시나리오의 고정 기상값만 사용합니다."}
        </p>
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
