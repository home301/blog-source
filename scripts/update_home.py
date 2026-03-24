#!/usr/bin/env python3
"""
빌드 전에 index.md의 '최신 글' 섹션을 자동 갱신한다.
blog/posts/ 하위의 마크다운 파일에서 date, description, slug를 읽어
최신 3개를 골라 index.md에 삽입한다.
"""

import os
import re
import sys
from pathlib import Path

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"
BLOG_POSTS_DIR = DOCS_DIR / "blog" / "posts"
INDEX_FILE = DOCS_DIR / "index.md"

# index.md 내 마커
START_MARKER = "<!-- LATEST_POSTS_START -->"
END_MARKER = "<!-- LATEST_POSTS_END -->"

MAX_POSTS = 3


def parse_frontmatter(filepath: Path) -> dict | None:
    """마크다운 파일의 프론트매터에서 date, description, slug, title을 추출한다."""
    text = filepath.read_text(encoding="utf-8")

    # frontmatter 파싱
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return None

    fm_text = match.group(1)
    body = text[match.end():]

    # draft 체크
    if re.search(r"^draft:\s*true", fm_text, re.MULTILINE):
        return None

    # date
    date_match = re.search(r"^date:\s*(\S+)", fm_text, re.MULTILINE)
    if not date_match:
        return None
    date_str = date_match.group(1)

    # slug
    slug_match = re.search(r"^slug:\s*(\S+)", fm_text, re.MULTILINE)
    slug = slug_match.group(1) if slug_match else filepath.stem

    # description
    desc_match = re.search(r'^description:\s*["\']?(.*?)["\']?\s*$', fm_text, re.MULTILINE)
    description = desc_match.group(1) if desc_match else ""

    # title: 본문의 첫 번째 # 헤딩
    title_match = re.search(r"^#\s+(.+)", body, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else filepath.stem

    return {
        "date": date_str,
        "slug": slug,
        "title": title,
        "description": description,
        "path": filepath,
    }


def collect_posts() -> list[dict]:
    """blog/posts/ 하위의 모든 마크다운 파일에서 포스트 정보를 수집한다."""
    posts = []
    for md_file in BLOG_POSTS_DIR.rglob("*.md"):
        if md_file.name == "index.md":
            continue
        info = parse_frontmatter(md_file)
        if info:
            posts.append(info)

    # 날짜 내림차순 정렬
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts[:MAX_POSTS]


def generate_section(posts: list[dict]) -> str:
    """최신 글 마크다운 섹션을 생성한다."""
    lines = [START_MARKER, ""]
    for post in posts:
        url = f"blog/{post['slug']}/"
        lines.append(f"### [{post['title']}]({url})")
        if post["description"]:
            lines.append(f"> {post['description']}")
        lines.append("")
    lines.append(END_MARKER)
    return "\n".join(lines)


def update_index(posts: list[dict]) -> bool:
    """index.md의 마커 사이를 최신 글로 교체한다."""
    content = INDEX_FILE.read_text(encoding="utf-8")

    if START_MARKER not in content or END_MARKER not in content:
        print(f"ERROR: index.md에 마커가 없습니다. {START_MARKER} / {END_MARKER}")
        return False

    pattern = re.compile(
        re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER),
        re.DOTALL,
    )

    new_section = generate_section(posts)
    new_content = pattern.sub(new_section, content)

    if new_content == content:
        print("index.md: 변경 없음")
        return True

    INDEX_FILE.write_text(new_content, encoding="utf-8")
    print(f"index.md: 최신 글 {len(posts)}개로 갱신 완료")
    return True


def main():
    posts = collect_posts()
    if not posts:
        print("WARNING: 포스트를 찾을 수 없습니다.")
        sys.exit(0)

    print(f"최신 포스트 {len(posts)}개:")
    for p in posts:
        print(f"  - [{p['date']}] {p['title']}")

    if not update_index(posts):
        sys.exit(1)


if __name__ == "__main__":
    main()
