"""tools/encode.py — 가짜 원본 영상으로 S&S 규격 인코딩·포스터가 나오는지 (ffmpeg·Pillow 업데이트 확인용)"""
import os, shutil, subprocess, sys
import pytest
from conftest import TOOLS

pytestmark = pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg 없음")


def test_encode_makes_video_and_poster(tmp_path):
    os.makedirs(tmp_path / "tools")
    for f in ("common.py", "encode.py"):
        shutil.copy(os.path.join(TOOLS, f), tmp_path / "tools" / f)
    for d in ("work", "videos", "posters"):
        os.makedirs(tmp_path / d)
    raw = tmp_path / "work" / "t01_raw.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error",
                    "-f", "lavfi", "-i", "testsrc=size=1920x1080:rate=30:duration=4",
                    "-f", "lavfi", "-i", "sine=frequency=440:duration=4",
                    "-c:v", "libx264", "-preset", "ultrafast", "-c:a", "aac", "-shortest", str(raw)],
                   check=True)
    r = subprocess.run([sys.executable, str(tmp_path / "tools" / "encode.py"), "t01", "0.5", "3.0"],
                       capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stderr
    out = tmp_path / "videos" / "t01.mp4"
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                            "-show_entries", "stream=width,height", "-of", "csv=p=0", str(out)],
                           capture_output=True, text=True).stdout.strip()
    assert probe == "720,1280"
    from PIL import Image
    with Image.open(tmp_path / "posters" / "t01.jpg") as im:
        assert im.size == (432, 317)
