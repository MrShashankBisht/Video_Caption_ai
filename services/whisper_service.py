# app/services/whisper_service.py

import json
import subprocess
from pathlib import Path

import torch
import whisper

from utils.helpers import _format_segments, _get_video_center


class WhisperService:
    def __init__(self):
        print("[WhisperService] Initializing service...")
        cuda_available = torch.cuda.is_available()
        print(f"[WhisperService] torch.cuda.is_available(): {cuda_available}")

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[WhisperService] Preferred device: {self.device}")

        try:
            print(f"[WhisperService] Loading Whisper model 'small' on {self.device}...")
            self.model = whisper.load_model("small", device=self.device)
            print(f"[WhisperService] Model loaded successfully on {self.device}.")
        except Exception as exc:
            print(f"[WhisperService] Failed to load model on {self.device}: {exc}")
            print("[WhisperService] Falling back to CPU...")
            self.model = whisper.load_model("small", device="cpu")
            self.device = "cpu"
            print("[WhisperService] Model loaded successfully on cpu.")

    def extract_audio(self, video_path, audio_path="assets/audios/audio.wav"):
        print(f"[WhisperService] Starting audio extraction from: {video_path}")
        print(f"[WhisperService] Target audio path: {audio_path}")

        audio_dir = Path(audio_path).parent
        print(f"[WhisperService] Ensuring audio directory exists: {audio_dir}")
        audio_dir.mkdir(parents=True, exist_ok=True)

        command = [
            "ffmpeg", "-i", video_path,
            "-ar", "16000",
            "-ac", "1",
            audio_path
        ]
        print(f"[WhisperService] Running ffmpeg command: {' '.join(command)}")
        subprocess.run(command, check=True)
        print(f"[WhisperService] Audio extraction completed: {audio_path}")
        return audio_path

    def save_transcription(self, video_id: str, result: dict):
        print(f"[WhisperService] Saving transcription for video_id: {video_id}")
        output_dir = Path("storage") / video_id
        print(f"[WhisperService] Ensuring transcription directory exists: {output_dir}")
        output_dir.mkdir(parents=True, exist_ok=True)

        transcript_path = output_dir / "transcription.json"
        print(f"[WhisperService] Writing transcription file: {transcript_path}")
        with transcript_path.open("w", encoding="utf-8") as file:
            json.dump(result, file, ensure_ascii=False, indent=2)

        print(f"[WhisperService] Transcription saved successfully: {transcript_path}")
        return str(transcript_path)

    def transcribe(self, video_id: str, video_path: str):
        print(f"[WhisperService] Starting transcription pipeline for video_id: {video_id}")
        print(f"[WhisperService] Using device: {self.device}")
        print(f"[WhisperService] Source video path: {video_path}")

        audio_path = self.extract_audio(video_path, audio_path=f"storage/{video_id}/audio.wav")
        print(f"[WhisperService] Audio ready for transcription: {audio_path}")
        print("[WhisperService] Calling Whisper model.transcribe()...")
        result = self.model.transcribe(
            audio_path,
            beam_size=5,
            best_of=1,
            temperature=0,
            word_timestamps=True
        )

        default_x, default_y = _get_video_center(video_path)
        segments = _format_segments(result["segments"], default_x, default_y)

        print("[WhisperService] Transcription completed successfully.")
        print(f"[WhisperService] Number of segments produced: {len(segments)}")

        saved_path = self.save_transcription(video_id, segments)
        print(f"[WhisperService] Transcription artifact stored at: {saved_path}")

        print(f"[WhisperService] Returning segments for video_id: {video_id}")
        return segments
