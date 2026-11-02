"""feed.json 규칙 검사 (CLAUDE.md의 클립 json 형식 기준)

기존 클립은 손대지 않는 게 규칙이라, 이미 규칙과 다른 클립은 아래 목록에 묶어 두고
새 클립이 같은 실수를 하면 테스트가 실패하게 했다.
"""
import json, os
import pytest
from conftest import ROOT

FEED = json.load(open(os.path.join(ROOT, "feed.json"), encoding="utf-8"))
CLIPS = FEED["clips"]
CATS = {"korean", "actor", "singer", "celeb", "brian"}
REQUIRED = ("id", "src", "source", "who", "cat", "band", "tags", "cues", "picks", "poster")

# 첫 자막 t가 0.0이 아닌 기존 클립 (2026-11 점검 시점)
LEGACY_FIRST_CUE = {"ss002", "ss021", "ss022", "ss033", "ss034", "ss035", "ss036", "ss037"}
# 자막 t가 거꾸로 된 기존 클립 — ss040은 29.4 다음에 27.5가 와서 한 줄이 화면에 안 뜬다
LEGACY_CUE_ORDER = {"ss040"}


def ids(f):
    return pytest.mark.parametrize("c", CLIPS, ids=[c["id"] for c in CLIPS])(f)


def test_top_level():
    assert set(FEED) >= {"version", "handle", "clips"}
    major, minor = FEED["version"].split(".")
    assert major.isdigit() and minor.isdigit()


def test_ids_unique():
    all_ids = [c["id"] for c in CLIPS]
    assert len(all_ids) == len(set(all_ids))


@ids
def test_fields(c):
    missing = [k for k in REQUIRED if k not in c]
    assert not missing
    assert c["cat"] in CATS
    assert c["who"].strip()
    assert 0 <= c["band"]["top"] < c["band"]["bottom"] <= 1
    assert len(c["tags"]) >= 2 and all(t.startswith("#") for t in c["tags"])


@ids
def test_media_files_exist(c):
    for k in ("src", "poster"):
        path = os.path.normpath(os.path.join(ROOT, c[k]))
        assert path.startswith(ROOT + os.sep), f"{k}가 레포 밖을 가리킴: {c[k]}"
        assert os.path.isfile(path), f"파일 없음: {c[k]}"


@ids
def test_cues(c):
    ts = [q["t"] for q in c["cues"]]
    assert ts, "자막 없음"
    if c["id"] not in LEGACY_FIRST_CUE:
        assert ts[0] == 0.0, "첫 자막 t는 0.0"
    if c["id"] not in LEGACY_CUE_ORDER:
        assert ts == sorted(ts), "자막 t가 시간순이 아님"
    for q in c["cues"]:
        assert q["en"].strip() and q["ko"].strip()


@ids
def test_picks(c):
    assert len(c["picks"]) == 3
    for p in c["picks"]:
        for k in ("chunk", "ko", "why", "use", "useKo"):
            assert p.get(k, "").strip(), f"{p.get('chunk')}: {k} 비어 있음"
        if "at" in p:
            assert isinstance(p["at"], int) and 0 <= p["at"] < len(c["cues"])
            if p.get("hl"):
                assert p["hl"] in c["cues"][p["at"]]["en"], f"hl이 자막에 없음: {p['chunk']}"


def test_legacy_lists_are_still_needed():
    """기존 클립을 고치면 예외 목록에서도 빼도록 알려 준다"""
    by = {c["id"]: c for c in CLIPS}
    for cid in LEGACY_FIRST_CUE:
        assert by[cid]["cues"][0]["t"] != 0.0, f"{cid}는 이제 규칙대로라 목록에서 빼도 됨"
    for cid in LEGACY_CUE_ORDER:
        ts = [q["t"] for q in by[cid]["cues"]]
        assert ts != sorted(ts), f"{cid}는 이제 규칙대로라 목록에서 빼도 됨"
