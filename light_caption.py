import whisper
import subprocess

video_file = "video.mp4"
audio_file = "audio.wav"

# Step 1 — Extract audio (lightweight)
subprocess.run([
    "ffmpeg",
    "-i", video_file,
    "-ar", "16000",
    "-ac", "1",
    "-c:a", "pcm_s16le",
    audio_file
])

# Step 2 — Load Whisper SMALL (optimized)
model = whisper.load_model("small")

# Step 3 — Transcribe (with timestamps)
result = model.transcribe(
    audio_file,
    word_timestamps=True,
    task="transcribe",
    verbose=False,
    fp16=False
)

segments = result["segments"]

# Step 4 — Convert to SRT
def format_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

with open("subtitles.srt", "w") as f:
    for i, seg in enumerate(segments):
        start = format_time(seg["start"])
        end = format_time(seg["end"])
        text = seg["text"]

        f.write(f"{i+1}\n")
        f.write(f"{start} --> {end}\n")
        f.write(f"{text.strip()}\n\n")

# Step 5 — Burn subtitles into video
subprocess.run([
    "ffmpeg",
    "-i", video_file,
    "-vf", "subtitles=subtitles.srt",
    "-c:a", "copy",
    "output.mp4"
])

print("✅ Done! Check output.mp4")