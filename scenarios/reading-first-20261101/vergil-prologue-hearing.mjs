/* Source-bound Vergil reading in the new unified Bookshelf/Reader.
 * Keeps the existing Fountain Press pages and SatzfunkPlayer transport.
 * This is the private, author-approved audition, not public distribution.
 * No transcript, second reader, synthesis in browser, or playback on HTTP.
 */
const MANIFEST = "/estate/media/first-readings/vergil-prologue-edition.private.json";
const TITLE = "Vergil — First Reading Prologue";
const SOURCE = "63eba43a777b39f9bb27ab8b54fcb7cb04f5ad61633a8f50e0e6aa44e56b3971";
const MEDIA = "4b2727e08bd7b3c0edea59f6faca92292e9447d980bfb1d2f963e829dba16881";
const VOLUMES = new Set(["solstice-reading-01--vergil"]);
const viewport = document.getElementById("page-viewport");
const template = document.querySelector('template[data-reader-volume="solstice-reading-01--vergil"]');
const header = document.querySelector(".header-actions");
const controls = document.querySelector(".frame-controls");
const toHex = buffer => [...new Uint8Array(buffer)].map(b => b.toString(16).padStart(2,"0")).join("");
const readerText = () => {
  if (!template) return null;
  const blocks = [...template.content.querySelectorAll('[data-source-block^="solstice-reading-01--vergil.text."]')]
    .filter(node => node.matches("h2,p") &&
      /^solstice-reading-01--vergil\.text\.\d+$/.test(node.dataset.sourceBlock));
  return blocks.length === 40 ? blocks.map(node => node.textContent.trim()).join("\n\n") : null;
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
        edition.status !== "private-candidate" || edition.sourceChapter !== "solstice-reading-01--vergil" ||
        edition.narrator !== "Vergil" || edition.publicReleaseAuthorized !== false ||
        edition.privateRehearsalAuthorized !== true || edition.independentTranscriptsAligned !== true || edition.sourceSHA256 !== SOURCE ||
        edition.recording?.sha256 !== MEDIA ||
        edition.recording?.media !== "/estate/media/first-readings/vergil-prologue-source-aligned.mp3" ||
        !(edition.recording.duration > 60 && edition.recording.duration < 2400)) return;
    const media = await fetch(edition.recording.media,{method:"HEAD",cache:"no-store"});
    if (!media.ok || Number(media.headers.get("content-length")) < 100000) return;
  } catch {return;}

  await customElements.whenDefined("satzfunk-player");
  const player = document.createElement("satzfunk-player");
  player.setAttribute("transport-only","");
  player.setAttribute("label","Vergil reads his prologue — AI-generated voice");
  player.hidden = true;
  document.body.append(player);
  player.configureVoice({csoundModule:"/estate/assets/linotype/book-csound-host.js"});
  const track = {
    id:"vergil-prologue-source-aligned-v1", title:TITLE,
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
  button.id = "vergil-prologue-read";
  button.type = "button";
  button.className = "header-books vergil-prologue-read";
  button.textContent = "Read aloud";
  button.setAttribute("aria-label","Read the Vergil prologue aloud with the AI-generated Vergil voice");
  button.setAttribute("aria-pressed","false");
  header.insertBefore(button,document.getElementById("reader-theme"));
  const sound = player.createVoiceSettingsControl();
  header.insertBefore(sound,document.getElementById("reader-theme"));

  const display = document.createElement("output");
  display.id = "vergil-prologue-clock";
  display.setAttribute("aria-live","off");
  display.setAttribute("aria-label","Vergil reading position");
  display.className = "vergil-prologue-clock";
  display.textContent = "0:00 / " + time(Math.round(edition.recording.duration));
  controls.insertBefore(display,document.getElementById("next-page"));

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
      " the Vergil prologue aloud with the AI-generated Vergil voice");
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
  window.addEventListener("hashchange",update);
  window.addEventListener("popstate",update);
  update();
}
install();
