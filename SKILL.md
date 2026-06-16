---
name: solar-track-project
description: 'Project rules for working on SolarTrack in C:\Projects\solar-track. Use when setting up, running, validating, or extending the Python 3.12 uv project and the planned SolarTrack React, FastAPI, LangGraph, and ESP32 simulator described in the project design document.'
---

# SolarTrack Project Rules

## Project Shape

- Treat this repository as the SolarTrack Agent simulator workspace.
- Current runnable project is a Python 3.12 `uv` project at the repository root.
- The project design document is the root Markdown file matching `SolarTrack_Agent_*.md`; read it as UTF-8 when implementing simulator behavior.
- Preserve the staged direction from the design document: start with a standalone simulator, then split backend/agent/hardware layers only when needed.

## Setup And Run

- Prefer `uv` for all Python commands.
- Do not assume `python` is available on PATH in this workspace.
- Run the current app with:

```powershell
uv run python main.py
```

- Check the managed Python version with:

```powershell
uv run python --version
```

- Sync dependencies after changing `pyproject.toml`:

```powershell
uv sync
```

## Validation

- After Python code changes in the current minimal project, at minimum run:

```powershell
uv run python -m py_compile main.py
uv run python main.py
```

- When source packages are added, compile explicit source paths such as `src/` instead of recursively compiling the whole repository.
- If tests are added later, prefer:

```powershell
uv run pytest
```

- Do not treat `.venv` contents as source files.

## Implementation Rules

- Keep simulation math deterministic and isolated from UI code.
- Model solar position, virtual sensors, power calculation, tracking control, and diagnosis as separate modules.
- Keep scenario names stable: `normal`, `cloudy`, `shade`, `soiling`, `overheat`, `charging_issue`, `overload`.
- Keep risk levels stable: `normal`, `warning`, `danger`.
- Prefer explicit state objects over loosely coupled globals.
- Do not introduce an LLM into motor control, real-time sensor loops, angle calculation, or emergency stop logic.
- Use LLM/agent behavior only for diagnosis explanations, action recommendations, reports, and user Q&A.

## Frontend Direction

- If implementing the design document's React simulator, create it as a Vite + React + TypeScript app unless existing project structure says otherwise.
- Keep the first implementation focused on a usable simulator, not a marketing landing page.
- Expected React separation:
  - `types/solar.ts` for shared state and enum-like types.
  - `logic/` for sun, sensor, power, tracking, and diagnosis models.
  - `components/` for scene, controls, sensor values, agent status, and charts.
  - `data/scenarios.ts` for scenario metadata.
- Use `recharts` only when graphing is needed; do not add it before a chart exists.

## Backend And Agent Direction

- Add FastAPI only when the frontend needs a backend boundary.
- Add LangGraph only after the deterministic simulator logic is working and there is a clear agent state graph to express.
- Keep hardware-facing ESP32 commands behind a backend boundary; never put direct hardware-control assumptions in UI code.

## File And Encoding Rules

- Keep new source files UTF-8.
- Korean documentation and UI text are allowed where they clarify the simulator domain.
- If PowerShell output shows broken Korean text, set UTF-8 output before reading files:

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

## Git Hygiene

- Do not commit `.venv`, `__pycache__`, build outputs, or generated dependency folders.
- Before broad edits, check `git status --short` and preserve unrelated user changes.
