---
date: 2026-03-28
categories:
  - AI/개발
tags:
  - github-pages
  - blog
  - mkdocs
  - mkdocs-material
  - python
slug: free-blog-2-mkdocs-material-setup
description: "MkDocs Material을 설치하고 프로젝트 구조를 잡은 뒤, 첫 글을 작성해 GitHub Pages에 배포한다."
---

# MkDocs Material 설치부터 첫 글 배포까지

> Python 환경 준비에서 GitHub Pages 배포까지, 실제로 따라 하면서 블로그를 만든다.

<!-- more -->

---

이 글은 **무료로 나만의 블로그 만들기** 시리즈의 두 번째 편이다.

| 편 | 제목 |
|---|------|
| 1 | [블로그 플랫폼 비교 — 그래도 GitHub Pages를 선택한 이유](free-blog-1-why-github-pages.md) |
| **2** | **MkDocs Material 설치부터 첫 글 배포까지** |
| 3 | GitHub Actions로 자동 빌드/배포 파이프라인 구축하기 |
| 4 | 커스텀 도메인 연결하기 — Cloudflare + GitHub Pages |
| 5 | SEO와 분석 도구 연동 — 검색에 노출되는 블로그 |
| 6 | 상용화 준비 — 저작권, 개인정보처리방침, AdSense |

---

## 시작하기 전에

이 글은 Linux 환경을 기준으로 작성됐다. 설치, 빌드, 배포를 전부 로컬 터미널에서 직접 수행한다.

"이걸 글 쓸 때마다 해야 하나?" 싶을 수 있다. 결론부터 말하면, **아니다**. 이번 편에서 하는 작업 대부분은 최초 1회 설정이다. 그리고 3편에서 GitHub Actions를 설정하면, 이후로는 글을 쓰고 `git push`만 하면 빌드와 배포가 자동으로 처리된다.

이번 편은 그 자동화의 토대를 만드는 과정이다. MkDocs Material이 어떻게 동작하는지, 프로젝트 구조가 어떻게 생겼는지를 직접 눈으로 확인하는 단계라고 생각하면 된다.


## 이 편에서 할 것

1. Python 환경 준비
2. MkDocs Material 설치
3. 프로젝트 생성 및 구조 잡기
4. 블로그 플러그인 설정
5. 첫 글 작성
6. 로컬 미리보기
7. GitHub에 올리고 배포


## 사전 준비

필요한 것:

- **Python 3.9 이상**
- **Git**
- **GitHub 계정**

터미널에서 확인한다.

```bash
python3 --version
# Python 3.12.x 이상이면 OK

git --version
# git version 2.x.x 이면 OK
```

Python이 없으면 배포판의 패키지 매니저로 설치한다.

```bash
# Ubuntu / Pop!_OS
sudo apt install python3 python3-venv python3-pip

# Fedora
sudo dnf install python3 python3-pip
```


## 1단계: 프로젝트 디렉토리 만들기

블로그 프로젝트를 위한 폴더를 만든다.

```bash
mkdir my-blog
cd my-blog
```

### 가상환경 생성

Python 패키지를 시스템 전역에 설치하면 나중에 버전 충돌이 생길 수 있다. 가상환경을 만들어서 프로젝트별로 격리한다.

```bash
python3 -m venv venv
source venv/bin/activate
```

프롬프트 앞에 `(venv)`가 붙으면 성공이다.

```
(venv) ~/my-blog $
```

!!! tip "가상환경이란"
    프로젝트마다 독립된 Python 환경을 만드는 기능이다. MkDocs Material은 의존성 패키지가 꽤 많아서, 시스템 Python에 직접 설치하면 다른 프로젝트와 충돌할 수 있다. 블로그 작업을 할 때마다 `source venv/bin/activate`를 실행하면 된다.


## 2단계: MkDocs Material 설치

가상환경이 활성화된 상태에서 설치한다.

```bash
pip install mkdocs-material
```

이 한 줄로 mkdocs, material 테마, 필요한 의존성이 전부 설치된다.

설치 확인:

```bash
mkdocs --version
# mkdocs, version 1.6.x
```


## 3단계: 프로젝트 초기화

MkDocs 프로젝트를 생성한다.

```bash
mkdocs new .
```

현재 디렉토리에 기본 구조가 만들어진다.

```
my-blog/
  ├── docs/
  │   └── index.md
  ├── mkdocs.yml
  └── venv/
```

- `docs/` — 마크다운 파일을 넣는 곳
- `mkdocs.yml` — 사이트 설정 파일
- `venv/` — 가상환경. Git에는 올리지 않는다.


## 4단계: mkdocs.yml 설정

