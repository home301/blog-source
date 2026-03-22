---
date: 2026-03-05
categories:
  - AI/개발
tags:
  - cache
  - backend
  - series
slug: cache-part2
description: "하드웨어부터 소프트웨어까지, 캐시가 동작하는 모든 계층을 정리한다."
---

# 캐시의 모든 것 2편: CPU부터 CDN까지 — 캐시가 쓰이는 모든 곳

> 하드웨어부터 소프트웨어까지, 캐시가 동작하는 모든 계층을 정리한다.

<!-- more -->

---

## 들어가며

[1편](./cache-part1.md)에서 캐시의 기본 원리를 다뤘다. 이번 편에서는 **캐시가 실제로 어디에서, 어떻게 쓰이는지** 계층별로 살펴본다.

컴퓨터 시스템에서 캐시는 하나가 아니다. **여러 계층에 걸쳐** 캐시가 중첩되어 있고, 각각이 협력하여 전체 시스템의 성능을 끌어올린다.

```
사용자의 요청이 거치는 캐시 계층:

[CPU 레지스터] → [L1] → [L2] → [L3] → [DRAM] → [OS 페이지 캐시]
→ [브라우저 캐시] → [CDN 엣지] → [리버스 프록시] → [Redis] → [DB 쿼리 캐시] → [디스크]
```

---

## 1. 하드웨어 캐시 — CPU 내부

### CPU 캐시 (L1 / L2 / L3)

현대 CPU의 핵심이다. CPU 다이(die) 위에 물리적으로 탑재되어 있다.

#### L1 캐시 — 가장 빠르고, 가장 작다

- **용량**: 32~64KB (코어당)
- **속도**: 1~4 클럭 사이클 (~1ns)
- **특징**: 명령어 캐시(I-cache)와 데이터 캐시(D-cache)로 분리 (Split Cache)
- CPU가 가장 먼저 확인하는 캐시

#### L2 캐시 — 중간 계층

- **용량**: 256KB~1MB (코어당)
- **속도**: 3~10ns
- **특징**: 보통 코어별로 독립. L1 미스 시 확인

#### L3 캐시 — 공유 캐시

- **용량**: 4~64MB (전체 코어 공유)
- **속도**: 10~30ns
- **특징**: 모든 코어가 공유. 멀티코어 간 데이터 공유 역할

#### 실제 CPU의 캐시 구성

| CPU | L1 (코어당) | L2 (코어당) | L3 (공유) |
|-----|-----------|-----------|----------|
| Intel i9-13900K | 12-way, 80KB | 16-way, 2MB | 12-way, 36MB |
| AMD Ryzen 9 7950X | 8-way, 80KB | 8-way, 1MB | 16-way, 64MB |
| Apple M2 | 8-way, 192KB | 16-way, 16MB | 16-way, 24MB |

AMD의 **3D V-Cache** 기술은 L3 캐시를 수직으로 쌓아 96MB~128MB까지 확장한다. 게임 성능이 10~15% 향상되는 것으로 알려져 있는데, 캐시의 위력을 보여주는 좋은 사례다.

### 캐시 매핑 방식

CPU 캐시는 메모리의 데이터를 어디에 저장할지 결정하는 **매핑 방식**이 필요하다.

#### 직접 사상 (Direct Mapped)

각 메모리 블록이 캐시의 **딱 한 곳**에만 저장된다.

```
메모리 블록 0 → 캐시 라인 0
메모리 블록 4 → 캐시 라인 0  ← 충돌!
```

빠르지만 **충돌 미스**가 잦다.

#### 완전 연관 사상 (Fully Associative)

어디든 저장 가능. 충돌 없지만, 모든 라인을 동시에 비교해야 해서 **비용이 높다**. TLB 같은 소형 캐시에서만 사용한다.

#### 집합 연관 사상 (Set Associative)

현대 CPU의 표준이다. 캐시를 세트로 나누고, 각 세트 내에서 N개 라인 중 선택한다.

```
8-way Set Associative:
세트 0: [라인0][라인1][라인2]...[라인7]  ← 8곳 중 택 1
세트 1: [라인0][라인1][라인2]...[라인7]
...
```

**직접 사상의 속도**와 **완전 연관의 유연성**을 절충한 방식이다.

### 캐시 라인과 주소 분해

캐시는 **64바이트 블록**(캐시 라인) 단위로 데이터를 가져온다.

