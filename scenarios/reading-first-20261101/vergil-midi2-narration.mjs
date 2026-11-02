import {admitReadingScore} from "/estate/assets/satzfunk-player/midi2-reading-score.mjs";
import {bindMidi2ReadingTransport} from "/estate/assets/satzfunk-player/midi2-reading-transport.mjs";
import {createNarratedPageController,makeLinotypeReadingCursor} from "/estate/assets/linotype/reading-audio-cursor.mjs";

// A source-bound optional adapter: the player owns time, Press owns physical
// pages, MIDI 2.0 owns the event projection. Nothing reads from Ear RMS to
// guess a spoken word. The private score itself must pass source digest admission.
export async function installVergilNarration({player,track,sourceBlocks,scoreURL,sound,active,viewport}={}){
 if(!player||!track||!Array.isArray(sourceBlocks)||!sound ||
    typeof active!=="function"||!viewport||
    !scoreURL?.startsWith("/estate/media/first-readings/"))
    throw new TypeError("Narration requires the admitted recording and canonical source");
 const response=await fetch(scoreURL,{cache:"no-store"});
 if(!response.ok)throw new Error("Private MIDI2 alignment is unavailable");
 const sidecar=await response.json();
 const score=await admitReadingScore(sidecar,{track,sourceBlocks});
 const bridge=window.FountainPressNarrationBridge;
 if(!bridge||typeof bridge.showPage!=="function")
  throw new Error("The existing Fountain Press pagination bridge is unavailable");
 let controller=null,disposed=false;
 const transport=bindMidi2ReadingTransport({player,score,onMoment:moment=>{
  if(disposed||!controller)return;
  controller.onMoment(active()&&bridge.volume===viewport.dataset.volume?moment:null);
 }});
 const cursor=makeLinotypeReadingCursor(document);
 controller=createNarratedPageController({
  engine:bridge,score,transport,cursor,mode:"follow",
  showPage:(page)=>bridge.showPage(page),
  onStatus:status=>{
   if(sound.dataset) sound.dataset.narrationStatus=status.state;
  }
 });
 // The reader's Audio disclosure is the existing settings location; no
 // overlay, transcript or duplicate transport control is introduced.
 const label=document.createElement("label");
 label.className="satzfunk-narration-setting";
 label.textContent="Narrator";
 const select=document.createElement("select");
 select.className="satzfunk-narration-mode";
 select.setAttribute("aria-label","Narrator page following");
 for(const [value,name] of [
  ["manual","Manual reading"],["follow","Follow narrator"],
  ["cursor","Follow + audio cursor"]]){
  const option=document.createElement("option");
  option.value=value;option.textContent=name;select.append(option);
 }
 select.value="follow";
 select.addEventListener("change",()=>controller?.setMode(select.value));
 label.append(select);
 sound.append(label);
 const detachScrub=controller.attachPointerScrub(viewport,document);
 const reflow=()=>{
  if(disposed)return;
  if(active()&&bridge.volume===viewport.dataset.volume){
   controller.onMoment(transport.current);
   controller.onReflow();
  }else controller.onMoment(null);
 };
 document.addEventListener("fountain:linotype-composed",reflow);
 const observe=new MutationObserver(reflow);
 observe.observe(viewport,{attributes:true,attributeFilter:["data-volume"]});
 reflow();
 return Object.freeze({
  scoreID:transport.scoreID,
  get mode(){return controller.mode},
  get current(){return transport.current},
  setMode(value){select.value=controller.setMode(value);return select.value},
  seekToSpan(blockID,offset){return controller.seekAt(blockID,offset)},
  dispose(){
   if(disposed)return;disposed=true;
   document.removeEventListener("fountain:linotype-composed",reflow);
   observe.disconnect();detachScrub();transport.dispose();controller.dispose();label.remove();
  }
 });
}
