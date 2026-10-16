import subprocess, json, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, "work")
os.makedirs(WORK, exist_ok=True)

def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", **kw)
    if r.returncode != 0:
        sys.stderr.write(r.stderr[-3000:])
        raise SystemExit(f"실패: {' '.join(cmd[:3])} ...")
    return r.stdout

def duration(path):
    out = run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",path])
    return float(out.strip())

def ts(s):
    """'4:31' / '1:02:05' / '271.5' -> seconds"""
    s = str(s).strip()
    if ":" not in s: return float(s)
    parts = [float(p) for p in s.split(":")]
    sec = 0
    for p in parts: sec = sec*60 + p
    return sec
