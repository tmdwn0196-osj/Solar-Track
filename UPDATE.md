## 2026-06-17 18:27 KST - Arduino CLI 펌웨어 컴파일 검증

- Changed: `.gitignore`, `UPDATE.md`
- Actions: 프로젝트 로컬 `.tools/` 경로에 Arduino CLI 1.5.1을 설치해 실행 확인했다. ESP32 보드 매니저 URL을 추가하고 `esp32:esp32@3.3.10` 코어와 펌웨어 의존 라이브러리를 설치했다. 로컬 도구 바이너리는 저장소에 포함되지 않도록 `.gitignore`에 추가했다.
- Validation: `arduino-cli compile --fqbn esp32:esp32:esp32 hardware\esp32_solartrack_gateway` passed; sketch uses 1,104,335 bytes of program storage and 50,524 bytes of dynamic memory.

## 2026-06-17 18:12 KST - 실제 하드웨어 BOM 및 펌웨어 추가

- Changed: `backend/hardware_gateway.py`, `docs/v12_hardware_bom.md`, `hardware/README.md`, `hardware/wiring.md`, `hardware/esp32_solartrack_gateway/esp32_solartrack_gateway.ino`
- Actions: 실제 ESP32 기반 모형 제작을 위한 BOM, 배선안, Arduino 펌웨어 골격을 추가했다. 백엔드 하드웨어 프로필을 벤치 게이트웨이 구성으로 확장하고, ESP32 텔레메트리의 강수/풍속/비상정지 조건에 따라 `move` 또는 `hold` 명령을 반환하도록 한국어 안전 사유를 정리했다.
- Validation: `uv run python -m py_compile main.py backend\__init__.py backend\app.py backend\models.py backend\simulation.py backend\agent_graph.py backend\vision_dataset.py backend\hardware_gateway.py backend\demo_report.py backend\kma_kim_weather.py` passed; `npm run build` passed; FastAPI TestClient calls for `/api/hardware/profile` and `/api/hardware/telemetry` returned `bench_gateway`, safe `move`, and rain/emergency `hold`; source search found no mojibake patterns. `arduino-cli` is not installed, so Arduino sketch compilation was not run.

## 2026-06-17 17:58 KST - KIM 기상 변수 확장

- Changed: `.env.example`, `UPDATE.md`, `backend/kma_kim_weather.py`, `backend/simulation.py`, `frontend/src/components/WeatherPanel.tsx`, `frontend/src/logic/weatherModel.ts`, `frontend/src/types/solar.ts`
- Actions: KIM 모드에서 `t2m` 온도뿐 아니라 `ws` 풍속과 `rh2m` 상대습도를 함께 반영하도록 확장했다. 기상 응답에 `valueSources`를 추가해 온도/풍속/습도는 KIM, 구름량/강수는 시나리오 기반임을 프론트 기상 패널에 표시하도록 했다.
- Validation: `npm run build` passed; `uv run python -m py_compile main.py backend\__init__.py backend\app.py backend\models.py backend\simulation.py backend\agent_graph.py backend\vision_dataset.py backend\hardware_gateway.py backend\demo_report.py backend\kma_kim_weather.py` passed; FastAPI TestClient calls for `/api/weather/context` returned `mode=scenario -> temperature=25, windSpeed=2.1, humidity=None, valueSources=scenario` and `mode=kma-kim -> temperature=17.2, windSpeed=1.6, humidity=64.8, valueSources temperature/windSpeed/humidity=kma-kim, cloudCover/rain=scenario`.

## 2026-06-17 17:48 KST - 기상 모드 선택 추가

- Changed: `UPDATE.md`, `backend/app.py`, `backend/models.py`, `frontend/src/App.tsx`, `frontend/src/components/ControlPanel.tsx`, `frontend/src/logic/apiClient.ts`, `frontend/src/types/solar.ts`
- Actions: 기상 컨텍스트를 `시나리오 기반` 모드와 `기상청 KIM` 모드로 명시적으로 분리했다. 프론트 제어 패널에 기상 모드 선택 UI를 추가하고, 백엔드 `/api/weather/context`가 `mode=scenario`이면 외부 API 없이 시나리오 기상값을 반환하고 `mode=kma-kim`이면 KIM API 값을 우선 반영하도록 변경했다.
- Validation: `npm run build` passed; `uv run python -m py_compile main.py backend\__init__.py backend\app.py backend\models.py backend\simulation.py backend\agent_graph.py backend\vision_dataset.py backend\hardware_gateway.py backend\demo_report.py backend\kma_kim_weather.py` passed; FastAPI TestClient calls for `/api/weather/context` returned `mode=scenario -> source=scenario, temperature=25` and `mode=kma-kim -> source=kma-kim, temperature=17.2, collectedAt=2026061700`; frontend/backend source search found no mojibake patterns.

