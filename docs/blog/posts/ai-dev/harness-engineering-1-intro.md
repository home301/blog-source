---
date: 2026-03-28
categories:
  - AI/개발
tags:
  - harness-engineering
  - ai-agent
  - coding-agent
  - openai
  - spec-driven-development
slug: harness-engineering-1-intro
description: "AI 코딩 에이전트가 만든 코드를 신뢰할 수 있으려면, 코드를 만드는 환경 자체를 설계해야 한다. 하네스 엔지니어링의 개념, 필요성, 주요 도구를 소개한다."
---

# Harness Engineering — AI 코딩 에이전트를 제어하는 기술

> AI 코딩 에이전트가 만든 코드를 신뢰할 수 있으려면, 코드를 만드는 환경 자체를 설계해야 한다.

---

## 하네스 엔지니어링이란

2026년 초, OpenAI가 Codex를 활용한 내부 실험 결과를 공개하면서 "Harness Engineering"이라는 표현이 주목받기 시작했다. 100만 줄의 코드를 수동 작성 0줄로 만들었다는 실험이다. 3명으로 시작해 7명으로 늘어난 팀이 5개월간 약 1,500개의 PR을 병합했고, 1인당 하루 평균 3.5개의 PR을 처리했다.

핵심 원칙은 간단하다.

> "Humans steer. Agents execute."

사람은 방향을 잡고, 에이전트가 실행한다. 여기서 "방향을 잡는다"는 것이 단순히 프롬프트를 잘 쓰는 것이 아니다. 에이전트가 작업하는 환경 자체를 설계하는 것이다. 이것이 하네스 엔지니어링이다.

전통적인 test harness가 "인간이 작성한 코드가 맞는지 검증하는 환경"이라면, agent harness engineering은 "AI 에이전트가 올바른 코드를 만들 수 있는 환경 전체를 설계하는 것"이다.

| 구분 | Test Harness | Agent Harness Engineering |
|------|-------------|--------------------------|
| 대상 | 인간이 작성한 코드 검증 | AI agent의 코드 생산 환경 전체 |
| 범위 | 테스트 실행, 리포트 | 스펙 전달 → 코드 생성 → 검증 → 피드백 루프 |
| 핵심 질문 | 코드가 맞는가? | agent가 올바른 코드를 만들 수 있는 환경인가? |
| 설계 대상 | 테스트 프레임워크 | 문서 구조, 제약 시스템, 컨텍스트 관리, 자동화 |

---

## 하네스 엔지니어링이 없으면

AI 코딩 에이전트를 아무 환경에 그냥 풀어놓으면 어떤 일이 벌어지는가.

**1. 아키텍처 부식**

에이전트는 "지금 당장 동작하는 코드"를 만드는 데 최적화되어 있다. 프로젝트 전체의 아키텍처 원칙이나 모듈 경계를 지키는 것은 관심 밖이다. 계층 간 의존성이 꼬이고, 추상화가 무너지고, 코드베이스가 점진적으로 썩는다. 인간 개발자도 같은 실수를 하지만, 에이전트는 훨씬 빠른 속도로 같은 실수를 반복한다.

**2. 컨텍스트 분실**

에이전트가 볼 수 없는 정보는 존재하지 않는 것과 같다. Slack에서 합의한 설계 결정, Google Docs에 적은 요구사항, 팀원의 머릿속에 있는 암묵지 — 이것들은 에이전트의 세계에 없다. 결과적으로 에이전트는 이미 결정된 사항을 무시하고, 이미 해결된 문제를 다시 만들어낸다.

**3. 검증 부재**

에이전트가 "완료했습니다"라고 하면 정말 완료된 건가? 테스트가 통과한다고 해서 요구사항을 충족하는 건 아니다. 스펙과 구현 사이의 정합성을 기계적으로 검증하지 않으면, 겉으로는 동작하지만 실제로는 다른 것을 만드는 상황이 생긴다.

**4. 피드백 루프 부재**

에이전트가 실패했을 때 무엇이 잘못됐는지 자동으로 파악하고 재시도하는 구조가 없으면, 결국 인간이 하나하나 확인하고 다시 지시해야 한다. 이러면 에이전트를 쓰는 의미가 반감된다.

**5. 규모 확장 불가**

위 문제들은 코드베이스가 작을 때는 사람이 감당할 수 있다. 하지만 코드가 수천, 수만 줄을 넘기는 순간 사람의 주의력만으로는 통제할 수 없게 된다. OpenAI가 하네스 엔지니어링을 제안한 것도 바로 이 지점이다.

---

## 하네스 엔지니어링은 이 문제를 어떻게 해결하는가

하네스 엔지니어링의 접근은 "에이전트에게 잘 시키는 것"이 아니라 "에이전트가 잘못하기 어려운 환경을 만드는 것"이다.

### 저장소를 시스템 오브 레코드로

에이전트가 참조할 모든 정보를 저장소 안에 버전 관리한다. 아키텍처 문서, 설계 원칙, 코딩 표준, 실행 계획이 마크다운 파일로 저장소에 존재한다. Slack 스레드도, Google Docs도, 사람의 기억도 아닌 — 저장소가 유일한 진실의 원천이다.

