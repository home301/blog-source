---
date: 2026-03-08
categories:
  - 재테크
tags:
  - 주식
  - api
  - 자동매매
  - 데이터수집
  - python
---

# 한국 증권사 Open API 비교 분석 (2026)

> 주식 데이터 수집이나 자동매매 시스템을 만들 때, 어떤 증권사 API를 써야 할까. 국내 주요 증권사 5곳의 Open API를 비교 분석한다.

<!-- more -->

## 비교 대상

이 글에서 다루는 증권사 API는 다음 5개다.

- **KIS Developers** (한국투자증권)
- **LS증권 Open API** (구 이베스트투자증권)
- **키움증권 REST API**
- **대신증권 CYBOS Plus**
- **신한투자증권 API Lab**

## 한눈에 보는 비교표

| 항목 | KIS (한국투자) | LS증권 | 키움증권 | 대신증권 | 신한투자 |
|------|:-:|:-:|:-:|:-:|:-:|
| **API 방식** | REST + WebSocket | REST + WebSocket | REST | COM+ (CYBOS Plus) | REST |
| **OS 지원** | Windows/Linux/Mac | Windows/Linux/Mac | Windows/Linux/Mac | **Windows 전용** | Windows/Linux/Mac |
| **실시간 시세** | WebSocket | WebSocket | 미제공 (REST만) | COM+ 이벤트 | 미제공 |
| **분봉 데이터** | O | O | O | O | 제한적 |
| **투자자별 매매** | O | O | O | O | 제한적 |
| **호가 정보** | O | O | O | O | O |
| **주문/매매** | O | O | O | O | O |
| **모의투자** | O | O | O | O | O |
| **Python 지원** | 공식 샘플 | 공식 샘플 | 공식 문서 | pywin32 필요 | 공식 문서 |
| **GitHub 샘플** | O | O | X | X | X |
| **조건검색** | X | X | O | O | X |
| **해외주식** | O | O | O | X | O |

---

## 1. KIS Developers (한국투자증권)

현재 국내에서 가장 적극적으로 Open API를 밀고 있는 증권사다. REST + WebSocket을 모두 지원하고, 문서화 수준이 높으며, GitHub에 공식 Python 샘플 코드를 제공한다. GPTs 기반 개발 지원 봇까지 운영하고 있다.

### 주요 특징

- **인증**: OAuth2 기반. AppKey + AppSecret으로 접근토큰 발급, 24시간 유효
- **REST API**: 주문, 시세, 잔고, 분봉, 일봉, 투자자별 매매동향
- **WebSocket**: 실시간 체결가, 호가, 체결통보
- **호출 제한**: 초당 20건 (REST), WebSocket 동시 접속 40건
- **분봉 조회**: 1회 요청당 최대 30건 반환

### 장점

- 문서가 잘 정리되어 있고, 테스트베드(API 호출 테스트 페이지)를 제공한다
- OS 제약 없음 — Linux, Mac에서도 완전히 동작한다
- GitHub에 Python REST/WebSocket 샘플 코드가 있어 빠르게 시작할 수 있다
- 해외주식 API도 제공한다

### 단점

- 조건검색 기능이 없다
- 분봉 데이터 1회 요청당 30건 제한이 있어, 전 종목 백필 시 호출 횟수가 많아진다
- 토큰 유효기간이 24시간이라 장기 운영 시 자동 갱신 로직이 필요하다

### 링크

- 개발자 포털: <https://apiportal.koreainvestment.com>
- API 문서: <https://apiportal.koreainvestment.com/apiservice>
- GitHub 샘플: <https://github.com/koreainvestment/open-trading-api>
- 서비스 신청 가이드: <https://apiportal.koreainvestment.com/about-howto>

---

## 2. LS증권 Open API (구 이베스트투자증권)

이베스트투자증권이 LS증권으로 사명을 변경하면서 기존 xingAPI를 Open API로 전환했다. REST + WebSocket 기반이며, 주식/선물/옵션/해외 주식/해외 선물까지 폭넓은 상품을 지원한다.

