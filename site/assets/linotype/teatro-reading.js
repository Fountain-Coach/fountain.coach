/* Vergil's source-bound reading stays in the persistent Linotype book frame.
   The WLAN preview does not implement HTTP byte ranges. Buffer this small
   source-bound MP3 once as an object URL so browser-native seeking works. */
(() => {
  const start = () => {
    const audio = document.getElementById("teatro-reading-audio");
    const button = document.getElementById("teatro-reading-toggle");
    const seek = document.getElementById("teatro-reading-seek");
    const elapsed = document.getElementById("teatro-reading-time");
    const status = document.getElementById("teatro-reading-status");
    if (!audio || !button || !seek || !elapsed || !status) return;

    const source = audio.dataset.src;
    if (!source || audio.hasAttribute("src")) return;
    let prepared = false;
    let bufferedURL = null;
    button.disabled = true;
    button.textContent = "Loading…";
    const format = (seconds) => {
      const safe = Number.isFinite(seconds) ? Math.max(0, Math.floor(seconds)) : 0;
      return String(Math.floor(safe / 60)) + ":" + String(safe % 60).padStart(2, "0");
    };
    const display = () => {
      const duration = audio.duration;
      const available = Number.isFinite(duration) && duration > 0;
      const seekable = available && audio.seekable.length > 0 &&
        audio.seekable.end(audio.seekable.length - 1) >= duration - 0.2;
      seek.disabled = !prepared || !seekable;
      seek.value = available ? String(Math.round(1000 * audio.currentTime / duration)) : "0";
      elapsed.textContent = format(audio.currentTime) + " / " + (available ? format(duration) : "8:19");
      button.setAttribute("aria-pressed", String(!audio.paused && !audio.ended));
      if (prepared) {
        button.textContent = audio.paused || audio.ended ? "Read aloud" : "Pause reading";
        button.setAttribute("aria-label", audio.paused || audio.ended ?
          "Play Vergil's reading of Teatro" : "Pause Vergil's reading of Teatro");
      }
    };
    button.addEventListener("click", async () => {
      if (!prepared) return;
      if (!audio.paused && !audio.ended) audio.pause();
      else {
        try {
          if (audio.ended) audio.currentTime = 0;
          await audio.play();
          status.textContent = "";
        } catch {
          status.textContent = "Audio could not start. Check the private staging connection.";
        }
      }
      display();
    });
    seek.addEventListener("input", () => {
      if (seek.disabled || !Number.isFinite(audio.duration) || audio.duration <= 0) return;
      audio.currentTime = (Number(seek.value) / 1000) * audio.duration;
      display();
    });
    seek.addEventListener("keydown", event => event.stopPropagation());
    for (const name of ["loadedmetadata", "timeupdate", "play", "pause", "ended",
                         "durationchange", "seeking", "seeked", "canplay"]) {
      audio.addEventListener(name, display);
    }
    audio.addEventListener("error", () => {
      status.textContent = "The private Vergil recording is unavailable.";
      display();
    });
    const prepare = async () => {
      try {
        const response = await fetch(source, {credentials:"same-origin",cache:"no-store"});
        if (!response.ok) throw Error("Private audio HTTP " + response.status);
        const blob = await response.blob();
        if (blob.size < 1_000_000 || blob.type && !blob.type.startsWith("audio/")) {
          throw Error("Unexpected audio payload");
        }
        bufferedURL = URL.createObjectURL(blob);
        audio.src = bufferedURL;
        audio.load();
        status.textContent = "";
      } catch {
        // Remain playable if the blob optimization is unsupported; the
        // seek control remains disabled unless the browser reports a full range.
        audio.src = source;
        audio.load();
        status.textContent = "Reading available; seeking may be limited on this connection.";
      }
      prepared = true;
      button.disabled = false;
      display();
    };
    window.addEventListener("pagehide", () => {
      if (bufferedURL) URL.revokeObjectURL(bufferedURL);
    }, {once:true});
    prepare();
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start, {once:true});
  else start();
})();
