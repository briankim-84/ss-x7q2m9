"""표현(picks)이 영상의 몇 번째 자막에서 나오는지 찾아 at / hl 를 채운다
  at : cues 배열 번호 (그 자막이 떠 있는 동안 표현 칩이 뜬다)
  hl : 그 자막 en 안에서 노란색으로 강조할 부분 (en 원문 그대로의 부분 문자열)
사용: python tools/locate_picks.py <id> [<id> ...]   → work/<id>_clip.json 갱신
      python tools/locate_picks.py --feed             → feed.json 전체 (이미 at 이 있는 표현은 건드리지 않음)
못 찾은 표현은 목록으로 출력한다. 그 표현은 json에 at / hl 를 손으로 적는다.
"""
import sys, os, json, re
from common import WORK, ROOT

WORD = re.compile(r"[A-Za-z0-9]+(?:['’][A-Za-z]+)*")
WILD = {"___": (1, 6), "someone": (1, 3), "someone's": (1, 3), "one's": (1, 1), "sb": (1, 3),
        "something": (1, 4), "a": None}   # a 는 보통 단어

def norm(w):
    return w.lower().replace("’", "'")

def stem(w):
    w = norm(w)
    for suf in ("'s", "ing", "ed", "es", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            return w[: -len(suf)]
    return w

def same(a, b):
    a, b = norm(a), norm(b)
    if a == b: return True
    if a.replace("'", "") == b.replace("'", ""): return True
    sa, sb = stem(a), stem(b)
    if sa == sb: return True
    if len(sa) >= 4 and len(sb) >= 4 and (sa.startswith(sb) or sb.startswith(sa)): return True
    return False

def chunk_tokens(chunk):
    c = re.sub(r"\([^)]*\)", " ", chunk)          # (for ___) 같은 선택 부분은 뺀다
    c = re.sub(r"_{2,}\w*", " ___ ", c)
    toks = []
    for t in re.findall(r"___|[A-Za-z0-9]+(?:['’][A-Za-z]+)*", c):
        n = norm(t)
        if n in ("a", "b") and t.isupper() and len(t) == 1:  # "I'd rather A than B"
            toks.append(("W", (1, 6)))
        elif n in WILD and WILD[n]:
            toks.append(("W", WILD[n]))
        else:
            toks.append(("L", t))
    while toks and toks[-1][0] == "W": toks.pop()   # 끝의 빈칸은 강조 범위에서 뺀다
    while toks and toks[0][0] == "W": toks.pop(0)
    return toks

def match_at(words, toks, s, budget):
    """words[s:]에서 toks를 맞춰 본다. 끝 단어 번호(exclusive)와 남은 budget을 돌려준다."""
    best = None
    def go(i, k, b, matched):
        nonlocal best
        if k == len(toks):
            if best is None or b > best[1] or (b == best[1] and i < best[0]):
                best = (i, b, matched)
            return
        kind, val = toks[k]
        if kind == "W":
            lo, hi = val
            for n in range(lo, hi + 1):
                if i + n <= len(words): go(i + n, k + 1, b, matched)
            return
        if i < len(words) and same(words[i][0], val):
            go(i + 1, k + 1, b, matched + 1)
        if b > 0:
            go(i, k + 1, b - 1, matched)                       # 표현 단어가 자막에 없음
            if i < len(words) and k > 0:
                go(i + 1, k, b - 1, matched)                   # 자막에 군더더기 단어 (like, really …)
    go(s, 0, budget, 0)
    return best

def locate(clip):
    misses = []
    for p in clip["picks"]:
        if "at" in p: continue
        toks = chunk_tokens(p["chunk"])
        lits = sum(1 for t in toks if t[0] == "L")
        found = None
        for i, q in enumerate(clip["cues"]):
            words = [(m.group(0), m.start(), m.end()) for m in WORD.finditer(q["en"])]
            budget = 1 if lits >= 4 else 0
            for s in range(len(words)):
                if not same(words[s][0], toks[0][1]) and budget == 0: continue
                r = match_at(words, toks, s, budget)
                if r and r[2] >= max(1, lits - budget):
                    end = r[0]
                    # 강조 범위: 첫 일치 단어 ~ 마지막 단어
                    a = words[s][1]; z = words[end - 1][2]
                    found = (i, q["en"][a:z]); break
            if found: break
        if found:
            p["at"], p["hl"] = found
        else:
            misses.append(p["chunk"])
    return misses

if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--feed"]:
        path = os.path.join(ROOT, "feed.json")
        feed = json.load(open(path, encoding="utf-8"))
        allm = []
        for c in feed["clips"]:
            allm += [(c["id"], m) for m in locate(c)]
        json.dump(feed, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        n = sum(len(c["picks"]) for c in feed["clips"])
        print(f"feed.json 표현 {n}개 중 위치 있음 {n - len(allm)}개, 못 찾음 {len(allm)}개")
        for cid, m in allm: print(" ", cid, "|", m)
    else:
        for cid in args:
            path = os.path.join(WORK, f"{cid}_clip.json")
            clip = json.load(open(path, encoding="utf-8"))
            ms = locate(clip)
            json.dump(clip, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            print(cid, "못 찾음:" if ms else "표현 3개 위치 확인", *ms)
