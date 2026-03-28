// controller.js

import { state } from "./model.js";
import { renderSegments } from "./view.js";
console.log("CONTROLLER JS LOADED");

const API = "http://localhost:8000";

export async function uploadVideo(file) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(API + "/upload", {
    method: "POST",
    body: formData
  });

  const data = await res.json();
  console.log("Upload response:", data);
  state.videoId = data.video_id;
}

export async function transcribe() {
  const res = await fetch(API + "/transcribe/" + state.videoId, {
    method: "POST"
  });

  const data = await res.json();
  state.segments = data.segments;

  renderSegments(state);
}