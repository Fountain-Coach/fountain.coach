import {installVergilNarration} from "/estate/assets/linotype/vergil-midi2-narration.mjs";

// An additional source-bound voice edition INSIDE the accepted Fountain Press.
// No alternate Reader, cursor, audio clock, transcript, or Csound UI.
const VOLUME = "essay--what-makes-a-page-modern";
const SOURCE = "10162c61a2729badd613085810d174dc3926082fbe31696994afafc29110c65b";
const MANIFEST = "/estate/media/first-readings/modern-page-vergil-edition.private.json";
const SCORE = "/estate/media/first-readings/modern-page-midi2-reading-score.private.json";
const MEDIA = "/estate/media/first-readings/modern-page-vergil-source-aligned.mp3";
const TRACK = "modern-page-vergil-source-aligned-v1";
const VOICE = "voice_6ae7539638508191b0013cc1f7fa709d";
const viewport = document.getElementById("page-viewport");
const template = document.querySelector('template[data-reader-volume="'+VOLUME+'"]');
const header = document.querySelector(".header-actions");
const controls = document.querySelector(".frame-controls");
const toHex = value => Array.from(new Uint8Array(value),
  byte => byte.toString(16).padStart(2,"0")).join("");
const active = () => viewport?.dataset.volume === VOLUME;
const format = seconds => {
  const time=Math.max(0,Math.floor(Number(seconds)||0));
  return Math.floor(time/60)+":"+String(time%60).padStart(2,"0");
};
const readBlocks = () => [...template.content.querySelectorAll("[data-source-block]")]
  .filter(node => node.matches("h2,p") &&
    node.dataset.sourceBlock.startsWith("what-makes-a-page-modern."))
  .map(node => ({id:node.dataset.sourceBlock,text:node.textContent.trim()}));

async function install() {
  if (!template || !viewport || !header || !controls ||
      location.protocol !== "https:" ||
      location.hostname !== "192.168.8.50" ||
      !window.isSecureContext) return;
  const blocks=readBlocks();
  if (blocks.length!==49 ||
      new Set(blocks.map(b=>b.id)).size!==49) return;
  const source=blocks.map(b=>b.text).join("\n\n");
  if (toHex(await crypto.subtle.digest("SHA-256",
      new TextEncoder().encode(source)))!==SOURCE) return;

  let edition;
  try {
    const response=await fetch(MANIFEST,{cache:"no-store"});
    if (!response.ok) return;
    edition=await response.json();
    if (edition.schema!=="satzfunk.spoken-edition.v1" ||
        edition.status!=="private-candidate" ||
        edition.sourceChapter!==VOLUME ||
        edition.narrator!=="Vergil" ||
        edition.narratorVoiceID!==VOICE ||
        edition.sourceSHA256!==SOURCE ||
        edition.publicReleaseAuthorized!==false ||
        edition.privateRehearsalAuthorized!==true ||
        edition.independentTranscriptsAligned!==true ||
        edition.recording?.media!==MEDIA ||
        !/^[a-f0-9]{64}$/.test(edition.recording.sha256||"") ||
        !(edition.recording.duration>60 &&
          edition.recording.duration<3600) ||
        !(edition.recording.bytes>100000)) return;
    const head=await fetch(MEDIA,{method:"HEAD",cache:"no-store"});
    if (!head.ok ||
        Number(head.headers.get("content-length"))!==edition.recording.bytes ||
        head.headers.get("accept-ranges")!=="bytes") return;
  } catch {return;}
  await customElements.whenDefined("satzfunk-player");
  const player=document.createElement("satzfunk-player");
  player.setAttribute("transport-only","");
  player.setAttribute("label","Vergil reads What Makes a Page Modern — AI-generated voice");
  player.hidden=true;
  document.body.append(player);
  player.configureVoice({csoundModule:"/estate/assets/linotype/book-csound-host.js",
    mode:"studio"});
  const track={id:TRACK,title:"What Makes a Page Modern?",
    media:MEDIA,mediaSHA256:edition.recording.sha256,
    sourceSHA256:SOURCE,voice:true,publicReleaseAuthorized:false,
    privateRehearsalAuthorized:true};
  const grant={scope:"private-wlan-rehearsal",origin:location.origin,
    trackID:TRACK,mediaSHA256:track.mediaSHA256,sourceSHA256:SOURCE};
  try {
    if (player.setEdition({origin:location.origin,tracks:[track],
        rehearsalGrant:grant}).state!=="ready") {player.remove();return;}
    // Fail closed: audio is not advertised as synchronized until the
    // REAL sound file, typed reading score and exact document digest admit.
    player.narrationBinding=await installVergilNarration({
      player,track,active,viewport,scoreURL:SCORE,sourceBlocks:blocks
    });
  } catch(error) {
    player.dataset.narrationStatus="unavailable";
    console.warn("Source-aligned Vergil edition refused",String(error));
    player.remove();
    return;
  }
  const button=document.createElement("button");
  button.id="modern-page-vergil-read";
  button.type="button";
  button.className="header-books teatro-vergil-read";
  button.textContent="▶";
  button.setAttribute("aria-label","Play Vergil narration — AI-generated voice");
  button.setAttribute("aria-pressed","false");
  header.insertBefore(button,document.getElementById("reader-theme"));

  const clock=document.createElement("output");
  clock.id="modern-page-vergil-clock";
  clock.className="teatro-vergil-clock";
  clock.setAttribute("aria-live","off");
  clock.setAttribute("aria-label","Vergil reading position");
  controls.insertBefore(clock,document.getElementById("next-page"));
  function update() {
    const visible=active();
    if (!visible && player.state.paused===false) player.pause();
    button.hidden=!visible;
    clock.hidden=!visible;
    const playing=player.state.paused===false;
    button.textContent=playing ? "❚❚" : "▶";
    button.setAttribute("aria-pressed",String(playing));
    button.setAttribute("aria-label",playing ?
      "Pause Vergil narration" : "Play Vergil narration — AI-generated voice");
    clock.textContent=format(player.state.currentTime)+" / "+
      format(Math.round(edition.recording.duration));
  }
  button.addEventListener("click",()=>{
    if (!active()) return;
    if (player.state.paused===false) player.pause();
    else player.play().catch(()=>{
      button.disabled=true;button.setAttribute("aria-label","Audio unavailable");
    });
  });
  for (const name of ["satzfunkplayer:position","satzfunkplayer:transport",
      "satzfunkplayer:ready","satzfunkplayer:refused"])
    player.addEventListener(name,update);
  new MutationObserver(update).observe(viewport,
    {attributes:true,attributeFilter:["data-volume","aria-label"]});
  window.addEventListener("hashchange",update);
  window.addEventListener("popstate",update);
  update();
}
void install();
