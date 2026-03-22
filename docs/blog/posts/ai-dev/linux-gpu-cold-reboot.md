---
date: 2026-03-08
categories:
  - AI/개발
tags:
  - linux
  - gpu
  - rtx5060ti
  - rtcwake
  - cold-boot
  - msi-bios
slug: linux-gpu-cold-reboot
description: "RTX 5060 Ti GPU 크래시 후 rtcwake 콜드부팅으로 자동 복구를 시도했으나, 1회 콜드부팅만으로는 GPU 드라이버가 완전히 초기화되지 않아 실패한 기록."
---

# Linux에서 GPU 크래시 후 자동 복구를 시도하다 — rtcwake 콜드부팅의 한계

> RTX 5060 Ti로 AI 이미지를 생성하다 GPU가 먹통이 됐다. 원격 환경에서 rtcwake 콜드부팅으로 자동 복구를 시도했지만, 결론부터 말하면 완전한 자동 복구에는 실패했다.

<!-- more -->

---

## 문제 상황

ComfyUI에서 SDXL + IP-Adapter를 돌리다 VRAM이 초과됐다. `nvidia-smi`를 찍어보면:

```
NVIDIA-SMI has failed because it couldn't communicate with the NVIDIA driver.
```

또는:

```
No devices were found
```

GPU가 완전히 응답을 멈춘 상태. `sudo reboot`으로 재시작해도 동일한 증상이 반복된다. 소프트 리부트로는 GPU 하드웨어 상태가 초기화되지 않기 때문이다.

**콜드부팅**(전원을 완전히 끄고 다시 켜는 것)만이 해결책이다.

---

## rtcwake로 콜드부팅 자동화

모니터 없이 원격으로만 접속하는 서버라면, 전원을 끄면 다시 켤 수가 없다. `rtcwake`를 쓰면 "전원 끄고 N초 뒤에 자동으로 켜라"를 예약할 수 있다.

```bash
sudo rtcwake -m off -s 60
```

- `-m off`: 전원 완전 차단 (콜드 파워오프)
- `-s 60`: 60초 후 자동 부팅

이 명령을 실행하면 시스템이 즉시 꺼지고, 메인보드의 RTC(Real Time Clock) 알람이 60초 후 시스템을 자동으로 켠다.

### 스크립트로 만들기

```bash
#!/bin/bash
# cold-reboot.sh
DELAY=${1:-60}
echo "$(date): 콜드부팅 예약 - ${DELAY}초 후 자동 재시작"
sudo rtcwake -m off -s "$DELAY"
```

```bash
chmod +x cold-reboot.sh
./cold-reboot.sh 60     # 60초 후 재시작
./cold-reboot.sh 300    # 5분 후 재시작
```

---

## MSI 메인보드 BIOS 설정

rtcwake를 실행했는데 전원이 꺼지기만 하고 자동으로 안 켜진다면, **BIOS 설정**을 확인해야 한다.

### 첫 번째 시도 — 실패

처음 rtcwake를 실행했을 때, 전원은 꺼졌지만 60초가 지나도 자동으로 켜지지 않았다.

```bash
cat /proc/driver/rtc
```

`alarm_IRQ: no` — BIOS에서 RTC Wake가 비활성화된 상태였다.

### RTC Wake 설정

MSI 메인보드 기준:

1. BIOS 진입 (부팅 시 DEL 키)
2. **Advanced** → **Wake Up Event Setup** → **Resume By RTC Alarm**
3. **OS 모드**로 설정

주의할 점이 있다. MSI BIOS의 RTC Wake에는 두 가지 모드가 있다.

- **BIOS 모드**: BIOS에서 직접 시간을 지정 (예: 매일 07:00에 켜기)
- **OS 모드**: OS(Linux)가 RTC 알람을 설정하도록 허용

`rtcwake`는 OS에서 RTC 알람을 설정하는 방식이므로, 반드시 **OS 모드**여야 한다. BIOS 모드로 두면 `rtcwake`가 설정한 알람이 무시된다.

설정 후 확인:

```bash
cat /proc/driver/rtc
```

`alarm_IRQ: yes`가 보이면 정상이다.

### 온보드 그래픽 출력 문제

BIOS 설정을 바꾸려면 모니터를 연결해야 하는데, 여기서 또 다른 문제가 있었다.

RTX 5060 Ti에는 DisplayPort와 HDMI만 있다. 기존 모니터가 DVI-D라면 직접 연결할 수 없다. 이 경우 메인보드의 **온보드 그래픽**(내장 GPU)으로 모니터를 연결해야 한다.

MSI 메인보드에서 온보드 그래픽 출력을 활성화하려면:

1. BIOS 진입
2. **Advanced** → **Integrated Graphics Configuration** (또는 **IGD Multi-Monitor**)
3. **Initiate Graphic Adapter**: **IGD**로 변경

기본값은 **PEG**(외장 GPU 우선)로 되어 있어서, 외장 GPU에 모니터를 연결하지 않으면 화면이 안 나온다. **IGD**로 바꾸면 메인보드의 HDMI/VGA 포트로 화면이 출력된다.

문제는 이미 BIOS에서 PEG로 설정된 상태에서 외장 GPU에 모니터를 연결할 수 없으면, BIOS 화면 자체를 볼 수 없다는 것이다. 이 경우:

1. **CMOS 초기화**: 메인보드의 CMOS 클리어 점퍼를 사용하거나 배터리를 빼서 BIOS를 초기화한다
2. 초기화 후 온보드 출력이 기본 활성화되므로, 메인보드 포트로 모니터를 연결한다
3. BIOS에서 IGD 설정 + RTC Wake OS 모드를 함께 잡는다

