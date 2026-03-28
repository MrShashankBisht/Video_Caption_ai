# CaptionAI API Documentation

## Overview

CaptionAI exposes a small FastAPI-based API for:

- uploading videos
- transcribing speech into timestamped segments
- generating `.srt` subtitle files
- rendering output videos with subtitles

Interactive documentation is available when the app is running:

- Swagger UI: `/docs`
- ReDoc: `/redoc`

## Best Practice

For FastAPI projects, the most practical API documentation setup is:

- define request and response models with Pydantic
- add `summary`, `description`, and tags to every endpoint
- keep interactive OpenAPI docs enabled
- maintain one short human-readable markdown file with examples
- version the API and update docs together with code changes

That setup is now in place in this project.

## Endpoints

### `POST /upload`

Uploads a video file and stores it in `storage/{video_id}/input.mp4`.

Response:

```json
{
  "video_id": "uuid-string",
  "path": "storage/uuid-string/input.mp4"
}
```

### `POST /transcribe/{video_id}`

Transcribes an uploaded video and returns formatted subtitle segments.

Response:

```json
{
  "segments": [
    {
      "start": 0.0,
      "end": 1.2,
      "words": [],
      "x": 640,
      "y": 360,
      "position_x": 640,
      "position_y": 360
    }
  ]
}
```

### `POST /generate-srt`

Uploads a video, transcribes it, and generates an SRT subtitle file.

Form fields:

- `file`: video file
- `words_count`: words per subtitle group

Response:

```json
{
  "video_id": "uuid-string",
  "srt": "storage/uuid-string/subtitles.srt"
}
```

### `POST /render/{video_id}`

Renders a subtitled output video using the render configuration.

Request body:

```json
{
  "word_group_size": 3,
  "style": {
    "font_size": 20,
    "color": "white",
    "stroke_color": "yellow",
    "stroke_width": 3
  },
  "default_position": {
    "x": 640,
    "y": 360
  },
  "segments": null
}
```

Response:

```json
{
  "video_id": "uuid-string",
  "output_video": "storage/uuid-string/output.mp4"
}
```
