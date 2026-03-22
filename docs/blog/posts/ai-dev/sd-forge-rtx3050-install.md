---
date: 2026-03-02
categories:
  - AI/개발
tags:
  - stable-diffusion
  - rtx3050
  - ai-image
  - tutorial
---

# RTX 3050 6GB로 Stable Diffusion Forge 설치하기

> VRAM 6GB GPU로 AI 이미지 생성이 가능한지 직접 설치하고 돌려봤다.

<!-- more -->

---

## 왜 Forge인가?

AI 이미지 생성의 대명사 **Stable Diffusion**을 로컬에서 돌리려면 WebUI가 필요하다. 가장 유명한 건 **AUTOMATIC1111**이지만, 2026년 현재 추천하는 건 **Stable Diffusion WebUI Forge**다.

**Forge를 추천하는 이유:**
- AUTOMATIC1111의 포크로 **UI가 거의 동일** (기존 가이드 대부분 호환)
- **VRAM 최적화가 훨씬 우수** — 6GB GPU에서 체감 차이 큼
- AUTOMATIC1111의 일부 의존 레포가 2025년 이후 비공개 전환되어 **신규 설치 불가**
- 최신 모델(SDXL, SD3 등) 지원이 더 빠름

---

## 내 PC 사양

| 항목 | 스펙 |
|------|------|
| **CPU** | Intel Core i7-6700K @ 4.00GHz |
| **RAM** | 16GB DDR4 |
| **GPU** | NVIDIA GeForce RTX 3050 (VRAM 6GB) |
| **OS** | Pop!_OS 24.04 LTS (Ubuntu 기반) |
| **NVIDIA 드라이버** | 580.119.02 |
| **저장공간** | 230GB SSD (여유 200GB+) |

> **Windows 사용자**도 과정은 거의 동일하다. 차이점은 아래에서 별도 안내한다.

---

## 사전 준비

### 1. Python 3.10 설치 (필수!)

Forge는 **Python 3.10**을 요구한다. 3.11이나 3.12에서는 torch 호환 문제가 발생한다.

```bash
# Ubuntu/Pop!_OS
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt install -y python3.10 python3.10-venv python3.10-dev
```

> **실제 겪은 문제:** Python 3.12에서 먼저 시도했더니 `torch==2.1.2` 버전을 찾을 수 없다는 에러가 발생했다. Python 3.10으로 바꾸니 바로 해결.

