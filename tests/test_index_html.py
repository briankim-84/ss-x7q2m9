"""index.html — feed.json 값이 HTML로 해석되지 않게 이스케이프하는지"""
import json, os, re, shutil, subprocess
import pytest
from conftest import ROOT

HTML = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()


@pytest.mark.skipif(not shutil.which("node"), reason="node 없음")
def test_esc_escapes_html_and_quotes():
    esc_src = re.search(r"^const esc=.*$", HTML, re.M).group(0)
    sample = '<img src=x onerror="a()">\'&'
    js = esc_src + f"\nprocess.stdout.write(esc({json.dumps(sample)}));"
    out = subprocess.run(["node", "-e", js], capture_output=True, text=True, check=True).stdout
    assert out == "&lt;img src=x onerror=&quot;a()&quot;&gt;&#39;&amp;"


@pytest.mark.parametrize("field", ["c.src", "c.poster", "c.id", "FEED.handle", "c.tags"])
def test_feed_fields_not_inserted_raw(field):
    """템플릿 안에 ${c.src} 처럼 이스케이프 없이 들어가는 곳이 없어야 한다"""
    raw = re.findall(r"\$\{" + re.escape(field) + r"[^}]*\}", HTML)
    assert not raw, f"이스케이프 없이 들어감: {raw}"


def test_third_party_scripts_are_pinned():
    for url in re.findall(r"https://www\.gstatic\.com/firebasejs/([^/]+)/", HTML):
        assert re.fullmatch(r"\d+\.\d+\.\d+", url), "Firebase SDK 버전을 고정해야 함"
