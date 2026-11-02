"""tools/merge_feed.py — 임시 폴더에 레포 구조를 흉내 내고 실제로 실행해 본다"""
import json, os, shutil, subprocess, sys
import pytest
from conftest import TOOLS


@pytest.fixture
def repo(tmp_path):
    os.makedirs(tmp_path / "tools")
    for f in ("common.py", "merge_feed.py"):
        shutil.copy(os.path.join(TOOLS, f), tmp_path / "tools" / f)
    for d in ("work", "videos", "posters"):
        os.makedirs(tmp_path / d)
    feed = {"version": "3.9", "handle": "h", "clips": [{"id": "ss001"}]}
    (tmp_path / "feed.json").write_text(json.dumps(feed), encoding="utf-8")
    return tmp_path


def add_clip(repo, cid, make_files=True):
    clip = {"id": cid, "src": f"videos/{cid}.mp4", "poster": f"posters/{cid}.jpg", "who": "테스트"}
    (repo / "work" / f"{cid}_clip.json").write_text(json.dumps(clip, ensure_ascii=False), encoding="utf-8")
    if make_files:
        (repo / "videos" / f"{cid}.mp4").write_bytes(b"x")
        (repo / "posters" / f"{cid}.jpg").write_bytes(b"x")


def run(repo, *ids):
    return subprocess.run([sys.executable, str(repo / "tools" / "merge_feed.py"), *ids],
                          capture_output=True, text=True, encoding="utf-8")


def test_merge_appends_and_bumps_version(repo):
    add_clip(repo, "ss002"); add_clip(repo, "ss003")
    r = run(repo, "ss002", "ss003")
    assert r.returncode == 0, r.stderr
    feed = json.loads((repo / "feed.json").read_text(encoding="utf-8"))
    assert feed["version"] == "3.10"          # 3.9 → 3.10 (문자열 비교가 아니라 숫자로)
    assert [c["id"] for c in feed["clips"]] == ["ss001", "ss002", "ss003"]
    assert feed["clips"][1]["who"] == "테스트"  # 한글이 깨지지 않음


def test_merge_rejects_duplicate_id(repo):
    add_clip(repo, "ss001")
    r = run(repo, "ss001")
    assert r.returncode != 0
    assert json.loads((repo / "feed.json").read_text())["version"] == "3.9"


def test_merge_rejects_missing_video(repo):
    add_clip(repo, "ss002", make_files=False)
    r = run(repo, "ss002")
    assert r.returncode != 0
    assert json.loads((repo / "feed.json").read_text())["version"] == "3.9"
