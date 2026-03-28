# app/routes/video_routes.py

import json

from fastapi import APIRouter, Body, File, Form, HTTPException, UploadFile, status
import shutil
from pathlib import Path
from typing import Any

from moviepy import VideoFileClip
from utils.helpers import generate_id

from models.schemas import (
    GenerateSrtResponse,
    RenderRequest,
    RenderResponse,
    TranscriptionResponse,
    UploadResponse,
)
from services.whisper_service import WhisperService
from services.subtitle_service import SubtitleService
from services.video_service import VideoService

router = APIRouter(tags=["Video Processing"])

whisper_service = WhisperService()
subtitle_service = SubtitleService()
video_service = VideoService()

BASE_DIR = Path("storage")


def _video_folder(video_id: str) -> Path:
    return BASE_DIR / video_id


def _input_video_path(video_id: str) -> Path:
    return _video_folder(video_id) / "input.mp4"


def _ensure_video_exists(video_id: str) -> Path:
    video_path = _input_video_path(video_id)
    if not video_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video '{video_id}' was not found.",
        )
    return video_path


def _save_upload_file(file: UploadFile, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        with destination.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

def _parse_render_config(config: Any) -> RenderRequest:
    if isinstance(config, str):
        try:
            config = json.loads(config)
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Render config must be valid JSON.",
            ) from exc

    if not isinstance(config, dict):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Render config must be a JSON object.",
        )

    try:
        return RenderRequest(**config)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid render config: {exc}",
        ) from exc


def _parse_transcribe_payload(transcribe: Any) -> list[dict[str, Any]] | None:
    if transcribe in (None, "", []):
        return None

    if isinstance(transcribe, str):
        try:
            transcribe = json.loads(transcribe)
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="transcribe must be valid JSON.",
            ) from exc

    if not isinstance(transcribe, list):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="transcribe must be a JSON array of segments.",
        )

    return transcribe

@router.post(
    "/upload",
    response_model=UploadResponse,
    summary="Upload a video",
    description="Uploads a video file and stores it under a generated `video_id` in the storage directory.",
)
async def upload_video(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A video file is required.",
        )

    video_id = generate_id()
    video_path = _input_video_path(video_id)
    _save_upload_file(file, video_path)

    return {"video_id": video_id, "path": str(video_path)}


@router.post(
    "/transcribe/{video_id}",
    response_model=TranscriptionResponse,
    summary="Transcribe a video",
    description="Extracts audio from the uploaded video, runs Whisper transcription, and returns formatted subtitle segments with centered default positions.",
)
async def transcribe_video(video_id: str):
    video_path = _ensure_video_exists(video_id)
    segments = whisper_service.transcribe(video_id, str(video_path))
    return {"segments": segments}
    

    # 👇 Send editable format to frontend
@router.post(
    "/generate-srt",
    response_model=GenerateSrtResponse,
    summary="Generate an SRT file",
    description="Uploads a video, transcribes it, groups words into subtitle chunks, and writes an `.srt` file to storage.",
)
async def generate_srt(
    file: UploadFile = File(...),
    words_count: int = Form(3),
    transcribe: str | None = Form(None),
):
    if words_count < 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="words_count must be at least 1.",
        )
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A video file is required.",
        )

    video_id = generate_id()
    video_path = _input_video_path(video_id)
    srt_path = _video_folder(video_id) / "subtitles.srt"

    _save_upload_file(file, video_path)
    segments = _parse_transcribe_payload(transcribe) or whisper_service.transcribe(video_id, str(video_path))
    subtitle_service.generate_srt(segments, words_count, output_path=str(srt_path))

    return {"video_id": video_id, "srt": str(srt_path)}


@router.post(
    "/render/{video_id}",
    response_model=RenderResponse,
    summary="Render subtitled video",
    description="Renders a final output video using either edited subtitle segments from the request or a fresh transcription from Whisper.",
)
async def render_video(video_id: str, config: Any = Body(...)):
    config_data = _parse_render_config(config)
    video_path = _ensure_video_exists(video_id)
    output_path = _video_folder(video_id) / "output.mp4"

    segments = config_data.transcribe or config_data.segments or whisper_service.transcribe(video_id, str(video_path))
    video_service.render_video(
        str(video_path),
        segments,
        config_data,
        str(output_path),
    )

    return {"video_id": video_id, "output_video": str(output_path)}
    

    # if frontend already edited segments → use them
