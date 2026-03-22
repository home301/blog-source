---
date: 2026-03-07
categories:
  - AI/개발
tags:
  - llm
  - ollama
  - rtx5060ti
  - qwen
slug: local-llm-rtx5060ti
---

# RTX 5060 Ti 16GB로 로컬 LLM 돌리기 — Ollama + Qwen

> 클라우드 API 없이 내 GPU에서 LLM을 돌린다.

<!-- more -->

---

## 왜 로컬 LLM인가

ChatGPT, Claude 같은 클라우드 API는 편하지만 비용이 든다. 로컬 LLM은:

- **무료** — 전기세 빼고
- **프라이버시** — 데이터가 외부로 나가지 않음
- **오프라인** — 인터넷 없이도 동작
- **커스터마이징** — 파인튜닝, 프롬프트 자유도

물론 클라우드 대비 성능은 떨어진다. 하지만 코딩 보조, 문서 요약, 번역 같은 작업에는 충분히 쓸 만하다.

---

## 환경

| 항목 | 스펙 |
|------|------|
| GPU | NVIDIA GeForce RTX 5060 Ti 16GB |
| OS | Pop!_OS 24.04 LTS |
| NVIDIA 드라이버 | 580.126.18 |
| RAM | 16GB + zram swap |
| 저장공간 | 2.7TB HDD (/mnt/data) |

---

## Ollama 설치

[Ollama](https://ollama.com)는 로컬 LLM을 가장 쉽게 실행할 수 있는 도구다. Docker 없이 단일 바이너리로 동작한다.

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

설치 확인:

```bash
ollama --version
```

Ollama는 systemd 서비스로 자동 등록된다. 설치 직후부터 바로 사용 가능하다.

---

## VRAM 제한 설정

16GB VRAM 전부를 LLM에 쓰면 디스플레이 출력이나 다른 GPU 작업에 영향이 간다. systemd 오버라이드로 제한을 건다.

```bash
sudo systemctl edit ollama
```

```ini
[Service]
Environment="OLLAMA_MAX_VRAM=14G"
```

```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

14GB로 제한하면 시스템용 2GB가 남는다.

---

## 모델 선택

16GB VRAM에서 돌릴 수 있는 모델은 양자화 수준에 따라 달라진다.

| 모델 | 파라미터 | 양자화 | VRAM 사용량 | 비고 |
|------|---------|--------|-----------|------|
| Qwen2.5:7b | 7B | Q4_K_M | ~5GB | 범용, 빠름 |
| Qwen3.5:35b-a3b | 35B (활성 3B) | Q4_K_M | ~4GB | MoE, 효율적 |
| Llama3.1:8b | 8B | Q4_K_M | ~5GB | Meta, 영어 강점 |
| Codestral:22b | 22B | Q4_K_M | ~13GB | 코딩 특화 |
| Mixtral:8x7b | 47B (활성 13B) | Q4_K_M | ~14GB | MoE, 다국어 |

> 16GB를 넘는 모델은 CPU 오프로드가 발생해 급격히 느려진다. VRAM 한계를 반드시 확인하고 모델을 선택해야 한다.

---

## 모델 다운로드 및 실행

```bash
# 가벼운 모델부터 시작
ollama pull qwen2.5:7b

# 대화 시작
ollama run qwen2.5:7b
```

```
>>> 한국어로 대답해줘. 캐시 스탬피드가 뭐야?

캐시 스탬피드(Cache Stampede)는 인기 있는 캐시 항목이 만료되는 순간,
대기 중이던 다수의 요청이 동시에 원본 데이터베이스로 몰리는 현상입니다...
```

### MoE 모델: Qwen3.5-35B-A3B

MoE(Mixture of Experts) 모델은 전체 파라미터 크기는 크지만 추론 시 일부만(활성 파라미터) 연산에 참여한다. 35B 파라미터 중 3B만 활성화되므로 VRAM에서 실제로 연산에 쓰이는 비중은 적으며 성능은 강력하다. 

단, 연산 시 사용되는 VRAM은 약 4GB 수준이더라도, **실제 모델의 가중치(약 10~20GB 이상) 전체 데이터는 시스템 RAM이나 VRAM 어딘가에 적재(Offloading)되어 있어야** 하므로 PC 전체의 가용 메모리 상태를 충분히 확보해야 한다.

```bash
ollama pull qwen3.5:35b-a3b
ollama run qwen3.5:35b-a3b
```

---

## API로 사용하기

Ollama는 OpenAI 호환 API를 제공한다. 기본 포트는 11434.

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5:7b",
  "prompt": "Python으로 퀵소트 구현해줘",
  "stream": false
}'
```

Python에서:

```python
import requests

response = requests.post("http://localhost:11434/api/generate", json={
    "model": "qwen2.5:7b",
    "prompt": "Redis 캐시 전략 3가지를 설명해줘",
    "stream": False
})

print(response.json()["response"])
```

OpenAI 호환 엔드포인트도 지원한다:

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="unused")
response = client.chat.completions.create(
    model="qwen2.5:7b",
    messages=[{"role": "user", "content": "캐시 무효화 전략을 설명해줘"}]
)
print(response.choices[0].message.content)
```

---

## VRAM 초과 시 주의

VRAM 한계를 넘는 모델을 무리하게 올리면 GPU 크래시가 발생할 수 있다. 이런 상황을 피하려면:

1. `OLLAMA_MAX_VRAM` 설정으로 VRAM 한도를 제한
2. 모델의 VRAM 요구량을 사전에 확인
3. Stable Diffusion 등 다른 GPU 프로그램과 **동시 실행 금지**

GPU 크래시가 발생했을 때의 복구 방법(콜드부팅, BIOS 설정 등)은 별도 글에서 다룬다.

> [Linux에서 GPU 크래시 후 자동 복구하기 — rtcwake 콜드부팅](../linux-gpu-cold-reboot.md)

---

## 모델 저장 경로 변경

기본 저장 경로는 `/usr/share/ollama/.ollama/`인데, SSD 용량이 부족하면 HDD로 변경할 수 있다.

```bash
sudo systemctl edit ollama
```

```ini
[Service]
Environment="OLLAMA_MODELS=/mnt/data/models/ollama"
```

```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

---

## 정리

| 항목 | 내용 |
|------|------|
| 설치 | `curl -fsSL https://ollama.com/install.sh \| sh` |
| VRAM 제한 | `OLLAMA_MAX_VRAM=14G` (systemd override) |
| 추천 모델 | Qwen2.5:7b (범용), Qwen3.5:35b-a3b (MoE, 고성능) |
| API | OpenAI 호환, localhost:11434 |
| 주의 | VRAM 초과 → CUDA 크래시 → 콜드 부트 필요 |

16GB VRAM이면 7~8B 모델은 쾌적하고, MoE 모델을 활용하면 더 큰 모델도 효율적으로 돌릴 수 있다. 클라우드 API의 대안이라기보다는 보조 수단으로 쓰기에 충분한 수준이다.

---

## 참고

- [Ollama 공식 사이트](https://ollama.com)
- [Ollama 모델 라이브러리](https://ollama.com/library)
- [Qwen 모델 시리즈](https://huggingface.co/Qwen)
