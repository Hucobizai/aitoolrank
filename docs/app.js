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

// Curated task-fit mapping. These are editorial rules, not quality ratings.
const taskFits = {
  'local-ai': {ollama:'Runs supported models on your own machine',continue:'Can connect coding workflows to compatible model providers'},
  'agent': {langgraph:'Designed for stateful agent workflows',ollama:'Can serve local models used by an agent'},
  'code': {continue:'Designed for coding assistance in developer workflows',aider:'Supports terminal-based pair programming'},
  'media': {comfyui:'Node-based workflows for generative images and compatible video models'}
};
const beginnerNotes = {
  ollama:'Local setup and suitable hardware are needed.',
  langgraph:'Requires programming knowledge; not a no-code builder.',
  continue:'Works best when you already use development tools.',
  aider:'Terminal and Git familiarity are helpful.',
  comfyui:'Node graphs and model setup involve a learning curve.'
};
function renderFinder(){
  const task=document.querySelector('#task').value;
  const level=document.querySelector('#level').value;
  const budget=document.querySelector('#budget').value;
  const out=document.querySelector('#recommendations');
  out.replaceChildren();
  const fits=taskFits[task]||{};
  const matched=Object.keys(fits).map(id=>tools.find(t=>t.id===id)).filter(Boolean);
  if(!matched.length){out.append(el('p','muted','No approved tools match yet.'));return;}
  matched.forEach((t,i)=>{
    const box=el('article','match');
    box.append(el('span','pill',i===0?'Starting point':'Alternative'),el('h3','',t.name),el('p','',fits[t.id]));
    if(level==='beginner')box.append(el('p','muted',beginnerNotes[t.id]||'Check setup requirements.'));
    if(budget==='free')box.append(el('p','muted','Check model, hosting, and hardware costs before choosing.'));
    const a=el('a','','Official website ↗');a.href=t.url;a.target='_blank';a.rel='noopener noreferrer nofollow';box.append(a);
    out.append(box);
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
  const a=tools.find(t=>t.id===document.querySelector('#compare-a').value);
  const b=tools.find(t=>t.id===document.querySelector('#compare-b').value);
  if(!a||!b)return;
  for(const t of [a,b]){
    const card=el('article','match');card.append(el('h3','',t.name),el('p','',t.summary),el('p','muted','Category: '+t.category),el('p','muted','Cost notes: '+(t.pricing||'Verify with vendor')),el('p','muted','Tags: '+(t.tags||[]).join(', ')));
    const link=el('a','','Official source ↗');link.href=t.url;link.target='_blank';link.rel='noopener noreferrer nofollow';card.append(link);out.append(card);
  }
}
['task','level','budget'].forEach(id=>document.getElementById(id).addEventListener('change',renderFinder));
['compare-a','compare-b'].forEach(id=>document.getElementById(id).addEventListener('change',renderComparison));
