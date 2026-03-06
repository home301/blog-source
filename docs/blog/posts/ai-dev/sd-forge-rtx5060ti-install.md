---
date: 2026-03-07
categories:
  - AI/개발
tags:
  - stable-diffusion
  - rtx5060ti
  - ai-image
  - pytorch
---

# RTX 5060 Ti 16GB에 Stable Diffusion Forge 설치하기

> RTX 50 시리즈 초기 사용자가 겪는 PyTorch 호환 삽질의 기록.

<!-- more -->

---

## 환경

| 항목 | 스펙 |
|------|------|
| GPU | NVIDIA GeForce RTX 5060 Ti 16GB |
| OS | Pop!_OS 24.04 LTS (커널 6.18.7) |
| NVIDIA 드라이버 | 580.126.18 |
| CUDA | 12.8 |
| Python | 3.10.20 |
| 저장공간 | 238GB SSD + 2.7TB HDD |

---

## 핵심 문제: sm_120

RTX 5060 Ti는 Blackwell 아키텍처로, CUDA compute capability가 **sm_120**이다. 2026년 3월 기준으로 이 아키텍처를 지원하는 PyTorch는 **nightly cu128 빌드뿐**이다.

안정 릴리스(cu121, cu126)로 설치하면 이런 에러가 나온다:

```
CUDA error: no kernel image is available for execution on the device
```

또는 아예 GPU를 인식하지 못한다.

---

## 설치 과정

### 1. Forge 클론

```bash
cd ~
git clone https://github.com/lllyasviel/stable-diffusion-webui-forge.git
cd stable-diffusion-webui-forge
```

### 2. Python 3.10 가상환경

```bash
python3.10 -m venv venv
source venv/bin/activate
```

### 3. PyTorch nightly cu128 설치

여기가 핵심이다. Forge의 기본 설치 스크립트를 쓰면 안정 버전 PyTorch가 설치되는데, sm_120에서는 동작하지 않는다. **수동으로 nightly를 먼저 설치**해야 한다.

```bash
pip install --pre torch torchvision torchaudio \
  --index-url https://download.pytorch.org/whl/nightly/cu128
```

설치되는 버전: `torch 2.12.0.dev20260304+cu128`

설치 후 확인:

```bash
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"
```

```
2.12.0.dev20260304+cu128
True
```

### 4. Forge 의존성 설치

PyTorch가 이미 설치된 상태에서 Forge를 실행하면 나머지 의존성만 추가로 설치된다.

```bash
bash webui.sh --xformers --skip-torch-cuda-test --skip-python-version-check
```

> `--skip-torch-cuda-test`를 빼면 nightly 버전에서 검증 에러가 날 수 있다.

### 5. WebUI 모드는 안 된다

여기서 한 가지 함정이 있다. 설치 완료 후 WebUI가 정상적으로 뜨는 것처럼 보이지만, 실제로는 **"Using online LoRAs in FP16: False"** 메시지 이후 조용히 멈춘다. 에러 메시지도 없다.

원인은 PyTorch nightly와 Gradio 간의 호환 문제로 추정된다. 해결책은 **API 모드로 실행**하는 것이다.

```bash
python launch.py --nowebui --api --listen --port 7861 \
  --skip-torch-cuda-test --xformers
```

이 모드에서는 `http://localhost:7861/sdapi/v1/txt2img` 엔드포인트로 이미지를 생성할 수 있다.

---

## 성능

DreamShaper v8 모델 기준:

| 해상도 | 스텝 | 소요 시간 | 속도 |
|--------|------|----------|------|
| 512x512 | 10 | 1.4초 | 7.02 it/s |
| 512x512 | 20 | 2.8초 | 7.02 it/s |
| 1024x1024 | 20 | ~11초 | — |

RTX 3050 6GB 대비 약 5배 빠르다. VRAM 16GB 덕분에 1024x1024도 무리 없이 생성된다.

| 모델 | 해상도 | 가능 여부 |
|------|--------|----------|
| SD 1.5 | 512~1024 | O |
| SDXL | 1024x1024 | O |
| SD 3 | 1024x1024 | O (VRAM 여유) |
| Flux | — | △ (모델에 따라) |

---

## API로 이미지 생성하기

WebUI가 없으니 API로 직접 호출한다.

```python
import requests, base64, io
from PIL import Image

response = requests.post("http://localhost:7861/sdapi/v1/txt2img", json={
    "prompt": "a fantasy landscape, detailed, 4k",
    "negative_prompt": "blurry, low quality",
    "steps": 20,
    "width": 512,
    "height": 512,
    "cfg_scale": 7,
    "sampler_name": "Euler a"
})

img_data = base64.b64decode(response.json()["images"][0])
image = Image.open(io.BytesIO(img_data))
image.save("output.png")
```

---

## 정리

RTX 5060 Ti에서 Forge를 돌리기 위한 핵심:

1. **PyTorch nightly cu128** 수동 설치 (안정 버전은 sm_120 미지원)
2. **`--nowebui --api` 모드** 사용 (WebUI는 조용히 멈춤)
3. `--skip-torch-cuda-test` 플래그 필수

RTX 50 시리즈 초기라 이런 삽질이 필요하지만, PyTorch 안정 릴리스에 sm_120 지원이 포함되면 일반적인 설치 방법으로 돌아갈 수 있다.

---

## 참고

- [Stable Diffusion WebUI Forge GitHub](https://github.com/lllyasviel/stable-diffusion-webui-forge)
- [PyTorch Nightly 설치](https://pytorch.org/get-started/locally/)
- [NVIDIA Blackwell 아키텍처](https://developer.nvidia.com/blackwell)
