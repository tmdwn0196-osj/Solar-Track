# backend

SolarTrack Agent의 FastAPI 백엔드다.

## 현재 포함 범위

- `GET /api/health`: 서버 상태 확인
- `POST /api/simulate/step`: 1스텝 시뮬레이션 계산
- `POST /api/weather/context`: 위치와 시나리오 기반 기상 컨텍스트 반환
- `POST /api/diagnosis`: 상태 재계산 후 진단 결과 반환
- `POST /api/vision/infer`: 시나리오 기반 가상 비전 추론
- `GET /api/vision/classes`: v09 비전 데이터셋 클래스와 폴더 구조 조회
- `POST /api/control/command`: 추적/홀드 제어 명령 검증
- `POST /api/agent/evaluate`: LangGraph 기반 Agent 상태 그래프 실행
- `GET /api/hardware/profile`: ESP32 하드웨어 구성과 안전 제한 조회
- `POST /api/hardware/telemetry`: ESP32 텔레메트리 검증 후 `hold` 또는 `move` 명령 반환
- `GET /api/demo/scenarios`: 발표용 시연 시나리오 목록 반환
- `POST /api/demo/report`: 현재 상태 기반 발표 리포트 생성

## LangGraph Agent 흐름

초기 v08 구현은 LLM 없이 규칙 기반 노드만 사용한다.

```text
collect_sensor
-> collect_weather
-> vision_inference
-> weather_gate
-> cloud_gate 또는 safety_hold
-> validate_sensor 또는 hold_servo
-> measure_before_power
-> azimuth_align
-> elevation_align
-> measure_after_power
-> verify_power_gain
-> fuse_sensor_vision_weather
-> diagnose_fault
-> generate_report
```

강수, 강풍, 높은 구름량, 비전 구름 감지는 모터 보류 경로로 분기한다. 모터 제어 판단은 LLM이 아니라 규칙 기반 함수가 수행한다.

## Hardware Gateway

하드웨어 명령은 항상 백엔드 안전 게이트를 통과한다. 현재 v10 구현은 실제 모터 제어가 아니라 ESP32가 보낸 텔레메트리를 검증하고 안전한 응답 JSON을 반환하는 단계다.

## 실행

```powershell
uv sync
uv run uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

프론트엔드는 기본적으로 `http://127.0.0.1:8000`을 호출한다. 다른 주소를 사용할 때는 `frontend` 실행 전에 `VITE_API_BASE_URL`을 설정한다.
