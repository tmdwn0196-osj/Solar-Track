import { useEffect, useMemo, useState } from "react";
import { AgentPanel } from "./components/AgentPanel";
import { ControlPanel } from "./components/ControlPanel";
import { LogPanel } from "./components/LogPanel";
import { PowerChart } from "./components/PowerChart";
import { SensorPanel } from "./components/SensorPanel";
import { SolarScene } from "./components/SolarScene";
import { VisionPanel } from "./components/VisionPanel";
import { WeatherPanel } from "./components/WeatherPanel";
import { scenarios } from "./data/scenarios";
import { diagnoseState } from "./logic/diagnosisAgent";
import { calculatePower, calculatePowerGain } from "./logic/powerModel";
import { calculateVirtualSensors } from "./logic/sensorModel";
import { calculateSunPosition } from "./logic/sunModel";
import { clamp, runTrackingStep } from "./logic/trackingAgent";
import { inferVirtualVision } from "./logic/visionModel";
import { calculateWeather } from "./logic/weatherModel";
import type { Scenario, SolarState } from "./types/solar";

const initialScenario: Scenario = "normal";

function createInitialState(): SolarState {
  const weather = calculateWeather(initialScenario);
  const vision = inferVirtualVision(initialScenario);
  const sun = calculateSunPosition(9);
  const baseState: SolarState = {
    time: 9,
    running: false,
    autoTracking: true,
    sunAzimuth: sun.sunAzimuth,
    sunElevation: sun.sunElevation,
    panelAzimuth: -35,
    panelElevation: 25,
    leftLight: 0,
    rightLight: 0,
    topLight: 0,
    bottomLight: 0,
    voltage: 0,
    current: 0,
    power: 0,
    fixedPower: 0,
    trackedPower: 0,
    powerGainRate: 0,
    panelTemp: 30,
    batteryVoltage: 12.1,
    scenario: initialScenario,
    phase: "idle",
    diagnosis: "시뮬레이션 대기",
    action: "시작 버튼을 눌러 태양 추적 흐름을 확인하세요.",
    riskLevel: "normal",
    weather,
    vision,
    history: [],
    logs: ["09:00 초기 상태가 준비되었습니다."],
  };

  const calculated = recalculateState(baseState);
  return {
    ...calculated,
    history: [
      {
        time: calculated.time,
        fixedPower: calculated.fixedPower,
        trackedPower: calculated.trackedPower,
      },
    ],
  };
}

function recalculateState(input: SolarState): SolarState {
  const weather = calculateWeather(input.scenario);
  const vision = inferVirtualVision(input.scenario);
  const sun = calculateSunPosition(input.time);
  const panelTemp = input.scenario === "overheat" ? 68 : weather.temperature + 5;
  const sensors = calculateVirtualSensors({
    ...sun,
    panelAzimuth: input.panelAzimuth,
    panelElevation: input.panelElevation,
    scenario: input.scenario,
  });
  const tracked = calculatePower({
    ...sun,
    panelAzimuth: input.panelAzimuth,
    panelElevation: input.panelElevation,
    panelTemp,
    scenario: input.scenario,
    weather,
  });
  const fixed = calculatePower({
    ...sun,
    panelAzimuth: 0,
    panelElevation: 35,
    panelTemp,
    scenario: input.scenario,
    weather,
  });
  const nextState = {
    ...input,
    ...sun,
    ...sensors,
    weather,
    vision,
    panelTemp,
    voltage: tracked.voltage,
    current: tracked.current,
    power: tracked.power,
    fixedPower: fixed.power,
    trackedPower: tracked.power,
    powerGainRate: calculatePowerGain(fixed.power, tracked.power),
    batteryVoltage: input.scenario === "charging_issue" ? 12.0 : 12.1 + tracked.power / 35,
  };
  const diagnosis = diagnoseState(nextState);

  return {
    ...nextState,
    ...diagnosis,
  };
}

