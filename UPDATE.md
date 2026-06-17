## 2026-06-17 10:11 KST - v08 LangGraph Agent 구조

- Changed: `pyproject.toml`, `uv.lock`, `backend/agent_graph.py`, `backend/app.py`, `backend/README.md`, `docs/v08_langgraph_agent_plan.md`, `README.md`
- Actions: LangGraph `StateGraph` 기반 Agent 흐름을 추가하고 센서, 기상, 비전, 안전 분기, 추적 정렬, 발전량 검증, 진단, 리포트 생성 노드를 규칙 기반으로 구성했다. `/api/agent/evaluate` 엔드포인트를 추가해 현재 SolarState를 그래프에 전달하고 trace와 진단 결과를 받을 수 있게 했다.
- Validation: `uv sync` installed LangGraph dependencies; `uv run python -m py_compile main.py backend\__init__.py backend\app.py backend\models.py backend\simulation.py backend\agent_graph.py` passed; `uv run python main.py` printed `Hello from solar-track!`; `npm run build` passed; FastAPI TestClient calls for `/api/agent/evaluate` normal and cloudy paths passed; temporary `uvicorn` server returned `/api/health` successfully.

## 2026-06-17 10:03 KST - v07 FastAPI 백엔드 분리

- Changed: `pyproject.toml`, `uv.lock`, `backend/__init__.py`, `backend/app.py`, `backend/models.py`, `backend/simulation.py`, `backend/README.md`, `frontend/README.md`, `frontend/src/App.tsx`, `frontend/src/logic/apiClient.ts`, `README.md`
- Actions: FastAPI 앱과 v07 API 엔드포인트를 추가하고, 프론트엔드 시뮬레이션 스텝과 기상 컨텍스트가 백엔드 API를 우선 호출하도록 연결했다. 백엔드 미실행 또는 요청 실패 시 기존 브라우저 내 계산으로 자동 fallback되도록 유지했다.
- Validation: `npm run build` passed; `uv sync` installed backend dependencies; `uv run python -m py_compile main.py backend\__init__.py backend\app.py backend\models.py backend\simulation.py` passed; `uv run python main.py` printed `Hello from solar-track!`; FastAPI TestClient calls for `/api/health`, `/api/simulate/step`, `/api/weather/context` passed; temporary `uvicorn` server returned `/api/health` successfully.

## 2026-06-16 15:48 KST - v06 대시보드 UI 구현

- Changed: `frontend/README.md`, `frontend/src/App.tsx`, `frontend/src/types/solar.ts`, `frontend/src/logic/energyModel.ts`, `frontend/src/components/DashboardPanel.tsx`, `frontend/src/components/PowerChart.tsx`, `frontend/src/styles.css`, `.gitignore`
- Actions: 상단 대시보드 요약을 추가하고 운전 상태, Agent 단계, 위험도, 현재 개선률, 누적 개선량, 기상 계수를 한눈에 확인하도록 구성함. 발전량 패널에 누적 고정식/추적식 발전량과 누적 개선률을 추가함
- Validation: `npm run build` passed; `npm audit --audit-level=high` found 0 vulnerabilities; `uv run python -m py_compile main.py` passed; `uv run python main.py` printed `Hello from solar-track!`; Chrome headless desktop/mobile screenshot and DOM render verified on `http://127.0.0.1:5174`

## 2026-06-16 15:39 KST - v05 위치 기상 Agent 구현

- Changed: `frontend/README.md`, `frontend/src/App.tsx`, `frontend/src/types/solar.ts`, `frontend/src/data/weatherLocations.ts`, `frontend/src/logic/weatherModel.ts`, `frontend/src/components/ControlPanel.tsx`, `frontend/src/components/WeatherPanel.tsx`, `frontend/src/styles.css`
- Actions: 서울/부산/제주/대전 위치 선택을 추가하고 Open-Meteo 현재 기상 수집 결과를 Agent 판단 보조 데이터와 발전량 기상 계수에 반영함. 수집 실패 시 시나리오 기반 대체값을 사용하도록 처리함
- Validation: `npm run build` passed; `npm audit --audit-level=high` found 0 vulnerabilities; `uv run python -m py_compile main.py` passed; `uv run python main.py` printed `Hello from solar-track!`; Chrome headless desktop/mobile screenshot and DOM render verified

## 2026-06-16 15:29 KST - v04 진단 Agent 근거 표시

- Changed: `frontend/README.md`, `frontend/src/App.tsx`, `frontend/src/types/solar.ts`, `frontend/src/logic/sensorModel.ts`, `frontend/src/logic/diagnosisAgent.ts`, `frontend/src/components/AgentPanel.tsx`, `frontend/src/styles.css`
- Actions: 진단 결과에 위험도와 근거 목록을 추가하고 평균 조도, 발전량 개선률, 기상, Vision, 시나리오 근거가 Agent 패널에 표시되도록 구현함
- Validation: `npm run build` passed; `npm audit --audit-level=high` found 0 vulnerabilities; `uv run python -m py_compile main.py` passed; `uv run python main.py` printed `Hello from solar-track!`; Chrome headless screenshot/DOM render verified

