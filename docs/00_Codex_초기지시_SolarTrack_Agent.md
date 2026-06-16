# Codex 초기 지시 프롬프트: SolarTrack Agent 프로젝트 단계별 구성

## 0. 역할 지시

너는 이 프로젝트의 **개발 기획자 겸 구현 보조자**다.  
한 번에 전체 기능을 구현하지 말고, 먼저 프로젝트를 단계별로 나누고, 각 단계를 버전별 Markdown 문서로 정리한 뒤, 그 순서에 따라 점진적으로 구현할 수 있도록 구성해라.

이 프로젝트는 **AIoT 기반 순차제어 2축 태양추적형 미니 태양광 발전 자가진단 Agent**를 React 웹 시뮬레이터로 먼저 구현하고, 이후 FastAPI, LangGraph, 비전모델, 실제 ESP32 하드웨어로 확장하는 것을 목표로 한다.

---

## 1. 프로젝트 핵심 목표

### 최종 프로젝트명

**SolarTrack Agent**

### 전체 주제

**AIoT 기반 순차제어 2축 태양추적형 미니 태양광 발전 자가진단 Agent**

### 핵심 아이디어

건물 옥상형 소형 태양광 설비를 가정한다.

시스템은 태양 위치를 추적하여 다음 순서로 동작한다.

```text
1. 태양 위치 또는 가상 센서값 확인
2. 설치 위치의 기상 정보 수집 및 일사 조건 고려
3. 하부 원판 방위각 먼저 정렬
4. 상부 패널 고도각 후정렬
5. 조정 전후 발전량 비교
6. 발전량 개선 여부 판단
7. 개선이 없으면 출력 저하 원인 진단
8. Agent가 조치 추천
```

단순한 태양추적기가 아니라, 다음 기능까지 포함해야 한다.

```text
태양추적
+ 발전량 검증
+ 고정식 대비 추적식 비교
+ 위치 기반 기상 정보 수집 및 일사 조건 반영
+ 출력 저하 원인 진단
+ 비전모델 기반 오염/음영/구름 검출 확장
+ 구름 감지 시 불필요한 서보모터 동작 억제
+ LangGraph 기반 Agent 확장
+ ESP32 실제 하드웨어 확장 가능 구조
```

---

## 2. 매우 중요한 개발 원칙

### 2-1. 한 번에 전부 구현하지 말 것

처음부터 React, FastAPI, LangGraph, ESP32, 비전모델을 모두 구현하지 마라.

반드시 아래 순서로 진행한다.

```text
1차: 문서화 및 프로젝트 구조 설계
2차: React 단독 가상 시뮬레이터
3차: 규칙 기반 Agent
4차: 가상 비전모델
5차: 대시보드 고도화
6차: FastAPI 백엔드 분리
7차: LangGraph Agent 구조
8차: 실제 데이터셋 및 비전모델 학습
9차: ESP32 하드웨어 연동
```

### 2-2. 코드는 최대한 단순하게 작성할 것

- 초보자가 이해할 수 있게 작성한다.
- 불필요한 추상화, 복잡한 패턴, 과한 폴더 구조를 피한다.
- TypeScript 타입은 사용하되, 너무 복잡하게 만들지 않는다.
- 전역 변수 남발은 피하고, 상태는 React state 또는 reducer로 관리한다.
- 함수는 작고 명확하게 나눈다.
- 주석은 한국어로 간단히 작성한다.

### 2-3. 안전 관련 원칙

- LLM이 직접 모터를 제어하는 구조로 설계하지 않는다.
- 모터 제어, 위험 정지, 각도 제한은 규칙 기반으로 설계한다.
- LLM 또는 LangChain은 진단 설명, 리포트 생성, 사용자 질의응답에만 사용한다.
- 실제 하드웨어 확장 시 저전압 DC 기반으로 설계한다.

### 2-4. 기상 정보 활용 원칙

- Agent는 설치 위치의 현재 기상 정보 또는 예보 정보를 수집하여 시뮬레이션과 진단에 참고한다.
- 기상 정보는 일사량, 구름량, 강수, 온도, 풍속처럼 발전량과 안전 판단에 영향을 주는 항목을 우선한다.
- 기상 정보는 모터를 직접 움직이는 명령이 아니라 판단 보조 데이터로만 사용한다.
- API가 없거나 통신에 실패하면 가상 시나리오 값으로 대체하고, 로그에 실패 이유를 남긴다.
- 기상 정보와 센서/비전 결과가 충돌하면 실제 센서값과 안전 규칙을 우선한다.

---

