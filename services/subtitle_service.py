# app/services/subtitle_service.py

from utils.helpers import format_time, group_words

class SubtitleService:

    def generate_srt(self, segments, words_count, output_path="assets/subtitles/subtitles.srt"):
        with open(output_path, "w", encoding="utf-8") as file:
            counter = 1

            for seg in segments:
                words = seg["words"]
                groups = group_words(words, words_count)

                for group in groups:
                    start = group[0]["start"]
                    end = group[-1]["end"]

                    text = " ".join([w["word"] for w in group]).upper()

                    file.write(f"{counter}\n")
                    file.write(f"{format_time(start)} --> {format_time(end)}\n")
                    file.write(f"{text}\n\n")

                    counter += 1

        return output_path