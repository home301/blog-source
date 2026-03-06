---
date: 2026-03-05
categories:
  - AI/개발
tags:
  - cache
  - backend
  - series
---

# 캐시의 모든 것 4편: 캐시 스탬피드 — 상황과 해법

> Cache Stampede, Penetration, Avalanche — 캐시가 오히려 장애를 일으키는 순간들

---

## 들어가며

캐시는 강력한 성능 도구이지만, **잘못 설계하면 오히려 서버를 죽일 수 있다.**

캐시가 정상 동작할 때 DB 부하의 90%를 흡수하고 있다면, 캐시가 갑자기 사라지면? **DB에 10배의 트래픽이 몰린다.** 단순한 성능 저하가 아니라 **장애**다.

이번 편에서는 캐시 관련 3대 장애 패턴과 각각의 방어법을 다룬다.

---

## 1. Cache Stampede (캐시 스탬피드)

### 문제

**인기 있는 캐시 항목 하나**가 만료되는 순간, 대기 중이던 수백~수천 개의 요청이 **동시에** DB로 몰리는 현상이다.

```
평상시:
  요청 1000개/초 → [Redis Hit] → 응답 (DB 부하 = 0)

캐시 만료 순간:
  요청 1000개/초 → [Redis Miss!] → 1000개 모두 DB 조회
  → DB 과부하 → 응답 지연 → 타임아웃 → 장애 확산
```

"스탬피드(stampede)"는 소 떼가 한꺼번에 달려드는 것을 의미합니다. 정확한 비유다.

### 해법 1: 뮤텍스 락 (Mutex Lock)

캐시 미스 시 **한 요청만** DB를 조회하고, 나머지는 대기한다.

```python
def get_with_lock(key):
    value = redis.get(key)
    if value:
        return json.loads(value)
    
    # 분산 락 획득 시도 (5초 타임아웃)
    lock_key = f"lock:{key}"
    if redis.set(lock_key, 1, nx=True, ex=5):
        try:
            # 락 획득 성공 → DB 조회
            value = db.query(key)
            redis.setex(key, 600, json.dumps(value))
            return value
        finally:
            redis.delete(lock_key)
    else:
        # 락 획득 실패 → 잠시 대기 후 재시도
        time.sleep(0.05)
        return get_with_lock(key)  # 재귀 호출
```

```
요청 1000개 동시 도착:
  요청 1 → 락 획득 → DB 조회 → 캐시 저장 → 락 해제
  요청 2~1000 → 락 실패 → 50ms 대기 → 캐시 Hit!
```

| 장점 | 단점 |
|------|------|
| DB에 1개 요청만 전달 | 대기 시간 발생 |
| 구현 직관적 | 데드락 위험 (타임아웃으로 방지) |

### 해법 2: 확률적 조기 만료 (Probabilistic Early Expiration)

캐시가 만료되기 **전에** 확률적으로 미리 갱신합니다.

```python
import math, random, time

def get_with_early_expiry(key, beta=1.0):
    value, expiry, delta = redis.get_with_meta(key)
    
    # 확률적으로 조기 갱신 여부 결정
    now = time.time()
    remaining = expiry - now
    
    # remaining이 작을수록 (만료가 가까울수록) 갱신 확률 증가
    if remaining - delta * beta * math.log(random.random()) <= 0:
        # 조기 갱신!
        value = db.query(key)
        redis.setex(key, 600, json.dumps(value))
    
    return value
```

**원리**: 만료 시간에 가까워질수록 갱신 확률이 높아져, 여러 서버 중 **하나가 먼저** 갱신합니다. 동시 만료를 회피한다.

이 방법은 "Optimal Probabilistic Cache Stampede Prevention" (Vattani et al., 2015) 논문에서 수학적으로 최적임이 증명되었다.

### 해법 3: 사전 갱신 (Eager Refresh)

캐시 TTL의 일정 비율이 지나면 백그라운드에서 갱신합니다.

```python
def get_with_eager_refresh(key, ttl=600, refresh_ratio=0.8):
    value, remaining_ttl = redis.get_with_ttl(key)
    
    if value and remaining_ttl < ttl * (1 - refresh_ratio):
        # TTL의 80%가 지남 → 백그라운드 갱신
        background_refresh(key)
    
    return value
```

사용자는 항상 **기존 캐시 데이터를 즉시 받고**, 백그라운드에서 조용히 갱신된다.

---

