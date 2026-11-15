// Offline JavaScript/DOM fixtures only. No browser or rendering is exercised.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const html = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8');
const context = JSON.parse(html.match(/<script id="context" type="application\/json">([\s\S]*?)<\/script>/)[1]);
const source = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n');
class Element {
  constructor(tag='div') { this.tag=tag;this.children=[];this.dataset={};this.textContent='';this.events={};this.value='';this.classes=new Set();this.classList={toggle:(name,on)=>on?this.classes.add(name):this.classes.delete(name)}; }
  append(child) { this.children.push(child); }
  replaceChildren() { this.children=[]; }
  addEventListener(name,fn) { this.events[name]=fn; }
  setAttribute(name,value) { this[name]=value; }
  get rows() { return this.children.filter(x=>x.tag==='tr'); }
}
const ids=new Map();
for(const id of ['context','column','column-detail','mapping','regions','processing','assembly','proxy-note','correspondence','reference-summary','full-count','observed-count','intersection-count','previous','next','reference','research-observation','scene','scene-image','scene-caption','motion'])ids.set(id,new Element());
for(const id of ['model-observation','science-detail','sequence-scores'])ids.set(id,new Element());
ids.get('context').textContent=JSON.stringify(context);
const buttons=[154,173].map(column=>{const x=new Element('button');x.dataset.column=String(column);return x;});
const document={getElementById:id=>{assert(ids.has(id),id);return ids.get(id);},createElement:tag=>new Element(tag),querySelectorAll:selector=>{assert.equal(selector,'[data-column]');return buttons;}};
vm.runInNewContext(source,{document});
const text=element=>element.textContent+' '+element.children.map(text).join(' ');
assert.equal(Number(ids.get('full-count').textContent),202);
assert.equal(Number(ids.get('observed-count').textContent),162);
assert.equal(Number(ids.get('intersection-count').textContent),159);
assert.match(text(ids.get('column-detail')),/1\/30 coverage/);
assert.match(text(ids.get('column-detail')),/alignment-only/);
ids.get('motion').events.click();assert.match(ids.get('scene-image').src,/coverage-evidence.gif$/);
ids.get('scene').events.change({target:{value:'ospc-dimer'}});
assert.match(ids.get('scene-image').src,/ospc-dimer.png$/);assert.equal(ids.get('motion')['aria-pressed'],'false');
assert.match(text(ids.get('scene-caption')),/proxy/);
ids.get('motion').events.click();ids.get('motion').events.click();assert.match(ids.get('scene-image').src,/\.png$/);
assert.match(text(ids.get('research-observation')),/1\/30 coverage/);
assert.equal(ids.get('mapping').rows.length,174);
buttons[1].events.click();assert.equal(Number(ids.get('column').value),173);
ids.get('previous').events.click();assert.equal(Number(ids.get('column').value),172);
ids.get('column').events.change({target:{value:500}});assert.equal(Number(ids.get('column').value),218);
ids.get('reference').events.change({target:{value:'1G5Z'}});
assert.equal(ids.get('mapping').rows.length,164);
assert.match(text(ids.get('assembly')),/symmetry/);
assert.match(text(ids.get('proxy-note')),/NOT CALCULATED/);
buttons[0].events.click();assert.match(text(ids.get('column-detail')),/1\/30 coverage/);
assert.match(text(ids.get('column-detail')),/alignment-only/);
assert(!html.includes('__CONTEXT_JSON__'));
assert(!/<(?:script|link|img)[^>]*(?:src|href)=["']https?:/i.test(html));
assert.equal(ids.get('sequence-scores').rows.length,30);
assert.match(text(ids.get('science-detail')),/unknown/);
assert.match(text(ids.get('science-detail')),/3.17222 nats/);
assert.match(text(ids.get('science-detail')),/not eligible/);
ids.get('column').events.change({target:{value:58}});
assert.match(text(ids.get('science-detail')),/3.96498 nats/);
assert.match(text(ids.get('science-detail')),/yes, observed/);
assert.match(text(ids.get('science-detail')),/79.11/);
ids.get('column').events.change({target:{value:177}});
assert.match(text(ids.get('science-detail')),/4.01135 nats/);
assert.match(text(ids.get('science-detail')),/no, observed/);
assert.match(text(ids.get('science-detail')),/loss 0.00/);
assert.match(text(ids.get('science-detail')),/1GGQ A/); // secondary map never relabels primary values
for(const c of context.spark_science.evidence.columns){
  ids.get('column').events.change({target:{value:c.alignment_column}});
  const display=text(ids.get('science-detail'));
  assert(display.includes(c.mean_masked_nll_nats.toFixed(5)+' nats'));
  if(c.reference_1GGQ_A_contact_4_5_A===null)assert.match(display,/contact.*unknown/);
}
console.log('PASS: offline UI handlers, all 218 saved NLLs, 30 sequence rows, null/false/zero, navigation and reference switching. Browser rendering NOT tested.');
