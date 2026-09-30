import {mkdir,writeFile,readFile,rm} from 'node:fs/promises';
import {dirname,resolve} from 'node:path';
import {site,services,technologies,professionals,publications} from '../content/site.mjs';
import {articles} from '../content/articles.mjs';
import {escapeHtml as e,filterPublished} from '../src/utils.mjs';
import * as t from '../src/templates.mjs';

const root=resolve(import.meta.dirname,'..');
const mode=process.env.SITE_MODE||site.publicationMode;
if(!['private-review','public'].includes(mode))throw new Error('SITE_MODE must be private-review or public');
const origin=process.env.SITE_ORIGIN||site.origin;
if(!/^https:\/\/[a-z0-9.-]+$/i.test(origin))throw new Error('SITE_ORIGIN must be a trusted HTTPS origin without a trailing slash');
const config={origin,private:mode==='private-review'};
const visibleArticles=filterPublished(articles,mode);
const pages=[];
const add=(path,title,description,body,active='',extra={})=>pages.push({path,title,description,body,active,...extra});
add('/','Layne Intellectual Property','Patent preparation, prosecution, and technical analysis with Robert M. Layne, Ph.D., U.S. Patent Agent.',t.home());
add('/services.html','Services','Patent-agent services, technical analysis for counsel, and research workflows.',t.servicesIndex(),'services');
services.forEach(s=>add(`/services/${s.slug}.html`,s.name,s.short,t.serviceDetail(s),'services'));
add('/technologies.html','Technologies','Patent and technical work across software, semiconductors, wireless systems, life sciences, chemistry, and medical research.',t.technologyIndex(),'technologies');
technologies.forEach(x=>add(`/technologies/${x.slug}.html`,x.name,x.summary,t.technologyDetail(x),'technologies'));
add('/professionals.html','Professionals','Meet the professionals at Layne Intellectual Property. Search by name and technical discipline.',t.peopleIndex(),'professionals');
professionals.forEach(p=>add(`/professionals/${p.slug}.html`,p.name,p.bio[0],t.profile(p),'professionals',{kind:'ProfilePage'}));
add('/insights.html','Insights','Published writing, scientific research, and practice notes from Layne Intellectual Property.',t.insightsIndex(visibleArticles),'insights');
visibleArticles.forEach(a=>add(`/insights/${a.slug}.html`,a.title,a.summary,t.articlePage(a),'insights',{noindex:a.status!=='published'}));
add('/systems.html','Systems','Research tools and methods for traceable evidence and reproducible technical work.',t.systems(),'systems');
add('/systems/evidence-manifest.html','Evidence Manifest','Create a source index, calculate file checksums locally, and export your evidence manifest.',t.evidenceTool(),'systems');
add('/contact.html','Contact','Contact Robert M. Layne, Ph.D., to discuss a patent or technical question. Prepare a non-confidential inquiry.',t.contact());
add('/about.html','About the practice','A patent-agent and scientific advisory practice built around clear questions and a reviewable technical record.',t.about());
add('/faq.html','Frequently asked questions','Questions about patent agents, attorney collaboration, initial inquiries, and engagement scope.',t.faqPage());
add('/resources.html','Resources','Practical guides, a browser-based evidence tool, and official USPTO resources.',t.resourcesPage(visibleArticles));
for(const [key,title] of [['legal','Legal notice'],['privacy','Privacy'],['accessibility','Accessibility']]){
  add(`/${key}.html`,title,`${title} for the Layne Intellectual Property website.`,`${t.hero('The practice',title,'Updated '+site.updated,true)}<section class="section-pad policy-layout detail-copy">${t.policyBodies(config)[key]}</section>`);
}
const mapBody=()=>`${t.hero('Navigation','Site map','Find a service, professional, technology, publication, or resource.',true)}<section class="section-pad sitemap-grid">${[['The practice',pages.filter(p=>!p.path.slice(1).includes('/')&&!['/sitemap.html','/404.html'].includes(p.path))],['Services',pages.filter(p=>p.path.startsWith('/services/'))],['Technologies',pages.filter(p=>p.path.startsWith('/technologies/'))],['People, insights & tools',pages.filter(p=>/^\/(professionals|insights|systems)\//.test(p.path))]].map(([label,items])=>`<section><h2>${label}</h2><ul>${items.map(p=>`<li><a href="${p.path}">${e(p.title)}</a></li>`).join('')}</ul></section>`).join('')}</section>`;
add('/sitemap.html','Site map','All pages of the Layne Intellectual Property website.',mapBody());
add('/404.html','Page not found','The requested page could not be found.',`${t.hero('404 / Page not found','Let’s get you<br>to the right place.','This address may have changed. Search the website or choose a destination below.',true)}<section class="section-pad error-links">${t.button('/','Go to the home page')}${t.link('/services.html','Explore services')}${t.link('/sitemap.html','Open the site map')}<button type="button" class="text-button" data-open-search>Search the website</button></section>`,'',{noindex:true});

