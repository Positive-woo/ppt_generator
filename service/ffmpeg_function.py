from io import BytesIO
import matplotlib.pyplot as plt
import subprocess
import librosa
import numpy as np

MAJOR_PROFILE = np.array(
    [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
)

MINOR_PROFILE = np.array(
    [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
)

CHROMA_LABELS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def extract_video_id(url: str) -> str | None:
    if "v=" in url:
        return url.split("v=")[-1].split("&")[0]
    if "youtu.be/" in url:
        return url.split("youtu.be/")[-1].split("?")[0]
    return None


def download_wav_to_memory(url: str) -> BytesIO:
    ytdlp = [
        "yt-dlp",
        "-f",
        "bestaudio",
        "-o",
        "-",
        url,
    ]

    ffmpeg = [
        "ffmpeg",
        "-i",
        "pipe:0",
        "-t",
        "30",
        "-f",
        "mp3",
        "pipe:1",
    ]

    ytdlp_proc = subprocess.Popen(
        ytdlp,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )

    ffmpeg_proc = subprocess.Popen(
        ffmpeg,
        stdin=ytdlp_proc.stdout,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )

    audio_bytes = ffmpeg_proc.stdout.read()
    return BytesIO(audio_bytes)


def get_bpm_from_buffer(buf) -> int:
    buf.seek(0)
    y, sr = librosa.load(buf, sr=None)

    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

    tempo = float(np.asarray(tempo).squeeze())
    return int(round(tempo))


def get_key_from_buffer(buf: BytesIO) -> str:
    buf.seek(0)
    y, sr = librosa.load(buf, sr=None, mono=True)
    res = key_find_algorithm(y, sr)
    return res


def preprocess_audio(y: np.ndarray, sr: int, trim: bool = True) -> np.ndarray:
    if y.ndim > 1:
        y = librosa.to_mono(y)

    if trim:
        y, _ = librosa.effects.trim(y)

    if len(y) == 0:
        raise ValueError("Audio buffer is empty after preprocessing")

    return y


def compute_chroma_vector(
    y: np.ndarray,
    sr: int,
    segment_seconds: float = 10.0,
    method: str = "cqt",
    hop_length: int = 512,
) -> np.ndarray:
    seg_len = int(sr * segment_seconds)
    num_segments = max(1, len(y) // seg_len)

    chroma_sum = np.zeros(12)

    for i in range(num_segments):
        start = i * seg_len
        end = min(len(y), (i + 1) * seg_len)
        segment = y[start:end]

        if method == "cqt":
            chroma = librosa.feature.chroma_cqt(y=segment, sr=sr, hop_length=hop_length)
        else:
            raise ValueError("method must be 'cqt' or 'stft'")

        chroma_sum += np.mean(chroma, axis=1)

    chroma_vec = chroma_sum / num_segments

    # L2 normalize
    norm = np.linalg.norm(chroma_vec)
    if norm < 1e-12:
        raise ValueError("Chroma vector is near zero")

    return chroma_vec / norm


def compute_ks_correlations(
    chroma_vec: np.ndarray,
    major_profile: np.ndarray = MAJOR_PROFILE,
    minor_profile: np.ndarray = MINOR_PROFILE,
):
    major_scores = []
    minor_scores = []

    for i in range(12):
        major_scores.append(np.corrcoef(np.roll(major_profile, i), chroma_vec)[0, 1])
        minor_scores.append(np.corrcoef(np.roll(minor_profile, i), chroma_vec)[0, 1])

    return np.array(major_scores), np.array(minor_scores)


def select_key(major_scores: np.ndarray, minor_scores: np.ndarray):
    major_idx = int(np.argmax(major_scores))
    minor_idx = int(np.argmax(minor_scores))

    if major_scores[major_idx] >= minor_scores[minor_idx]:
        return {
            "key": CHROMA_LABELS[major_idx],
            "mode": "Major",
            "score": float(major_scores[major_idx]),
        }
    else:
        return {
            "key": CHROMA_LABELS[minor_idx],
            "mode": "Minor",
            "score": float(minor_scores[minor_idx]),
        }


def build_ranked_results(
    major_scores: np.ndarray, minor_scores: np.ndarray, top_n: int = 5
):
    results = []

    for i, s in enumerate(major_scores):
        results.append((CHROMA_LABELS[i], "Major", float(s)))

    for i, s in enumerate(minor_scores):
        results.append((CHROMA_LABELS[i], "Minor", float(s)))

    results.sort(key=lambda x: x[2], reverse=True)
    return results[:top_n]


def key_find_algorithm(y: np.ndarray, sr: int, segment_seconds: float = 10.0):
    y = preprocess_audio(y, sr)

    chroma_vec = compute_chroma_vector(y, sr, segment_seconds=segment_seconds)

    major_scores, minor_scores = compute_ks_correlations(chroma_vec)

    primary = select_key(major_scores, minor_scores)
    ranked = build_ranked_results(major_scores, minor_scores)

    return {
        "primary_key": primary,  # key, mode, score
        "ranked_candidates": ranked,  # top-N with scores
        "major_scores": major_scores,
        "minor_scores": minor_scores,
        "chroma_vector": chroma_vec,
    }
