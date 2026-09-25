from pathlib import Path
import subprocess
import tempfile
import json
import os


def get_video_info(path) -> dict | None:
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_streams", "-show_format",
        str(path),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    try:
        data = json.loads(res.stdout)
    except Exception:
        return None

    stream = next(
        (s for s in data.get("streams", []) if s.get("codec_type") == "video"),
        None,
    )
    if not stream:
        return None

    duration = float(
        stream.get("duration") or data.get("format", {}).get("duration", 0)
    )
    return {
        "duration": duration,
        "width": int(stream["width"]),
        "height": int(stream["height"]),
    }


def extract_frame_bytes(path, time: float = 1.0) -> bytes:
    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    tmp.close()
    subprocess.run(
        ["ffmpeg", "-y", "-ss", str(time), "-i", str(path), "-vframes", "1", tmp.name],
        capture_output=True,
    )
    try:
        with open(tmp.name, "rb") as f:
            return f.read()
    finally:
        os.unlink(tmp.name)


def compute_crop(vid_w: int, vid_h: int, ratio_str: str | None):
    if not ratio_str:
        return vid_w, vid_h, 0, 0
    w_r, h_r = map(int, ratio_str.split(":"))
    target = w_r / h_r
    current = vid_w / vid_h
    if current > target:
        cw = int(vid_h * target) & ~1  # 짝수 맞추기
        ch = vid_h
    else:
        cw = vid_w
        ch = int(vid_w / target) & ~1
    cx = (vid_w - cw) // 2
    cy = (vid_h - ch) // 2
    return cw, ch, cx, cy


def export_video(
    input_path,
    trim_start: float,
    trim_end: float,
    crop,
    speed: float,
    web_preview: bool = False,
) -> bytes:
    out_tmp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
    out_tmp.close()

    vf, af = [], []
    if crop:
        cw, ch, cx, cy = crop
        vf.append(f"crop={cw}:{ch}:{cx}:{cy}")
    if speed != 1.0:
        vf.append(f"setpts={1/speed:.6f}*PTS")
        af.append(f"atempo={speed:.2f}")

    cmd = ["ffmpeg", "-y", "-ss", str(trim_start), "-to", str(trim_end), "-i", str(input_path)]
    if vf:
        cmd += ["-vf", ",".join(vf)]
    if af:
        cmd += ["-af", ",".join(af)]
    if web_preview:
        cmd += ["-c:v", "libx264", "-c:a", "aac", "-movflags", "+faststart"]
    cmd.append(out_tmp.name)

    try:
        subprocess.run(cmd, capture_output=True, check=True)
        with open(out_tmp.name, "rb") as f:
            return f.read()
    finally:
        os.unlink(out_tmp.name)
