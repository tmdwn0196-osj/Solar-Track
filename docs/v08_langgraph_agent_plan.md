# v08 LangGraph Agent 계획

## 1. 사용하는 이유

진단 흐름이 길어지면 단순 함수 호출보다 상태 그래프가 이해하기 쉽다. LangGraph는 센서, 기상, 비전, 발전량 검증을 단계별 노드로 표현하는 데 적합하다.

## 2. State 설계

State에는 센서값, 기상 정보, 비전 결과, 발전량 전후 비교, 위험도, 진단 문구, 추천 조치를 포함한다.

## 3. Node 설계

- `collect_sensor`
- `collect_weather`
- `vision_inference`
- `weather_gate`
- `cloud_gate`
- `validate_sensor`
- `measure_before_power`
- `azimuth_align`
- `elevation_align`
- `measure_after_power`
- `verify_power_gain`
- `fuse_sensor_vision_weather`
- `diagnose_fault`
- `generate_report`

## 4. Edge 설계

강수나 강풍이면 `safety_hold`로 이동한다. 구름이면 `hold_servo`로 이동한다. 안전하고 맑으면 정렬 단계로 진행한다.

## 5. 조건 분기

분기 조건은 규칙 기반으로 둔다. LLM은 분기 판단을 직접 수행하지 않는다.

## 6. 기상 위험 분기

`weather_context`에서 강수, 강풍, 높은 구름량을 확인한다. 위험 조건이면 추적을 보류한다.

## 7. 센서, 비전, 기상 융합

세 정보가 같은 방향을 가리키면 진단 신뢰도를 높인다. 충돌하면 실제 센서값과 안전 규칙을 우선한다.

## 8. LLM 사용 위치

LLM은 진단 설명, 사용자용 리포트, 질의응답에 사용한다.

## 9. LLM을 사용하지 말아야 할 위치

모터 제어, 각도 제한, 위험 정지, 실시간 센서 루프에는 사용하지 않는다.

## 10. v08 구현 상태

현재 구현은 `backend/agent_graph.py`에 LangGraph `StateGraph`로 구성되어 있다.

| 항목 | 구현 내용 |
|---|---|
| API | `POST /api/agent/evaluate` |
| 그래프 입력 | 현재 `SolarState` JSON |
| 그래프 출력 | 갱신 상태, 센서 스냅샷, 기상, 비전, 제어 결과, 진단, 리포트, 노드 trace |
| 분기 | `weather_gate`, `cloud_gate` |
| 안전 보류 | `safety_hold`, `hold_servo` |
| LLM 사용 | 아직 사용하지 않음 |

초기 목적은 Agent 흐름을 상태 그래프로 분리하는 것이다. 실제 LLM은 이후 리포트 설명이나 사용자 질의응답에만 붙인다.