## 2. Cache Penetration (캐시 관통)

### 문제

**존재하지 않는 데이터**를 반복 요청하면, 매번 캐시 미스 → DB 조회가 발생한다. 캐시가 아무런 보호 역할을 하지 못한다.

```
공격자: GET /user/9999999999 (존재하지 않는 사용자)
  → Redis: Miss
  → DB: SELECT * FROM users WHERE id = 9999999999 → 결과 없음
  → 캐시에 저장할 것도 없음
  → 다음 요청에도 또 DB 조회!
```

이것은 의도적인 **공격(DDoS)**에도 악용될 수 있다.

### 해법 1: Null 캐싱

"없다"는 사실도 캐시한다.

```python
def get_user(user_id):
    cached = redis.get(f"user:{user_id}")
    
    if cached == "NULL":
        return None  # 없다는 걸 캐시에서 확인
    if cached:
        return json.loads(cached)
    
    user = db.query(user_id)
    if user is None:
        # "없음"을 짧은 TTL로 캐시 (1분)
        redis.setex(f"user:{user_id}", 60, "NULL")
        return None
    
    redis.setex(f"user:{user_id}", 600, json.dumps(user))
    return user
```

| 장점 | 단점 |
|------|------|
| 구현 간단 | 메모리 낭비 (무의미한 키가 많을 수 있음) |
| 즉시 효과 | 짧은 TTL 필요 (나중에 생성되는 경우 대비) |

### 해법 2: Bloom Filter

**존재 가능한 키의 집합**을 확률적으로 판별한다.

```python
from pybloom_live import BloomFilter

# 시작 시 DB의 모든 유효 키를 Bloom Filter에 등록
bf = BloomFilter(capacity=10000000, error_rate=0.001)
for key in db.get_all_keys():
    bf.add(key)

def get_user(user_id):
    # Bloom Filter로 사전 체크
    if user_id not in bf:
        return None  # 확실히 없음 → DB 조회 자체를 안 함
    
    # 있을 수도 있음 → 정상 캐시 로직
    cached = redis.get(f"user:{user_id}")
    if cached:
        return json.loads(cached)
    return db.query(user_id)
```

**Bloom Filter 특성**:
- "없다" → **100% 확실** (False Negative 없음)
- "있다" → **거의 확실하지만 가끔 오탐** (False Positive 가능, 0.1% 수준)
- 메모리 효율: 1억 개 키를 ~120MB로 관리 가능

### 해법 3: 요청 검증

애초에 유효하지 않은 요청을 **입구에서 차단**한다.

```python
def get_user(user_id):
    # ID 형식 검증
    if not isinstance(user_id, int) or user_id < 1 or user_id > 100000000:
        return None  # 범위 밖 → 즉시 거부
    
    # 정상 캐시 로직 ...
```

---

## 3. Cache Avalanche (캐시 눈사태)

### 문제

**많은 캐시 항목이 동시에 만료**되어 DB에 부하가 집중된다. 스탬피드가 "하나의 인기 키"라면, 눈사태는 "수천 개의 키가 동시에"다.

```
서버 시작 시 모든 캐시를 TTL=3600으로 설정
→ 정확히 1시간 후, 수만 개의 캐시가 동시 만료
→ DB에 수만 개 쿼리가 한꺼번에 → 장애
```

### 해법 1: TTL 지터 (Jitter)

TTL에 랜덤 값을 추가하여 만료 시점을 분산한다.

```python
import random

base_ttl = 3600  # 1시간
jitter = random.randint(0, 600)  # 0~10분 랜덤
redis.setex(key, base_ttl + jitter, value)
```

```
기존: 모든 키가 정확히 13:00:00에 만료
지터: 키마다 12:50~13:10 사이에 만료 → 부하 분산
```

**가장 간단하고 효과적인 방법**이다.

### 해법 2: 다단계 캐시

캐시를 여러 계층으로 두어, 하나가 무너져도 다른 계층이 버틴다.

```python
def get_user(user_id):
    # L1: 로컬 캐시 (프로세스 메모리, 매우 빠름)
    value = local_cache.get(user_id)
    if value:
        return value
    
    # L2: Redis (네트워크 캐시)
    value = redis.get(f"user:{user_id}")
    if value:
        local_cache.set(user_id, value, ttl=60)  # L1에도 저장
        return json.loads(value)
    
    # L3: DB
    value = db.query(user_id)
    redis.setex(f"user:{user_id}", 600, json.dumps(value))
    local_cache.set(user_id, value, ttl=60)
    return value
```

