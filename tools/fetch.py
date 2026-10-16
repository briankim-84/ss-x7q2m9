"""유튜브에서 구간만 내려받기
사용: python tools/fetch.py <id> <url> <start> <end>
예:   python tools/fetch.py 043 https://youtu.be/xxxx 4:31 5:59
결과: work/<id>_raw.mp4  (원본 해상도, 구간은 앞뒤 1초 여유)
"""
import sys, os, shutil
from common import run, WORK, ts
cid, url, a, b = sys.argv[1:5]
a, b = max(0, ts(a)-1.0), ts(b)+1.0
out = os.path.join(WORK, f"{cid}_raw.%(ext)s")
for f in os.listdir(WORK):
    if f.startswith(f"{cid}_raw."): os.remove(os.path.join(WORK,f))
cmd = ["yt-dlp","--no-playlist",
       "-f","bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[ext=mp4]/b",
       "--download-sections",f"*{a:.1f}-{b:.1f}","--force-keyframes-at-cuts",
       "--merge-output-format","mp4","-o",out,url]
# 로그인된 크롬 쿠키로 시도 → 실패하면 쿠키 없이
try:
    run(cmd[:1]+["--cookies-from-browser","chrome"]+cmd[1:])
except SystemExit:
    run(cmd)
final = os.path.join(WORK, f"{cid}_raw.mp4")
print("저장:", final)