// Remove only files produced by an earlier generation (e.g., drafts omitted in public mode).
const manifestPath=resolve(root,'.generated-pages.json');
const previous=JSON.parse(await readFile(manifestPath,'utf8').catch(()=> '[]'));
const filenames=pages.map(p=>p.path==='/'?'index.html':p.path.slice(1));
for(const filename of previous.filter(p=>!filenames.includes(p))) {
  if(/^(insights|services|technologies|professionals|systems)\/[a-z0-9-]+\.html$/.test(filename))await rm(resolve(root,filename),{force:true});
}
for(const p of pages){const filename=resolve(root,p.path==='/'?'index.html':p.path.slice(1));await mkdir(dirname(filename),{recursive:true});await writeFile(filename,t.layout(p,config));}
await writeFile(manifestPath,JSON.stringify(filenames,null,2)+'\n');
await mkdir(resolve(root,'public'),{recursive:true});
const index=pages.filter(p=>!['/404.html','/sitemap.html','/legal.html','/privacy.html','/accessibility.html'].includes(p.path)).map(({path,title,description,active,body})=>({path,title,description,category:active||'The practice',keywords:body.replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim()}));
await writeFile(resolve(root,'public/search-index.json'),JSON.stringify(index));
const xml=s=>e(s).replaceAll('&#39;','&apos;');
await writeFile(resolve(root,'public/sitemap.xml'),'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+pages.filter(p=>!p.noindex).map(p=>`<url><loc>${xml(origin+p.path)}</loc><lastmod>${site.updated}</lastmod></url>`).join('')+'</urlset>');
await writeFile(resolve(root,'public/robots.txt'),config.private?'User-agent: *\nDisallow: /\n':`User-agent: *\nAllow: /\nSitemap: ${origin}/sitemap.xml\n`);
// Unapproved drafts never enter the syndication feed, including in private review mode.
const feedItems=[...publications,...articles.filter(a=>a.status==='published').map(a=>({...a,url:origin+'/insights/'+a.slug+'.html'}))].sort((a,b)=>b.date.localeCompare(a.date));
await writeFile(resolve(root,'public/feed.xml'),'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Layne Intellectual Property — Insights</title><link>'+xml(origin+'/insights.html')+'</link><description>Published writing and scientific research.</description><language>en-us</language>'+feedItems.map(p=>`<item><title>${xml(p.title)}</title><link>${xml(p.url)}</link><guid isPermaLink="true">${xml(p.url)}</guid><description>${xml(p.summary)}</description><pubDate>${new Date(p.date+'T12:00:00Z').toUTCString()}</pubDate></item>`).join('')+'</channel></rss>');
await writeFile(resolve(root,'public/robert-m-layne.vcf'),['BEGIN:VCARD','VERSION:3.0','N:Layne;Robert;M.;;Ph.D.','FN:Robert M. Layne, Ph.D.','ORG:Layne Intellectual Property','TITLE:Patent Agent & Scientific Advisor','EMAIL;TYPE=WORK:robert@layneip.com','TEL;TYPE=WORK,VOICE:+15712740684','URL:'+origin,'NOTE:U.S. Patent Agent - Registration No. 82\,283','END:VCARD',''].join('\r\n'));
console.log(`Generated ${pages.length} pages (${mode}) for ${origin}`);