function App() {
  const [state, setState] = useState<SolarState>(() => createInitialState());
  const currentScenario = useMemo(
    () => scenarios.find((item) => item.value === state.scenario),
    [state.scenario],
  );

  useEffect(() => {
    if (!state.running) return;

    const timer = window.setInterval(() => {
      setState((previous) => {
        const nextTime = previous.time >= 18 ? 6 : Number((previous.time + 0.1).toFixed(1));
        const prepared = recalculateState({ ...previous, time: nextTime, phase: "weather_check" });
        const tracking = runTrackingStep(prepared);
        const updated = recalculateState({ ...prepared, ...tracking });
        const nextHistory = [
          ...updated.history,
          {
            time: updated.time,
            fixedPower: updated.fixedPower,
            trackedPower: updated.trackedPower,
          },
        ].slice(-60);
        const logMessage = `${formatTime(updated.time)} ${logForPhase(updated)}`;

        return {
          ...updated,
          history: nextHistory,
          logs: appendLog(updated.logs, logMessage),
        };
      });
    }, 900);

    return () => window.clearInterval(timer);
  }, [state.running]);

  function updateScenario(scenario: Scenario) {
    setState((previous) => {
      const next = recalculateState({
        ...previous,
        scenario,
        phase: "weather_check",
        logs: appendLog(previous.logs, `${formatTime(previous.time)} 시나리오를 변경했습니다.`),
      });
      return next;
    });
  }

  function adjustPanel(field: "azimuth" | "elevation", amount: number) {
    setState((previous) => {
      const next = recalculateState({
        ...previous,
        panelAzimuth:
          field === "azimuth" ? clamp(previous.panelAzimuth + amount, -90, 90) : previous.panelAzimuth,
        panelElevation:
          field === "elevation" ? clamp(previous.panelElevation + amount, 0, 70) : previous.panelElevation,
        logs: appendLog(previous.logs, `${formatTime(previous.time)} 수동으로 ${field === "azimuth" ? "방위각" : "고도각"}을 조정했습니다.`),
      });
      return next;
    });
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">v01 React 단독 시뮬레이터</p>
          <h1>SolarTrack Agent</h1>
        </div>
        <div className="status-strip">
          <span>{currentScenario?.label}</span>
          <span>{state.running ? "실행 중" : "정지"}</span>
          <span>{formatTime(state.time)}</span>
        </div>
      </header>

      <div className="workspace">
        <div className="main-column">
          <SolarScene state={state} />
          <PowerChart state={state} />
          <LogPanel logs={state.logs} />
        </div>
        <aside className="side-column">
          <ControlPanel
            running={state.running}
            autoTracking={state.autoTracking}
            scenario={state.scenario}
            onStart={() => setState((previous) => ({ ...previous, running: true }))}
            onPause={() => setState((previous) => ({ ...previous, running: false }))}
            onReset={() => setState(createInitialState())}
            onScenarioChange={updateScenario}
            onAutoTrackingChange={(enabled) =>
              setState((previous) => ({ ...previous, autoTracking: enabled }))
            }
            onManualAdjust={adjustPanel}
          />
          <WeatherPanel weather={state.weather} />
          <SensorPanel state={state} />
          <VisionPanel vision={state.vision} />
          <AgentPanel state={state} />
        </aside>
      </div>
    </main>
  );
}

function formatTime(time: number) {
  const hour = Math.floor(time);
  const minute = Math.round((time - hour) * 60);
  return `${String(hour).padStart(2, "0")}:${String(minute).padStart(2, "0")}`;
}

function logForPhase(state: SolarState) {
  if (state.phase === "hold") return "기상 또는 비전 조건으로 추적을 보류했습니다.";
  if (state.phase === "azimuth_align") return "하부 방위각을 정렬했습니다.";
  if (state.phase === "elevation_align") return "상부 고도각을 정렬했습니다.";
  if (state.phase === "power_verify") return "발전량 개선률을 검증했습니다.";
  return "기상, 센서, 발전량 상태를 갱신했습니다.";
}

function appendLog(logs: string[], message: string) {
  if (logs[logs.length - 1] === message) return logs;
  return [...logs, message].slice(-40);
}

export default App;
