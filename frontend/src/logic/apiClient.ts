import type { Scenario, SolarState, WeatherMode, WeatherState } from "../types/solar";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";
const REQUEST_TIMEOUT_MS = 2500;

type SimulateStepResponse = {
  state: SolarState;
};

type WeatherContextResponse = {
  weather: WeatherState;
};

export async function requestSimulationStep(state: SolarState): Promise<SolarState> {
  const data = await postJson<SimulateStepResponse>("/api/simulate/step", { state });
  return data.state;
}

export async function requestWeatherContext(
  scenario: Scenario,
  locationId: string,
  mode: WeatherMode,
): Promise<WeatherState> {
  const data = await postJson<WeatherContextResponse>("/api/weather/context", {
    scenario,
    locationId,
    mode,
  });
  return data.weather;
}

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
      signal: controller.signal,
    });

    if (!response.ok) {
      throw new Error(`SolarTrack API ${response.status}`);
    }

    return (await response.json()) as T;
  } finally {
    window.clearTimeout(timeoutId);
  }
}