## 2026-06-17 12:08 KST - 프론트 표시 문구 한글화

- Changed: `UPDATE.md`, `backend/demo_report.py`, `backend/kma_kim_weather.py`, `backend/simulation.py`, `backend/vision_dataset.py`, `frontend/src/App.tsx`, `frontend/src/components/AgentPanel.tsx`, `frontend/src/components/ControlPanel.tsx`, `frontend/src/components/DashboardPanel.tsx`, `frontend/src/components/DemoReportPanel.tsx`, `frontend/src/components/LogPanel.tsx`, `frontend/src/components/ModelPanel.tsx`, `frontend/src/components/PowerChart.tsx`, `frontend/src/components/SensorPanel.tsx`, `frontend/src/components/SolarScene.tsx`, `frontend/src/components/VisionPanel.tsx`, `frontend/src/components/WeatherPanel.tsx`, `frontend/src/data/scenarios.ts`, `frontend/src/logic/reportModel.ts`, `frontend/src/logic/trackingAgent.ts`, `frontend/src/logic/visionModel.ts`, `frontend/src/logic/weatherModel.ts`
- Actions: 프론트에 표시되는 깨진 한글, 영어 상태 문구, `Fallback`, `Agent`, `Class` 표기를 한글 문장으로 정리했다. 백엔드에서 프론트로 내려오는 기상, 시뮬레이션, 비전 데이터셋, 리포트 문구도 한글 응답으로 맞췄다.
- Validation: `npm run build` passed; `uv run python -m py_compile main.py backend\__init__.py backend\app.py backend\models.py backend\simulation.py backend\agent_graph.py backend\vision_dataset.py backend\hardware_gateway.py backend\demo_report.py backend\kma_kim_weather.py` passed; frontend/backend source search found no mojibake patterns or remaining user-facing `Fallback`, `Weather is`, `Clear`, `Cloudy`, `Rain`, `Hot`, `Demo Report`, `Agent 진단`, `action=`, `risk=`, `powerGain=` strings.

## 2026-06-17 11:52 KST - 승인된 KMA 8km API 경로 반영

- Changed: `.env.example`, `UPDATE.md`, `backend/README.md`, `backend/kma_kim_weather.py`
- Actions: 기존 `typ06` 지점 조회 API가 403을 반환하는 원인을 확인하고, 현재 인증키로 활용신청이 통과된 KIM 8km `typ01` 영역 조회 API(`nph-kim_nc_xy_txt2`, `KIMG/NE57/t2m/map=R`)로 백엔드 기상 어댑터를 전환했다. KMA가 최신 발표시각 파일을 아직 제공하지 않을 때 최근 6시간 주기를 순차 재시도하고, 한반도 영역 격자에서 선택 위치에 가장 가까운 온도값을 추출하도록 수정했다.
- Validation: `uv run python -m py_compile main.py backend\__init__.py backend\app.py backend\models.py backend\simulation.py backend\agent_graph.py backend\vision_dataset.py backend\hardware_gateway.py backend\demo_report.py backend\kma_kim_weather.py` passed; `npm run build` passed; FastAPI TestClient call for `/api/weather/context` returned `source=kma-kim`, `collectedAt=2026061700`, and KMA-derived temperature `17.2`.

## 2026-06-17 11:36 KST - KMA fallback 원인 재검토

- Changed: `UPDATE.md`, `backend/README.md`, `backend/kma_kim_weather.py`
- Actions: KMA API Hub KIM 호출을 실제 `.env` 로드 경로로 재검증했고, 현재 fallback 원인이 `403 활용신청이 필요한 API 입니다` 응답임을 확인했다. 백엔드가 httpx 예외 문자열을 그대로 반환하지 않고 KMA 응답의 상태/메시지만 추출하도록 변경해 인증키가 응답에 노출되지 않게 했다.
- Validation: `uv run python -m py_compile main.py backend\__init__.py backend\app.py backend\models.py backend\simulation.py backend\agent_graph.py backend\vision_dataset.py backend\hardware_gateway.py backend\demo_report.py backend\kma_kim_weather.py` passed; `npm run build` passed; FastAPI TestClient call for `/api/weather/context` returned `source=fallback`, `collectedAt=fallback 데이터 사용`, `HTTP 403 - 활용신청이 필요한 API 입니다`, and no `authKey` or key prefix in the response.

## 2026-06-17 11:23 KST - 기상 fallback 안내 문구 명시

