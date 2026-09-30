import '@fontsource/manrope/latin-400.css';
import '@fontsource/manrope/latin-500.css';
import '@fontsource/manrope/latin-600.css';
import '@fontsource/manrope/latin-700.css';
import '@fontsource/newsreader/latin-400.css';
import '@fontsource/newsreader/latin-400-italic.css';
import '@fontsource/dm-mono/latin-400.css';
import './styles.css';
import {matchesQuery,makeBrief,emailLink,makeCsv} from './utils.mjs';

document.documentElement.classList.add('js');
const $=(q,root=document)=>root.querySelector(q);
const $$=(q,root=document)=>[...root.querySelectorAll(q)];
const menu=$('.menu-toggle');
const closeMenu=()=>{menu?.setAttribute('aria-expanded','false');$('#site-nav')?.classList.remove('open');};
menu?.addEventListener('click',()=>{const open=menu.getAttribute('aria-expanded')!=='true';menu.setAttribute('aria-expanded',String(open));$('#site-nav').classList.toggle('open',open);});
document.addEventListener('keydown',e=>{if(e.key==='Escape'){closeMenu();const dialog=$('#site-search');if(dialog?.open){e.preventDefault();dialog.close();}}});
document.addEventListener('click',e=>{if(!e.target.closest('.site-header'))closeMenu();});
$$('#site-nav a').forEach(a=>a.addEventListener('click',closeMenu));

const search=$('#site-search');let searchIndex;let searchLoading;
const renderSearch=()=>{
  const query=$('#site-search-input').value.trim();
  const entries=(searchIndex||[]).filter(p=>matchesQuery(p.title+' '+p.description+' '+p.category+' '+p.keywords,query)).slice(0,12);
  const results=$('.search-results');results.replaceChildren();
  for(const p of entries){const li=document.createElement('li'),a=document.createElement('a'),h=document.createElement('strong'),desc=document.createElement('span');a.href=p.path;h.textContent=p.title;desc.textContent=p.description;a.append(h,desc);li.append(a);results.append(li);}
  $('.search-status').textContent=!query?'Browse popular pages or type a search.':entries.length?`${entries.length}${entries.length===12?' or more':''} matching pages`:'No matching pages. Try a different term.';
};
$$('[data-open-search]').forEach(b=>b.addEventListener('click',async()=>{
  closeMenu();search.showModal();$('#site-search-input').focus();
  if(searchIndex){renderSearch();return;}
  $('.search-status').textContent='Loading search…';
  try{searchLoading||=fetch('/search-index.json').then(r=>{if(!r.ok)throw Error();return r.json();});searchIndex=await searchLoading;renderSearch();}
  catch{searchLoading=null;$('.search-status').textContent='Search could not load. Please use the navigation or site map.';}
}));
$('[data-close-search]')?.addEventListener('click',()=>search.close());
search?.addEventListener('click',e=>{if(e.target===search){const r=search.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)search.close();}});
$('#site-search-input')?.addEventListener('input',renderSearch);

$$('[data-service-filter]').forEach(b=>b.addEventListener('click',()=>{
  let count=0;$$('[data-service-group]').forEach(card=>{card.hidden=b.dataset.serviceFilter!=='all'&&b.dataset.serviceFilter!==card.dataset.serviceGroup;if(!card.hidden)count++;});
  $$('[data-service-filter]').forEach(x=>{x.classList.toggle('active',x===b);x.setAttribute('aria-pressed',String(x===b));});$('[data-service-count]').textContent=`${count} services`;
}));

function setupFilter({root,search,select,items,count,empty,reset,category,word}){
  const container=$(root);if(!container)return;
  const run=()=>{let n=0;const query=$(search,container).value,chosen=$(select,container).value;$$(items,container).forEach(card=>{const categories=(card.dataset[category]||'').split('|');card.hidden=!matchesQuery(card.dataset.search,query)||(chosen!=='all'&&!categories.includes(chosen));if(!card.hidden)n++;});$(count,container).textContent=`${n} ${word}${n===1?'':'s'}`;$(empty,container).hidden=n!==0;};
  $(search,container).addEventListener('input',run);$(select,container).addEventListener('change',run);
  $(reset,container).addEventListener('click',()=>{$(search,container).value='';$(select,container).value='all';run();$(search,container).focus();});
}
setupFilter({root:'[data-directory]',search:'[data-professional-search]',select:'[data-professional-filter]',items:'[data-professional-card]',count:'[data-directory-count]',empty:'[data-directory-empty]',reset:'[data-directory-reset]',category:'disciplines',word:'professional'});
setupFilter({root:'[data-insights]',search:'[data-insight-search]',select:'[data-insight-filter]',items:'[data-filter-item]',count:'[data-insight-count]',empty:'[data-insight-empty]',reset:'[data-insight-reset]',category:'category',word:'item'});

async function copy(text,status){try{await navigator.clipboard.writeText(text);status.textContent='Copied to clipboard.';}catch{status.textContent='Clipboard unavailable. Select and copy the text, or download it.';}}
function download(text,filename,type){const blob=new Blob([text],{type}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=filename;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);}
$$('[data-print]').forEach(b=>b.addEventListener('click',()=>window.print()));
$('[data-copy-link]')?.addEventListener('click',()=>copy(location.href,$('[data-share-status]')));

