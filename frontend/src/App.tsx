import { useEffect, useMemo, useRef, useState } from "react";
import { AgentPanel } from "./components/AgentPanel";
import { ControlPanel } from "./components/ControlPanel";
import { DashboardPanel } from "./components/DashboardPanel";
import { DemoReportPanel } from "./components/DemoReportPanel";
import { LogPanel } from "./components/LogPanel";
import { ModelPanel } from "./components/ModelPanel";
import { PowerChart } from "./components/PowerChart";
import { SensorPanel } from "./components/SensorPanel";
import { SolarScene } from "./components/SolarScene";
import { VisionPanel } from "./components/VisionPanel";
import { WeatherPanel } from "./components/WeatherPanel";
import { scenarios } from "./data/scenarios";
import { defaultWeatherLocation, findWeatherLocation } from "./data/weatherLocations";
import { diagnoseState } from "./logic/diagnosisAgent";
import { calculatePower, calculatePowerGain } from "./logic/powerModel";
import { calculateVirtualSensors } from "./logic/sensorModel";
import { calculateSunPosition } from "./logic/sunModel";
import { calculateAngleErrors, clamp, runTrackingStep } from "./logic/trackingAgent";
import { inferVirtualVision } from "./logic/visionModel";
import { calculateWeather } from "./logic/weatherModel";
import { requestSimulationStep, requestWeatherContext } from "./logic/apiClient";
import type { Scenario, SolarState, WeatherMode } from "./types/solar";

const initialScenario: Scenario = "normal";
const initialWeatherMode: WeatherMode = "kma-kim";

