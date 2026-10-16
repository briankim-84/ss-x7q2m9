"""완성본 검증: 자막 싱크 / 마지막 큐 / 표현 3개 / 음량
사용: python tools/verify.py <id>   (work/<id>_clip.json 필요)
"""
import sys, os, json, re
from common import run, duration, WORK, ROOT
cid = sys.argv[1]
clip = json.load(open(os.path.join(WORK, f"{cid}_clip.json"), encoding="utf-8"))
vid = os.path.join(ROOT, clip["src"])
d = duration(vid)
ok = True
def bad(msg):
    global ok; ok = False; print("!!", msg)
# 음량
import subprocess
r = subprocess.run(["ffmpeg","-i",vid,"-af","loudnorm=print_format=summary","-f","null","-"],capture_output=True,text=True)
m = re.search(r"Input Integrated:\s*(-?[\d.]+)", r.stderr); lufs = float(m.group(1)) if m else None
print(f"길이 {d:.1f}s  음량 {lufs} LUFS  자막 {len(clip['cues'])}줄  표현 {len(clip['picks'])}개")
if lufs is None or not (-25 <= lufs <= -19): bad("음량이 기존 클립 범위(-19~-25 LUFS) 밖")
if len(clip["picks"]) != 3: bad("표현은 3개여야 함")
if clip["cues"][0]["t"] != 0.0: bad("첫 자막 t는 0.0이어야 함")
if clip["cues"][-1]["t"] > d - 0.4: bad("마지막 자막이 영상 끝을 넘음")
for k in ("id","src","source","band","tags","cues","picks","poster"):
    if k not in clip: bad(f"필드 누락: {k}")
# 싱크: 완성본 재전사 후 각 큐 시작이 어떤 단어 시작과 0.6초 이내인지
run(["python", os.path.join(ROOT,"tools","transcribe.py"), cid, "--file", vid])
words = [w["s"] for s in json.load(open(os.path.join(WORK,f"{cid}_words.json"),encoding="utf-8")) for w in s["words"]]
errs = [(q["t"], min(abs(w-q["t"]) for w in words)) for q in clip["cues"][1:]]
worst = max(errs, key=lambda x:x[1]) if errs else (0,0)
print(f"싱크 최대 오차 {worst[1]:.2f}s (t={worst[0]})")
if worst[1] > 0.6: bad("자막 싱크 0.6초 초과 — 해당 큐 t 수정 필요")
print("검증 통과" if ok else "검증 실패 — 위 항목 수정 후 재실행")
sys.exit(0 if ok else 1)
