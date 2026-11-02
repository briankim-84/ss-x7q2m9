"""공개 레포에 비밀값이 올라가지 않았는지 검사

Firebase 웹 설정의 apiKey는 브라우저에 그대로 내려가는 '식별자'라 예외로 둔다.
(보안은 키가 아니라 Realtime Database 규칙과 키 사용 제한으로 지킨다.)
"""
import os, re, subprocess
import pytest
from conftest import ROOT

BINARY = (".mp4", ".jpg", ".jpeg", ".png", ".gif", ".webp", ".ico", ".woff", ".woff2")
PATTERNS = {
    "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "GitHub token": re.compile(r"\b(gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{20,})\b"),
    "Slack token": re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}"),
    "OpenAI/Anthropic key": re.compile(r"\bsk-(ant-)?[A-Za-z0-9_-]{20,}"),
    "Google API key": re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
    "password literal": re.compile(r"(?i)\b(password|passwd|pwd|secret)\b\s*[:=]\s*[\"'][^\"']{4,}[\"']"),
}
# (파일, 패턴 이름) — 일부러 공개하는 값
ALLOWED = {("index.html", "Google API key")}
FORBIDDEN_FILES = re.compile(r"(^|/)(\.env(\..+)?|.*\.pem|.*\.key|.*\.p12|cookies.*\.txt|.*service-account.*\.json)$")


def tracked_files():
    try:
        out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("git 저장소가 아님")
    return [f for f in out.splitlines() if f]


def test_no_secret_files_tracked():
    bad = [f for f in tracked_files() if FORBIDDEN_FILES.search(f)]
    assert not bad, f"비밀 파일이 커밋돼 있음: {bad}"


def test_no_secret_strings():
    hits = []
    for f in tracked_files():
        if f.lower().endswith(BINARY) or f.startswith("tests/"):
            continue
        try:
            text = open(os.path.join(ROOT, f), encoding="utf-8").read()
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        for name, pat in PATTERNS.items():
            if (f, name) in ALLOWED:
                continue
            for m in pat.finditer(text):
                line = text.count("\n", 0, m.start()) + 1
                hits.append(f"{f}:{line} {name}")
    assert not hits, "비밀값으로 보이는 문자열:\n" + "\n".join(hits)


def test_firebase_key_only_in_firebase_config():
    """허용한 Google 키도 FIREBASE 설정 블록 안에서만, 한 번만 나와야 한다"""
    html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    keys = PATTERNS["Google API key"].findall(html)
    assert len(keys) <= 1
    if keys:
        block = re.search(r"const FIREBASE = \{.*?\};", html, re.S).group(0)
        assert keys[0] in block
