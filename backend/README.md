# backend

SolarTrack Agent의 FastAPI 백엔드다.

## 현재 포함 범위

- `GET /api/health`: 서버 상태 확인
- `POST /api/simulate/step`: 1스텝 시뮬레이션 계산
- `POST /api/weather/context`: 위치와 시나리오 기반 기상 컨텍스트 반환
- `POST /api/diagnosis`: 상태 재계산 후 진단 결과 반환
- `POST /api/vision/infer`: 시나리오 기반 가상 비전 추론
- `POST /api/control/command`: 추적/홀드 제어 명령 검증

## 실행

```powershell
uv sync
uv run uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

프론트엔드는 기본적으로 `http://127.0.0.1:8000`을 호출한다. 다른 주소를 사용할 때는 `frontend` 실행 전에 `VITE_API_BASE_URL`을 설정한다.
