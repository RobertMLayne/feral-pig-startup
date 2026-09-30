import test from 'node:test';
import assert from 'node:assert/strict';
import {cp,mkdir,mkdtemp,readFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {execFileSync} from 'node:child_process';

const root=resolve(import.meta.dirname,'..');

test('a public generation removes earlier draft pages and passes the full source checks',async()=>{
  const reports=resolve(root,'test-results');
  await mkdir(reports,{recursive:true});
  // Retain this isolated source output for review; never change the active private edition.
  const output=await mkdtemp(resolve(reports,'public-review-'));
  for(const name of ['scripts','src','content','public']){
    await cp(resolve(root,name),resolve(output,name),{recursive:true});
  }
  await mkdir(resolve(output,'tests'));
  await cp(resolve(root,'tests/site.test.mjs'),resolve(output,'tests/site.test.mjs'));
  await cp(resolve(root,'package.json'),resolve(output,'package.json'));
  const environment={...process.env};
  // A separate Node test runner must not inherit the parent's child-test marker.
  delete environment.NODE_TEST_CONTEXT;
  const generate=mode=>execFileSync(process.execPath,['scripts/generate.mjs'],{
    cwd:output,env:{...environment,SITE_MODE:mode,SITE_ORIGIN:'https://layneip.com'},encoding:'utf8'
  });
  generate('private-review');
  assert.equal(JSON.parse(await readFile(resolve(output,'.generated-pages.json'),'utf8')).length,37);
  generate('public');
  execFileSync(process.execPath,['--test','tests/site.test.mjs'],{
    cwd:output,env:{...environment,SITE_MODE:'public',SITE_ORIGIN:'https://layneip.com'},encoding:'utf8'
  });
  console.log('Public source review: '+output);
});
