from io import BytesIO
from pathlib import Path
import tempfile
import subprocess
import librosa
import os
import numpy as np

MAJOR_PROFILE = (6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88)
MINOR_PROFILE = (6.33, 2.68, 3.52, 5.38, 2.6, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17)
CHROMA_LABELS = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")


def extract_video_id(url: str) -> str:
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    if "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    return ""


def download_wav_to_memory(url: str) -> BytesIO:
    ytdlp = subprocess.Popen(
        ["yt-dlp", "-f", "bestaudio", "-o", "-", url],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    ffmpeg = subprocess.Popen(
        ("ffmpeg", "-loglevel", "error", "-i", "pipe:0", "-ac", "1", "-ar", "16000", "-f", "wav", "pipe:1"),
        stdin=ytdlp.stdout,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    audio_bytes = ffmpeg.stdout.read()
    return BytesIO(audio_bytes)


def download_wav_to_tempfile(url: str) -> Path:
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp_path = Path(tmp.name)
    tmp.close()

    cmd = [
        "yt-dlp",
        "--no-playlist",
        "--playlist-items", "1",
        "-f", "bestaudio[abr<=192]/bestaudio",
        "-x",
        "--audio-format", "wav",
        "--postprocessor-args", "-t 240 -ac 1 -ar 22050",
        "--force-overwrites",
        "-o", str(tmp_path),
        url,
    ]
    print("$", " ".join(cmd))
    subprocess.run(cmd, check=True)
    return tmp_path


def get_bpm_from_wav(wav_path) -> int:
    y, sr = librosa.load(wav_path, sr=None, mono=True)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    return int(round(float(np.asarray(tempo).squeeze())))


def get_key_from_wav(wav_path) -> dict:
    y, sr = librosa.load(wav_path, sr=None, mono=True)
    return key_find_algorithm(y, sr)


def get_bpm_from_buffer(buf) -> int:
    buf.seek(0)
    y, sr = librosa.load(buf, sr=None)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    return int(round(float(np.asarray(tempo).squeeze())))


def get_key_from_buffer(buf) -> dict:
    buf.seek(0)
    y, sr = librosa.load(buf, sr=None, mono=True)
    return key_find_algorithm(y, sr)


def preprocess_audio(y: np.ndarray, sr: int, trim: bool = True):
    if y.ndim > 1:
        y = librosa.to_mono(y)
    if trim:
        y, _ = librosa.effects.trim(y)
    if len(y) == 0:
        raise ValueError("Audio buffer is empty after preprocessing")
    return y, sr


def compute_chroma_vector(
    y: np.ndarray,
    sr: int,
    segment_seconds: float = 10.0,
    method: str = "cqt",
    hop_length: int = 512,
) -> np.ndarray:
    seg_len = int(segment_seconds * sr)
    num_segments = max(1, len(y) // seg_len)
    chroma_sum = np.zeros(12)

    for i in range(num_segments):
        start = i * seg_len
        end = min(start + seg_len, len(y))
        segment = y[start:end]

        if method == "cqt":
            chroma = librosa.feature.chroma_cqt(y=segment, sr=sr, hop_length=hop_length)
        else:
            raise ValueError("method must be 'cqt' or 'stft'")

        chroma_sum += np.mean(chroma, axis=1)

    chroma_vec = chroma_sum / num_segments
    norm = np.linalg.norm(chroma_vec)
    if norm < 1e-12:
        raise ValueError("Chroma vector is near zero")
    return chroma_vec / norm


def compute_ks_correlations(chroma_vec, major_profile, minor_profile):
    major_scores = []
    minor_scores = []
    for i in range(12):
        major_scores.append(np.corrcoef(chroma_vec, np.roll(np.array(major_profile), i))[0, 1])
        minor_scores.append(np.corrcoef(chroma_vec, np.roll(np.array(minor_profile), i))[0, 1])
    return major_scores, minor_scores


def select_key(major_scores, minor_scores) -> dict:
    major_idx = int(np.argmax(major_scores))
    minor_idx = int(np.argmax(minor_scores))
    if major_scores[major_idx] >= minor_scores[minor_idx]:
        return {"key": CHROMA_LABELS[major_idx], "mode": "Major", "score": float(major_scores[major_idx])}
    return {"key": CHROMA_LABELS[minor_idx], "mode": "Minor", "score": float(minor_scores[minor_idx])}


def build_ranked_results(major_scores, minor_scores, top_n: int = 5) -> list:
    results = []
    for i, s in enumerate(major_scores):
        results.append((CHROMA_LABELS[i], "Major", float(s)))
    for i, s in enumerate(minor_scores):
        results.append((CHROMA_LABELS[i], "Minor", float(s)))
    results.sort(key=lambda x: x[2], reverse=True)
    return results[:top_n]


def key_find_algorithm(y: np.ndarray, sr: int, segment_seconds: float = 10.0) -> dict:
    y, sr = preprocess_audio(y, sr)
    chroma_vec = compute_chroma_vector(y, sr, segment_seconds=segment_seconds)
    major_scores, minor_scores = compute_ks_correlations(chroma_vec, MAJOR_PROFILE, MINOR_PROFILE)
    primary = select_key(major_scores, minor_scores)
    ranked = build_ranked_results(major_scores, minor_scores)
    return {
        "primary_key": primary,
        "ranked_candidates": ranked,
        "major_scores": major_scores,
        "minor_scores": minor_scores,
        "chroma_vector": chroma_vec,
    }
