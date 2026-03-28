# app/services/video_service.py

from moviepy import VideoFileClip, TextClip, CompositeVideoClip
from utils.helpers import group_words

class VideoService:

    def render_video(self, video_path, segments, config, output_path="output.mp4"):
        video = VideoFileClip(video_path)
        text_clips = []

        group_size = config.word_group_size
        style = config.style
        default_pos = config.default_position

        for seg in segments:
            words = seg["words"]
            groups = group_words(words, group_size)

            for group in groups:
                start = group[0]["start"]
                end = group[-1]["end"]

                text = " ".join([w["word"] for w in group]).upper()

                # Prefer word-level positions when individual words were edited.
                first_word = group[0]
                pos_x = first_word.get("position_x", first_word.get("x", seg.get("x", default_pos.x)))
                pos_y = first_word.get("position_y", first_word.get("y", seg.get("y", default_pos.y)))

                txt_clip = (
                    TextClip(
                        text=text,
                        font_size=style.font_size,
                        color=style.color,
                        stroke_color=style.stroke_color,
                        stroke_width=style.stroke_width
                    )
                    .with_start(start)
                    .with_end(end)
                    .with_position((pos_x, pos_y))  # 🔥 pixel-based
                )

                text_clips.append(txt_clip)

        final = CompositeVideoClip([video, *text_clips])
        final.write_videofile(output_path, fps=24, codec="libx264")

        return output_path
