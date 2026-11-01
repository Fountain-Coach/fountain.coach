/* Vergil's source-bound reading: one persistent transport, one paginated work.
   Never clone audio into measured Linotype leaves. No autoplay or text duplication. */
(() => {
  const start = () => {
    const audio = document.getElementById("teatro-reading-audio");
    const button = document.getElementById("teatro-reading-toggle");
    const seek = document.getElementById("teatro-reading-seek");
    const elapsed = document.getElementById("teatro-reading-time");
    const status = document.getElementById("teatro-reading-status");
    if (!audio || !button || !seek || !elapsed || !status) return;

    const format = (seconds) => {
      const safe = Number.isFinite(seconds) ? Math.max(0, Math.floor(seconds)) : 0;
      return String(Math.floor(safe / 60)) + ":" + String(safe % 60).padStart(2, "0");
    };
    const display = () => {
      const duration = audio.duration;
      const available = Number.isFinite(duration) && duration > 0;
      seek.disabled = !available;
      seek.value = available ? String(Math.round(1000 * audio.currentTime / duration)) : "0";
      elapsed.textContent = format(audio.currentTime) + " / " + (available ? format(duration) : "8:19");
      button.setAttribute("aria-pressed", String(!audio.paused && !audio.ended));
      button.textContent = audio.paused || audio.ended ? "Read aloud" : "Pause reading";
      button.setAttribute("aria-label", audio.paused || audio.ended ?
        "Play Vergil's reading of Teatro" : "Pause Vergil's reading of Teatro");
    };
    button.addEventListener("click", async () => {
      if (!audio.paused && !audio.ended) {
        audio.pause();
      } else {
        try {
          if (audio.ended) audio.currentTime = 0;
          await audio.play();
          status.textContent = "";
        } catch {
          status.textContent = "Audio could not start. Verify the private staging connection.";
        }
      }
      display();
    });
    seek.addEventListener("input", () => {
      if (!Number.isFinite(audio.duration) || audio.duration <= 0) return;
      audio.currentTime = (Number(seek.value) / 1000) * audio.duration;
      display();
    });
    // Arrow keys change the focused audio seek position, not the book page.
    seek.addEventListener("keydown", event => event.stopPropagation());
    for (const name of ["loadedmetadata", "timeupdate", "play", "pause", "ended",
                         "durationchange", "seeking", "seeked"]) {
      audio.addEventListener(name, display);
    }
    audio.addEventListener("error", () => {
      status.textContent = "The private Vergil recording is unavailable.";
      display();
    });
    display();
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start, {once: true});
  else start();
})();