## 3. 첫 번째로 수행할 작업

이번 지시에서는 **구현 코드를 바로 많이 작성하지 말고**, 먼저 프로젝트의 전체 문서 구조를 만든다.

다음 작업을 수행해라.

### 작업 1. 프로젝트 폴더 구조 생성

아래 구조를 기준으로 폴더와 빈 파일 또는 초안 파일을 만들어라.

```text
solartrack-agent/
├─ README.md
├─ docs/
│  ├─ v00_project_overview.md
│  ├─ v01_react_simulator_plan.md
│  ├─ v02_sun_sensor_power_model.md
│  ├─ v03_sequential_tracking_agent.md
│  ├─ v04_diagnosis_agent.md
│  ├─ v05_virtual_vision_model.md
│  ├─ v06_dashboard_ui.md
│  ├─ v07_fastapi_backend_plan.md
│  ├─ v08_langgraph_agent_plan.md
│  ├─ v09_dataset_vision_training_plan.md
│  ├─ v10_esp32_hardware_plan.md
│  └─ v11_demo_scenario_and_report.md
├─ frontend/
│  └─ README.md
├─ backend/
│  └─ README.md
├─ hardware/
│  └─ README.md
└─ datasets/
   └─ README.md
```

현재 단계에서는 `frontend`, `backend`, `hardware`, `datasets` 폴더에는 README만 만들어도 된다.  
실제 구현은 이후 단계에서 진행한다.

---

## 4. 각 문서에 들어가야 할 내용

### 4-1. `README.md`

프로젝트 전체 소개를 작성한다.

반드시 포함할 내용:

```text
- 프로젝트명: SolarTrack Agent
- 한 줄 설명
- 문제 정의
- 핵심 기능
- 단계별 개발 계획
- 최종 확장 구조
- 현재 진행 단계
```

현재 진행 단계는 다음처럼 적어라.

```text
현재 단계: v00 문서화 및 프로젝트 구조 설계
```

---

### 4-2. `docs/v00_project_overview.md`

프로젝트 전체 개요 문서다.

포함할 내용:

```text
1. 프로젝트 배경
2. 왜 단순 태양추적기가 아닌 Agent 구조인지
3. 옥상형 소형 태양광 설비를 대상으로 잡는 이유
4. 전체 시스템 흐름
5. 최종 시스템 구성
6. 단계별 버전 계획
7. 위치 기반 기상 정보 수집 Agent의 역할
8. 제외할 범위
```

제외할 범위에는 다음을 포함한다.

```text
- 대규모 태양광 발전소용 상용 시스템 구현은 제외
- 220V AC 인버터 실험 제외
- LLM 직접 모터 제어 제외
- 초기 단계에서 실제 비전모델 학습은 제외
- 초기 단계에서 실제 ESP32 하드웨어 연결은 제외
```

---

### 4-3. `docs/v01_react_simulator_plan.md`

React 웹 시뮬레이터 설계 문서다.

포함할 내용:

```text
1. React 시뮬레이터 목표
2. 화면 구성
3. 주요 컴포넌트
4. 상태값 설계
5. 시뮬레이션 루프
6. 시나리오 버튼
7. 고정식 vs 추적식 비교 방식
8. 기상 정보 표시 영역
```

컴포넌트는 다음을 기준으로 한다.

```text
SolarScene
ControlPanel
SensorPanel
PowerChart
AgentPanel
VisionPanel
WeatherPanel
LogPanel
```

---

### 4-4. `docs/v02_sun_sensor_power_model.md`

시뮬레이션 모델 문서다.

포함할 내용:

```text
1. 태양 위치 모델
2. 가상 조도 센서 모델
3. 발전량 계산 모델
4. 온도 계수
5. 시나리오 계수
6. 전압/전류 가상 계산
7. 고정식 발전량 계산
8. 추적식 발전량 계산
9. 기상 정보가 발전량 계수에 영향을 주는 방식
```

발전량 계산식은 단순하게 잡는다.

```text
발전량 = 최대출력 × 태양광 계수 × 각도 일치율 × 시나리오 계수 × 온도 계수
```

---

### 4-5. `docs/v03_sequential_tracking_agent.md`

순차제어 Agent 문서다.

포함할 내용:

```text
1. 순차제어가 필요한 이유
2. 하부 방위각 우선 정렬
3. 상부 고도각 후정렬
4. 동시에 모터를 움직이지 않는 이유
5. 구름 감지 시 모터 동작 보류
6. 기상 정보 확인 후 추적 보류 또는 감속 판단
7. 각도 제한
8. 제어 흐름
9. 의사코드
```