**Windows:** [Python 3.10.6 공식 다운로드](https://www.python.org/downloads/release/python-3106/)에서 설치. "Add to PATH" 체크 필수.

### 2. Git 설치

```bash
# Ubuntu/Pop!_OS
sudo apt install -y git

# Windows: https://git-scm.com/ 에서 다운로드
```

### 3. NVIDIA 드라이버 확인

```bash
nvidia-smi
```

드라이버 버전이 **530 이상**이면 OK. 안 나오면 NVIDIA 드라이버부터 설치해야 한다.

---

## 설치 과정

### Step 1: Forge 클론

```bash
cd ~
git clone https://github.com/lllyasviel/stable-diffusion-webui-forge.git
cd stable-diffusion-webui-forge
```

### Step 2: Python 3.10 가상환경 생성

```bash
python3.10 -m venv venv
```

> 이 단계를 건너뛰면 시스템 Python(3.12 등)이 사용되어 에러가 발생할 수 있다.

### Step 3: WebUI 실행 (첫 실행 시 자동 설치)

```bash
bash webui.sh --xformers --skip-python-version-check
```

**Windows:**
```cmd
webui-user.bat
```

첫 실행 시 자동으로 다운로드되는 것들:
- **PyTorch + CUDA** (~780MB)
- **cuDNN, cuBLAS 등 NVIDIA 라이브러리** (~1.5GB)
- **xformers** (VRAM 최적화 라이브러리)
- **기타 의존성** (clip, open_clip, BLIP 등)

> **소요 시간:** 인터넷 속도에 따라 10~30분. 약 15분 걸렸다.

### Step 4: 정상 실행 확인

모든 설치가 끝나면 이런 메시지가 나온다:

```
Running on local URL: http://127.0.0.1:7860
```

브라우저에서 `http://localhost:7860` 접속하면 WebUI가 나타난다.

---

## 설치 중 만난 에러와 해결법

### 에러 1: python3-venv 패키지 없음

```
The virtual environment was not created successfully because ensurepip is not available.
```

**해결:**
```bash
sudo apt install python3.10-venv
```

### 에러 2: torch 버전 호환 (Python 3.12)

```
ERROR: Could not find a version that satisfies the requirement torch==2.1.2
```

**해결:** Python 3.10 설치 후 venv 재생성 (위 가이드 참고)

### 에러 3: AUTOMATIC1111 레포 클론 실패

```
fatal: could not read Username for 'https://github.com'
RuntimeError: Couldn't clone Stable Diffusion
```

**원인:** Stability-AI GitHub 레포가 비공개로 전환됨.
**해결:** AUTOMATIC1111 대신 **Forge 사용** (이 가이드를 따르면 문제없음)

### 에러 4: numpy 바이너리 호환성

```
ValueError: numpy.dtype size changed, may indicate binary incompatibility
```

**해결:**
```bash
./venv/bin/pip install --upgrade numpy scikit-image
```

### 에러 5: svglib 설치 실패 (무시 가능)

```
Couldn't install sd-forge-controlnet requirement: svglib
```

**영향:** ControlNet 일부 프리프로세서만 영향. 핵심 이미지 생성에는 문제없음. 무시해도 된다.

---

## RTX 3050 6GB에서의 성능

| 모델 | 해상도 | 생성 가능 여부 | 비고 |
|------|--------|--------------|------|
| **SD 1.5** | 512x512 | O 쾌적 | 가장 추천 |
| **SD 1.5** | 768x768 | O 가능 | 약간 느림 |
| **SDXL** | 1024x1024 | △ 가능하나 느림 | xformers 필수 |
| **SD 3** | 1024x1024 | X VRAM 부족 | 8GB 이상 권장 |
| **Flux** | — | X VRAM 부족 | 12GB 이상 권장 |

> **팁:** `--xformers` 옵션은 **필수**다. VRAM 사용량을 크게 줄여준다. Forge는 여기에 추가 최적화가 적용되어 AUTOMATIC1111보다 약 20~30% 적은 VRAM을 사용한다.

---

## 모델 다운로드

Forge 설치만으로는 이미지 생성이 안 된다. **체크포인트 모델**을 따로 받아야 한다.

### 추천 모델 (RTX 3050 6GB용)

| 모델 | 크기 | 용도 | 다운로드 |
|------|------|------|----------|
| **Realistic Vision v5.1** | ~2GB | 실사풍 | [CivitAI](https://civitai.com/models/4201) |
| **DreamShaper v8** | ~2GB | 범용 (실사+일러스트) | [CivitAI](https://civitai.com/models/4384) |
| **Anything v5** | ~2GB | 애니메이션풍 | [CivitAI](https://civitai.com/models/9409) |

다운로드 후 이 경로에 넣으면 된다:
```
stable-diffusion-webui-forge/models/Stable-diffusion/
```

---

## 마무리

RTX 3050 6GB는 AI 이미지 생성의 **최소 스펙**에 가깝지만, Forge + xformers 조합이면 SD 1.5 모델은 충분히 실용적으로 사용 가능하다.

**총 소요 시간:** 약 30분 (트러블슈팅 포함 1시간)
**총 비용:** 0원 (모든 소프트웨어 무료)

고사양 GPU가 없어도 로컬 AI 이미지 생성을 시작할 수 있다는 게 핵심이다.

---

**관련 링크:**
- [Stable Diffusion WebUI Forge GitHub](https://github.com/lllyasviel/stable-diffusion-webui-forge)
- [CivitAI — 모델 다운로드](https://civitai.com/)
- [Python 3.10 다운로드](https://www.python.org/downloads/release/python-3106/)

---


