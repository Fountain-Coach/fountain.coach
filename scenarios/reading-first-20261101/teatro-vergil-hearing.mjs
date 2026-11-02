import {mountVoicePatchView} from "/estate/assets/satzfunk-player/voice-patch-view.mjs";
/* Source-bound Vergil reading in the new unified Bookshelf/Reader.
 * Keeps the existing Fountain Press pages and SatzfunkPlayer transport.
 * This is the private, author-approved audition, not public distribution.
 * No transcript, second reader, synthesis in browser, or playback on HTTP.
 */
const MANIFEST = "/estate/media/first-readings/teatro-vergil-edition.private.json";
const TITLE = "Teatro — An Unfinished Composition";
const SOURCE = "6aefe374f2109d6d432cc3952d4703d8795fbeaf728e62b0113543e6ff11e43c";
const MEDIA = "d5ce996b8d42db2a665263877e35b772220cc1faef6c2e1e54c3a6e0a6a65fcd";
const VOLUMES = new Set(["teatro", "essay--teatro-an-unfinished-composition"]);
const viewport = document.getElementById("page-viewport");
const template = document.querySelector('template[data-reader-volume="teatro"]');
const header = document.querySelector(".header-actions");
const controls = document.querySelector(".frame-controls");
const toHex = buffer => [...new Uint8Array(buffer)].map(b => b.toString(16).padStart(2,"0")).join("");
const readerText = () => {
  if (!template) return null;
  const blocks = [...template.content.querySelectorAll('[data-source-block^="teatro-an-unfinished-composition."]')]
    .filter(node => node.matches("h2,p") &&
      /^teatro-an-unfinished-composition\.(?:title|p\d+)$/.test(node.dataset.sourceBlock));
  return blocks.length === 29 ? blocks.map(node => node.textContent.trim()).join("\n\n") : null;
};
const active = () => VOLUMES.has(viewport?.dataset.volume);
const time = seconds => {
  const n = Math.max(0, Math.floor(Number(seconds)||0));
  return Math.floor(n/60) + ":" + String(n%60).padStart(2,"0");
};
async function install() {
  if (!viewport || !template || !header || !controls ||
      location.protocol !== "https:" || location.hostname !== "192.168.8.50" ||
      !window.isSecureContext) return;
  const text = readerText();
  if (!text || toHex(await crypto.subtle.digest("SHA-256",new TextEncoder().encode(text))) !== SOURCE) return;

  let edition;
  try {
    const response = await fetch(MANIFEST,{cache:"no-store"});
    if (!response.ok) return;
    edition = await response.json();
    if (edition.schema !== "satzfunk.spoken-edition.v1" ||
        edition.status !== "private-candidate" || edition.sourceChapter !== "teatro" ||
        edition.narrator !== "Vergil" || edition.publicReleaseAuthorized !== false ||
        edition.privateRehearsalAuthorized !== true || edition.sourceSHA256 !== SOURCE ||
        edition.recording?.sha256 !== MEDIA ||
        edition.recording?.media !== "/estate/media/first-readings/teatro-vergil-auto-corrected-v2.mp3" ||
        !(edition.recording.duration > 498 && edition.recording.duration < 500)) return;
    const media = await fetch(edition.recording.media,{method:"HEAD",cache:"no-store"});
    if (!media.ok || Number(media.headers.get("content-length")) !== 4126392) return;
  } catch {return;}

  await customElements.whenDefined("satzfunk-player");
  const player = document.createElement("satzfunk-player");
  player.setAttribute("transport-only","");
  player.setAttribute("label","Vergil reads Teatro — AI-generated voice");
  player.hidden = true;
  document.body.append(player);
  player.configureVoice({csoundModule:"/estate/assets/linotype/book-csound-host.js"});
  const track = {
    id:"teatro-vergil-source-aligned-v2", title:TITLE,
    media:edition.recording.media,mediaSHA256:MEDIA,sourceSHA256:SOURCE,voice:true,
    publicReleaseAuthorized:false,privateRehearsalAuthorized:true
  };
  const grant = {scope:"private-wlan-rehearsal",origin:location.origin,
    trackID:track.id,mediaSHA256:MEDIA,sourceSHA256:SOURCE};
  let binding;
  try {binding=player.setEdition({origin:location.origin,tracks:[track],rehearsalGrant:grant});}
  catch {player.remove();return;}
  if (binding.state !== "ready") {player.remove();return;}

  const button = document.createElement("button");
  button.id = "teatro-vergil-read";
  button.type = "button";
  button.className = "header-books teatro-vergil-read";
  button.textContent = "Read aloud";
  button.setAttribute("aria-label","Read Teatro aloud with the AI-generated Vergil voice");
  button.setAttribute("aria-pressed","false");
  header.insertBefore(button,document.getElementById("reader-theme"));
  const sound = player.createVoiceSettingsControl();
  header.insertBefore(sound,document.getElementById("reader-theme"));

  const display = document.createElement("output");
  display.id = "teatro-vergil-clock";
  display.setAttribute("aria-live","off");
  display.setAttribute("aria-label","Vergil reading position");
  display.className = "teatro-vergil-clock";
  display.textContent = "0:00 / " + time(Math.round(edition.recording.duration));
  controls.insertBefore(display,document.getElementById("next-page"));

  const updateScore = () => {
    const patch = viewport.querySelector(".voice-mastering-leaf .voice-patch-surface:not([data-patch-mounted])");
    if (patch) mountVoicePatchView(patch,player);
    const out = viewport.querySelector(".voice-mastering-leaf .voice-score-live");
    if (!out) return;
    const ear = player.audioSettings.ear;
    if (player.state.paused || player.audioSettings.mode === "original") {
      out.textContent = player.audioSettings.mode === "original"
        ? "Original source · Csound bypassed" : "Ear listens when the reading plays.";
    } else if (ear && Number.isFinite(ear.rms) && Number.isFinite(ear.samplePeak)) {
      out.textContent = "Ear · RMS " + ear.rms.toFixed(3) + " · sample peak " +
        ear.samplePeak.toFixed(3) + " (before output gain)";
    } else {
      out.textContent = "Ear listening · awaiting the next audio window";
    }
  };
  player.addEventListener("satzfunkplayer:ear-observation",updateScore);
  player.addEventListener("satzfunkplayer:audio-settings",updateScore);
  const update = () => {
    const visible = active();
    if (!visible && player.state.paused === false) player.pause();
    button.hidden = !visible;
    sound.hidden = !visible;
    display.hidden = !visible;
    const playing = player.state.paused === false;
    button.textContent = playing ? "Pause reading" : "Read aloud";
    button.setAttribute("aria-pressed",String(playing));
    button.setAttribute("aria-label",(playing ? "Pause" : "Read")+
      " Teatro aloud with the AI-generated Vergil voice");
    updateScore();
    display.textContent = time(player.state.currentTime) +
      " / " + time(Math.round(edition.recording.duration));
  };
  button.addEventListener("click",() => {
    if (!active()) return;
    if (player.state.paused === false) player.pause();
    else player.play().catch(() => {button.textContent="Audio unavailable";button.disabled=true;});
  });
  for (const event of ["satzfunkplayer:position","satzfunkplayer:transport","satzfunkplayer:ready","satzfunkplayer:refused"]) {
    player.addEventListener(event,update);
  }
  new MutationObserver(update).observe(viewport,{attributes:true,attributeFilter:["data-volume","aria-label"]});
  // Linotype replaces the page on navigation and responsive re-composition.
  // Mount the patch surface only on the current measured page, not the source.
  new MutationObserver(() => {
    if (viewport.querySelector(".voice-patch-surface:not([data-patch-mounted])")) updateScore();
  }).observe(viewport,{childList:true,subtree:true});
  window.addEventListener("hashchange",update);
  window.addEventListener("popstate",update);
  update();
}
install();