```
메모리 주소 → [Tag | Index | Offset]
              식별자  위치   라인 내 바이트
```

- **Tag**: 어떤 메모리 블록인지 식별
- **Index**: 캐시의 어느 세트인지
- **Offset**: 64바이트 라인 내 위치

### Write 정책

- **Write-through**: 캐시와 메모리에 동시에 쓰기 (안전하지만 느림)
- **Write-back**: 캐시에만 쓰고, 교체 시 메모리 반영 (빠르지만 복잡)

현대 CPU는 대부분 **Write-back**을 사용한다.

---

## 2. 하드웨어 캐시 — 기타

### 디스크 캐시 (HDD/SSD)

HDD와 SSD 내부에도 **DRAM 버퍼**(캐시)가 있다.

- HDD: 64~256MB DRAM 캐시. 자주 읽는 섹터를 버퍼에 보관
- SSD: DRAM 캐시 + SLC 캐시. FTL(Flash Translation Layer)의 매핑 테이블을 캐싱

SSD의 "SLC 캐시"는 MLC/TLC 셀의 일부를 SLC 모드로 운영하여 **쓰기 속도를 일시적으로 높이는** 기법이다. 대량 파일을 복사할 때 처음엔 빠르다가 갑자기 느려지는 경험이 있다면, SLC 캐시가 소진된 것이다.

### GPU 캐시

GPU에도 L1/L2 캐시가 있다:
- **텍스처 캐시**: 텍스처 데이터 접근 최적화
- **셰이더 캐시**: 셰이더 프로그램 캐싱
- **공유 메모리**: 프로그래머가 직접 제어하는 소프트웨어 관리 캐시

### TLB (Translation Lookaside Buffer)

가상 주소 → 물리 주소 변환 결과를 캐시한다.

```
가상 주소 0x1234 → 물리 주소 0xABCD  (TLB에 캐시)
다음 접근 시 페이지 테이블 조회 없이 즉시 변환
```

TLB 미스는 페이지 테이블 워크(page table walk)를 유발하여 수십~수백 사이클이 소요된다. 보통 **완전 연관 사상**으로 구현된다.

---

## 3. OS 캐시

### 페이지 캐시 (Page Cache)

OS가 파일 시스템의 데이터를 **메인 메모리에 캐시**한다.

```bash
# Linux에서 페이지 캐시 확인
$ free -h
              total        used        free      shared  buff/cache   available
Mem:           15Gi       5.2Gi       1.1Gi       312Mi       9.2Gi       9.5Gi
```

`buff/cache`가 9.2GB — OS가 빈 메모리를 파일 캐시로 활용하고 있는 것이다.

파일을 처음 읽으면 디스크에서 가져오지만, 두 번째 읽기부터는 **메모리에서 즉시** 반환된다. `cat`으로 큰 파일을 두 번 읽어보면 두 번째가 훨씬 빠른 것을 체감할 수 있다.

### dentry/inode 캐시

파일 경로 → inode 매핑을 캐시한다. `/home/user/documents/file.txt` 같은 경로를 해석할 때 매번 디스크를 읽지 않아도 된다.

---

## 4. 웹 브라우저 캐시

### HTTP 캐시

브라우저가 서버 응답을 로컬에 저장하여, 같은 리소스를 다시 요청할 때 네트워크 왕복 없이 반환한다.

핵심 HTTP 헤더:

| 헤더 | 역할 | 예시 |
|------|------|------|
| `Cache-Control` | 캐시 정책 결정 | `max-age=3600, public` |
| `ETag` | 리소스의 "지문" | `"abc123"` |
| `Last-Modified` | 마지막 수정 시간 | `Thu, 01 Mar 2026 10:00:00 GMT` |

#### Cache-Control 주요 디렉티브

```
# 정적 에셋 — 1년 캐시, 절대 안 변함
Cache-Control: public, max-age=31536000, immutable

# HTML — 매번 서버에 확인
Cache-Control: no-cache

# 개인 데이터 — 캐시하지 않음
Cache-Control: no-store
```

#### 조건부 요청 (304 Not Modified)

```
첫 요청:
  GET /image.png → 200 OK + ETag: "abc123"

재요청:
  GET /image.png + If-None-Match: "abc123"
  → 변경 없으면: 304 Not Modified (본문 없음, 대역폭 절약)
  → 변경 있으면: 200 OK + 새 데이터
```

### Service Worker 캐시

