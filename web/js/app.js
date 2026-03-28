// js/app.js

import { state } from "./model.js";
import * as controller from "./controller.js";
import { renderSegments } from "./view.js";

const video = document.getElementById("video");
const subtitle = document.getElementById("subtitle");
console.log("APP JS LOADED");
/* Upload */
document.getElementById("videoUpload").addEventListener("change", async (e) => {
  console.log("Video file selected");
  const file = e.target.files[0];
  video.src = URL.createObjectURL(file);

  await controller.uploadVideo(file);
});

document.getElementById("btnUpload").addEventListener("click", async () => {
  console.log("Uploading video...");
  const fileInput = document.getElementById("videoUpload");
  const file = fileInput.files[0];

  if (!file) {
      alert("Please select a file");
      return;
  }

  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch("http://localhost:8000/upload", {
      method: "POST",
      body: formData
  });

  const result = await response.json();
  console.log(result);
  alert("Upload success!");

});

/* Transcribe */
document.getElementById("btnTranscribe").addEventListener("click", async () => {
  await controller.transcribe();
  renderSegments(state);
});

/* Render */
document.getElementById("btnRender").addEventListener("click", async () => {
  await controller.renderVideo();
});

/* Subtitle Preview */
video.addEventListener("timeupdate", () => {
  const t = video.currentTime;

  const seg = state.segments.find(s => t >= s.start && t <= s.end);

  if (seg) {
    subtitle.style.display = "block";
    subtitle.innerText = seg.words.map(w => w.word).join(" ");
    subtitle.style.left = seg.x + "px";
    subtitle.style.top = seg.y + "px";
  } else {
    subtitle.style.display = "none";
  }
});

/* Drag Subtitle */
let dragging = false;

subtitle.addEventListener("mousedown", () => {
  dragging = true;
});

document.addEventListener("mouseup", () => {
  dragging = false;
});

document.addEventListener("mousemove", (e) => {
  if (!dragging || state.activeIndex === null) return;

  const rect = video.getBoundingClientRect();

  const scaleX = video.videoWidth / rect.width;
  const scaleY = video.videoHeight / rect.height;

  const x = (e.clientX - rect.left) * scaleX;
  const y = (e.clientY - rect.top) * scaleY;

  state.segments[state.activeIndex].x = Math.round(x);
  state.segments[state.activeIndex].y = Math.round(y);

  subtitle.style.left = x + "px";
  subtitle.style.top = y + "px";
});