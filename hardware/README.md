# hardware

실제 SolarTrack 모형 제작을 위한 ESP32 펌웨어와 배선 문서를 둔다.

## 문서

- `../docs/v12_hardware_bom.md`: 부품 추천, 대체안, 제작 순서
- `wiring.md`: ESP32 핀맵과 배선 주의사항
- `esp32_solartrack_gateway/esp32_solartrack_gateway.ino`: 센서 수집, 백엔드 통신, 모터 명령 실행 예제

## 백엔드 API

```text
GET  /api/hardware/profile
POST /api/hardware/telemetry
```

ESP32는 센서값과 현재 각도, 목표 각도를 백엔드로 보내고 백엔드는 `hold` 또는 `move` 명령을 반환한다.

## 펌웨어 필요 라이브러리

Arduino IDE Library Manager에서 다음 라이브러리를 설치한다.

- ArduinoJson
- Adafruit INA219
- OneWire
- DallasTemperature
- ESP32Servo
- AccelStepper

## 안전 원칙

- LLM은 모터를 직접 제어하지 않는다.
- ESP32는 백엔드 검증 없이 목표 각도를 실행하지 않는다.
- 비상 정지, 리미트 스위치, 강수, 강풍, 과열, 저전압, 센서 이상, Wi-Fi 단절은 모두 `hold`로 처리한다.
- 220V AC와 상용 인버터 제어는 이 모형 범위에서 제외한다.
