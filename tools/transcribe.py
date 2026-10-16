"""전사 (단어 단위 타임스탬프)
사용: python tools/transcribe.py <id> [--file 경로]
결과: work/<id>_words.json, 화면에 세그먼트 출력
"""
import sys, os, json
from common import run, WORK
cid = sys.argv[1]
src = sys.argv[sys.argv.index("--file")+1] if "--file" in sys.argv else os.path.join(WORK, f"{cid}_raw.mp4")
wav = os.path.join(WORK, f"{cid}_16k.wav")
run(["ffmpeg","-y","-v","error","-i",src,"-vn","-ac","1","-ar","16000",wav])
try:
    from faster_whisper import WhisperModel
    m = WhisperModel("small", device="cpu", compute_type="int8")
    import numpy as np, wave
    with wave.open(wav) as w: audio = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)/32768.0
    segs, _ = m.transcribe(audio, language="en", word_timestamps=True)
    out = [{"start":s.start,"end":s.end,"text":s.text.strip(),
            "words":[{"w":w.word,"s":w.start,"e":w.end} for w in (s.words or [])]} for s in segs]
except ImportError:
    import whisper
    r = whisper.load_model("small").transcribe(wav, language="en", word_timestamps=True)
    out = [{"start":s["start"],"end":s["end"],"text":s["text"].strip(),
            "words":[{"w":w["word"],"s":w["start"],"e":w["end"]} for w in s["words"]]} for s in r["segments"]]
json.dump(out, open(os.path.join(WORK, f"{cid}_words.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
for s in out: print(f'{s["start"]:7.2f} - {s["end"]:7.2f}  {s["text"]}')
