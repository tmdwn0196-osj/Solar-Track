import type { SolarState } from "../types/solar";

type SolarSceneProps = {
  state: SolarState;
};

export function SolarScene({ state }: SolarSceneProps) {
  const sunX = 50 + (state.sunAzimuth / 90) * 38;
  const sunY = 82 - (state.sunElevation / 70) * 64;
  const panelRotation = state.panelAzimuth / 3;

  return (
    <section className="scene-panel" aria-label="태양과 패널 시각화">
      <div className="sky-grid">
        <div
          className="sun"
          style={{ left: `${sunX}%`, top: `${sunY}%` }}
          aria-label="태양 위치"
        />
        <div className="horizon" />
        <div className="mount">
          <div className="azimuth-ring" style={{ transform: `rotate(${panelRotation}deg)` }}>
            <div
              className="panel-face"
              style={{ transform: `rotateX(${state.panelElevation / 1.6}deg)` }}
            >
              <span />
            </div>
          </div>
        </div>
      </div>
      <div className="scene-stats">
        <span>태양 방위각 {state.sunAzimuth.toFixed(1)}도</span>
        <span>태양 고도각 {state.sunElevation.toFixed(1)}도</span>
        <span>패널 방위각 {state.panelAzimuth.toFixed(1)}도</span>
        <span>패널 고도각 {state.panelElevation.toFixed(1)}도</span>
      </div>
    </section>
  );
}
