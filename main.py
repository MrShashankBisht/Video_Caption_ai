# app/main.py

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from routes.video_routes import BASE_DIR, router
import os
import mimetypes
from fastapi.middleware.cors import CORSMiddleware

API_DESCRIPTION = """
BishtAI provides APIs to upload videos, transcribe speech with Whisper, generate subtitle files, and render videos with styled captions.

Documentation best practice:
- keep request and response schemas explicit
- add summaries and descriptions to each endpoint
- group endpoints with tags
- publish both interactive docs and a short human-readable guide
"""

app = FastAPI(
    title="Bisht API",
    description=API_DESCRIPTION,
    version="1.0.0",
    summary="Video upload, transcription, subtitle generation, and rendering APIs.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Video Processing",
            "description": "Endpoints for uploading videos, transcribing audio, generating subtitle files, and rendering subtitled output videos.",
        }
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


mimetypes.add_type("application/javascript", ".js")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Serve static files
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "web")),
    name="static"
)

# Serve index.html
@app.get(
    "/",
    include_in_schema=False,
)
def home():
    return FileResponse(os.path.join(BASE_DIR, "web", "index.html"))

app.include_router(router)