프로그래밍 가능한 캐시 계층이다. 오프라인 지원, 커스텀 캐시 전략 구현에 사용된다.

---

## 5. CDN (Content Delivery Network)

전 세계에 분산된 서버 네트워크에 콘텐츠 사본을 배치하여, 사용자와 **물리적으로 가까운 서버**에서 응답한다.

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#f0f0f0', 'primaryBorderColor': '#ccc', 'primaryTextColor': '#333', 'lineColor': '#ccc'}}}%%
graph LR
    Origin["원본 서버 (미국)"] --> Seoul["CDN 엣지 (서울)"]
    Origin --> Tokyo["CDN 엣지 (도쿄)"]
    Origin --> Frankfurt["CDN 엣지 (프랑크푸르트)"]
    Seoul --> KR["한국 사용자"]
    Tokyo --> JP["일본 사용자"]
    Frankfurt --> EU["유럽 사용자"]
```

### 동작 흐름

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#f0f0f0', 'primaryBorderColor': '#ccc', 'primaryTextColor': '#333', 'lineColor': '#ccc'}}}%%
graph TD
    A["사용자"] --> B["CDN 엣지"]
    B -->|Hit| C["즉시 응답 (원본 접촉 없음)"]
    B -->|Miss| D["원본에서 가져옴"] --> E["CDN에 저장"] --> F["응답"]
```

### 캐시 무효화

> 컴퓨터 과학에서 어려운 것 두 가지: 캐시 무효화와 이름 짓기. — Phil Karlton

| 방법 | 설명 | 추천도 |
|------|------|--------|
| **파일명 해싱** | `style.css` → `style.a3b2c1.css` | 가장 추천 |
| **Purge API** | CDN에 삭제 요청 | 보통 |
| **TTL 만료** | 시간이 지나면 자동 갱신 | 보통 이하 |

### 주요 CDN 서비스

| 서비스 | 특징 | 무료 플랜 |
|--------|------|----------|
| **Cloudflare** | 가장 널리 사용, DDoS 방어 | O 관대함 |
| **AWS CloudFront** | AWS 통합, 세밀한 제어 | 1TB/월 (12개월) |
| **Vercel Edge** | Next.js 최적화 | O 취미용 |
| **Fastly** | 실시간 퍼지, VCL 커스텀 | 제한적 |

---

## 6. 애플리케이션 로컬 캐시

Redis 같은 원격 캐시에 접근하려면 네트워크 왕복이 필요하다. 부하가 높은 서비스에서는 이 왕복 비용도 부담이 된다. 그래서 **애플리케이션 프로세스 메모리에 직접 캐시를 두는** 방식을 사용한다.

- **Java**: Caffeine, Guava Cache, EhCache
- **Go**: Ristretto, BigCache
- **Python**: `functools.lru_cache`, cachetools

```python
from cachetools import TTLCache

# 최대 1000개 항목, TTL 60초
local_cache = TTLCache(maxsize=1000, ttl=60)

def get_user(user_id):
    if user_id in local_cache:
        return local_cache[user_id]  # 네트워크 왕복 없음
    
    # 로컬 캐시 미스 → Redis 조회 → DB 조회 순으로 이어짐
    value = redis.get(f"user:{user_id}")
    if value:
        local_cache[user_id] = json.loads(value)
        return local_cache[user_id]
    ...
```

장점은 속도(마이크로초 단위)와 네트워크 장애에 대한 내성이다. 단점은 프로세스마다 캐시가 따로라 **일관성 관리가 어렵다**는 것이다. 보통 짧은 TTL(수십 초)을 두고 약간의 불일치를 허용하는 방식으로 운영한다.

---

## 7. 서버 캐시 — Redis와 Memcached

서버 측에서 **DB 부하를 줄이기 위해** 사용하는 인메모리 캐시다.

### Cache-Aside 패턴 (가장 일반적)

```python
def get_user(user_id):
    # 1. 캐시에서 먼저 찾기
    cached = redis.get(f"user:{user_id}")
    if cached:
        return json.loads(cached)  # Hit! (~1ms)
    
    # 2. 캐시 미스 → DB 조회
    user = db.query("SELECT * FROM users WHERE id = ?", user_id)
    
    # 3. 결과를 캐시에 저장 (TTL 10분)
    redis.setex(f"user:{user_id}", 600, json.dumps(user))
    return user
```

### Write-Through vs Write-Behind

