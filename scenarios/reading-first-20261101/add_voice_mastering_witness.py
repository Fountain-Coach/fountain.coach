#!/usr/bin/env python3
"""Projection-only Ear witness on the authored Linotype mastering end leaf."""
from pathlib import Path
root=Path(__file__).resolve().parent
for name in ["teatro-vergil-hearing.mjs","vergil-prologue-hearing.mjs"]:
 p=root/name
 s=p.read_text()
 marker="  const update = () => {"
 assert s.count(marker)==1,(name,s.count(marker))
 addition='''  const updateScore = () => {
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
'''
 s=s.replace(marker,addition+marker)
 end='    display.textContent = time(player.state.currentTime) +'
 assert s.count(end)==1
 s=s.replace(end,'    updateScore();\n'+end)
 p.write_text(s)
 print("END_LEAF_WITNESS",name)
