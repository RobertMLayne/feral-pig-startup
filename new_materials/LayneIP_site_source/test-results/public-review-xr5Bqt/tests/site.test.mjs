import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile,access} from 'node:fs/promises';
import {resolve} from 'node:path';
import {escapeHtml,matchesQuery,makeCsv,emailLink,filterPublished} from '../src/utils.mjs';
import {site,services,technologies,professionals} from '../content/site.mjs';
import {articles} from '../content/articles.mjs';
const root=resolve(import.meta.dirname,'..');
const mode=process.env.SITE_MODE||site.publicationMode;
const origin=process.env.SITE_ORIGIN||site.origin;

test('all internal page links and local public assets resolve',async()=>{
 const files=JSON.parse(await readFile(resolve(root,'.generated-pages.json'),'utf8'));const titles=new Set();
 for(const file of files){const html=await readFile(resolve(root,file),'utf8');const title=html.match(/<title>(.*?)<\/title>/)[1];assert.ok(!titles.has(title),`Duplicate title: ${file}`);titles.add(title);
  assert.equal([...html.matchAll(/<h1[ >]/g)].length,1,`${file}: one primary heading`);
  for(const [,href] of html.matchAll(/(?:href|src)="([^"]+)"/g)){
   if(!href.startsWith('/')||href.startsWith('//'))continue;
   const path=href.split(/[?#]/)[0];const local=path==='/'?'index.html':path.slice(1);
   await access(resolve(root,local)).catch(()=>access(resolve(root,'public',local))).catch(()=>assert.fail(`${file}: missing ${path}`));
  }
 }
 assert.equal(files.length,34+filterPublished(articles,mode).length);
});
test('related content references real records',()=>{
 const slugs=new Set(services.map(s=>s.slug));
 for(const s of services)for(const related of s.related)assert.ok(slugs.has(related),`${s.slug} -> ${related}`);
 for(const t of technologies)for(const s of t.services)assert.ok(slugs.has(s));
 assert.equal(professionals.length,1);assert.equal(professionals[0].registration,'82,283');
});
test('search handles accents, case and independent query terms',()=>{
 assert.ok(matchesQuery('Biotechnology & Pharmaceutical analysis','ANALYSIS bio'));
 assert.ok(matchesQuery('René scientific adviser','rene'));
 assert.ok(!matchesQuery('Patent prosecution','patent litigation'));
});
test('inquiry data remains plain text in a properly encoded email URL',()=>{
 const values={name:'A & B',service:'Patent preparation',summary:'A < B\nC & D #1?'};
 const url=new URL(emailLink(values));assert.equal(url.protocol,'mailto:');assert.equal(url.pathname,'robert@layneip.com');
 assert.ok(url.searchParams.get('body').includes(values.summary));assert.ok(url.searchParams.get('body').includes('Name: A & B'));
 assert.equal(escapeHtml('<img src=x onerror="bad">'),'&lt;img src=x onerror=&quot;bad&quot;&gt;');
});
test('CSV quotes data and neutralizes spreadsheet formula injection',()=>{
 const csv=makeCsv([{title:'=WEBSERVICE("example")',notes:'a,b\nnext'}],['title','notes']);
 assert.equal(csv,'"title","notes"\r\n"\'=WEBSERVICE(""example"")","a,b\nnext"');
});
test('draft practice guides never enter public builds or RSS',async()=>{
 assert.equal(filterPublished(articles,'public').length,0);assert.equal(filterPublished(articles,'private-review').length,3);
 const rss=await readFile(resolve(root,'public/feed.xml'),'utf8');
 for(const article of articles)assert.ok(!rss.includes(article.slug));
 const robots=await readFile(resolve(root,'public/robots.txt'),'utf8');
 if(mode==='private-review')assert.match(robots,/Disallow: \//);
 else {
  assert.ok(robots.includes('Sitemap: '+origin+'/sitemap.xml'));
  assert.ok(!robots.includes('Disallow: /'));
  const files=JSON.parse(await readFile(resolve(root,'.generated-pages.json'),'utf8'));
  const index=await readFile(resolve(root,'public/search-index.json'),'utf8');
  const sitemap=await readFile(resolve(root,'public/sitemap.xml'),'utf8');
  for(const article of articles.filter(a=>a.status!=='published')){
   const draft='insights/'+article.slug+'.html';
   assert.ok(!files.includes(draft));
   await assert.rejects(access(resolve(root,draft)),{code:'ENOENT'});
   assert.ok(!index.includes(article.slug));
   assert.ok(!sitemap.includes(article.slug));
  }
  for(const file of files){
   const html=await readFile(resolve(root,file),'utf8');
   assert.ok(html.includes('href="'+origin+(file==='index.html'?'/':'/'+file)+'"'),file+': canonical');
   assert.ok(html.includes('content="'+(file==='404.html'?'noindex, nofollow':'index, follow')+'"'),file+': robots');
  }
  const privacy=await readFile(resolve(root,'privacy.html'),'utf8');
  const legal=await readFile(resolve(root,'legal.html'),'utf8');
  assert.ok(!privacy.includes('This private edition'));
  assert.ok(!legal.includes('private review edition'));
 }
});
