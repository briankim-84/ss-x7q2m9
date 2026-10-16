"""feed.json에 클립 추가 + 버전 올리기
사용: python tools/merge_feed.py <id> [<id> ...]
"""
import sys, os, json
from common import WORK, ROOT
p = os.path.join(ROOT, "feed.json")
feed = json.load(open(p, encoding="utf-8"))
ids = {c["id"] for c in feed["clips"]}
for cid in sys.argv[1:]:
    clip = json.load(open(os.path.join(WORK, f"{cid}_clip.json"), encoding="utf-8"))
    if clip["id"] in ids: raise SystemExit(f"{clip['id']} 이미 있음")
    for k in ("src","poster"):
        if not os.path.exists(os.path.join(ROOT, clip[k])): raise SystemExit(f"파일 없음: {clip[k]}")
    feed["clips"].append(clip); ids.add(clip["id"])
major, minor = feed["version"].split(".")
feed["version"] = f"{major}.{int(minor)+1}"
json.dump(feed, open(p,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"feed.json → v{feed['version']}, 클립 {len(feed['clips'])}개, 마지막 {feed['clips'][-1]['id']}")
