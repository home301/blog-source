---
date: 2026-03-07
categories:
  - AI/개발
tags:
  - openclaw
  - ai-assistant
  - telegram
  - claude
slug: openclaw-personal-assistant
---

# OpenClaw으로 개인 AI 비서 만들기 — 텔레그램 + Claude

> 텔레그램으로 대화하면 Claude가 내 서버에서 파일을 읽고, 명령어를 실행하고, 이미지를 보내주는 환경을 구축한다.

<!-- more -->

---

## OpenClaw이 뭔가

[OpenClaw](https://openclaw.ai)은 AI 에이전트를 메신저(텔레그램, WhatsApp, Discord 등)에 연결하는 게이트웨이다. 단순한 챗봇이 아니라, 서버에서 직접 명령어를 실행하고 파일을 다루는 **개인 비서** 수준의 에이전트를 만들 수 있다.

할 수 있는 것들:

- 텔레그램으로 대화하면 Claude/GPT가 응답
- 서버의 파일 읽기/쓰기
- 셸 명령어 실행
- 웹 검색
- 이미지 생성 후 메신저로 전송
- 크론 작업 (정기적으로 알림, 모니터링 등)
- 브라우저 자동화

---

## 환경

| 항목 | 내용 |
|------|------|
| 서버 | Pop!_OS 24.04 LTS |
| Node.js | v22.22.0 |
| OpenClaw | 2026.2.26 |
| AI 모델 | Anthropic Claude Opus 4.6 |
| 메신저 | 텔레그램 |

---

## 설치

### 1. Node.js 22 설치

OpenClaw은 Node.js 22 이상이 필요하다.

```bash
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs
```

### 2. OpenClaw 설치

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

설치 스크립트가 npm 글로벌 설치와 초기 설정 마법사를 자동으로 실행한다.

### 3. 초기 설정

마법사가 묻는 것들:

1. **AI 프로바이더** — Anthropic, OpenAI 등 선택
2. **API 키** — 선택한 프로바이더의 API 키 입력
3. **모델** — 사용할 모델 선택 (예: claude-opus-4-6)
4. **메신저 채널** — 텔레그램, WhatsApp 등 선택

---

## 텔레그램 연동

### 봇 생성

1. 텔레그램에서 [@BotFather](https://t.me/BotFather)에게 `/newbot` 명령
2. 봇 이름과 username 설정
3. 발급된 **Bot Token** 복사

### OpenClaw 설정

```bash
openclaw config
```

텔레그램 채널 설정에서 Bot Token을 입력하고, `allowFrom`에 자신의 텔레그램 ID를 등록한다. 이렇게 해야 본인만 봇과 대화할 수 있다.

```bash
# 텔레그램 ID 확인: @userinfobot에게 메시지를 보내면 알려준다
```

### 게이트웨이 시작

```bash
openclaw gateway start
```

이제 텔레그램에서 봇에게 메시지를 보내면 Claude가 응답한다.

---

## 실제 사용 예

### 파일 작업

```
나: 워크스페이스에 있는 파일 목록 보여줘
봇: (ls 실행 후 결과 전달)

나: MEMORY.md 내용 보여줘
봇: (파일 읽어서 내용 전달)
```

### 이미지 생성

로컬에 Stable Diffusion이 설치되어 있으면 API로 호출해서 이미지를 생성하고 텔레그램으로 바로 보내준다.

```
나: 판타지 풍경 이미지 생성해줘
봇: (Forge/ComfyUI API 호출 → 이미지 생성 → 텔레그램 전송)
```

### 웹 검색

```
나: RTX 5060 Ti 벤치마크 검색해줘
봇: (Brave Search API 호출 → 결과 요약)
```

### 크론 작업

```
나: 매일 아침 9시에 날씨 알려줘
봇: (크론 작업 등록 → 매일 9시에 텔레그램으로 날씨 전송)
```

---

## 주요 설정

### 모델 설정

`openclaw.json`에서 기본 모델과 폴백을 설정할 수 있다. API 과부하 시 자동으로 하위 모델로 전환하는 것도 가능하다.

### 하트비트

에이전트가 주기적으로 깨어나서 할 일을 체크하는 기능이다. 이메일 확인, 캘린더 알림, 날씨 체크 등을 자동으로 수행할 수 있다.

### 워크스페이스

`~/.openclaw/workspace/`가 에이전트의 작업 디렉토리다. 에이전트의 성격(SOUL.md), 사용자 정보(USER.md), 기억(MEMORY.md) 등을 파일로 관리한다.

| 파일 | 역할 |
|------|------|
| SOUL.md | 에이전트의 성격, 말투 |
| USER.md | 사용자 정보, 선호도 |
| MEMORY.md | 장기 기억 |
| RULES.md | 운영 규칙 |
| memory/YYYY-MM-DD.md | 일별 기록 |

---

## 보안 주의사항

OpenClaw은 서버에서 셸 명령어를 실행할 수 있는 강력한 도구다. 반드시 지켜야 할 것:

- **allowFrom 설정** — 본인의 메신저 ID만 허용. 설정하지 않으면 누구나 서버에 명령을 내릴 수 있다
- **전용 계정 사용** — root가 아닌 일반 사용자 계정으로 실행
- **API 키 관리** — 설정 파일 권한 확인 (chmod 600)

---

## 정리

OpenClaw은 설치 자체는 간단하지만, 진짜 가치는 설정 이후에 나온다. 텔레그램 하나로 서버 관리, 이미지 생성, 웹 검색, 파일 작업을 할 수 있는 개인 비서가 만들어진다.

로컬 LLM(Ollama)이나 Stable Diffusion과 결합하면 클라우드 의존도를 더 줄일 수도 있다.

---

## 참고

- [OpenClaw 공식 문서](https://docs.openclaw.ai)
- [OpenClaw GitHub](https://github.com/openclaw/openclaw)
- [OpenClaw 커뮤니티 (Discord)](https://discord.com/invite/clawd)