function createInitialState(): SolarState {
  const weather = calculateWeather(initialScenario, defaultWeatherLocation);
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
    azimuthError: 0,
    elevationError: 0,
    leftLight: 0,
    rightLight: 0,
    topLight: 0,
    bottomLight: 0,
    lightAverage: 0,
    voltage: 0,
    current: 0,
    power: 0,
    fixedPower: 0,
    trackedPower: 0,
    powerGainRate: 0,
    powerBreakdown: {
      maxPower: 10,
      sunFactor: 0,
      angleFactor: 0,
      scenarioFactor: 1,
      tempFactor: 1,
      weatherFactor: 1,
    },
    panelTemp: 30,
    batteryVoltage: 12.1,
    scenario: initialScenario,
    weatherLocationId: defaultWeatherLocation.id,
    weatherMode: initialWeatherMode,
    phase: "idle",
    phaseReason: "시뮬레이션 시작 전입니다.",
    diagnosis: "시뮬레이션 대기",
    action: "시작 버튼을 눌러 태양 추적 흐름을 확인하세요.",
    riskLevel: "normal",
    diagnosisReasons: ["아직 추적 루프가 실행되지 않았습니다."],
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
  const weather = input.weather;
  const vision = inferVirtualVision(input.scenario);
  const sun = calculateSunPosition(input.time);
  const panelTemp = input.scenario === "overheat" ? 68 : weather.temperature + 5;
  const angleErrors = calculateAngleErrors({
    ...sun,
    panelAzimuth: input.panelAzimuth,
    panelElevation: input.panelElevation,
  });
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
    ...angleErrors,
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
    powerBreakdown: tracked.powerBreakdown,
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
  const stateRef = useRef(state);
  const currentScenario = useMemo(
    () => scenarios.find((item) => item.value === state.scenario),
    [state.scenario],
  );

  useEffect(() => {
    stateRef.current = state;
  }, [state]);

  useEffect(() => {
    const location = findWeatherLocation(state.weatherLocationId);
    const weatherMode = state.weatherMode;
    let cancelled = false;

    setState((previous) =>
      recalculateState({
        ...previous,
        weather: calculateWeather(previous.scenario, location, weatherMode === "scenario" ? "scenario" : "fallback"),
        logs: appendLog(
          previous.logs,
          `${formatTime(previous.time)} ${location.name} ${weatherMode === "kma-kim" ? "기상청 KIM" : "시나리오 기반"} 기상 수집을 시작했습니다.`,
        ),
      }),
    );

    async function syncWeather() {
      const weather =
        weatherMode === "scenario"
          ? calculateWeather(state.scenario, location)
          : await requestWeatherContext(state.scenario, location.id, weatherMode).catch(() =>
              calculateWeather(state.scenario, location, "fallback"),
            );
      if (cancelled) return;

      setState((previous) => {
        if (
          previous.weatherLocationId !== location.id ||
          previous.scenario !== state.scenario ||
          previous.weatherMode !== weatherMode
        ) {
          return previous;
        }

        return recalculateState({
          ...previous,
          weather,
          logs: appendLog(previous.logs, `${formatTime(previous.time)} ${weather.locationName} 기상 반영: ${weather.label}`),
        });
      });
    }

    void syncWeather();

    return () => {
      cancelled = true;
    };
  }, [state.weatherLocationId, state.scenario, state.weatherMode]);

  useEffect(() => {
    if (!state.running) return;

    let inFlight = false;
    let cancelled = false;

    const timer = window.setInterval(() => {
      if (inFlight) return;
      inFlight = true;
      const requestState = stateRef.current;

      requestSimulationStep(requestState)
        .then((nextState) => {
          if (cancelled) return;
          setState((previous) => {
            if (
              !previous.running ||
              previous.scenario !== requestState.scenario ||
              previous.weatherLocationId !== requestState.weatherLocationId
            ) {
              return previous;
            }

            return {
              ...nextState,
              running: previous.running,
              autoTracking: previous.autoTracking,
            };
          });
        })
        .catch(() => {
          if (cancelled) return;
          setState(advanceLocalSimulation);
        })
        .finally(() => {
          inFlight = false;
        });
    }, 900);

    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, [state.running]);

  function updateScenario(scenario: Scenario) {
    setState((previous) =>
      recalculateState({
        ...previous,
        scenario,
        phase: "weather_check",
        logs: appendLog(previous.logs, `${formatTime(previous.time)} 시나리오를 변경했습니다.`),
      }),
    );
  }

  function updateWeatherLocation(locationId: string) {
    setState((previous) =>
      recalculateState({
        ...previous,
        weatherLocationId: locationId,
        phase: "weather_check",
        logs: appendLog(previous.logs, `${formatTime(previous.time)} 기상 위치를 변경했습니다.`),
      }),
    );
  }

  function updateWeatherMode(weatherMode: WeatherMode) {
    setState((previous) =>
      recalculateState({
        ...previous,
        weatherMode,
        phase: "weather_check",
        logs: appendLog(
          previous.logs,
          `${formatTime(previous.time)} 기상 모드를 ${weatherMode === "kma-kim" ? "기상청 KIM" : "시나리오 기반"}으로 변경했습니다.`,
        ),
      }),
    );
  }

  function adjustPanel(field: "azimuth" | "elevation", amount: number) {
    setState((previous) =>
      recalculateState({
        ...previous,
        panelAzimuth:
          field === "azimuth" ? clamp(previous.panelAzimuth + amount, -90, 90) : previous.panelAzimuth,
        panelElevation:
          field === "elevation" ? clamp(previous.panelElevation + amount, 0, 70) : previous.panelElevation,
        logs: appendLog(previous.logs, `${formatTime(previous.time)} 수동으로 ${field === "azimuth" ? "방위각" : "고도각"}을 조정했습니다.`),
      }),
    );
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">v11 시연 시나리오 리포트</p>
          <h1>SolarTrack 에이전트</h1>
        </div>
        <div className="status-strip">
          <span>{currentScenario?.label}</span>
          <span>{state.running ? "실행 중" : "정지"}</span>
          <span>{formatTime(state.time)}</span>
        </div>
      </header>

      <DashboardPanel state={state} />

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
            weatherLocationId={state.weatherLocationId}
            weatherMode={state.weatherMode}
            onStart={() => setState((previous) => ({ ...previous, running: true }))}
            onPause={() => setState((previous) => ({ ...previous, running: false }))}
            onReset={() => setState(createInitialState())}
            onScenarioChange={updateScenario}
            onWeatherLocationChange={updateWeatherLocation}
            onWeatherModeChange={updateWeatherMode}
            onAutoTrackingChange={(enabled) =>
              setState((previous) => ({ ...previous, autoTracking: enabled }))
            }
            onManualAdjust={adjustPanel}
          />
          <WeatherPanel weather={state.weather} />
          <SensorPanel state={state} />
          <ModelPanel powerBreakdown={state.powerBreakdown} />
          <VisionPanel vision={state.vision} />
          <AgentPanel state={state} />
          <DemoReportPanel state={state} />
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
  return state.phaseReason || "기상, 센서, 발전량 상태를 갱신했습니다.";
}

function advanceLocalSimulation(previous: SolarState): SolarState {
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
}

function appendLog(logs: string[], message: string) {
  if (logs[logs.length - 1] === message) return logs;
  return [...logs, message].slice(-40);
}

export default App;
