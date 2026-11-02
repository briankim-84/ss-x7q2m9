"""tools/locate_picks.py — 표현이 몇 번째 자막에 나오는지 찾기"""
from locate_picks import same, stem, chunk_tokens, locate


def clip(cues, *chunks):
    return {"cues": [{"t": float(i), "en": en, "ko": ""} for i, en in enumerate(cues)],
            "picks": [{"chunk": c} for c in chunks]}


def test_same_handles_inflection_and_apostrophes():
    assert same("rooting", "root")
    assert same("went", "went")
    assert same("I’m", "i'm")
    assert not same("cat", "dog")


def test_stem():
    assert stem("rooting") == "root"
    assert stem("is") == "is"          # 너무 짧으면 그대로


def test_chunk_tokens_wildcards_and_optional_parts():
    toks = chunk_tokens("root for someone")
    assert toks == [("L", "root"), ("L", "for")]          # 끝 빈칸은 강조에서 뺀다
    toks = chunk_tokens("go (for ___) big")
    assert [t for t in toks if t[0] == "L"] == [("L", "go"), ("L", "big")]


def test_locate_finds_inflected_form():
    c = clip(["Hi there.", "I was rooting for her the whole time.", "Bye."], "root for someone")
    assert locate(c) == []
    assert c["picks"][0]["at"] == 1
    assert c["picks"][0]["hl"] == "rooting for"
    assert c["picks"][0]["hl"] in c["cues"][1]["en"]


def test_locate_reports_miss_and_leaves_pick_untouched():
    c = clip(["Nothing relevant here."], "the real deal")
    assert locate(c) == ["the real deal"]
    assert "at" not in c["picks"][0]


def test_locate_keeps_existing_at():
    c = clip(["the real deal", "the real deal"], "the real deal")
    c["picks"][0]["at"] = 1
    locate(c)
    assert c["picks"][0]["at"] == 1
