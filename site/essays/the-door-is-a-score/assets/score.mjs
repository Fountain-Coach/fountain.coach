// Authored sound-study score. Not an admitted Csound Teatro Scenario or UMP adapter.
export const duration = 14;
export const directions = {
  present: {title:'A careful closing', sentence:'Vorsichtig schloss sie die Holztür.', note:'Keys, hinge, closure. Close, restrained, and in the present.', gain:0.70,rate:1,pan:0.40,cutoff:14500,wet:0.06, echoes:[]},
  beyond: {title:'From the next room', sentence:'Nebenan schloss sie die Holztür.', note:'The same gestures and timing, heard across an intervening room.',gain:0.29,rate:1,pan:0.79,cutoff:2100,wet:0.47, echoes:[]},
  memory: {title:'A remembered closing', sentence:'Sie erinnerte sich, wie sie die Holztür geschlossen hatte.',note:'The gesture slows; the closing returns twice, each time further away. An authored treatment of memory.',gain:0.42,rate:0.66,pan:0.28,cutoff:4200,wet:0.77,echoes:[{time:6.8,gain:0.30,pan:0.70},{time:9.3,gain:0.16,pan:0.36}]},
  withheld: {title:'The door stays open',sentence:'Sie wollte die Holztür schließen. Sie tat es nicht.',note:'Keys and a hinge prepare an action. The closing is deliberately absent. Let the silence finish.',gain:0.70,rate:1,pan:0.40,cutoff:14500,wet:0.06,echoes:[],omitClosure:true}
};
export const sourceFiles = ['keys.wav','wood-hinge.wav','wood-close.wav'];
export function eventsFor(id) {
  const d=directions[id]; if(!d) throw new Error('Unknown authored direction');
  const e=[{source:1,time:1,duration:1.1,amp:d.gain*0.48,rate:d.rate,pan:d.pan,cutoff:d.cutoff,wet:d.wet},{source:2,time:2.6,duration:2.4,amp:d.gain*0.58,rate:d.rate,pan:d.pan,cutoff:d.cutoff,wet:d.wet}];
  if(!d.omitClosure)e.push({source:3,time:4.3,duration:3,amp:d.gain,rate:d.rate,pan:d.pan,cutoff:d.cutoff,wet:d.wet});
  for(const x of d.echoes)e.push({source:3,time:x.time,duration:3.2,amp:x.gain,rate:d.rate,pan:x.pan,cutoff:d.cutoff,wet:d.wet});
  return e;
}
export function csdFor(id, output='-n') {
  const events=eventsFor(id);
  return `<CsoundSynthesizer>
<CsOptions>
${output} -d -m0
</CsOptions>
<CsInstruments>
sr=48000
ksmps=32
nchnls=2
0dbfs=1
gaLeft init 0
gaRight init 0
instr 1
 if p4 == 1 then
  Sfile = "keys.wav"
 elseif p4 == 2 then
  Sfile = "wood-hinge.wav"
 else
  Sfile = "wood-close.wav"
 endif
 aSource diskin2 Sfile, p6, 0, 0
 aFiltered tone aSource, p8
 aEnvelope linen 1, 0.008, p3, 0.07
 aLeft, aRight pan2 aFiltered * aEnvelope * p5, p7
 outs aLeft * (1-p9*0.4), aRight * (1-p9*0.4)
 gaLeft = gaLeft + aLeft*p9
 gaRight = gaRight + aRight*p9
endin
instr 99
 aLeft,aRight reverbsc gaLeft,gaRight,0.82,6500
 outs aLeft*0.55,aRight*0.55
 clear gaLeft,gaRight
endin
</CsInstruments>
<CsScore>
i 99 0 ${duration}
${events.map(e=>`i 1 ${e.time} ${e.duration} ${e.source} ${e.amp} ${e.rate} ${e.pan} ${e.cutoff} ${e.wet}`).join('\n')}
f 0 ${duration}
e
</CsScore>
</CsoundSynthesizer>`;
}
