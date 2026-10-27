// Reproduce the four sound studies using the same Csound WASM and score as the essay.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
globalThis.self=globalThis; globalThis.window=globalThis;
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const base=path.join(root,'site/essays/the-door-is-a-score/assets');
const {libcsound}=await import(path.join(base,'vendor/csound.js'));
const {directions,sourceFiles,csdFor}=await import(path.join(base,'score.mjs'));
const results=[];
for(const id of Object.keys(directions)) {
 const cs=await libcsound();
 for(const name of sourceFiles) cs.writeFile(undefined,name,new Uint8Array(fs.readFileSync(path.join(base,name))));
 const ptr=cs.csoundCreate();
 const compiled=cs.csoundCompileCSD(ptr,csdFor(id)); if(compiled!==0)throw new Error(`${id}: compile ${compiled}`);
 const started=cs.csoundStart(ptr); if(started!==0)throw new Error(`${id}: start ${started}`);
 const block=cs.csoundGetKsmps(ptr)*cs.csoundGetNchnls(ptr);
 const chunks=[]; let blocks=0;
 while(cs.csoundPerformKsmps(ptr)===0) {
  const samples=new Float64Array(cs.getMemory().buffer,cs.csoundGetSpout(ptr),block);
  chunks.push(Float32Array.from(samples)); if(++blocks>30000)throw new Error('Bound exceeded');
 }
 const pcm=new Float32Array(chunks.length*block);chunks.forEach((x,i)=>pcm.set(x,i*block));
 let square=0,peak=0;for(const x of pcm){square+=x*x;peak=Math.max(peak,Math.abs(x));}
 const out=Buffer.alloc(44+pcm.length*4);out.write('RIFF',0);out.writeUInt32LE(out.length-8,4);out.write('WAVEfmt ',8);out.writeUInt32LE(16,16);out.writeUInt16LE(3,20);out.writeUInt16LE(2,22);out.writeUInt32LE(48000,24);out.writeUInt32LE(384000,28);out.writeUInt16LE(8,32);out.writeUInt16LE(32,34);out.write('data',36);out.writeUInt32LE(pcm.length*4,40);Buffer.from(pcm.buffer).copy(out,44);
 fs.writeFileSync(path.join(base,`${id}-float.wav`),out);
 results.push({direction:id,engineVersion:cs.csoundGetVersion(),frames:pcm.length/2,sampleRate:48000,channels:2,peak,rms:Math.sqrt(square/pcm.length),compiled,started});
 cs.csoundStop(ptr);cs.csoundDestroy(ptr);
}
console.log(JSON.stringify(results,null,2));
