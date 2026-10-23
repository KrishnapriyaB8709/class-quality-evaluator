"""
Autonomous Audio Transcription Module
Extracts audio from video files using ffmpeg and transcribes speech to timestamped dialogue using Whisper.
Optimized for resilience, portable ffmpeg discovery, and Grok LPU acceleration.
"""

import os
import shutil
import subprocess
import whisper
from typing import Optional, List

FFMPEG_DEFAULT_PATH = r"C:\Users\KrishnapriyaB\Downloads\ffmpeg-8.0.1-essentials_build\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe"

def get_ffmpeg_cmd() -> str:
    """Finds ffmpeg executable from system PATH or local download."""
    found = shutil.which("ffmpeg")
    if found:
        return found
    if os.path.exists(FFMPEG_DEFAULT_PATH):
        return FFMPEG_DEFAULT_PATH
    return "ffmpeg"

def format_timestamp(seconds: float) -> str:
    """Formats seconds to [HH:MM:SS]."""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"[{hrs:02d}:{mins:02d}:{secs:02d}]"

def extract_and_transcribe_video(
    video_path: str,
    max_duration_seconds: Optional[int] = None,
    model_size: str = "tiny"
) -> str:
    """
    Extracts audio from any uploaded video file and transcribes dialogue
    into timestamped classroom cues: [HH:MM:SS] Speaker: dialogue.
    Works with Grok Whisper (large-v3-turbo) and local Whisper fallback.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    # Unique per-execution audio file to prevent concurrent collisions
    import uuid
    session_id = uuid.uuid4().hex[:8]
    temp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(temp_dir, exist_ok=True)
    audio_path = os.path.join(temp_dir, f"audio_{session_id}.mp3")

    try:
        # Extract 16kHz mono audio via ffmpeg compressed to 32kbps MP3
        ffmpeg_bin = get_ffmpeg_cmd()
        cmd = [
            ffmpeg_bin, "-y",
            "-i", video_path,
            "-vn",
            "-ac", "1",
            "-ar", "16000",
            "-c:a", "libmp3lame",
            "-b:a", "32k"
        ]
        if max_duration_seconds and max_duration_seconds > 0:
            cmd.extend(["-t", str(max_duration_seconds)])
        cmd.append(audio_path)

        try:
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, timeout=300)
        except subprocess.TimeoutExpired:
            raise RuntimeError("FFmpeg audio extraction timed out after 300 seconds.")
        except Exception as e:
            raise RuntimeError(f"FFmpeg audio extraction failed: {e}")

        # Guard: Check file existence and size limit (Groq API max 25MB)
        if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
            raise RuntimeError("FFmpeg completed but extracted audio file is missing or empty.")
            
        file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)

        # Try ultra-fast transcription via GROK_API_KEY (Whisper Large v3 Turbo)
        grok_key = os.getenv("GROK_API_KEY")
        if grok_key and file_size_mb <= 25.0:
            try:
                from groq import Groq
                client = Groq(api_key=grok_key)
                with open(audio_path, "rb") as f:
                    tr = client.audio.transcriptions.create(
                        file=f,
                        model="whisper-large-v3-turbo",
                        response_format="verbose_json"
                    )
                lines = []
                segments = getattr(tr, "segments", []) or []
                for seg in segments:
                    start_sec = seg.get("start", 0) if isinstance(seg, dict) else getattr(seg, "start", 0)
                    text = (seg.get("text", "") if isinstance(seg, dict) else getattr(seg, "text", "")).strip()
                    if text:
                        lines.append(f"{format_timestamp(start_sec)} Speaker: {text}")
                if lines:
                    return "\n".join(clean_whisper_hallucinations(lines))
                elif getattr(tr, "text", None):
                    return f"[00:00:00] Speaker: {tr.text.strip()}"
            except Exception as e:
                print(f"Notice: Groq Whisper transcription notice: {e}. Falling back to local Whisper.")

        # Offline local Whisper fallback
        model = whisper.load_model(model_size)
        result = model.transcribe(audio_path)

        lines = []
        for seg in result.get("segments", []):
            ts = format_timestamp(seg["start"])
            text = seg["text"].strip()
            if text:
                lines.append(f"{ts} Speaker: {text}")

        if not lines and result.get("text"):
            return f"[00:00:00] Speaker: {result['text'].strip()}"

        return "\n".join(clean_whisper_hallucinations(lines))
    finally:
        # Guarantee disk cleanup of the temporary audio file
        if os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except OSError:
                pass

def clean_whisper_hallucinations(lines: List[str]) -> List[str]:
    """
    Filters out consecutive identical filler lines (e.g., repeated 'Thank you.'
    generated by Whisper during pre-class silence or unmuted dead air).
    """
    cleaned = []
    last_content = None
    repeat_count = 0

    for line in lines:
        parts = line.split("Speaker:", 1)
        content = parts[1].strip() if len(parts) == 2 else line.strip()
        norm = content.strip(" .,!?:;'\"").lower()

        is_filler = norm in {
            "thank you", "thanks for watching", "you", "bye", 
            "subtitles by", "subtitle", "subscribe", "like and subscribe"
        }

        if norm == last_content:
            repeat_count += 1
            if is_filler or repeat_count > 1:
                continue
        else:
            last_content = norm
            repeat_count = 0

        cleaned.append(line)

    return cleaned
