/* Original-image reader with semantic identity and reversible native navigation. */
const pages = [...document.querySelectorAll(".visual-page")];
const frame = document.getElementById("visual-book");
const previous = document.getElementById("visual-previous");
const next = document.getElementById("visual-next");
const progress = document.querySelector(".visual-track");
const progressFill = document.querySelector(".visual-progress-fill");
const status = document.getElementById("visual-status");
const back = document.querySelector(".visual-return");
const count = pages.length;
if (count === 0 || count !== Number(document.body.dataset.pageCount)) {
  throw new Error("Source-declared plate count mismatch");
}
const numberFromLocation = () => {
  if (!location.hash) return 1;
  const matched = /^#plate-([1-9][0-9]*)$/.exec(location.hash);
  if (!matched) return null;
  const number = Number(matched[1]);
  return number <= count ? number : null;
};
let current = null;
const render = () => {
  const page = numberFromLocation();
  current = page;
  frame.dataset.invalid = page === null ? "true" : "false";
  pages.forEach((item, index) => { item.hidden = index + 1 !== page; });
  previous.disabled = page === null || page === 1;
  next.disabled = page === null || page === count;
  progress.setAttribute("aria-valuenow", String(page || 1));
  progressFill.style.transform = "scaleX(" + (page ? page / count : 0) + ")";
  status.textContent = page === null ? "Unrecognized illustration address" :
    "Original illustration " + page + " of " + count;
};
const show = (page) => {
  if (current === null || page < 1 || page > count || page === current) return;
  history.pushState({ visualPlate: page }, "",
                    location.pathname + location.search + "#plate-" + page);
  render();
};
previous.addEventListener("click", () => show(current - 1));
next.addEventListener("click", () => show(current + 1));
addEventListener("popstate", render);
addEventListener("hashchange", render);
addEventListener("keydown", (event) => {
  if (event.defaultPrevented || event.altKey || event.metaKey || event.ctrlKey ||
      /^(INPUT|TEXTAREA|SELECT)$/.test(event.target?.tagName || "")) return;
  if (event.key === "ArrowRight") { event.preventDefault(); show(current + 1); }
  if (event.key === "ArrowLeft") { event.preventDefault(); show(current - 1); }
  if (event.key === "Escape") { event.preventDefault(); location.assign(back.href); }
});
let gesture = null;
frame.addEventListener("pointerdown", (event) => {
  if (!event.isPrimary) return;
  gesture = { x: event.clientX, y: event.clientY, pointer: event.pointerId };
});
frame.addEventListener("pointerup", (event) => {
  if (!gesture || gesture.pointer !== event.pointerId) return;
  const dx = event.clientX - gesture.x, dy = event.clientY - gesture.y;
  gesture = null;
  if (Math.abs(dx) >= 48 && Math.abs(dx) > 1.3 * Math.abs(dy)) {
    show(current + (dx < 0 ? 1 : -1));
  }
});
frame.addEventListener("pointercancel", () => { gesture = null; });
render();