### 주요 특징

- **인증**: OAuth2 기반
- **REST API**: 업종, 주식, 선물/옵션, 해외선물, 해외주식, 기타
- **WebSocket**: 실시간 시세 지원
- **모의투자 도메인** 별도 제공
- **TR 코드 체계**: 기존 xingAPI의 TR 구조를 REST로 래핑한 형태

### 장점

- 상품 커버리지가 넓다 (국내주식 + 선물/옵션 + 해외선물 + 해외주식)
- REST + WebSocket 모두 지원하여 실시간 데이터 수신이 가능하다
- 기존 xingAPI 사용자라면 TR 코드 체계에 익숙하다

### 단점

- 기존 xingAPI에서 전환되면서 문서가 다소 산만한 편이다
- GitHub 공식 샘플은 있지만 KIS에 비해 예제가 적다
- 법인 계좌 관련 절차가 별도로 필요하다

### 링크

- 개발자 포털: <https://openapi.ls-sec.co.kr>
- API 가이드: <https://openapi.ls-sec.co.kr/apiservice>
- 기존 xingAPI 안내: <https://www.ls-sec.co.kr/xingapi>

---

## 3. 키움증권 REST API

국내 개인투자자 점유율 1위 증권사답게, 키움도 REST API를 제공한다. 가장 큰 차별점은 **조건검색** 기능이다. 영웅문4에서 만든 조건검색식을 API로 호출할 수 있다.

### 주요 특징

- **인증**: IP 기반 접근 제한 + 인증토큰
- **REST API**: 시세, 차트, 주문, 계좌, 투자자별 매매, 순위 정보
- **조건검색**: 영웅문4 조건검색식 연동 가능
- **보안**: 허용 IP에서만 API 요청 가능

### 장점

- **조건검색 연동**은 키움만의 고유 기능이다. 복잡한 종목 스크리닝 로직을 HTS에서 만들고 API로 가져올 수 있다
- 국내 개인투자자 커뮤니티에서 관련 자료가 가장 많다
- REST 기반이라 OS 제약이 없다

### 단점

- **WebSocket/실시간 시세가 없다**. REST 폴링으로만 시세를 가져와야 한다
- GitHub 공식 샘플 코드가 없다
- API 문서가 최근 리뉴얼되면서 일부 구버전 링크가 깨져 있다

### 링크

- 개발자 포털: <https://openapi.kiwoom.com>
- API 서비스: <https://openapi.kiwoom.com/main/home>
- 키움 금융센터: 1544-9000

---

## 4. 대신증권 CYBOS Plus

가장 오래된 증권사 API 중 하나다. Windows COM+(OLE Automation) 기반이라 반드시 **Windows + 32비트 Python** 환경이 필요하다. 역사가 긴 만큼 제공하는 데이터 종류는 풍부하지만, 기술적 제약이 크다.

### 주요 특징

- **인증**: CYBOS Plus(대신증권 HTS) 로그인 필수. 프로그램이 실행 중이어야 API 호출 가능
- **통신 방식**: Windows COM+ 객체 (`win32com.client`)
- **데이터**: 분봉, 일봉, 체결강도, 매수/매도 잔량, 조건검색
- **호출 제한**: 15초당 60건

### 장점

- 데이터 종류가 매우 풍부하다 (체결강도, 누적 매수/매도 등 세부 지표 제공)
- 조건검색을 API에서 사용할 수 있다
- 실시간 이벤트를 COM+ 이벤트 핸들러로 수신할 수 있다

### 단점

- **Windows 전용**, **32비트 Python 전용** — Linux/Mac 사용 불가
- CYBOS Plus HTS가 반드시 실행 중이어야 한다
- COM+ 기반이라 프로그래밍이 번거롭다 (`pywin32` 필수)
- REST API가 없어 현대적 웹 서비스 구조와 호환이 안 된다
- 해외주식을 지원하지 않는다

### 링크

