const q = document.querySelector('#q');
const cat = document.querySelector('#cat');
const cards = document.querySelector('#cards');
const count = document.querySelector('#count');
const empty = document.querySelector('#empty');
let tools = [];
function el(tag, className, text) { const node = document.createElement(tag); if(className) node.className=className; if(text!==undefined) node.textContent=text; return node; }
function render() {
  const term=q.value.toLocaleLowerCase().trim();
  const matches=tools.filter(t=>(!cat.value||t.category===cat.value)&&[t.name,t.category,t.summary,...(t.tags||[])].join(' ').toLocaleLowerCase().includes(term));
  cards.replaceChildren(); count.textContent=`${matches.length} tools`; empty.hidden=matches.length!==0;
  for(const t of matches){
    const card=el('article','tool'); card.append(el('span','pill',t.category),el('h3','',t.name),el('p','',t.summary),el('div','price',t.pricing||'Check vendor for pricing'));
    const a=el('a','', 'Visit official website ↗'); a.href=t.url; a.target='_blank'; a.rel='noopener noreferrer nofollow'; card.append(a); cards.append(card);
  }
}
q.addEventListener('input',render);cat.addEventListener('change',render);
fetch('tools.json').then(r=>{if(!r.ok)throw Error('Failed to load tool database');return r.json()}).then(data=>{tools=data;render();populateComparison();renderFinder()}).catch(()=>{count.textContent='Unavailable';empty.hidden=false;empty.textContent='Unable to load tools. Serve the site through a local web server.'});

// Explicit editorial task fit; never represented as measured performance rankings.
const fit = {
 'local-ai': [{id:'ollama',levels:['beginner','intermediate','advanced'],reason:'Runs supported open models locally; requires installation and suitable hardware.'}],
 'agent': [
  {id:'langgraph',levels:['intermediate','advanced'],reason:'Code-first framework for stateful agent workflows.'},
  {id:'ollama',levels:['beginner','intermediate','advanced'],reason:'Provides local model serving for an agent, but is not an agent builder.'}
 ],
 'code': [
  {id:'continue',levels:['beginner','intermediate','advanced'],reason:'Coding assistant integrated into development workflows.'},
  {id:'aider',levels:['intermediate','advanced'],reason:'Terminal-first coding workflow; familiarity with Git is helpful.'}
 ],
 'media': [{id:'comfyui',levels:['intermediate','advanced'],reason:'Node-based generative media workflows; setup and models require learning.'}]
};
const needs = {
 ollama:'Install locally; hardware and model selection matter.',
 langgraph:'Python or JavaScript programming skills recommended.',
 continue:'An editor and compatible model/provider configuration are needed.',
 aider:'Terminal, Git, and a supported model/provider are needed.',
 comfyui:'Node-based workflow setup, models, and sufficient compute are needed.'
};
function renderFinder(){
 const task=document.querySelector('#task').value, level=document.querySelector('#level').value;
 const budget=document.querySelector('#budget').value, out=document.querySelector('#recommendations');
 out.replaceChildren();
 const choices=(fit[task]||[]).map(f=>({...f,tool:tools.find(t=>t.id===f.id)})).filter(f=>f.tool);
 const suitable=choices.filter(f=>f.levels.includes(level));
 if(!suitable.length){
  out.append(el('p','muted','No beginner-friendly match has been verified in our current catalog for this task. We will not recommend an advanced framework as beginner-friendly.'));
  if(choices.length)out.append(el('p','muted','Technical options exist, but require additional setup or coding knowledge. Try Intermediate to explore them.'));
  return;
 }
 suitable.forEach((f,i)=>{
  const t=f.tool,box=el('article','match');
  box.append(el('span','pill',i===0?'Suggested starting point':'Also relevant'),el('h3','',t.name),el('p','',f.reason),el('p','muted','Requirements: '+needs[t.id]));
  if(budget==='free')box.append(el('p','muted','Budget check: '+(t.pricing||'Verify vendor pricing')+'. Free software does not guarantee zero total cost.'));
  const a=el('a','','Official website ↗');a.href=t.url;a.target='_blank';a.rel='noopener noreferrer nofollow';box.append(a);out.append(box);
 });
}
function populateComparison(){
 const a=document.querySelector('#compare-a'),b=document.querySelector('#compare-b');
 for(const sel of [a,b]){sel.replaceChildren();tools.forEach(t=>{const o=document.createElement('option');o.value=t.id;o.textContent=t.name;sel.append(o);});}
 if(tools.length>1)b.selectedIndex=1;
 renderComparison();
}
function renderComparison(){
 const out=document.querySelector('#comparison');out.replaceChildren();
 const a=tools.find(t=>t.id===document.querySelector('#compare-a').value),b=tools.find(t=>t.id===document.querySelector('#compare-b').value);
 if(!a||!b)return;
 if(a.id===b.id){out.append(el('p','muted','Choose two different tools to compare.'));return;}
 const pairs={
  'langgraph|ollama':'These tools complement each other: LangGraph orchestrates agent workflows, while Ollama can provide locally served models.',
  'aider|continue':'Both help with coding. Continue is designed around editor workflows; Aider focuses on terminal-based pair programming.',
 };
 const key=[a.id,b.id].sort().join('|');
 const insight=pairs[key]||'These tools may serve different workflows. Compare their stated purposes and requirements; no performance winner is claimed.';
 const note=el('p','comparison-insight',insight);out.append(note);
 for(const t of [a,b]){
  const card=el('article','match');card.append(el('h3','',t.name),el('p','',t.summary),el('p','muted','Category: '+t.category),el('p','muted','Cost notes: '+(t.pricing||'Verify with vendor')),el('p','muted','Setup: '+(needs[t.id]||'Check official documentation')),el('p','muted','Tags: '+(t.tags||[]).join(', ')));
  const link=el('a','','Official source ↗');link.href=t.url;link.target='_blank';link.rel='noopener noreferrer nofollow';card.append(link);out.append(card);
 }
}
['task','level','budget'].forEach(id=>document.getElementById(id).addEventListener('change',renderFinder));
['compare-a','compare-b'].forEach(id=>document.getElementById(id).addEventListener('change',renderComparison));
