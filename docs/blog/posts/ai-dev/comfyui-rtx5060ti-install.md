---
date: 2026-03-07
categories:
  - AI/개발
tags:
  - comfyui
  - rtx5060ti
  - ai-image
  - pytorch
slug: comfyui-rtx5060ti-install
description: "노드 기반 워크플로우로 이미지 생성 파이프라인을 구축한다."
---

# RTX 5060 Ti 16GB에 ComfyUI 설치하기

> 노드 기반 워크플로우로 이미지 생성 파이프라인을 구축한다.

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

Forge 설치 글에서 다뤘듯이, RTX 5060 Ti(sm_120)에서는 **PyTorch nightly cu128**이 필수다. ComfyUI도 마찬가지.

---

## 설치

### 1. ComfyUI 클론

```bash
cd ~
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
```

### 2. 가상환경 + PyTorch nightly

```bash
python3.10 -m venv venv
source venv/bin/activate

pip install --pre torch torchvision torchaudio \
  --index-url https://download.pytorch.org/whl/nightly/cu128
```

### 3. ComfyUI 의존성

```bash
pip install -r requirements.txt
```

Forge와 달리 ComfyUI는 의존성이 가볍다. 설치가 빠르게 끝난다.

### 4. 실행

```bash
python main.py --listen --port 8188
```

`http://localhost:8188`로 접속하면 노드 에디터가 나타난다. Forge와 달리 **WebUI 모드가 정상 동작**한다.

---

## 모델 설정

### 체크포인트

모델 파일을 `models/checkpoints/`에 넣는다. Forge와 모델을 공유하려면 심볼릭 링크가 편하다.

```bash
ln -s ~/stable-diffusion-webui-forge/models/Stable-diffusion/dreamshaper_8.safetensors \
      ~/ComfyUI/models/checkpoints/dreamshaper_8.safetensors
```

### ControlNet

```bash
# OpenPose
wget -P models/controlnet/ \
  https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15_openpose.pth
```

| 모델 | 용도 | 크기 |
|------|------|------|
| control_v11p_sd15_openpose | 포즈 제어 | 1.4GB |
| control_v11p_sd15_canny | 윤곽선 제어 | 1.4GB |
| control_v11f1p_sd15_depth | 깊이 맵 제어 | 1.4GB |

### IP-Adapter

캐릭터 일관성 유지에 유용하다. 참조 이미지의 스타일이나 구도를 유지하면서 새 이미지를 생성할 수 있다.

```bash
# IP-Adapter Plus SD1.5
wget -P models/ipadapter/ \
  https://huggingface.co/h94/IP-Adapter/resolve/main/models/ip-adapter-plus_sd15.safetensors

# CLIP Vision (IP-Adapter가 필요로 함)
wget -P models/clip_vision/ \
  https://huggingface.co/h94/IP-Adapter/resolve/main/models/image_encoder/model.safetensors
```

---

## 커스텀 노드 설치

ComfyUI의 강점은 커스텀 노드 생태계다. `custom_nodes/` 디렉토리에 클론하면 된다.

```bash
cd custom_nodes

# IP-Adapter Plus
git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git

# ControlNet 전처리기 (OpenPose, Canny 등)
git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git
cd comfyui_controlnet_aux && pip install -r requirements.txt && cd ..

# AnimateDiff (애니메이션 생성)
git clone https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved.git
```

설치 후 ComfyUI를 재시작하면 노드 목록에 추가된다.

---

## 백그라운드 실행

SSH 세션이 끊겨도 유지되도록 `setsid`를 사용한다.

```bash
cd ~/ComfyUI
setsid ./venv/bin/python main.py --listen --port 8188 \
  > /tmp/comfyui.log 2>&1 &
```

또는 재시작 스크립트를 만들어 두면 편하다:

```bash
#!/bin/bash
pkill -f "ComfyUI/main.py" 2>/dev/null
sleep 2
cd ~/ComfyUI
setsid ./venv/bin/python main.py --listen --port 8188 \
  > /tmp/comfyui.log 2>&1 &
echo "ComfyUI started on port 8188"
```

---

## Forge와 비교

| 항목 | Forge | ComfyUI |
|------|-------|---------|
| UI | 전통적인 WebUI (RTX 5060 Ti에서 비정상) | 노드 에디터 (정상 동작) |
| 사용 난이도 | 낮음 | 중간 (노드 개념 이해 필요) |
| 유연성 | 제한적 | 매우 높음 (워크플로우 자유 구성) |
| ControlNet | 탭에서 설정 | 노드로 연결 (다중 ControlNet 용이) |
| IP-Adapter | 확장 설치 | 노드로 바로 사용 |
| 배치 작업 | API 호출 | API 호출 + 워크플로우 저장/재사용 |
| RTX 5060 Ti 호환 | API 모드만 가능 | WebUI 정상 동작 |

간단한 이미지 생성이라면 Forge API가 빠르다. 하지만 ControlNet + IP-Adapter를 조합하거나, 캐릭터 파이프라인처럼 복잡한 워크플로우가 필요하면 ComfyUI가 훨씬 유리하다.

---

## 성능

DreamShaper v8, 1024x1024, 20 스텝 기준으로 Forge API 모드와 거의 동일한 속도가 나온다. 같은 PyTorch 백엔드를 쓰니 당연한 결과다.

VRAM 16GB 덕분에 SD 1.5 + ControlNet + IP-Adapter를 동시에 로드해도 여유가 있다.

---

## 정리

1. PyTorch nightly cu128 설치 (Forge와 동일)
2. ComfyUI 자체 설치는 단순 — `git clone` + `pip install -r requirements.txt`
3. 모델은 Forge와 심볼릭 링크로 공유 가능
4. WebUI가 정상 동작하므로 Forge처럼 API 모드를 강제할 필요 없음
5. 커스텀 노드로 기능 확장이 자유로움

---

## 참고

- [ComfyUI GitHub](https://github.com/comfyanonymous/ComfyUI)
- [ComfyUI Manager](https://github.com/ltdrdata/ComfyUI-Manager) — 커스텀 노드 관리 UI
- [IP-Adapter Plus](https://github.com/cubiq/ComfyUI_IPAdapter_plus)
- [ControlNet 전처리기](https://github.com/Fannovel16/comfyui_controlnet_aux)
