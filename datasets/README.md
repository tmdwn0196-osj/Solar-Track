# datasets

비전모델 학습용 데이터셋 계획과 샘플 구조가 들어갈 영역이다.

v09에서는 실제 데이터셋 다운로드나 학습을 수행하지 않는다. 대신 이미지와 라벨을 넣을 위치, 클래스 정의, 샘플 매니페스트 형식만 확정한다.

## 클래스

| 클래스 | 용도 | 설명 |
|---|---|---|
| `sky_clear` | 분류 | 맑은 하늘 |
| `sky_cloudy` | 분류 | 흐린 하늘 |
| `sun_cloud_block` | 검출 | 구름이 태양을 가리는 상황 |
| `panel_clean` | 분류 | 깨끗한 패널 |
| `panel_soiling` | 검출 | 먼지, 오염, 물자국 |
| `panel_partial_shadow` | 검출 | 부분 음영 |
| `panel_foreign_object` | 검출 | 낙엽, 이물질 |
| `panel_damage` | 검출 | 균열, 그을림, 손상 후보 |

## 폴더 구조

```text
datasets/
  images/
    raw/
    train/
    val/
  labels/
    classification/
    detection/
  sample_manifest.csv
```

## 라벨 기준

- 분류 라벨은 이미지 전체 상태를 하나 이상 기록한다.
- 검출 라벨은 YOLO 형식 후보를 기준으로 `class_id x_center y_center width height`를 사용한다.
- 실제 하드웨어 촬영 전까지는 공개 데이터셋 또는 직접 촬영 후보 목록만 조사한다.
- 학습 전에는 FastAPI의 가상 비전 추론 결과로 UI와 Agent 흐름을 검증한다.