const contact=$('#consultation-form');let brief='';
if(contact){
  const params=new URLSearchParams(location.search);
  for(const name of ['service','technology']){const field=contact.elements.namedItem(name);if([...field.options].some(o=>o.value===params.get(name)))field.value=params.get(name);}
  contact.addEventListener('submit',event=>{event.preventDefault();if(!contact.reportValidity())return;const values=Object.fromEntries(new FormData(contact));brief=makeBrief(values);$('[data-brief-preview]').textContent=brief;$('[data-open-email]').href=emailLink(values);$('#brief-result').hidden=false;$('[data-brief-status]').textContent='No message has been sent.';$('#brief-result').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'start'});});
  $('[data-copy-brief]').addEventListener('click',()=>copy(brief,$('[data-brief-status]')));
  $('[data-download-brief]').addEventListener('click',()=>download(brief,'layne-ip-consultation.txt','text/plain;charset=utf-8'));
  $('[data-local-fields]',contact).disabled=false;
}

const manifest=$('#manifest-form');
if(manifest){
  const rows=[];let nextId=1;
  const status=$('#manifest-status');
  const render=()=>{
    const body=$('[data-manifest-rows]');body.replaceChildren();
    for(const row of rows){const tr=document.createElement('tr');
      for(const field of ['title','locator','status','sha256']){const td=document.createElement('td');if(field==='title'){const b=document.createElement('strong'),small=document.createElement('small');b.textContent=row.title;small.textContent=row.id+' · '+row.type;td.append(b,small);}else if(field==='sha256'){const code=document.createElement('code');code.textContent=row.sha256||'Not calculated';td.append(code);}else td.textContent=row[field];tr.append(td);}
      const action=document.createElement('td'),remove=document.createElement('button');remove.type='button';remove.className='text-button';remove.textContent='Remove';remove.setAttribute('aria-label','Remove '+row.title);remove.addEventListener('click',()=>{rows.splice(rows.indexOf(row),1);render();status.textContent='Source removed.';});action.append(remove);tr.append(action);body.append(tr);
    }
    $('[data-manifest-count]').textContent=`(${rows.length})`;$('[data-manifest-empty]').hidden=rows.length!==0;$$('[data-export]').forEach(b=>b.disabled=rows.length===0);
  };
  manifest.addEventListener('submit',async event=>{
    event.preventDefault();if(!manifest.reportValidity())return;const fields=Object.fromEntries(new FormData(manifest)),file=fields.sourceFile;
    if(!fields.title.trim()||!fields.locator.trim()){status.textContent='Enter a source title and a locator; blank spaces are not sufficient.';return;}
    if(file?.size>20*1024*1024){status.textContent='This file exceeds 20 MB. Choose a smaller file or add the source without a checksum.';return;}
    const submit=$('[type="submit"]',manifest);submit.disabled=true;status.textContent=file?.name?'Calculating the checksum locally…':'';
    try{let sha256='';if(file?.name){if(!crypto.subtle)throw Error('Checksum calculation needs a secure browser connection.');sha256=[...new Uint8Array(await crypto.subtle.digest('SHA-256',await file.arrayBuffer()))].map(n=>n.toString(16).padStart(2,'0')).join('');}
      rows.push({id:'SRC-'+String(nextId++).padStart(3,'0'),title:fields.title.trim(),type:fields.type,locator:fields.locator.trim(),status:fields.status,notes:fields.notes.trim(),filename:file?.name||'',bytes:file?.name?file.size:'',sha256,capturedAt:new Date().toISOString()});manifest.reset();render();status.textContent='Source added. Export your manifest to save it.';
    }catch(error){status.textContent=error.message||'The file could not be read. Try again or add the source without a file.';}finally{submit.disabled=false;}
  });
  $('[data-example]').addEventListener('click',()=>{rows.push({id:'SRC-'+String(nextId++).padStart(3,'0'),title:'Illustrative technical reference',type:'Technical documentation',locator:'Example only — Figure 4, paragraph 23',status:'Not reviewed',notes:'Demonstration entry. Replace with an actual source before relying on this manifest.',filename:'',bytes:'',sha256:'',capturedAt:new Date().toISOString()});render();status.textContent='Illustrative example added.';});
  $$('[data-export]').forEach(b=>b.addEventListener('click',()=>{if(!rows.length)return;const json=b.dataset.export==='json';const output=json?JSON.stringify({format:'layne-ip-evidence-manifest',version:1,exportedAt:new Date().toISOString(),sources:rows},null,2):makeCsv(rows,['id','title','type','locator','status','notes','filename','bytes','sha256','capturedAt']);download(output,'evidence-manifest.'+(json?'json':'csv'),json?'application/json':'text/csv;charset=utf-8');status.textContent=`${json?'JSON':'CSV'} download prepared. Check your browser’s downloads.`;}));
  render();
  $('[data-local-fields]',manifest).disabled=false;
}