OpenAI는 이를 "AGENTS.md를 백과사전이 아닌 목차로 취급하라"고 표현했다. AGENTS.md는 100줄 내외의 짧은 진입점이고, 실제 지식은 `docs/` 디렉토리에 구조화되어 있다.

### 기계적 강제

인간에게 "이 규칙을 지켜주세요"라고 부탁하듯 에이전트에게도 부탁만 하면 안 된다. 에이전트는 지시를 따를 수도 있고 무시할 수도 있다. 따라서 규칙은 기계적으로 강제한다.

- **아키텍처 경계**: 커스텀 린터가 모듈 간 import 방향을 검사한다. 위반하면 CI가 실패한다.
- **코딩 표준**: pre-commit hook이 네이밍 컨벤션, 파일 크기 제한, 구조화된 로깅을 강제한다.
- **품질 게이트**: 테스트 통과, 커버리지 임계값, 정적 분석 통과가 PR 병합 조건이다.

에이전트가 만든 코드가 이 게이트를 통과하지 못하면 자동으로 거부된다. 여기에 에이전트의 "판단"이 개입할 여지는 없다.

### 피드백 루프

검증 실패 → 에이전트에게 실패 원인 전달 → 에이전트가 수정 → 재검증. 이 루프가 자동으로 돌아야 한다. OpenAI의 경우 에이전트가 자기 변경사항을 자체적으로 리뷰하고, 다른 에이전트에게도 리뷰를 요청하며, 모든 리뷰어가 만족할 때까지 반복하는 루프를 구축했다.

### 점진적 공개

에이전트에게 한꺼번에 모든 정보를 주지 않는다. 작은 진입점(AGENTS.md)에서 시작해서, 필요한 시점에 필요한 문서를 참조하도록 안내한다. 컨텍스트 윈도우는 유한하다. 불필요한 정보로 채우면 정작 중요한 정보를 놓친다.

### 격리된 실행 환경

각 작업을 독립된 환경에서 실행한다. git worktree 단위로 앱을 부팅하고, 임시 관찰 스택(로그, 메트릭)을 붙이고, 작업이 끝나면 환경을 정리한다. 한 에이전트의 작업이 다른 에이전트의 작업에 영향을 주지 않는다.

---

## 어떤 도구들이 있는가

하네스 엔지니어링의 핵심 역할을 수행하는 도구들은 크게 두 부류로 나뉜다.

**대형 도구** — 이미 대규모 커뮤니티를 형성한 스펙 주도 개발 도구들이다. 스펙 관리, 태스크 분해, 제약 주입 등을 다룬다.

| 도구 | Stars | 핵심 |
|------|-------|------|
| [Spec Kit](https://github.com/github/spec-kit) (GitHub) | 83,000+ | Phase gate 방식 스펙 주도 개발. constitution으로 에이전트 행동 제약. |
| [BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) | 42,600+ | 12+ 전문 페르소나로 역할 분리. 구현자와 검증자가 다르다. |
| [OpenSpec](https://github.com/Fission-AI/OpenSpec) (Fission-AI) | 35,000+ | change 단위 격리. brownfield에 강함. "유연하되 엄격하지 않게". |
| [Hive](https://github.com/aden-hive/hive) (Aden) | 9,900+ | 목표 주도 에이전트 프레임워크. 자기 개선 루프 내장. YC 투자. |
| [Kiro](https://github.com/kirodotdev/Kiro) (AWS) | 3,300+ | 스펙 주도 IDE. Steering + Hooks로 피드백 루프 자동화. |

**신흥 도구** — 2026년 초에 등장하기 시작한 하네스 전용 도구들이다. 검증, 측정, 기계적 강제에 특화되어 있다. 아직 초기 단계지만 독특한 접근을 가지고 있어 주시할 가치가 있다.

| 도구 | Stars | 핵심 |
|------|-------|------|
| [Entrix](https://github.com/phodal/entrix) | 31 | 규칙을 실행 가능한 가드레일로 변환. tier별 검증. |
| [AI Harness Scorecard](https://github.com/markmishaev76/ai-harness-scorecard) | 14 | 리포의 하네스 수준을 A~F로 정량 평가. |
| [Reins](https://github.com/WellDunDun/reins) | 6 | scaffold → audit → evolve → doctor. 점진적 하네스 도입 CLI. |

각 도구의 상세 분석과 비교는 [2편](harness-engineering-2-analysis.md)에서 다룬다.

---

## 참고 자료

- [OpenAI — Harness Engineering: Leveraging Codex in an Agent-First World](https://openai.com/index/harness-engineering/)
- [HumanLayer — Skill Issue: Harness Engineering for Coding Agents](https://www.humanlayer.dev/blog/skill-issue-harness-engineering-for-coding-agents)
- [Viv Trivedy — The Anatomy of an Agent Harness](https://blog.langchain.com/the-anatomy-of-an-agent-harness/)
- [전체 도구 수집 목록](https://github.com/botmarch301/workspace-view/blob/main/blog/preview/harness-engineering/survey.md)