### 해법 3: 캐시 예열 (Cache Warming)

서버 시작/배포 시 **미리 인기 데이터를 캐시에 로드**한다.

```python
def warm_cache():
    """서버 시작 시 호출"""
    popular_keys = db.query("SELECT id FROM users ORDER BY access_count DESC LIMIT 10000")
    for key in popular_keys:
        value = db.query(key)
        redis.setex(f"user:{key}", 3600 + random.randint(0, 600), json.dumps(value))
    print(f"캐시 예열 완료: {len(popular_keys)}개")
```

---

## 4. 종합 방어 전략

실전에서는 이 문제들이 **동시에** 발생할 수 있다. 종합적인 방어가 필요하다.

```python
class RobustCache:
    def __init__(self, redis_client, db_client):
        self.redis = redis_client
        self.db = db_client
        self.bloom = BloomFilter(capacity=10000000, error_rate=0.001)
        self.local_cache = LRUCache(maxsize=1000)
    
    def get(self, key, query_fn, base_ttl=600):
        # 1. 관통 방지: Bloom Filter
        if key not in self.bloom:
            return None
        
        # 2. 눈사태 방지: 로컬 캐시 (L1)
        value = self.local_cache.get(key)
        if value:
            return value
        
        # 3. Redis 조회 (L2)
        value = self.redis.get(key)
        if value:
            if value == b"NULL":
                return None
            parsed = json.loads(value)
            self.local_cache.set(key, parsed, ttl=30)
            return parsed
        
        # 4. 스탬피드 방지: 뮤텍스 락
        lock_key = f"lock:{key}"
        if self.redis.set(lock_key, 1, nx=True, ex=5):
            try:
                result = query_fn(key)
                if result is None:
                    self.redis.setex(key, 60, "NULL")
                else:
                    # 눈사태 방지: TTL 지터
                    jitter = random.randint(0, int(base_ttl * 0.1))
                    self.redis.setex(key, base_ttl + jitter, json.dumps(result))
                    self.local_cache.set(key, result, ttl=30)
                return result
            finally:
                self.redis.delete(lock_key)
        else:
            time.sleep(0.05)
            return self.get(key, query_fn, base_ttl)
```

---

## 정리

| 문제 | 원인 | 핵심 해법 |
|------|------|----------|
| **Stampede** | 인기 키 1개 만료 | 뮤텍스 락, 확률적 조기 만료 |
| **Penetration** | 존재하지 않는 키 | Bloom Filter, Null 캐싱 |
| **Avalanche** | 대량 동시 만료 | TTL 지터, 다단계 캐시 |

**실전 체크리스트:**

- [ ] TTL에 지터를 추가했는가?
- [ ] 인기 키에 대한 스탬피드 방어가 있는가?
- [ ] 존재하지 않는 키에 대한 방어가 있는가?
- [ ] 서버 시작 시 캐시 예열을 하는가?
- [ ] 캐시 장애 시 DB가 버틸 수 있는가? (Graceful Degradation)

---

## 시리즈 총정리

| 편 | 주제 | 핵심 |
|----|------|------|
| **1편** | 캐시란 무엇이고 왜 쓰는가 | 지역성 원리, 히트율, AMAT, Memory Wall |
| **2편** | CPU부터 CDN까지 | 7개 계층의 캐시, 매핑 방식, Write 정책 |
| **3편** | 캐시 교체 정책 | LRU/LFU/ARC/W-TinyLFU, 캐시 친화 코드 |
| **4편** | 캐시 스탬피드와 해법 | Stampede/Penetration/Avalanche 방어 |

캐시는 "자주 쓰는 것을 가까이 두자"라는 단순한 아이디어에서 시작하지만, 제대로 다루려면 하드웨어부터 분산 시스템까지 폭넓은 이해가 필요하다.

---

## 참고문헌

1. Vattani, A., Chierichetti, F. & Lowenstein, K. (2015). "Optimal Probabilistic Cache Stampede Prevention." *PVLDB*, 8(8).
2. Nishtala, R. et al. (2013). "Scaling Memcache at Facebook." *NSDI '13*.
3. Redis Documentation. "Key eviction." https://redis.io/docs/reference/eviction/
4. Bloom, B. H. (1970). "Space/time trade-offs in hash coding with allowable errors." *Communications of the ACM*, 13(7).

---


