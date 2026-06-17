# v07 FastAPI 백엔드 계획

## 1. 백엔드를 붙이는 이유

React 단독 구현으로 흐름을 검증한 뒤, 계산과 진단을 백엔드로 분리한다. 이후 외부 기상 API, 비전 추론 API, LangGraph를 붙이기 쉬워진다.

## 2. API 엔드포인트 계획

| Method | Path | 역할 |
|---|---|---|
| GET | `/api/health` | 서버 상태 확인 |
| POST | `/api/simulate/step` | 한 단계 시뮬레이션 |
| POST | `/api/weather/context` | 위치 기반 기상 정보 조회 |
| POST | `/api/diagnosis` | 진단 결과 반환 |
| POST | `/api/vision/infer` | 비전 추론 결과 반환 |
| POST | `/api/control/command` | 제어 명령 검증 |

## 3. 상태 전달 방식

프론트엔드는 현재 `SolarState`를 JSON으로 전달하고, 백엔드는 갱신된 state와 로그를 반환한다.

## 4. 진단 결과 반환 형식

`diagnosis`, `action`, `riskLevel`, `reason`, `logs`를 반환한다.

## 5. 기상 정보 연동

초기에는 가상 기상 값을 반환한다. 이후 외부 날씨 API를 연결할 수 있도록 `location`, `timestamp`, `cloudCover`, `rain`, `temperature`, `windSpeed` 필드를 둔다.

현재 구현은 백엔드 `/api/weather/context`에서 기상청 API 허브의 한국형수치예보모델(KIM) 자료 조회를 우선 사용한다. 인증키는 `KMA_APIHUB_AUTH_KEY` 환경변수로만 주입하고 코드에 저장하지 않는다. 인증키가 없거나 KIM 응답 파싱에 실패하면 시나리오 기반 대체값을 반환한다.

## 6. 비전모델 API 연동

초기에는 시나리오 기반 가상 결과를 반환하고, 이후 실제 모델 서버로 교체한다.