---

## 두 번째 시도 — 부분 성공

BIOS 설정을 마치고 다시 테스트했다.

```bash
sudo rtcwake -m off -s 60
```

이번에는 성공했다. 전원이 꺼지고 60초 후 자동으로 켜졌다. GPU도 정상이었다.

여기서 "해결됐다"고 생각했다.

---

## 실전 투입 — 실패

실제 GPU 크래시가 다시 발생했다. 이미지 생성 작업(3모델 x 4표정) 중이었다.

```
nvidia-smi: "Unable to determine the device handle"
nvidia-smi: "No devices were found"
```

콜드부팅 스크립트를 실행했다.

```bash
sudo rtcwake -m off -s 60
```

전원 차단은 성공했다. 60초 후 자동 재시작도 됐다. **하지만 OS 부팅에 실패했다.**

화면에는 GPU 드라이버 에러 메시지가 반복 출력됐다. 부팅이 완료되지 않아 SSH 접속도 불가능했다.

결국 직접 전원 버튼을 길게 눌러 강제 종료하고, 수동으로 전원을 다시 켜서야 정상 부팅됐다.

---

## 왜 실패했는가

테스트 때는 GPU가 정상인 상태에서 콜드부팅을 했고, 실전에서는 **GPU가 크래시된 상태**에서 콜드부팅을 했다. 차이는 이렇다.

- **정상 상태 콜드부팅**: 전원 차단 → 60초 대기 → 재시작 → GPU 초기화 성공
- **크래시 상태 콜드부팅**: 전원 차단 → 60초 대기 → 재시작 → GPU 드라이버가 비정상 상태의 GPU를 초기화하지 못함

추정하건대, rtcwake의 60초 대기로는 GPU 하드웨어의 전원이 완전히 방전되지 않은 것 같다. GPU 내부의 상태가 잔류해서, 재시작 시 드라이버가 정상적으로 초기화하지 못한 것으로 보인다.

수동으로 전원 버튼을 길게 눌러 강제 종료한 뒤 몇 초간 전원이 완전히 꺼진 상태를 거치면, GPU가 완전히 초기화되어 정상 부팅이 가능했다.

---

## GPU 크래시를 재현해보려 했다

콜드부팅 복구 흐름을 다시 테스트하려면 GPU 크래시를 의도적으로 만들어야 한다. 여러 방법을 시도했다.

### 시도 1: VRAM 가득 채우기

```python
import torch
tensors = []
while True:
    tensors.append(torch.randn(1024, 1024, 256, device='cuda'))
```

결과: CUDA가 OOM(Out of Memory) 에러를 내고 **정상 종료**한다. GPU는 멀쩡하다.

### 시도 2: Ollama + ComfyUI 동시 실행

35B 모델을 Ollama에 올린 상태에서 ComfyUI로 SDXL 이미지 생성을 시도했다.

결과: VRAM이 부족하면 Ollama가 모델을 CPU로 오프로딩하거나, ComfyUI가 OOM으로 중단한다. GPU 크래시는 발생하지 않았다.

### 시도 3: 직접 CUDA 메모리 할당

`cudaMalloc`으로 VRAM 전체를 직접 할당하는 C 프로그램을 작성해봤다.

결과: 역시 CUDA 런타임이 할당 실패를 반환할 뿐, GPU 드라이버 크래시로 이어지지 않았다.

### 결론

**최신 CUDA 드라이버는 OOM을 graceful하게 처리한다.** 단순히 VRAM을 초과하는 것만으로는 GPU 크래시가 나지 않는다.

실제로 크래시가 발생했던 상황은 PyTorch nightly + ComfyUI에서 SDXL + IP-Adapter를 `--lowvram` 없이 돌렸을 때였다. nightly 빌드의 드라이버 레벨 버그와 여러 대형 모델의 동시 로딩이 결합되어 발생한 것으로 추정된다.

---

## 남은 과제

rtcwake 콜드부팅은 **정상 상태에서의 원격 재시작 수단**으로는 유효하지만, **GPU 크래시 후 자동 복구 수단**으로는 불완전하다.

개선 가능성이 있는 방향:

- **대기 시간 연장**: 60초가 아닌 300초(5분) 이상 대기하여 GPU 전원 방전 시간을 확보
- **다중 콜드부팅**: 1회 실패 시 watchdog으로 2차 콜드부팅 시도
- **스마트 플러그**: 네트워크 제어 가능한 전원 플러그로 물리적 전원 차단/투입

현재로서는 이 중 어느 것도 검증하지 못했다. GPU 크래시를 의도적으로 재현할 수 없기 때문이다.

---

## 정리

| 항목 | 내용 |
|------|------|
| **문제** | GPU 크래시 후 소프트 리부트로 복구 불가 |
| **시도** | `rtcwake -m off -s 60`으로 콜드부팅 |
| **BIOS 설정** | RTC Wake → OS 모드, 그래픽 → IGD |
| **테스트 결과** | 정상 상태에서 콜드부팅 성공 |
| **실전 결과** | GPU 크래시 상태에서 콜드부팅 후 OS 부팅 실패 |
| **최종 복구** | 수동 전원 강제 종료 → 수동 재시작으로 복구 |
| **교훈** | rtcwake 1회 콜드부팅으로는 GPU가 완전히 초기화되지 않을 수 있다 |

환경: Pop!_OS 24.04 LTS, RTX 5060 Ti 16GB, NVIDIA 드라이버 580.126.18, MSI 메인보드
