from __future__ import annotations

import json
import mimetypes
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".opus", ".aac", ".wma", ".webm"}


def require_binary(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise RuntimeError(f"Required binary not found: {name}. Install ffmpeg and ensure it is on PATH.")
    return path


def get_mime_type(file_path: str | Path) -> str:
    mime, _ = mimetypes.guess_type(str(file_path))
    return mime or "application/octet-stream"


def get_file_format(file_path: str | Path) -> str:
    return Path(file_path).suffix.lstrip(".").lower()


def detect_media_type(file_path: str | Path) -> str:
    path = Path(file_path)
    mime = get_mime_type(path)
    if mime.startswith("image/"):
        return "image"
    if mime.startswith("audio/"):
        return "audio"
    if mime.startswith("video/"):
        return "video"
    ext = path.suffix.lower()
    if ext in AUDIO_EXTENSIONS:
        return "audio"
    if ext in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff", ".svg"}:
        return "image"
    if ext in {".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".m4v", ".3gp"}:
        return "video"
    return "unknown"


def ffprobe_info(file_path: str | Path) -> dict:
    require_binary("ffprobe")
    proc = subprocess.run(
        [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            str(file_path),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "ffprobe failed")
    return json.loads(proc.stdout or "{}")


def audio_duration_seconds(file_path: str | Path) -> float:
    try:
        info = ffprobe_info(file_path)
        return float(info.get("format", {}).get("duration") or 0)
    except Exception:
        return 0.0


def format_duration(seconds: float) -> str:
    total = max(0, int(round(seconds)))
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}小时{m}分{s}秒"
    return f"{m}分{s}秒"


def ensure_mp3_or_wav(audio_path: str | Path, output_dir: str | Path | None = None) -> Path:
    """Return original path for mp3/wav, otherwise convert a sibling copy to mp3."""
    path = Path(audio_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Audio file not found: {path}")
    if path.suffix.lower() in {".mp3", ".wav"}:
        return path
    require_binary("ffmpeg")
    out_dir = Path(output_dir).expanduser().resolve() if output_dir else path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{path.stem}_converted.mp3"
    proc = subprocess.run(
        [
            "ffmpeg",
            "-nostdin",
            "-y",
            "-i",
            str(path),
            "-acodec",
            "libmp3lame",
            "-b:a",
            "128k",
            str(out_path),
        ],
        capture_output=True,
        text=True,
        stdin=subprocess.DEVNULL,
        timeout=1800,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg convert failed: {(proc.stderr or proc.stdout)[-1000:]}")
    return out_path


def split_audio(audio_path: str | Path, segment_seconds: int, timeout: float) -> tuple[Path, list[Path]]:
    require_binary("ffmpeg")
    path = Path(audio_path).expanduser().resolve()
    tmpdir = Path(tempfile.mkdtemp(prefix="audio_transcribe_llm_"))
    output_pattern = tmpdir / "segment_%04d.mp3"
    proc = subprocess.run(
        [
            "ffmpeg",
            "-nostdin",
            "-y",
            "-i",
            str(path),
            "-f",
            "segment",
            "-segment_time",
            str(segment_seconds),
            "-c:a",
            "libmp3lame",
            "-b:a",
            "128k",
            str(output_pattern),
        ],
        capture_output=True,
        text=True,
        stdin=subprocess.DEVNULL,
        timeout=timeout,
    )
    if proc.returncode != 0:
        shutil.rmtree(tmpdir, ignore_errors=True)
        raise RuntimeError(f"ffmpeg split failed: {(proc.stderr or proc.stdout)[-1000:]}")
    segments = sorted(tmpdir.glob("segment_*.mp3"))
    if not segments:
        shutil.rmtree(tmpdir, ignore_errors=True)
        raise RuntimeError("ffmpeg produced no audio segments")
    return tmpdir, segments


def remove_tree(path: str | Path) -> None:
    shutil.rmtree(path, ignore_errors=True)

