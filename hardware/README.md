# hardware

ESP32 하드웨어 확장 문서와 예제 코드가 들어갈 영역이다.

v10에서는 실제 모터 제어를 바로 수행하지 않는다. FastAPI 백엔드가 센서값을 검증하고 안전한 명령만 반환하는 통신 경계와 ESP32 예제 스케치만 제공한다.

## 권장 부품

| 영역 | 후보 |
|---|---|
| MCU | ESP32 DevKit |
| 조도 | LDR 4개 또는 BH1750 |
| 전압/전류 | INA219 |
| 패널 온도 | DS18B20 |
| 하부 방위각 | NEMA17 + A4988/DRV8825 |
| 상부 고도각 | 고토크 서보모터 |
| 비전 | ESP32-CAM 또는 외부 카메라 모듈 |

## 백엔드 API

```text
GET  /api/hardware/profile
POST /api/hardware/telemetry
```

ESP32는 센서값과 현재 각도, 목표 각도를 서버로 보내고 서버는 `hold` 또는 `move` 명령을 반환한다.

## 안전 원칙

- LLM은 모터를 직접 제어하지 않는다.
- ESP32는 백엔드 검증 없이 목표 각도를 실행하지 않는다.
- 비, 강풍, 과열, 저전압, 센서 이상, emergency stop 상태에서는 `hold`만 수행한다.
- 초기 실험은 저전압 DC 환경에서만 수행한다.
- 220V AC 인버터 실험은 제외한다.

## 예제

`esp32_solartrack_gateway/esp32_solartrack_gateway.ino`는 통신 계약 확인용 스케치다. 실제 센서 핀과 모터 출력은 bench test 이후에만 연결한다.
