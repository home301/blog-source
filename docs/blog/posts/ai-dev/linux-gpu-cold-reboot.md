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
description: "RTX 5060 Ti로 AI 이미지를 생성하다 GPU가 먹통이 됐다. 소프트 리부트로는 안 살아나고, 전원을 완전히 끄는 콜드부팅만이 답이었다. 원격 환경에서 이걸 자동화한 기록."
---

# Linux에서 GPU 크래시 후 자동 복구하기 — rtcwake 콜드부팅

> RTX 5060 Ti로 AI 이미지를 생성하다 GPU가 먹통이 됐다. 소프트 리부트로는 안 살아나고, 전원을 완전히 끄는 콜드부팅만이 답이었다. 원격 환경에서 이걸 자동화한 기록.

<!-- more -->

## 문제 상황

ComfyUI에서 SDXL + IP-Adapter를 돌리다 VRAM이 초과됐다. `nvidia-smi`를 찍어보면:

```
NVIDIA-SMI has failed because it couldn't communicate with the NVIDIA driver.
```

또는:

```
No devices were found
```

GPU가 완전히 응답을 멈춘 상태. `sudo reboot`으로 재시작해도 동일한 증상이 반복된다. 소프트 리부트으로는 GPU 하드웨어 상태가 초기화되지 않기 때문이다.

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

`alarm_IRQ: yes`가 보이면 정상이다. `alarm_IRQ: no`라면 BIOS 설정이 잘못된 것이다.

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

## 부팅 후 자동 복구 확인

콜드부팅 후 시스템이 켜지면, 서비스들이 제대로 올라왔는지 확인해야 한다.

```bash
# GPU 정상 확인
nvidia-smi

# OpenClaw (또는 다른 상주 서비스) 확인
systemctl --user status openclaw-gateway

# ComfyUI 등은 수동 시작 필요
cd ~/ComfyUI && ./venv/bin/python main.py --lowvram --listen --port 8188 &
```

원격 환경이라면 cron이나 systemd 타이머로 부팅 후 자동 알림을 설정해두면 편하다.

```bash
# crontab -e
@reboot sleep 30 && curl -s "https://api.telegram.org/bot<TOKEN>/sendMessage?chat_id=<ID>&text=서버 재부팅 완료"
```

---

## GPU 크래시를 재현해보려 했다

콜드부팅 자동 복구 흐름을 테스트하려면 GPU 크래시를 의도적으로 만들어야 한다. 여러 방법을 시도했다.

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

실제로 크래시가 발생했던 상황은 PyTorch nightly + ComfyUI에서 SDXL + IP-Adapter를 `--lowvram` 없이 돌렸을 때였다. nightly 빌드의 드라이버 레벨 버그와 여러 대형 모델의 동시 로딩이 결합되어 발생한 것으로 추정된다. 안정적인 드라이버 + 적절한 VRAM 관리(`--lowvram` 모드)를 사용하면 사실상 GPU 크래시를 걱정할 필요가 없다.

그래도 만약을 위해 콜드부팅 스크립트는 만들어두는 게 좋다. 복구 수단이 있다는 것 자체가 안심이 된다.

---

## 정리

| 항목 | 내용 |
|------|------|
| **문제** | GPU 크래시 후 소프트 리부트으로 복구 불가 |
| **해결** | `rtcwake -m off -s 60`으로 콜드부팅 |
| **BIOS 설정** | RTC Wake → OS 모드, 그래픽 → IGD |
| **크래시 재현** | CUDA OOM은 graceful 처리되어 크래시 불가 |
| **교훈** | `--lowvram` 모드 사용하면 OOM 자체를 방지할 수 있다 |

환경: Pop!_OS 24.04 LTS, RTX 5060 Ti 16GB, NVIDIA 드라이버 580.126.18, MSI 메인보드