- Changed: `UPDATE.md`, `backend/kma_kim_weather.py`, `frontend/src/components/WeatherPanel.tsx`, `frontend/src/logic/weatherModel.ts`, `frontend/src/styles.css`
- Actions: 기상청 KIM 데이터를 사용할 수 없어 fallback으로 전환될 때 API 응답과 프론트엔드 기상 패널에 fallback 데이터를 사용한다는 문구와 403 거부 원인이 명확히 표시되도록 보강했다. 런타임과 문서에서 특정 외부 기상 서비스 직접 사용 표현을 제거했다.
- Validation: deprecated external weather service references were removed; `uv run python -m py_compile main.py backend\__init__.py backend\app.py backend\models.py backend\simulation.py backend\agent_graph.py backend\vision_dataset.py backend\hardware_gateway.py backend\demo_report.py backend\kma_kim_weather.py` passed; `npm run build` passed; `uv run python main.py` printed `Hello from solar-track!`; FastAPI TestClient call for `/api/weather/context` returned `source=fallback`, `collectedAt=fallback 데이터 사용`, and explicit fallback message; temporary `uvicorn` server returned `/api/health` successfully.

## 2026-06-17 11:21 KST - 기상청 KIM 기상 API 연동

- Changed: `.gitignore`, `.env.example`, `README.md`, `UPDATE.md`, `backend/app.py`, `backend/kma_kim_weather.py`, `backend/README.md`, `docs/v07_fastapi_backend_plan.md`, `frontend/README.md`, `frontend/src/App.tsx`, `frontend/src/components/WeatherPanel.tsx`, `frontend/src/logic/weatherModel.ts`, `frontend/src/types/solar.ts`
- Actions: 백엔드 `/api/weather/context`를 기상청 API 허브 한국형수치예보모델(KIM) 자료 조회 우선 구조로 변경했다. 인증키는 `KMA_APIHUB_AUTH_KEY` 환경변수로만 읽고, 인증키 미설정 또는 KIM 응답 실패 시 시나리오 기상값으로 fallback하도록 처리했다. 프론트엔드 직접 외부 기상 호출 경로를 제거하고 기상 출처에 `kma-kim`을 추가했다.
- Validation: `uv run python -m py_compile main.py backend\__init__.py backend\app.py backend\models.py backend\simulation.py backend\agent_graph.py backend\vision_dataset.py backend\hardware_gateway.py backend\demo_report.py backend\kma_kim_weather.py` passed; `npm run build` passed; `uv run python main.py` printed `Hello from solar-track!`; FastAPI TestClient calls for `/api/health` and `/api/weather/context` without `KMA_APIHUB_AUTH_KEY` returned fallback successfully; temporary `uvicorn` server returned `/api/health` successfully.

## 2026-06-17 10:29 KST - v11 시연 리포트 구성

- Changed: `README.md`, `UPDATE.md`, `backend/app.py`, `backend/models.py`, `backend/demo_report.py`, `backend/README.md`, `docs/v11_demo_scenario_and_report.md`, `frontend/README.md`, `frontend/src/App.tsx`, `frontend/src/components/DemoReportPanel.tsx`, `frontend/src/logic/reportModel.ts`, `frontend/src/styles.css`
- Actions: 발표용 시나리오 목록과 현재 SolarState 기반 리포트 생성 API를 추가하고, 프론트엔드에 Demo Report 패널을 추가했다. 시나리오별 목표, 발전량 비교, 위험도, 진단, 조치, 발표 문장을 한 화면과 API 응답에서 확인할 수 있게 했다.
- Validation: `uv run python -m py_compile main.py backend\__init__.py backend\app.py backend\models.py backend\simulation.py backend\agent_graph.py backend\vision_dataset.py backend\hardware_gateway.py backend\demo_report.py` passed; `uv run python main.py` printed `Hello from solar-track!`; `npm run build` passed; FastAPI TestClient calls for `/api/demo/scenarios` and `/api/demo/report` passed; temporary `uvicorn` server returned `/api/health` successfully.

## 2026-06-17 10:21 KST - v10 ESP32 하드웨어 게이트웨이 준비

