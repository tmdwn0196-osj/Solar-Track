# SolarTrack ESP32 배선안

기준 보드는 ESP32 DevKitC 계열이다. 실제 보드 실크스크린이 다르면 GPIO 번호 기준으로 다시 확인한다.

## 핀맵

| 기능 | ESP32 GPIO | 연결 대상 | 비고 |
|---|---:|---|---|
| I2C SDA | 21 | INA219 SDA | 3.3V 로직 |
| I2C SCL | 22 | INA219 SCL | 3.3V 로직 |
| LDR 좌측 | 34 | LDR 전압분배 중간점 | ADC 입력 전용 |
| LDR 우측 | 35 | LDR 전압분배 중간점 | ADC 입력 전용 |
| LDR 상단 | 32 | LDR 전압분배 중간점 | ADC |
| LDR 하단 | 33 | LDR 전압분배 중간점 | ADC |
| 풍속 입력 선택 | 39 | 아날로그 풍속계 | 미사용 시 0 처리 |
| DS18B20 데이터 | 4 | DS18B20 DQ | 4.7k pull-up 권장 |
| 고도각 서보 PWM | 18 | MG996R signal | 서보 전원 별도 |
| 스텝퍼 STEP | 26 | A4988/DRV8825 STEP | 방위각 |
| 스텝퍼 DIR | 27 | A4988/DRV8825 DIR | 방위각 |
| 스텝퍼 ENABLE | 25 | A4988/DRV8825 ENABLE | LOW enable |
| 방위각 최소 리미트 | 13 | NC/NO 스위치 | INPUT_PULLUP |
| 방위각 최대 리미트 | 14 | NC/NO 스위치 | INPUT_PULLUP |
| 고도각 최소 리미트 | 16 | NC/NO 스위치 | INPUT_PULLUP |
| 고도각 최대 리미트 | 17 | NC/NO 스위치 | INPUT_PULLUP |
| 비상 정지 | 23 | emergency stop switch | INPUT_PULLUP |
| 강수 감지 | 19 | rain switch/module | INPUT_PULLUP |

## LDR 전압분배

각 LDR은 3.3V와 ADC 핀 사이에 두고, ADC 핀과 GND 사이에는 10k 저항을 둔다. 이 프로젝트는 절대 lux보다 방향별 상대 차이가 중요하므로 같은 종류의 LDR과 같은 저항값을 사용한다.

## INA219

INA219는 패널 또는 배터리의 + 라인에 high-side로 직렬 연결한다. 모형에서는 패널 출력 측 전압과 전류를 보는 구성이 가장 직접적이다. 보드 정격 전류와 션트 저항 발열을 넘기지 않는다.

## DS18B20

방수형 DS18B20은 패널 뒷면에 열전도 테이프로 붙인다. DATA와 3.3V 사이에는 4.7k pull-up 저항을 둔다.

## 모터 전원

서보와 스텝퍼는 ESP32 3.3V 핀에서 전원을 공급하지 않는다. 별도 5V/12V 전원을 사용하고 GND만 공통으로 연결한다. 모터 테스트 전에는 패널을 분리한 무부하 상태에서 방향과 리미트 스위치를 먼저 확인한다.