## 2026-06-16 15:12 KST - v03 순차제어 Agent 구현

- Changed: `frontend/src/App.tsx`, `frontend/src/types/solar.ts`, `frontend/src/logic/trackingAgent.ts`, `frontend/src/logic/diagnosisAgent.ts`, `frontend/src/components/AgentPanel.tsx`
- Actions: 방위각 우선 정렬, 고도각 후정렬, 기상/비전 기반 추적 보류, 발전량 검증 단계 사유를 Agent 상태와 로그에 표시하도록 순차제어 흐름을 명확히 함
- Validation: `npm run build` passed; `npm audit --audit-level=high` found 0 vulnerabilities; `uv run python -m py_compile main.py` passed; `uv run python main.py` printed `Hello from solar-track!`; Chrome headless desktop/mobile screenshots rendered successfully

## 2026-06-16 15:04 KST - v02 태양/센서/발전량 모델 구현

- Changed: `frontend/README.md`, `frontend/src/App.tsx`, `frontend/src/types/solar.ts`, `frontend/src/logic/powerModel.ts`, `frontend/src/components/ModelPanel.tsx`, `frontend/src/styles.css`
- Actions: 발전량 계산식을 최대출력, 태양광 계수, 각도 일치율, 시나리오 계수, 온도 계수, 기상 계수로 분해하고 화면에 계산 모델 패널을 추가함
- Validation: `npm run build` passed; `npm audit --audit-level=high` found 0 vulnerabilities; `uv run python -m py_compile main.py` passed; `uv run python main.py` printed `Hello from solar-track!`; Chrome headless desktop/mobile screenshots rendered successfully

## 2026-06-16 14:46 KST - v01 React 시뮬레이터 구현

- Changed: `.gitignore`, `frontend/README.md`, `frontend/package.json`, `frontend/package-lock.json`, `frontend/index.html`, `frontend/tsconfig*.json`, `frontend/vite.config.ts`, `frontend/src/`
- Actions: Vite + React + TypeScript 기반 단독 시뮬레이터를 만들고 태양/패널 시각화, 제어 패널, 센서, 기상, Vision, Agent, 발전량 그래프, 로그 패널을 구현함
- Validation: `npm run build` passed; `npm audit --audit-level=high` found 0 vulnerabilities; `uv run python -m py_compile main.py` passed; `uv run python main.py` printed `Hello from solar-track!`; Chrome headless desktop/mobile screenshots rendered successfully

## 2026-06-16 14:32 KST - draft initial documentation

- Changed: `README.md`, `.gitignore`, `docs/`, `frontend/README.md`, `backend/README.md`, `hardware/README.md`, `datasets/README.md`
- Actions: created the `draft` branch and generated the v00 project documentation structure from `docs/00_Codex_초기지시_SolarTrack_Agent.md`, including weather-context handling in simulator, diagnosis, FastAPI, and LangGraph plans
- Validation: `uv run python -m py_compile main.py` passed; `uv run python main.py` printed `Hello from solar-track!`
## 2026-06-16 15:39 KST - v05 위치 기상 Agent 구현

- Changed: `frontend/README.md`, `frontend/src/App.tsx`, `frontend/src/types/solar.ts`, `frontend/src/data/weatherLocations.ts`, `frontend/src/logic/weatherModel.ts`, `frontend/src/components/ControlPanel.tsx`, `frontend/src/components/WeatherPanel.tsx`, `frontend/src/styles.css`
- Actions: 서울/부산/제주/대전 위치 선택을 추가하고 Open-Meteo 현재 기상 수집 결과를 Agent 판단 보조 데이터와 발전량 기상 계수에 반영함. 수집 실패 시 시나리오 기반 대체값을 사용하도록 처리함
- Validation: `npm run build` passed; `npm audit --audit-level=high` found 0 vulnerabilities; `uv run python -m py_compile main.py` passed; `uv run python main.py` printed `Hello from solar-track!`; Chrome headless desktop/mobile screenshot and DOM render verified

## 2026-06-16 15:29 KST - v04 진단 Agent 근거 표시

- Changed: `frontend/README.md`, `frontend/src/App.tsx`, `frontend/src/types/solar.ts`, `frontend/src/logic/sensorModel.ts`, `frontend/src/logic/diagnosisAgent.ts`, `frontend/src/components/AgentPanel.tsx`, `frontend/src/styles.css`
- Actions: 진단 결과에 위험도와 근거 목록을 추가하고 평균 조도, 발전량 개선률, 기상, Vision, 시나리오 근거가 Agent 패널에 표시되도록 구현함
- Validation: `npm run build` passed; `npm audit --audit-level=high` found 0 vulnerabilities; `uv run python -m py_compile main.py` passed; `uv run python main.py` printed `Hello from solar-track!`; Chrome headless screenshot/DOM render verified