- Changed: `README.md`, `UPDATE.md`, `backend/app.py`, `backend/models.py`, `backend/hardware_gateway.py`, `backend/README.md`, `docs/v10_esp32_hardware_plan.md`, `hardware/README.md`, `hardware/esp32_solartrack_gateway/esp32_solartrack_gateway.ino`
- Actions: ESP32 하드웨어 프로필과 텔레메트리 검증 API를 추가하고, 비/강풍/과열/저전압/센서 이상/emergency stop 조건에서 `hold` 명령을 반환하는 안전 게이트를 구현했다. 실제 모터 제어 전 통신 계약을 확인할 수 있는 ESP32 예제 스케치를 추가했다.
- Validation: `uv run python -m py_compile main.py backend\__init__.py backend\app.py backend\models.py backend\simulation.py backend\agent_graph.py backend\vision_dataset.py backend\hardware_gateway.py` passed; `uv run python main.py` printed `Hello from solar-track!`; `npm run build` passed; FastAPI TestClient calls for `/api/hardware/profile` and `/api/hardware/telemetry` move/hold paths passed; temporary `uvicorn` server returned `/api/health` successfully.

## 2026-06-17 10:16 KST - v09 데이터셋 및 비전모델 학습 준비

- Changed: `README.md`, `UPDATE.md`, `backend/app.py`, `backend/simulation.py`, `backend/vision_dataset.py`, `backend/README.md`, `docs/v09_dataset_vision_training_plan.md`, `datasets/README.md`, `datasets/sample_manifest.csv`, `datasets/images/`, `datasets/labels/`, `frontend/README.md`, `frontend/src/App.tsx`, `frontend/src/components/VisionPanel.tsx`, `frontend/src/logic/visionModel.ts`, `frontend/src/styles.css`, `frontend/src/types/solar.ts`
- Actions: v09 데이터셋 폴더 골격과 샘플 매니페스트를 추가하고, 비전 클래스 메타데이터 및 `/api/vision/classes` 엔드포인트를 구현했다. 가상 비전 추론 결과에 `primaryClass`, `confidence`, `detections`, `modelMode`를 추가하고 Vision 패널에서 클래스와 신뢰도를 확인할 수 있게 했다.
- Validation: `npm run build` passed; `uv run python -m py_compile main.py backend\__init__.py backend\app.py backend\models.py backend\simulation.py backend\agent_graph.py backend\vision_dataset.py` passed; `uv run python main.py` printed `Hello from solar-track!`; FastAPI TestClient calls for `/api/health`, `/api/vision/classes`, `/api/vision/infer` passed; temporary `uvicorn` server returned `/api/health` successfully.

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
- Actions: 서울/부산/제주/대전 위치 선택을 추가하고 외부 기상 API 결과 수집 결과를 Agent 판단 보조 데이터와 발전량 기상 계수에 반영함. 수집 실패 시 시나리오 기반 대체값을 사용하도록 처리함
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
- Actions: 서울/부산/제주/대전 위치 선택을 추가하고 외부 기상 API 결과 수집 결과를 Agent 판단 보조 데이터와 발전량 기상 계수에 반영함. 수집 실패 시 시나리오 기반 대체값을 사용하도록 처리함
- Validation: `npm run build` passed; `npm audit --audit-level=high` found 0 vulnerabilities; `uv run python -m py_compile main.py` passed; `uv run python main.py` printed `Hello from solar-track!`; Chrome headless desktop/mobile screenshot and DOM render verified

## 2026-06-16 15:29 KST - v04 진단 Agent 근거 표시

- Changed: `frontend/README.md`, `frontend/src/App.tsx`, `frontend/src/types/solar.ts`, `frontend/src/logic/sensorModel.ts`, `frontend/src/logic/diagnosisAgent.ts`, `frontend/src/components/AgentPanel.tsx`, `frontend/src/styles.css`
- Actions: 진단 결과에 위험도와 근거 목록을 추가하고 평균 조도, 발전량 개선률, 기상, Vision, 시나리오 근거가 Agent 패널에 표시되도록 구현함
- Validation: `npm run build` passed; `npm audit --audit-level=high` found 0 vulnerabilities; `uv run python -m py_compile main.py` passed; `uv run python main.py` printed `Hello from solar-track!`; Chrome headless screenshot/DOM render verified
## 2026-06-17 15:32 KST - 백엔드 .env 자동 로드

- Changed: `backend/__init__.py`, `backend/README.md`, `UPDATE.md`
- Actions: 백엔드 패키지 초기화 시 저장소 루트의 `.env`를 자동 로드하도록 추가해, KMA API Hub 인증키가 프로세스 환경변수로 주입되지 않아 fallback으로 떨어지는 문제를 해결했다. 현재 fallback은 `.env` 값이 읽힌 뒤 KMA API Hub가 403으로 요청을 거부할 때만 발생한다.
- Validation: `uv run python -m py_compile backend\__init__.py backend\kma_kim_weather.py backend\app.py` passed; `uv run python`-based FastAPI TestClient weather call still returned `source=fallback` with explicit KMA 403 reason because the API Hub rejected the current key.
