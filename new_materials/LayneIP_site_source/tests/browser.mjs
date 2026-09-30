import {chromium} from 'playwright';
import AxeBuilder from '@axe-core/playwright';
import {createServer} from 'node:http';
import {readFile,mkdir} from 'node:fs/promises';
import {resolve,extname,relative,isAbsolute,sep,join} from 'node:path';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
const root=resolve(import.meta.dirname,'../dist');
const reports=resolve(import.meta.dirname,'../test-results');await mkdir(reports,{recursive:true});
const types={'.html':'text/html','.js':'text/javascript','.json':'application/json','.css':'text/css','.svg':'image/svg+xml','.woff':'font/woff','.woff2':'font/woff2'};
const server=createServer(async(req,res)=>{try{let path=decodeURIComponent(new URL(req.url,'http://localhost').pathname);if(path==='/')path='/index.html';const file=resolve(root,'.'+path);const local=relative(root,file);if(local==='..'||local.startsWith('..'+sep)||isAbsolute(local))throw Error();const bytes=await readFile(file);res.writeHead(200,{'Content-Type':types[extname(file)]||'application/octet-stream'});res.end(bytes);}catch{res.writeHead(404);res.end('Not found');}});
await new Promise(ok=>server.listen(0,'127.0.0.1',ok));
const origin=`http://127.0.0.1:${server.address().port}`;
let browser;
const errors=[];
try{
 browser=await chromium.launch({...(process.env.LAYNE_TEST_BROWSER?{executablePath:process.env.LAYNE_TEST_BROWSER}:{}),args:['--disable-dev-shm-usage'],headless:true});
 const context=await browser.newContext({viewport:{width:1440,height:1000},permissions:['clipboard-read','clipboard-write']});
 const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));
 await page.goto(origin);await page.evaluate(()=>document.fonts.ready);
 await page.screenshot({path:join(reports,'home-desktop.png'),fullPage:true});
 const routes=['/','/services.html','/technologies.html','/professionals.html','/professionals/robert-m-layne.html','/contact.html','/insights.html','/systems/evidence-manifest.html'];
 for(const route of routes){await page.goto(origin+route);const results=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();assert.deepEqual(results.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)})),[],`Accessibility: ${route}`);}
 await page.goto(origin+'/services.html');await page.getByRole('button',{name:'Analyze',exact:true}).click();assert.equal(await page.locator('[data-service-group]:visible').count(),3);
 await page.goto(origin+'/professionals.html');await page.locator('[data-professional-search]').fill('unknown person');assert.equal(await page.locator('[data-professional-card]:visible').count(),0);assert.ok(await page.locator('[data-directory-empty]').isVisible());await page.getByRole('button',{name:'Clear filters'}).click();assert.equal(await page.locator('[data-professional-card]:visible').count(),1);
 await page.getByRole('button',{name:'Search the website',exact:true}).click();await page.locator('#site-search-input').fill('office action');await page.locator('.search-results a').first().waitFor();assert.match(await page.locator('.search-results').innerText(),/Patent prosecution/);await page.keyboard.press('Escape');await page.locator('#site-search').waitFor({state:'hidden'});
 await page.goto(origin+'/insights.html');await page.locator('[data-insight-filter]').selectOption('Scientific research');assert.equal(await page.locator('[data-filter-item]:visible').count(),2);
 await page.goto(origin+'/contact.html?service=Patent%20preparation');assert.equal(await page.locator('[name=service]').inputValue(),'Patent preparation');
 await page.locator('[name=name]').fill('Test Inventor');await page.locator('[name=email]').fill('inventor@example.com');await page.locator('[name=summary]').fill('A non-confidential test inquiry: <script>unsafe()</script> & research.');await page.locator('[name=acknowledged]').check();await page.getByRole('button',{name:'Prepare email'}).click();assert.ok(await page.locator('#brief-result').isVisible());const mail=new URL(await page.locator('[data-open-email]').getAttribute('href'));assert.match(mail.searchParams.get('body'),/Test Inventor/);assert.equal(await page.locator('#brief-result script').count(),0);assert.equal(await page.locator('[data-brief-status]').innerText(),'No message has been sent.');await page.getByRole('button',{name:'Copy brief',exact:true}).click();assert.match(await page.evaluate(()=>navigator.clipboard.readText()),/Test Inventor/);
 await page.goto(origin+'/systems/evidence-manifest.html');assert.ok(await page.getByRole('button',{name:'Export JSON'}).isDisabled());await page.locator('[name=title]').fill('=1+1');await page.locator('[name=locator]').fill('Figure 4');await page.locator('[name=sourceFile]').setInputFiles({name:'sample.txt',mimeType:'text/plain',buffer:Buffer.from('sample evidence')});await page.getByRole('button',{name:'Add source'}).click();await page.locator('[data-manifest-rows] tr').waitFor();const expected=createHash('sha256').update('sample evidence').digest('hex');assert.match(await page.locator('[data-manifest-rows]').innerText(),new RegExp(expected));
 const downloadPromise=page.waitForEvent('download');await page.getByRole('button',{name:'Export CSV'}).click();const dl=await downloadPromise;const csv=await readFile(await dl.path(),'utf8');assert.match(csv,/"'=1\+1"/);await page.getByRole('button',{name:'Remove =1+1'}).click();assert.equal(await page.locator('[data-manifest-rows] tr').count(),0);
 const mobile=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});const mp=await mobile.newPage();
 for(const route of ['/','/services.html','/professionals.html','/contact.html','/systems/evidence-manifest.html']){await mp.goto(origin+route);assert.ok(await mp.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),`Horizontal overflow ${route}`);}
 await mp.goto(origin);await mp.evaluate(()=>document.fonts.ready);await mp.screenshot({path:join(reports,'home-mobile.png'),fullPage:true});await mp.getByRole('button',{name:'Menu',exact:false}).click();assert.ok(await mp.locator('#site-nav').isVisible());await mp.locator('#site-nav').getByRole('link',{name:'Professionals',exact:true}).click();assert.ok(mp.url().endsWith('/professionals.html'));await mp.screenshot({path:join(reports,'professionals-mobile.png'),fullPage:true});
 const noJS=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844}});const np=await noJS.newPage();await np.goto(origin+'/services.html');assert.equal(await np.locator('.service-card:visible').count(),11);assert.ok(await np.locator('#site-nav').isVisible());
 for(const route of ['/contact.html','/systems/evidence-manifest.html']){await np.goto(origin+route);assert.ok(await np.locator('[data-local-fields]').isDisabled());assert.ok(await np.locator('form button[type=submit]').isDisabled());}
 assert.deepEqual(errors,[]);console.log('PASS: desktop/mobile layout, accessibility, directory, site search, insights, consultation, SHA-256/CSV, no-JavaScript content.');
}finally{await browser?.close();await new Promise(ok=>server.close(ok));}
