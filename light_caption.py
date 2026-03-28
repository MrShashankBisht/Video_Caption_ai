from moviepy import *
import whisper
import torch
import subprocess

def limit_text(text, max_chars=40):
    return text[:max_chars] + "..." if len(text) > max_chars else text

def group_words(words, group_size=3):
    return [words[i:i+group_size] for i in range(0, len(words), group_size)]

def format_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"



video_file = "video_5_larg_v3.mp4"

# Load video
video = VideoFileClip(video_file)

device = "cuda" if torch.cuda.is_available() else "cpu"

# Load model
try:
    model = whisper.load_model("large-v3", device=device)
except:
    print("⚠️ Falling back to CPU")
    model = whisper.load_model("large-v3", device="cpu")

# extract audio with ffmpeg to ensure compatibility
subprocess.run([
    "ffmpeg",
    "-i", video_file,
    "-ar", "16000",
    "-ac", "1",
    "audio.wav"
])

# Transcribe with word timestamps
result = model.transcribe("audio.wav", task="translate" , language=None, beam_size=5, best_of=1, fp16=(device == "cuda"), verbose=False, temperature=0, word_timestamps=True)

segments = result["segments"]

text_clips = []

# 🎨 CONFIG (FULL CONTROL HERE)
FONT_SIZE = 20
MAIN_COLOR = "white"
HIGHLIGHT_COLOR = "pink"
STROKE_COLOR = "yellow"
POSITION = (100, 100)

with open("subtitles.srt", "w", encoding="utf-8") as file:
    counter = 0 #global subtitle counter
    for seg in segments:
        words = seg["words"]

        groups = group_words(words, group_size=3)
        print(f"Segment from {seg['start']:.2f}s to {seg['end']:.2f}s has {len(words)} words, grouped into {len(groups)} groups")
        
        for group in groups:
            print(f"Processing group of {len(group)} words: {[w['word'] for w in group]} from {group[0]['start']:.2f}s to {group[-1]['end']:.2f}s")
            start = group[0]["start"]
            end = group[-1]["end"]

            text = " ".join([w["word"] for w in group]).upper()
            subtitle_start = format_time(start)
            subtitle_end = format_time(end)
            file.write(f"{counter+1}\n")
            file.write(f"{subtitle_start} --> {subtitle_end}\n")
            file.write(f"{text}\n\n")
            counter += 1

            txt_clip = (
                TextClip(
                    text=text,
                    font_size=FONT_SIZE,
                    color=MAIN_COLOR,
                    stroke_color=STROKE_COLOR,
                    stroke_width=1,
                    method="label",
                    margin=(10, 5)
                )
                .with_start(start)
                .with_end(end)
                .with_position(POSITION)
                .resized(lambda t: 1 + 0.08 * min(t, 0.2))
            )

            print(f"Created text clip for word '{text}' from {start:.2f}s to {end:.2f}s")
            text_clips.append(txt_clip)

print(f"Generated {len(text_clips)} text clips")

# Combine everything
final = CompositeVideoClip([video, *text_clips])

final.write_videofile("reels_output.mp4", fps=24, codec="libx264")