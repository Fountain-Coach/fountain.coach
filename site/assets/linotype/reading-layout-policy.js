/* Shared device-responsive reading policy for the editable Linotype reader
   and the accepted Fountain Press proof. No viewport-width magic number near
   an iPad landscape breakpoint: two pages fit if orientation and physical
   usable page width allow them. Never rely on user-agent sniffing. */
(() => {
"use strict";
function mode(width,height) {
  const w=Number(width),h=Number(height);
  if(!Number.isFinite(w)||!Number.isFinite(h)||w<=0||h<=0)return "single";
  // Minimum useful single leaf for a readable side-by-side A-series proof.
  // Keeping the thresholds far below full-screen iPad landscape sizes means
  // showing/hiding Safari bars does not change the reading mode.
  const gutter=Math.min(24,Math.max(12,w*.017));
  const leaf=(w-gutter-36)/2;
  return w>=900 && h>=500 && w/h>=1.12 && leaf>=380
    ? "spread" : "single";
}
window.FountainReadingLayout=Object.freeze({mode});
})();