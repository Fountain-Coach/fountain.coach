// One immutable publication snapshot, compiled from the exact admitted source.
// The source templates retain complete original text; this snapshot owns which
// source identities are active, ordered, illustrated or historical.
const publication=JSON.parse(document.getElementById('reader-publication-data')?.textContent||'null');
if(publication?.schema!=='fountain.press.publication-snapshot.v1'||
   !Array.isArray(publication.books)||!publication.books.length)
 throw Error('Admitted Fountain Press publication snapshot unavailable');
const books=publication.books;
const collectionOrder=books.map(book=>book.id);
if(new Set(collectionOrder).size!==collectionOrder.length)
 throw Error('Duplicate published book identity');
const bookById=new Map(books.map(book=>[book.id,book]));
const contents=Object.fromEntries(books.map(book=>[book.id,book.orderedWorkIDs]));
const archivedOwners=new Map();
for(const book of books){
 const privatePreview=publication.publicationLane==='private-owner-WLAN-editorial-review';
 if(privatePreview){
  if(book.stageOnly!==true||book.publicReleaseAuthorized!==false||book.stagePreviewAuthorized!==true||
     book.publicationState!=='private-owner-WLAN-editorial-review')
   throw Error('Unadmitted private preview book: '+book.id);
 }else if(book.publicationState!=='public-production'||book.publicReleaseAuthorized!==true||book.stageOnly!==false)
  throw Error('Unreleased book admitted to public Bookshelf: '+book.id);
 for(const entry of book.unlistedSourceWorks||[]){
  if(archivedOwners.has(entry.id))throw Error('Duplicate archival identity');
  archivedOwners.set(entry.id,book.id);
 }
}
const labels=new Map([['publication-notes','Publication Notes'],['continuity','On Continuity'],
 ['library','Bookshelf'],['solstice','First Readings'],['solstice-reading-01','First Readings'],
 ['teatro','Teatro — An Unfinished Composition'],['notes--the-door-is-a-score','References · The Door Is a Score']]);
for(const book of books)labels.set(book.id,book.title);
const activeWorks=new Set(books.flatMap(book=>book.orderedWorkIDs));
if(activeWorks.size!==books.reduce((n,book)=>n+book.orderedWorkIDs.length,0))
 throw Error('One work admitted to multiple public books');
for(const [key,template] of templates){
 if(activeWorks.has(key)||archivedOwners.has(key)||key.startsWith('essay--')||
    key.startsWith('solstice-reading-01--')||key.startsWith('orange-dot--')){
  const label=template.content.querySelector('h2')?.textContent?.trim()||key;
  labels.set(key,label);
  if(activeWorks.has(key)){
   const book=books.find(b=>b.orderedWorkIDs.includes(key));
   const option=document.createElement('option');
   option.value=key;option.textContent=book.title+' · '+label;
   section.append(option);
  }
 }
}
for(const id of publication.requiredEditorialProemWorkIDs){
 const template=templates.get(id);
 const proems=template?.content.querySelectorAll('.frame-editorial-proem[data-editorial-role="proem"],.frame-lead[data-editorial-role="proem"]');
 if(proems?.length!==1||!proems[0].textContent.trim()||!proems[0].hasAttribute('data-source-block'))
  throw Error('Authored editorial proem is missing: '+id);
}
const galleryData=JSON.parse(document.getElementById('reader-gallery-data')?.textContent||'null');
if(galleryData?.schema!=='fountain.press.bookshelf-gallery.v1')
 throw Error('Bookshelf gallery source missing');
const galleries=galleryData.collections;
if(Object.keys(galleries).length!==books.length||
   Object.keys(galleries).some(id=>!bookById.has(id)))
 throw Error('Gallery collections disagree with published books');
for(const book of books){
 if(!Array.isArray(book.orderedWorkIDs)||!Array.isArray(book.illustratedWorkIDs)||
    !book.orderedWorkIDs.length||new Set(book.orderedWorkIDs).size!==book.orderedWorkIDs.length)
  throw Error('Invalid published work order: '+book.id);
 if(book.orderedWorkIDs.some(id=>!templates.has(id)))
  throw Error('Published work missing original source: '+book.id);
 const gallery=galleries[book.id];
 if(!Array.isArray(gallery)||gallery.length!==book.illustratedWorkIDs.length||
    gallery.some((item,i)=>item.id!==book.illustratedWorkIDs[i]))
  throw Error('Gallery no longer matches publication source order: '+book.id);
 let lastIndex=-1;
 for(const id of book.illustratedWorkIDs){
  const index=book.orderedWorkIDs.indexOf(id);
  if(index<=lastIndex)throw Error('Illustrated work not ordered within contents: '+book.id);
  lastIndex=index;
 }
}
function entryVolume(name){
 if(name==='solstice'||name==='solstice-reading-01')return 'first-readings';
 return name;
}
const isContents=name=>bookById.has(name);
const isSurface=name=>name==='library'||isContents(name);
function owningContents(name){
 const member=books.find(book=>book.orderedWorkIDs.includes(name));
 if(member)return member.id;
 if(archivedOwners.has(name))return archivedOwners.get(name);
 if(name==='teatro'||name==='notes--the-door-is-a-score')return bookById.has('essays')?'essays':null;
 return null;
}
function adjacentVolume(name,step){
 if(name==='continuity'&&step>0)return 'library';
 const collection=books.find(book=>book.orderedWorkIDs.includes(name));
 if(!collection)return null;
 const sequence=collection.orderedWorkIDs;
 const at=sequence.indexOf(name)+step;
 return sequence[at]||(at<0?collection.id:null);
}
const surfaceOffsets={shelf:0,...Object.fromEntries(collectionOrder.map(id=>[id,0]))};
const galleryOffsets=Object.fromEntries(collectionOrder.map(id=>[id,0]));
const shelfContentsOffsets=Object.fromEntries(collectionOrder.map(id=>[id,0]));
