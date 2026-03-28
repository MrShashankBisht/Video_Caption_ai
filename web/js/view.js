// view.js
console.log("view JS LOADED");
export function renderSegments(state) {
  const container = document.getElementById("transcriptList");
  container.innerHTML = "";

  state.segments.forEach((seg, i) => {
    const div = document.createElement("div");

    div.innerText = seg.words.map(w => w.word).join(" ");
    div.onclick = () => {
      state.activeIndex = i;
    };

    container.appendChild(div);
  });
}