- CYBOS Plus 도움말: <https://money2.daishin.com/e5/mboard/ptype_basic/HTS_Plus_Helper/DW_Basic_List_Page.aspx?boardseq=285>
- CYBOS Plus 다운로드: <https://money2.daishin.com> (로그인 후 CYBOS Plus 메뉴)
- 모의투자: <https://vtsweb.daishin.com>

---

## 5. 신한투자증권 API Lab

신한투자증권도 REST 기반 Open API를 제공한다. 다만 다른 증권사에 비해 API 기능 범위가 제한적이고, 문서화 수준도 낮은 편이다.

### 주요 특징

- **인증**: OAuth2 기반
- **REST API**: 주문, 시세, 계좌
- **모의투자**: 지원

### 장점

- 신한금융 계열 통합 서비스와 연동 가능성이 있다
- REST 기반이라 OS 제약이 없다

### 단점

- 분봉 데이터, 투자자별 매매동향 등 데이터 분석에 필요한 API가 제한적이다
- WebSocket/실시간 시세를 제공하지 않는다
- API 문서와 개발자 커뮤니티가 부족하다
- 외부 접근 시 간헐적으로 500 에러가 발생한다

### 링크

- API Lab: <https://www.shinhansec.com/siw/wealth-management/api-lab/SOSIE0000000.do>

---

## 용도별 추천

### 데이터 수집 (분봉/일봉/수급)

**KIS Developers**를 추천한다. REST + WebSocket을 모두 지원하고 Linux에서 동작하며, 분봉, 투자자별 매매동향, 호가 데이터를 모두 제공한다. 공식 Python 샘플이 있어 시작이 빠르다.

대신증권 CYBOS Plus도 데이터 종류는 풍부하지만, Windows + 32비트 Python이라는 환경 제약이 너무 크다. Windows 서버를 따로 운영할 게 아니라면 추천하지 않는다.

### 자동매매 시스템

**KIS** 또는 **LS증권**을 추천한다. 둘 다 REST로 주문을 넣고 WebSocket으로 체결통보를 실시간으로 받을 수 있다. 해외 선물까지 커버해야 한다면 LS증권이 더 폭넓다.

### 조건검색 기반 트레이딩

**키움증권**이 유일한 선택지다. 영웅문4의 조건검색식을 API로 가져올 수 있는 건 키움뿐이다. 다만 실시간 시세가 없으니, 조건검색 + 키움 주문 / 시세 보조는 다른 API 조합을 고려할 수도 있다.

### Linux 환경에서 운영

대신증권을 제외하면 모두 가능하다. 그 중에서도 **KIS**가 문서화, 샘플 코드, 커뮤니티 지원 면에서 가장 낫다.

---

## 개발자 관점 정리

| 관점 | 추천 | 이유 |
|------|------|------|
| 문서 품질 | KIS | 테스트베드, GPTs 봇, GitHub 샘플 |
| 데이터 풍부성 | 대신증권 | 체결강도, 누적 매수/매도 등 세부 지표 |
| 크로스플랫폼 | KIS, LS, 키움 | REST 기반 |
| 실시간 데이터 | KIS, LS | WebSocket 지원 |
| 조건검색 | 키움, 대신 | HTS 조건검색 API 연동 |
| 시작 난이도 | KIS | 가입 → 토큰 발급 → 바로 호출 |

---

## 마치며

2026년 기준, 새로 시작하는 개인 프로젝트에는 **KIS Developers**가 가장 무난한 선택이다. REST + WebSocket 기반으로 Linux/Mac에서 동작하고, 문서와 샘플이 충실하며, 분봉부터 수급 데이터까지 대부분의 데이터를 커버한다.

다만 각 증권사마다 고유 강점이 있으니 목적에 따라 선택하면 된다. 조건검색이 필수라면 키움, 해외 선물까지 한 API로 해결하고 싶다면 LS증권, 세부 체결 데이터가 필요하고 Windows 환경이라면 대신증권이 답이다.

결국 "계좌를 어디서 만드느냐"보다 "어떤 데이터를, 어떤 환경에서, 얼마나 자주 쓸 것인가"가 API 선택의 핵심이다.
