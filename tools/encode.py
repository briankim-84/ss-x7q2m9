"""S&S 규격으로 인코딩 + 포스터
사용: python tools/encode.py <id> <컷시작> <컷끝>   (raw 파일 기준 초)
규격: 720x1280 / 영상 밴드 0.294~0.706 (좌우 크롭) / CRF25 / -22 LUFS / AAC 96k
결과: videos/<id>.mp4, posters/<id>.jpg
"""
import sys, os, io, subprocess
from PIL import Image
from common import run, duration, WORK, ROOT, ts
cid, a, b = sys.argv[1], ts(sys.argv[2]), ts(sys.argv[3])
src = os.path.join(WORK, f"{cid}_raw.mp4")
out = os.path.join(ROOT, "videos", f"{cid}.mp4")
poster = os.path.join(ROOT, "posters", f"{cid}.jpg")
fo = b - a - 0.12
vf = "scale=-2:527,crop=720:527,pad=720:1280:(ow-iw)/2:377:black,setsar=1"
af = f"afade=t=in:d=0.08,afade=t=out:st={fo:.3f}:d=0.12,loudnorm=I=-22:TP=-3:LRA=11"
run(["ffmpeg","-y","-v","error","-ss",f"{a:.3f}","-to",f"{b:.3f}","-i",src,
     "-vf",vf,"-r","30","-c:v","libx264","-crf","25","-preset","medium","-pix_fmt","yuv420p",
     "-af",af,"-ar","48000","-c:a","aac","-b:a","96k","-movflags","+faststart",out])
d = duration(out)
png = subprocess.run(["ffmpeg","-v","error","-ss",f"{d*0.35:.2f}","-i",out,"-frames:v","1","-f","image2","-vcodec","png","-"],capture_output=True).stdout
Image.open(io.BytesIO(png)).convert("RGB").crop((0,377,720,904)).resize((432,317),Image.LANCZOS).save(poster,quality=76,optimize=True)
print(f"videos/{cid}.mp4  {d:.1f}s  {os.path.getsize(out)//1024}KB")
print(f"posters/{cid}.jpg")
