# v09 데이터셋 및 비전모델 학습 계획

## 1. 필요한 이미지 데이터

하늘 상태, 패널 표면 상태, 부분 음영, 이물질, 손상 후보 이미지를 수집한다.

## 2. 클래스 정의

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

## 3. 데이터셋 폴더 구조

```text
datasets/
  images/
  labels/
  README.md
```

## 4. 초기 데이터

초기에는 공개 데이터셋 또는 직접 촬영 이미지를 검토한다. 단, v00~v05 단계에서는 실제 다운로드나 학습을 하지 않는다.

## 5. 모델 후보

MobileNetV3, EfficientNet-B0, ResNet18은 분류 후보로 둔다. YOLOv8n, YOLOv11n은 객체 검출 후보로 둔다.

## 6. 먼저 검증할 것

학습보다 먼저 가상 추론으로 프론트엔드, 백엔드, Agent 흐름을 검증한다.

## 7. API 연결

학습 후에는 FastAPI의 `/api/vision/infer`로 추론 결과를 반환한다.
