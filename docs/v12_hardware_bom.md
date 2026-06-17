# v12 실제 하드웨어 BOM

SolarTrack Agent를 실제 모형으로 만들 때의 1차 부품안이다. 목표는 발표용 벤치 테스트와 저전압 시연이며, 상용 태양광 설비나 고출력 인버터 제어는 범위에서 제외한다.

## 권장 구성

| 영역 | 1차 추천 | 수량 | 용도 | 대체안 |
|---|---:|---:|---|---|
| MCU | ESP32 DevKitC 또는 호환 ESP32 DevKit | 1 | Wi-Fi 통신, 센서 수집, 모터 명령 실행 | ESP32-S3 DevKitC |
| 조도 센서 | LDR + 10k 저항 전압분배 | 4 | 좌우상하 광량 비교 | BH1750 2~4개 |
| 전압/전류 | INA219 breakout | 1 | 패널 또는 배터리 전압/전류 측정 | INA226 |
| 패널 온도 | 방수형 DS18B20 | 1 | 패널 표면 온도 측정 | NTC + ADC |
| 방위각 구동 | NEMA17 + A4988 또는 DRV8825 | 1세트 | 좌우 회전 | 고토크 서보 |
| 고도각 구동 | MG996R급 금속기어 서보 | 1 | 패널 기울기 조정 | 리니어 액추에이터 + 모터 드라이버 |
| 안전 입력 | 리미트 스위치 | 2~4 | 방위각/고도각 끝단 보호 | 홀 센서 |
| 비상 정지 | 잠금 push button | 1 | 모든 모터 출력 보류 | 토글 스위치 |
| 전원 | 12V 배터리 또는 DC 어댑터 | 1 | 모터/시스템 전원 | 2S/3S 배터리팩 |
| 강압 | 12V to 5V buck converter | 1 | ESP32/센서/서보 전원 | USB 전원 + 별도 서보 전원 |
| 배선 | Dupont, 터미널블록, 퓨즈 | 필요 | 저전압 배선 | JST/XH 커넥터 |

## 선택 근거

- ESP32 DevKitC는 대부분의 I/O가 양쪽 핀 헤더로 나와 있어 브레드보드와 점퍼선 기반 제작에 적합하다. 참고: https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/index.html
- INA219는 3V/5V MCU와 I2C로 연결할 수 있고 high-side 전류와 버스 전압을 측정할 수 있다. 일반 breakout 기준 최대 26V 계측이 가능하다. 참고: https://learn.adafruit.com/adafruit-ina219-current-sensor-breakout/overview
- DS18B20은 1-Wire 방식이라 데이터선 1개로 온도를 읽을 수 있고, 방수형 프로브를 패널 뒷면에 붙이기 쉽다. 참고: https://www.analog.com/media/en/technical-documentation/data-sheets/ds18b20.pdf
- BH1750은 I2C 기반 lux 센서이며 넓은 조도 범위를 읽을 수 있다. 다만 4방향 비교를 하려면 주소 충돌 처리나 I2C mux가 필요하므로 1차 모형은 LDR 4개가 더 단순하다. 참고: https://www.adafruit.com/product/4681

## 권장 제작 순서

1. ESP32가 백엔드 `/api/hardware/telemetry`에 더미 JSON을 보내고 `move`/`hold` 응답을 받는지 확인한다.
2. LDR 4개와 INA219, DS18B20만 연결해 센서값 범위를 확인한다.
3. 모터 전원을 분리한 상태에서 리미트 스위치와 emergency stop 입력을 먼저 테스트한다.
4. 고도각 서보만 연결해 작은 각도 변경 테스트를 한다.
5. 방위각 스텝퍼를 무부하 상태로 테스트한 뒤 패널 구조물에 연결한다.
6. 마지막에 실제 패널과 배터리 부하를 연결한다.

## 안전 기준

- ESP32는 백엔드가 `hold`를 반환하면 즉시 모든 모터 출력을 비활성화한다.
- emergency stop, 리미트 스위치, Wi-Fi 단절, 백엔드 오류는 모두 `hold`로 처리한다.
- 220V AC, 인버터, 상용 태양광 설비 연동은 이 모형 범위에서 제외한다.
- 서보 전원과 ESP32 5V/3.3V 전원은 가능하면 분리하고 GND만 공통으로 묶는다.
