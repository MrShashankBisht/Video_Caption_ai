# app/utils/helpers.py

from pathlib import Path
from typing import Any
import uuid

from moviepy import VideoFileClip


DEFAULT_SEGMENT_X = 50
DEFAULT_SEGMENT_Y = 80

def format_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def group_words(words, group_size=3):
    return [words[i:i+group_size] for i in range(0, len(words), group_size)]

def generate_id():
    return str(uuid.uuid4())

def _get_video_center(video_path: Path) -> tuple[int, int]:
    with VideoFileClip(str(video_path)) as video:
        width, height = video.size
    return int(width / 2), int(height / 2)

def _format_segments(
    segments: list[dict[str, Any]],
    default_x: int = DEFAULT_SEGMENT_X,
    default_y: int = DEFAULT_SEGMENT_Y,
) -> list[dict[str, Any]]:
    formatted_segments = []
    for seg in segments:
        position_x = seg.get("position_x", seg.get("x", default_x))
        position_y = seg.get("position_y", seg.get("y", default_y))
        formatted_words = []
        for word in seg["words"]:
            word_x = word.get("position_x", word.get("x", position_x))
            word_y = word.get("position_y", word.get("y", position_y))
            formatted_words.append(
                {
                    **word,
                    "x": word_x,
                    "y": word_y,
                    "position_x": word_x,
                    "position_y": word_y,
                }
            )
        formatted_segments.append(
            {
                "start": seg["start"],
                "end": seg["end"],
                "words": formatted_words,
                "x": position_x,
                "y": position_y,
                "position_x": position_x,
                "position_y": position_y,
            }
        )
    return formatted_segments