핵심 흐름은 다음을 유지한다.

```text
센서값 확인
↓
설치 위치 기상 정보 수집
↓
구름/강수/강풍 여부 확인
↓
구름/태양 가림 여부 확인
↓
구름 또는 강수/강풍 조건이면 서보모터 동작 보류 또는 제한
↓
기상 조건이 안전하면 하부 방위각 정렬
↓
하부 정렬 완료 후 상부 고도각 정렬
↓
발전량 검증
```

---

### 4-6. `docs/v04_diagnosis_agent.md`

진단 Agent 문서다.

포함할 내용:

```text
1. 진단 Agent 역할
2. 센서 기반 진단 규칙
3. 발전량 개선률 기반 판단
4. 기상 정보 기반 광량 부족/강수/강풍 영향 판단
5. 오염/음영/과열/충전 문제 판단
6. 위험도 normal/warning/danger
7. 사용자 조치 추천 문구
```

진단 예시는 다음을 포함한다.

```text
- 추적 보정 성공
- 광량 부족
- 기상 영향으로 인한 일시적 출력 저하
- 부분 음영 의심
- 패널 오염 의심
- 패널 과열
- 충전 계통 문제
- 부하 과다
```

---

### 4-7. `docs/v05_virtual_vision_model.md`

가상 비전모델 문서다.

포함할 내용:

```text
1. 비전모델을 추가하는 이유
2. 초기에는 실제 모델 대신 가상 추론으로 구현하는 이유
3. 구름/태양 가림 검출
4. 패널 오염 검출
5. 부분 음영 검출
6. 이물질/낙엽 검출
7. 패널 손상 후보 검출
8. 서보모터 불필요 동작 억제 방식
9. 추후 데이터셋 학습 방향
```

비전모델의 핵심 역할은 다음이다.

```text
- 구름에 의한 일시적 발전량 저하를 각도 문제로 오판하지 않게 한다.
- 패널 표면 오염, 부분 음영, 이물질을 검출하여 출력 저하 원인 판단을 보완한다.
- 구름 감지 시 하부 원판과 패널 각도 조정을 보류하여 불필요한 서보모터 동작을 줄인다.
```

---

### 4-8. `docs/v06_dashboard_ui.md`

대시보드 UI 문서다.

포함할 내용:

```text
1. 전체 화면 레이아웃
2. 태양/패널 시각화
3. 센서값 카드
4. 발전량 그래프
5. 고정식 vs 추적식 비교
6. Agent 판단 카드
7. Vision 결과 카드
8. 로그 패널
9. 시나리오 제어 패널
```

---

### 4-9. `docs/v07_fastapi_backend_plan.md`

FastAPI 확장 계획 문서다.

포함할 내용:

```text
1. React 단독 구현 이후 백엔드를 붙이는 이유
2. API 엔드포인트 계획
3. 상태 전달 방식
4. 진단 결과 반환 형식
5. 기상 정보 수집 API 또는 외부 날씨 API 연동 계획
6. 비전모델 API 연동 계획
```

예상 API:

```text
GET /api/health
POST /api/simulate/step
POST /api/weather/context
POST /api/diagnosis
POST /api/vision/infer
POST /api/control/command
```

---

### 4-10. `docs/v08_langgraph_agent_plan.md`

LangGraph Agent 구조 문서다.

포함할 내용:

```text
1. 왜 LangGraph를 사용하는지
2. State 설계
3. Node 설계
4. Edge 설계
5. 조건 분기
6. weather_context 수집 및 기상 위험 분기
7. 구름 감지 시 hold_servo 분기
8. 센서 + 비전 + 기상 결과 융합
9. LLM 사용 위치
10. LLM을 사용하지 말아야 할 위치
```

LangGraph 노드 흐름은 다음을 기준으로 한다.

```text
START
↓
collect_sensor
↓
collect_weather
↓
vision_inference
↓
weather_gate
├─ rain_or_high_wind → safety_hold
└─ safe_weather → cloud_gate
cloud_gate
├─ cloud_detected → hold_servo
└─ clear → validate_sensor
↓
measure_before_power
↓
azimuth_align
↓
elevation_align
↓
measure_after_power
↓
verify_power_gain
↓
fuse_sensor_vision_weather
↓
diagnose_fault
↓
generate_report
↓
END
```

---

### 4-11. `docs/v09_dataset_vision_training_plan.md`

데이터셋 및 비전모델 학습 계획 문서다.

포함할 내용:

