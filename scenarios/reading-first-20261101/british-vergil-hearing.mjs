/* A source-bound British Vergil audition within the existing paginated Linotype.
 * No browser synthesis, transcript, paginator or second audio engine.
 * The entire control remains absent without an authorized, present recording. */
const editionURL = "/estate/media/vergil-on-continuity/edition.json";
const viewport = document.getElementById("page-viewport");
const template = document.querySelector('template[data-reader-volume="continuity"]');
const header = document.querySelector(".header-actions");
const reader = document.querySelector(".frame-controls");
const names = ["continuity.title", ...Array.from({length:9},(_,i)=>"continuity.p"+(i+1))];
const hex64 = /^[a-f0-9]{64}$/;
const sourceText = () => {
  if (!template) return null;
  const paragraphs = names.map(name =>
    template.content.querySelector('[data-source-block="'+name+'"]')?.textContent?.trim());
  return paragraphs.every(Boolean) ? paragraphs.join("\n\n") : null;
};
async function sha256(text) {
  const bytes = new TextEncoder().encode(text);
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(digest)].map(x=>x.toString(16).padStart(2,"0")).join("");
}
const isContinuity = () => viewport?.getAttribute("aria-label")?.includes("On Continuity");
const formatTime = time => {
  const n = Math.max(0, Math.floor(Number(time)||0));
  return Math.floor(n/60)+":"+String(n%60).padStart(2,"0");
};
async function prepare() {
  if (!viewport || !template || !header || !reader || !window.isSecureContext) return;
  // A private rehearsal is allowed only on the existing owner-WLAN or loopback.
  if (location.hostname !== "192.168.8.50" &&
      !["localhost","127.0.0.1","[::1]"].includes(location.hostname)) return;
  let edition;
  try {
    const response = await fetch(editionURL,{cache:"no-store"});
    if (!response.ok) return;
    edition = await response.json();
    const text = sourceText();
    if (edition.schema !== "satzfunk.spoken-edition.v1" ||
        edition.status !== "private-candidate" ||
        edition.sourceChapter !== "continuity" ||
        edition.narrator !== "Vergil" ||
        edition.embodiment !== "British Vergil" ||
        edition.publicReleaseAuthorized !== false ||
        edition.privateRehearsalAuthorized !== true ||
        !hex64.test(edition.sourceSHA256 || "") ||
        !hex64.test(edition.recording?.sha256 || "") ||
        edition.text !== text ||
        edition.sourceSHA256 !== await sha256(text) ||
        !/^\/estate\/media\/vergil-on-continuity\/[a-z0-9-]+\.mp3$/.test(edition.recording?.media||"") ||
        !Number.isFinite(edition.recording?.duration) ||
        edition.recording.duration <= 0) return;
    const file = await fetch(edition.recording.media,{method:"HEAD",cache:"no-store"});
    if (!file.ok) return;
  } catch { return; }
  await customElements.whenDefined("satzfunk-player");
  const player = document.createElement("satzfunk-player");
  player.hidden = true;
  player.setAttribute("transport-only","");
  player.setAttribute("label","On Continuity British Vergil reading");
  document.body.append(player);
  const track = {
    id:edition.id, title:"On Continuity — British Vergil",
    media:edition.recording.media, mediaSHA256:edition.recording.sha256,
    sourceSHA256:edition.sourceSHA256, publicReleaseAuthorized:false,
    privateRehearsalAuthorized:true
  };
  const grant = {
    scope:"private-wlan-rehearsal", origin:location.origin,
    trackID:track.id, mediaSHA256:track.mediaSHA256, sourceSHA256:track.sourceSHA256
  };
  let binding;
  try { binding = player.setEdition({origin:location.origin,tracks:[track],rehearsalGrant:grant}); }
  catch { player.remove(); return; }
  if (binding.state !== "ready") { player.remove(); return; }
  const button=document.createElement("button");
  button.type="button";
  button.className="header-books reader-hearing-button";
  button.textContent="Listen · AI";
  button.setAttribute("aria-label","Read On Continuity aloud — AI-generated British Vergil voice");
  header.insertBefore(button,document.getElementById("reader-theme"));
  const rail=document.createElement("div");
  rail.className="reader-hearing-rail";
  rail.hidden=true;
  const seek=document.createElement("input");
  seek.type="range";seek.min="0";seek.max=String(edition.recording.duration);
  seek.step="0.1";seek.value="0";seek.setAttribute("aria-label","Read aloud position");
  const clock=document.createElement("output");
  clock.setAttribute("aria-live","off");
  clock.textContent="0:00 / "+formatTime(edition.recording.duration);
  rail.append(seek,clock);
  reader.insertBefore(rail,document.getElementById("next-page"));
  const style=document.createElement("style");
  style.textContent=".reader-hearing-rail{display:flex;align-items:center;gap:.45rem;min-width:0;max-width:12rem}.reader-hearing-rail[hidden]{display:none}.reader-hearing-rail input{width:6rem;min-width:2rem}.reader-hearing-rail output{white-space:nowrap;font-size:.7rem;font-variant-numeric:tabular-nums}@media(max-width:720px){.reader-hearing-rail{max-width:7.5rem}.reader-hearing-rail input{width:3rem}.reader-hearing-button{font-size:.8rem}}";
  document.head.append(style);
  const refresh=()=>{
    const relevant=Boolean(isContinuity());
    button.hidden=!relevant;
    rail.hidden=!relevant || player.state.paused !== false;
    if (!relevant && player.state.paused===false) player.pause();
    button.textContent=player.state.paused===false?"Pause · AI":"Listen · AI";
    button.setAttribute("aria-label",(player.state.paused===false?"Pause":"Read")+" On Continuity aloud — AI-generated British Vergil voice");
  };
  button.addEventListener("click",()=>{
    if(player.state.paused===false){player.pause();return;}
    player.play().catch(()=>{button.textContent="Unavailable";button.disabled=true;});
  });
  seek.addEventListener("input",()=>player.seek(Number(seek.value)));
  player.addEventListener("satzfunkplayer:position",()=>{
    seek.value=String(player.state.currentTime||0);
    clock.textContent=formatTime(player.state.currentTime)+" / "+formatTime(edition.recording.duration);
  });
  for(const name of ["transport","ready","refused"]) player.addEventListener("satzfunkplayer:"+name,refresh);
  new MutationObserver(refresh).observe(viewport,{attributes:true,attributeFilter:["aria-label"]});
  window.addEventListener("hashchange",refresh);
  refresh();
}
prepare();