`mkdocs.yml`을 열고 아래 내용으로 교체한다. 이 설정이 블로그의 뼈대다.

```yaml
site_name: My Blog
site_url: https://username.github.io/
site_description: 나의 기술 블로그

theme:
  name: material
  language: ko
  palette:
    - media: "(prefers-color-scheme: light)"
      scheme: default
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-7
        name: 다크 모드로 전환
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-4
        name: 라이트 모드로 전환
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.top
    - search.suggest
    - search.highlight
    - content.code.copy
  font:
    text: Noto Sans KR
    code: JetBrains Mono

plugins:
  - search:
      lang:
        - ko
        - en
  - blog:
      blog_dir: blog
      post_date_format: yyyy년 M월 d일
      post_url_format: "{slug}"
      categories: true

markdown_extensions:
  - toc:
      permalink: "#"
  - admonition
  - pymdownx.details
  - pymdownx.superfences
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.inlinehilite
  - pymdownx.tabbed:
      alternate_style: true
  - attr_list
  - tables

nav:
  - Home: index.md
  - Blog:
      - blog/index.md
```

`username`을 자신의 GitHub 사용자명으로 바꾼다. `site_name`도 원하는 이름으로 변경한다.

### 주요 설정 설명

**theme.palette** — 라이트/다크 모드 전환을 제공한다. `primary`와 `accent`는 테마 색상이다. [Material 색상 팔레트](https://squidfunk.github.io/mkdocs-material/setup/changing-the-colors/)에서 고를 수 있다.

**plugins.blog** — MkDocs Material의 블로그 플러그인이다. `blog_dir: blog`로 설정하면 `docs/blog/posts/` 안의 마크다운 파일을 날짜순으로 정렬해서 보여준다.

**markdown_extensions** — 마크다운 확장 기능이다.

- `admonition` — `!!! tip`, `!!! warning` 같은 알림 박스
- `superfences` — 코드 블록 안에서 언어별 하이라이팅
- `tabbed` — 탭 UI
- `content.code.copy` — 코드 블록에 복사 버튼 자동 추가

전부 기술 블로그에서 자주 쓰는 기능이다. 지금 전부 이해할 필요는 없고, 글을 쓰다가 필요할 때 [공식 문서](https://squidfunk.github.io/mkdocs-material/reference/)를 참고하면 된다.


## 5단계: 블로그 디렉토리 구조 만들기

블로그 플러그인이 인식할 디렉토리를 만든다.

```bash
mkdir -p docs/blog/posts
```

블로그 인덱스 페이지:

```bash
cat > docs/blog/index.md << 'EOF'
---
hide:
  - navigation
---

# Blog
EOF
```

홈페이지 수정:

```bash
cat > docs/index.md << 'EOF'
# Welcome

나의 기술 블로그.

최신 글은 [Blog](blog/) 페이지에서 확인할 수 있다.
EOF
```

현재 구조:

```
my-blog/
  ├── docs/
  │   ├── blog/
  │   │   ├── index.md
  │   │   └── posts/        ← 여기에 글을 넣는다
  │   └── index.md
  ├── mkdocs.yml
  └── venv/
```


## 6단계: 첫 글 작성

`docs/blog/posts/` 디렉토리에 마크다운 파일을 만든다.

```bash
cat > docs/blog/posts/hello-world.md << 'EOF'
---
date: 2026-03-25
categories:
  - 일반
slug: hello-world
description: "첫 번째 블로그 글."
---

# 첫 번째 글

블로그를 시작한다.

<!-- more -->

## 본문

MkDocs Material로 만든 블로그의 첫 글이다.

코드 블록:

```python
print("Hello, Blog!")
```

!!! tip "팁 박스"
    admonition 확장으로 이런 알림 박스를 만들 수 있다.
EOF
```

### front matter

파일 맨 위의 `---`로 감싼 영역이 front matter다.

```yaml
---
date: 2026-03-25        # 필수. 이 날짜 기준으로 정렬된다.
categories:              # 선택. 카테고리 분류.
  - 일반
slug: hello-world        # 선택. URL 경로. 없으면 파일명이 쓰인다.
description: "설명"      # 선택. 검색 결과와 미리보기에 표시된다.
---
```

`date`는 필수다. 이 값이 없으면 블로그 목록에 글이 표시되지 않는다.

### `<!-- more -->` 태그

이 태그 위의 내용이 블로그 목록에서 미리보기로 표시된다. 없으면 글 전체가 목록에 노출된다.


## 7단계: 로컬 미리보기

```bash
mkdocs serve
```

```
INFO    -  Building documentation...
INFO    -  [xx:xx:xx] Serving on http://127.0.0.1:8000/
```

브라우저에서 `http://127.0.0.1:8000`을 열면 블로그가 보인다.

`mkdocs serve`는 파일 변경을 감시한다. 마크다운을 수정하고 저장하면 브라우저가 자동으로 갱신된다. 글을 쓰면서 실시간으로 결과를 확인할 수 있다.

`Ctrl+C`로 서버를 종료한다.

!!! warning "`mkdocs.yml`을 크게 수정했을 때"
    설정 파일을 수정하면 서버가 에러를 내며 멈출 수 있다. 서버를 종료하고 다시 `mkdocs serve`를 실행하면 된다.


## 8단계: Git 초기화

```bash
git init
```

`.gitignore`:

```bash
cat > .gitignore << 'EOF'
venv/
site/
__pycache__/
.cache/
EOF
```

첫 커밋:

```bash
git add .
git commit -m "Initial blog setup with MkDocs Material"
```


## 9단계: GitHub 저장소 생성 및 푸시

### 저장소 만들기

GitHub에서 새 저장소를 만든다.

- **저장소 이름**: `username.github.io` (자신의 GitHub 사용자명)
- **공개**(Public)로 설정
- README, .gitignore 등은 추가하지 않는다 (이미 로컬에 있으므로)

!!! note "저장소 이름 규칙"
    `username.github.io` 형태로 만들어야 GitHub Pages의 User 사이트로 인식된다. 다른 이름으로 만들면 `username.github.io/repo-name/` 경로가 되어 URL이 깔끔하지 않다.

### 푸시

```bash
git remote add origin https://github.com/username/username.github.io.git
git branch -M main
git push -u origin main
```


## 10단계: GitHub Pages 배포

```bash
mkdocs gh-deploy --force
```

이 명령은 세 가지를 한꺼번에 처리한다.

1. `mkdocs build` — 마크다운을 HTML로 변환한다
2. `gh-pages` 브랜치에 결과물을 커밋한다
3. 해당 브랜치를 원격 저장소에 푸시한다

GitHub 저장소의 **Settings > Pages**에서 Source가 `gh-pages` 브랜치로 설정되어 있는지 확인한다. 보통 자동으로 잡히지만, 안 되면 수동으로 선택한다.

1~2분 후 `https://username.github.io`에 접속하면 블로그가 보인다.

!!! note "이 과정은 임시다"
    지금은 글을 쓸 때마다 `mkdocs gh-deploy`를 직접 실행해야 한다. 다음 편에서 GitHub Actions를 설정하면, `git push`만으로 이 과정이 자동으로 실행된다. 로컬에 Python이 없어도 GitHub 서버에서 빌드와 배포가 처리된다.


## 삽질 기록

### blog 플러그인이 없다는 에러

```
ERROR   -  Config value 'plugins': The "blog" plugin is not installed
```

`mkdocs-material`이 아닌 기본 `mkdocs`만 설치된 경우 나타난다. `pip install mkdocs-material`로 다시 설치한다. 가상환경이 활성화되어 있는지도 확인한다.

### 글이 블로그 목록에 안 보인다

두 가지를 확인한다.

1. 파일이 `docs/blog/posts/` 디렉토리 안에 있는가. 다른 위치에 넣으면 블로그 플러그인이 인식하지 못한다.
2. front matter에 `date` 필드가 있는가. 날짜가 없으면 목록에 표시되지 않는다.

### 배포 후 404

- `gh-pages` 브랜치가 푸시되었는지 GitHub 저장소에서 확인한다.
- Settings > Pages에서 Source가 `gh-pages` / `(root)`로 되어 있는지 확인한다.
- 배포 후 반영까지 최대 10분 정도 걸릴 수 있다. 처음이라면 잠시 기다려본다.


## 여기까지의 결과

이 글을 따라왔다면:

- MkDocs Material이 설치된 로컬 환경이 갖춰져 있다
- 블로그 프로젝트 구조가 잡혀 있다
- 첫 글이 작성되어 있다
- `https://username.github.io`에 블로그가 배포되어 있다

다음 편에서는 GitHub Actions 워크플로를 작성한다. `main` 브랜치에 push하면 자동으로 빌드되고 배포되는 파이프라인을 구축한다. 이걸 설정하고 나면, 이후의 블로그 작업은 "글 쓰기 → push" 두 단계로 줄어든다.

---

## 참고 자료

- [MkDocs Material 공식 문서](https://squidfunk.github.io/mkdocs-material/)
- [MkDocs Material 블로그 플러그인](https://squidfunk.github.io/mkdocs-material/plugins/blog/)
- [MkDocs 공식 문서](https://www.mkdocs.org/)
- [GitHub Pages 공식 문서](https://docs.github.com/pages)
