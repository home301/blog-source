---
date: 2026-03-02
categories:
  - AI/개발
tags:
  - linux
  - popos
  - korean
  - fcitx5
---

# Pop!_OS 24.04 LTS 설치 후 한글 입력 해결기 — fcitx5가 답이다

리눅스에서 한글 입력이 안 되는 건 일종의 통과의례다. 근데 Pop!_OS 24.04는 그 통과의례가 좀 매웠다.

한글이 안 쳐지니까 한글로 검색을 할 수가 없다. "Pop OS 한글 입력"을 치고 싶은데 한글이 안 되니까 영어로 검색해야 하는 아이러니. 이 글은 그 삽질의 기록이자, 같은 고통을 겪을 누군가를 위한 해결 가이드다.

## 환경

```
PRETTY_NAME="Pop!_OS 24.04 LTS"
VERSION_ID="24.04"
VERSION_CODENAME=noble
```

Pop!_OS 24.04부터는 **COSMIC 데스크탑**이 기본이다. System76이 Rust로 밑바닥부터 새로 만든 DE. GNOME이 아니다. 이게 핵심이다. 기존에 "Ubuntu 한글 설정" 검색해서 나오는 가이드 대부분이 GNOME 기준이라 COSMIC에서는 안 먹힌다.

세션은 Wayland. X11이 아니다.

## 삽질의 시작: ibus-hangul

검색하면 대부분의 가이드가 이렇게 말한다:

```bash
sudo apt install ibus-hangul
```

그리고 Settings → Keyboard → Input Sources에서 Korean (Hangul) 추가하라고. Ubuntu + GNOME이면 이게 맞다. 근데 COSMIC에서는?

- ibus 설정 UI가 GNOME Settings에 통합되어 있는데, COSMIC은 GNOME이 아니다
- Electron 앱(VS Code, Slack 등)에서 한글 조합이 깨진다
- Wayland 세션에서 한/영 전환이 들쑥날쑥

ibus를 지우고 싶었지만 **COSMIC DE가 ibus에 종속성**이 걸려 있어서 삭제하면 데스크탑째 날아간다. 그냥 놔두고 비활성화하는 수밖에 없다.

결국 싹 밀고 재설치까지 했다. (네, 진짜로요.)

## 정답: fcitx5

여러 삽질 끝에 도달한 결론: **Pop!_OS 24.04 + COSMIC + Wayland 환경에서는 fcitx5가 답이다.**

현재 이 시스템에서 정상 동작 중인 설정을 그대로 공유한다.

### Step 1: 패키지 설치

```bash
sudo apt update
sudo apt install fcitx5 fcitx5-hangul fcitx5-frontend-all fcitx5-config-qt
```

`fcitx5-frontend-all`이 중요하다. GTK2, GTK3, GTK4, Qt5, Qt6 프론트엔드를 한 번에 설치해서 어떤 앱에서든 한글 입력이 작동하게 해준다.

실제 설치된 패키지 확인:

```
$ dpkg -l | grep fcitx5-hangul
ii  fcitx5-hangul:amd64    5.1.1-1    amd64    Hangul input method wrapper for fcitx5
```

### Step 2: 환경변수 설정

`~/.bashrc` 끝에 다음 3줄을 추가한다:

```bash
export GTK_IM_MODULE=fcitx
export QT_IM_MODULE=fcitx
export XMODIFIER=@im=fcitx
```

이 3종 세트가 없으면 fcitx5를 설치해도 앱에서 한글이 안 먹힌다. **가장 많이 빠뜨리는 부분**이니까 꼭 확인하자.

```bash
source ~/.bashrc
```

### Step 3: fcitx5 설정

```bash
fcitx5-configtool
```

설정 도구가 뜨면:

1. **Input Method** 탭에서 `+` 버튼 클릭
2. "Hangul" 검색해서 추가
3. **Global Options** → **Trigger Input Method**에 한/영 전환키 등록
   - `Hangul` 키 또는 `Alt_R` (오른쪽 Alt)

### Step 4: 자동 시작 설정