| 패턴 | 동작 | 장점 | 단점 |
|------|------|------|------|
| **Write-Through** | 캐시 + DB 동시 쓰기 | 일관성 높음 | 쓰기 느림 |
| **Write-Behind** | 캐시만 쓰고 나중에 DB | 쓰기 빠름 | 데이터 유실 위험 |

### Redis vs Memcached

| | Redis | Memcached |
|--|-------|-----------|
| **데이터 구조** | String, Hash, List, Set... | String만 |
| **영속성** | RDB/AOF 지원 | 없음 |
| **교체 정책** | LRU, LFU 등 6가지 | LRU |
| **추천** | **범용** | 단순 캐시만 필요할 때 |

---

## 8. DB 캐시

### 쿼리 캐시

동일한 쿼리 결과를 메모리에 캐시한다.

```sql
SELECT * FROM products WHERE category = 'electronics';
-- 첫 실행: 디스크 스캔 → 결과 캐시
-- 두 번째: 캐시에서 즉시 반환
```

MySQL 8.0부터는 쿼리 캐시가 **제거**되었다. 쿼리 캐시 락(lock)으로 인한 동시성 처리 병목 현상이 오히려 성능을 저하시키는 핵심 원인이었기 때문이다. 대신 애플리케이션 레벨에서 Redis 등 외부 캐시를 사용하는 것이 권장된다.

### Buffer Pool

InnoDB의 Buffer Pool은 테이블과 인덱스 데이터를 메모리에 캐시한다. 자주 접근하는 데이터를 디스크에서 읽지 않아도 되게 한다.

---

## 9. 전체 캐시 계층 요약

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#f0f0f0', 'primaryBorderColor': '#ccc', 'primaryTextColor': '#333', 'lineColor': '#ccc'}}}%%
graph TD
    A["사용자 클릭"] --> B{"브라우저 캐시 Hit?"}
    B -->|Yes| B1["즉시 표시"]
    B -->|No| C{"CDN 엣지 Hit?"}
    C -->|Yes| C1["가까운 서버에서 응답"]
    C -->|No| D{"리버스 프록시 Hit?"}
    D -->|Yes| D1["원본 서버 부담 감소"]
    D -->|No| E{"앱 로컬 캐시 Hit?"}
    E -->|Yes| E1["네트워크 왕복 없이 응답"]
    E -->|No| F{"Redis/Memcached Hit?"}
    F -->|Yes| F1["DB 조회 생략"]
    F -->|No| H{"DB Buffer Pool Hit?"}
    H -->|Yes| H1["디스크 I/O 생략"]
    H -->|No| I["디스크 — 최종 원본 데이터"]
```

**각 계층에서 캐시 히트가 발생할수록** 아래 계층의 부담이 줄어든다. 잘 설계된 시스템에서는 요청의 90% 이상이 브라우저나 CDN 레벨에서 처리된다.

---

## 정리

| 계층 | 캐시 | 속도 | 관리 주체 |
|------|------|------|----------|
| **CPU** | L1/L2/L3 | 1~30ns | 하드웨어 |
| **디스크** | DRAM 버퍼, SLC 캐시 | ~μs | 펌웨어 |
| **OS** | 페이지 캐시, TLB | ~μs | 커널 |
| **브라우저** | HTTP 캐시 | ~ms | HTTP 헤더 |
| **CDN** | 엣지 캐시 | ~10ms | 설정/API |
| **앱 로컬** | 프로세스 내 캐시 (Caffeine, Guava 등) | ~μs | 개발자 |
| **서버** | Redis/Memcached | ~1ms | 개발자 |
| **DB** | Buffer Pool | ~μs | DB 설정 |

---

## 다음 편 예고

**3편: 캐시 교체 정책 완벽 정리**에서는 LRU, LFU, FIFO 등 기본 정책 비교부터 ARC, W-TinyLFU 같은 현대적 하이브리드 정책, 그리고 캐시 친화적 코드 작성법을 다룬다.

---

## 참고문헌

1. Hennessy, J. L. & Patterson, D. A. (2017). *Computer Architecture: A Quantitative Approach*, 6th Edition.
2. Bryant, R. E. & O'Hallaron, D. R. (2015). *Computer Systems: A Programmer's Perspective*, 3rd Edition.
3. MDN Web Docs. "HTTP caching." https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching
4. Cloudflare. "What is a CDN?" https://www.cloudflare.com/learning/cdn/what-is-a-cdn/
5. Redis Documentation. https://redis.io/docs/
