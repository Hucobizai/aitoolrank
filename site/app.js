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
fetch('tools.json').then(r=>{if(!r.ok)throw Error('Failed to load tool database');return r.json()}).then(data=>{tools=data;render()}).catch(()=>{count.textContent='Unavailable';empty.hidden=false;empty.textContent='Unable to load tools. Serve the site through a local web server.'});