재부팅하면 fcitx5가 자동으로 안 올라온다. autostart에 등록해야 한다:

```bash
mkdir -p ~/.config/autostart
cp /usr/share/applications/org.fcitx.Fcitx5.desktop ~/.config/autostart/
```

파일이 없으면 직접 만든다:

```bash
cat > ~/.config/autostart/fcitx5.desktop << 'EOF'
[Desktop Entry]
Name=Fcitx5
Exec=fcitx5
Type=Application
X-GNOME-Autostart-enabled=true
EOF
```

### Step 5: 재부팅

```bash
sudo reboot
```

재부팅 후 확인:

```
$ fcitx5 --version
5.1.7
```

이 숫자가 나오면 성공이다.

## 현재 시스템 상태

실제로 이 글을 쓰고 있는 시스템의 설정이다:

```
$ locale
LANG=ko_KR.UTF-8
LC_CTYPE="ko_KR.UTF-8"
LC_TIME="ko_KR.UTF-8"
...
```

로캘이 `ko_KR.UTF-8`로 잡혀 있어야 한글이 제대로 표시된다. 설치 시 한국어를 선택했다면 자동으로 설정된다.

fcitx5 진단 도구로 상태를 확인할 수 있다:

```bash
fcitx5-diagnose
```

이 명령어가 문제 원인을 꽤 정확하게 짚어주니까, 뭔가 안 되면 일단 이것부터 돌려보자.

## 자주 겪는 문제

**한/영 전환이 안 된다**
→ `fcitx5-configtool` → Global Options → Trigger Input Method에 키가 등록되어 있는지 확인

**특정 앱에서만 한글이 안 된다**
→ 환경변수 3종 세트 (`GTK_IM_MODULE`, `QT_IM_MODULE`, `XMODIFIER`) 확인. `fcitx5-frontend-all` 설치 확인

**재부팅하면 한글이 초기화된다**
→ `~/.config/autostart/fcitx5.desktop` 파일이 있는지 확인

**ibus랑 fcitx5가 충돌하는 것 같다**
→ ibus는 삭제하지 말고 (COSMIC 종속성) 자동시작만 제거. fcitx5만 autostart에 등록

**fcitx5 트레이 아이콘이 안 보인다**
→ COSMIC에서는 정상이다. 아이콘 없어도 입력은 잘 된다. 당황하지 말자.

## ibus vs fcitx5, COSMIC에서의 선택

| 항목 | ibus | fcitx5 |
|------|------|--------|
| COSMIC DE 호환 | △ 설정 UI 불편 | ○ 별도 설정 도구 |
| Wayland 지원 | ○ | ○ |
| Electron 앱 | △ 조합 깨짐 | ○ |
| 설정 자유도 | 낮음 | 높음 |
| GNOME 통합 | ◎ | — |

**GNOME이면 ibus, COSMIC이면 fcitx5.** 이게 결론이다.

## 마무리

Pop!_OS 24.04는 좋은 배포판이다. COSMIC DE도 빠르고 깔끔하다. 근데 한국어 사용자한테는 초기 설정이 좀 불친절하다. 기존 Ubuntu/GNOME 가이드가 안 먹히니까 더 혼란스럽고.

정리하면:

1. `fcitx5` + `fcitx5-hangul` + `fcitx5-frontend-all` 설치
2. 환경변수 3종 세트를 `~/.bashrc`에 추가
3. `fcitx5-configtool`로 Hangul 엔진 추가 + 한/영 전환키 설정
4. autostart 등록
5. 재부팅

이 5단계면 끝이다. 더 이상 한글 때문에 OS를 재설치하는 일은 없기를.

---

## 참고

- [Pop!_OS 공식 사이트](https://pop.system76.com)
- [Pop!_OS 설치 가이드 (System76)](https://support.system76.com/articles/install-pop/)
- [fcitx5 공식 문서](https://fcitx-im.org/wiki/Fcitx_5)
- [Pop OS 한글 입력 설정 (11ci 블로그)](https://11ci.tistory.com/56)