```text
1. 필요한 이미지 데이터 종류
2. 클래스 정의
3. 데이터셋 폴더 구조
4. 초기에는 공개 데이터셋 또는 직접 촬영 이미지 사용
5. 모델 후보
6. 학습보다 먼저 가상 추론으로 구조 검증
7. 추후 FastAPI 추론 API 연결
```

클래스 예시:

```text
sky_clear
sky_cloudy
sun_cloud_block
panel_clean
panel_soiling
panel_partial_shadow
panel_foreign_object
panel_damage
```

모델 후보:

```text
MobileNetV3
EfficientNet-B0
ResNet18
YOLOv8n
YOLOv11n
```

---

### 4-12. `docs/v10_esp32_hardware_plan.md`

ESP32 하드웨어 확장 문서다.

포함할 내용:

```text
1. 실제 하드웨어 확장 목표
2. 센서 구성
3. 하부 회전 구동부
4. 상부 패널 각도 구동부
5. 카메라 모듈
6. 전원 구성
7. 통신 방식
8. 안전 제한
```

부품 예시:

```text
ESP32
LDR 4개 또는 BH1750
INA219
DS18B20
NEMA17 스텝모터
A4988 또는 DRV8825
고토크 서보모터
미니 태양광 패널
카메라 모듈
```

---

### 4-13. `docs/v11_demo_scenario_and_report.md`

시연 및 발표 문서다.

포함할 내용:

```text
1. 정상 추적 시나리오
2. 흐림 시나리오
3. 구름에 의한 태양 가림 시나리오
4. 부분 음영 시나리오
5. 패널 오염 시나리오
6. 패널 과열 시나리오
7. 충전 계통 문제 시나리오
8. 기상 정보가 출력 저하 판단에 반영되는 시나리오
9. 발표용 설명 문장
10. 기대 효과
11. 한계점
12. 향후 확장
```

---

## 5. 문서 작성 스타일

모든 문서는 한국어로 작성한다.

문체는 다음 기준을 따른다.

```text
- 설명은 짧고 명확하게
- 표를 적극 활용
- 코드가 필요한 부분은 의사코드 중심
- 실제 구현 코드는 최소화
- 발표 자료로 바꿔도 자연스럽게
- 과장 표현 금지
- 상용화되지 않은 기술처럼 말하지 말 것
- 기존 2축 태양추적기는 상용화/연구가 있음을 인정할 것
- 차별점은 순차제어, 발전량 검증, 자가진단 Agent, 비전모델 확장으로 잡을 것
```

---

## 6. 첫 작업의 완료 기준

이번 첫 작업이 끝나면 다음 조건을 만족해야 한다.

```text
1. 프로젝트 루트에 README.md가 있다.
2. docs 폴더 안에 v00~v11 문서가 있다.
3. 각 문서는 빈 파일이 아니라 초안 내용을 포함한다.
4. 각 문서는 다음 단계에서 바로 구현 지시로 사용할 수 있다.
5. frontend, backend, hardware, datasets 폴더가 생성되어 있다.
6. 각 폴더에는 README.md가 있다.
7. 실제 React 구현은 아직 많이 하지 않는다.
8. 전체 프로젝트 흐름이 문서만 봐도 이해되어야 한다.
```

---

## 7. 절대 하지 말 것

이번 단계에서는 다음을 하지 마라.

```text
- React 앱 전체 구현
- FastAPI 서버 전체 구현
- LangGraph 코드 전체 구현
- ESP32 코드 작성
- 실제 비전모델 학습 코드 작성
- 복잡한 UI 라이브러리 설치
- 데이터셋 다운로드
- 대규모 리팩토링
```

이번 단계는 **문서화와 프로젝트 뼈대 구성**이 목적이다.

---

## 8. 다음 단계 예고

첫 작업이 완료되면 다음 단계에서는 `v01_react_simulator_plan.md`를 기준으로 React 프로젝트를 생성하고, 다음 최소 기능부터 구현한다.

```text
1. 태양 위치 표시
2. 패널 방위각/고도각 상태 표시
3. 시뮬레이션 시작/정지
4. 시나리오 선택
5. 기본 상태 카드 표시
```

그 다음 단계에서 `v02_sun_sensor_power_model.md`를 기준으로 태양 위치 모델, 가상 센서 모델, 발전량 계산 모델을 구현한다.

---

## 9. 최종 요청

위 요구사항에 맞춰 프로젝트 초기 구조와 버전별 Markdown 문서를 생성해라.  
작업이 끝나면 생성한 파일 목록과 각 문서의 요약을 출력해라.  
또한 다음 작업으로 무엇을 하면 되는지 짧게 제안해라.
