
const q = document.querySelector('#q');
const cat = document.querySelector('#cat');
const cards = document.querySelector('#cards');
const count = document.querySelector('#count');
const empty = document.querySelector('#empty');
let tools = [];

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function linkTo(t, label = 'Official website ↗') {
  const a = el('a', '', label);
  a.href = t.url;
  a.target = '_blank';
  a.rel = 'noopener noreferrer nofollow';
  return a;
}

function render() {
  const term = q.value.toLocaleLowerCase().trim();
  const matches = tools.filter(t =>
    (!cat.value || t.category === cat.value) &&
    [t.name, t.category, t.summary, ...(t.tags || [])]
      .join(' ').toLocaleLowerCase().includes(term)
  );
  cards.replaceChildren();
  count.textContent = `${matches.length} tools`;
  empty.hidden = matches.length !== 0;

  for (const t of matches) {
    const card = el('article', 'tool');
    card.append(
      el('span', 'pill', t.category),
      el('h3', '', t.name),
      el('p', '', t.summary),
      el('div', 'price', t.pricing || 'Check vendor for pricing'),
      linkTo(t, 'Visit official website ↗')
    );
    cards.append(card);
  }
}

q.addEventListener('input', render);
cat.addEventListener('change', render);

// Editorial suitability metadata.
// Candidates must also exist in published tools.json.
// These are not measured performance rankings.
const profiles = {
  ollama: {
    tasks: ['local-ai', 'agent'],
    levels: ['beginner', 'intermediate', 'advanced'],
    reasons: {
      'local-ai': 'Runs supported open models locally.',
      agent: 'Can serve local models for agent projects; it is not an agent builder.'
    },
    needs: 'Local installation and suitable hardware.',
    budget: 'free'
  },
  langgraph: {
    tasks: ['agent'],
    levels: ['intermediate', 'advanced'],
    reasons: {
      agent: 'Framework for stateful, code-first agent workflows.'
    },
    needs: 'Python or JavaScript skills.',
    budget: 'free'
  },
  continue: {
    tasks: ['code'],
    levels: ['beginner', 'intermediate', 'advanced'],
    reasons: {
      code: 'Integrates AI assistance into development workflows.'
    },
    needs: 'Compatible editor and model/provider setup.',
    budget: 'variable'
  },
  aider: {
    tasks: ['code'],
    levels: ['intermediate', 'advanced'],
    reasons: {
      code: 'Terminal-first AI pair programming.'
    },
    needs: 'Terminal, Git, and compatible model/provider.',
    budget: 'variable'
  },
  comfyui: {
    tasks: ['media'],
    levels: ['intermediate', 'advanced'],
    reasons: {
      media: 'Node-based generative image and video workflows.'
    },
    needs: 'Models, workflow setup, and suitable compute.',
    budget: 'free'
  },
  cursor: {
    tasks: ['code'],
    levels: ['beginner', 'intermediate', 'advanced'],
    reasons: {
      code: 'AI-focused code editor with chat and agent features.'
    },
    needs: 'Install the editor; usage limits depend on plan.',
    budget: 'free-tier'
  },
  replit: {
    tasks: ['code'],
    levels: ['beginner', 'intermediate', 'advanced'],
    reasons: {
      code: 'Browser-based environment for creating and deploying apps.'
    },
    needs: 'Account; deployment and AI usage may incur charges.',
    budget: 'free-tier'
  },
  'github-copilot': {
    tasks: ['code'],
    levels: ['beginner', 'intermediate', 'advanced'],
    reasons: {
      code: 'Coding assistance within supported developer tools.'
    },
    needs: 'Supported editor or GitHub workflow; account.',
    budget: 'free-tier'
  },
  bolt: {
    tasks: ['code'],
    levels: ['beginner', 'intermediate', 'advanced'],
    reasons: {
      code: 'Builds and edits web apps from natural-language prompts.'
    },
    needs: 'Account; token limits and usage-based restrictions.',
    budget: 'free-tier'
  },
  lovable: {
    tasks: ['code'],
    levels: ['beginner', 'intermediate', 'advanced'],
    reasons: {
      code: 'Prompt-driven web application creation.'
    },
    needs: 'Account; free credits are limited.',
    budget: 'free-tier'
  }
};

const taskNames = {
  'local-ai': 'local AI',
  agent: 'AI agents',
  code: 'coding and app building',
  media: 'generative media'
};

function renderFinder() {
  const task = document.querySelector('#task').value;
  const level = document.querySelector('#level').value;
  const budget = document.querySelector('#budget').value;
  const out = document.querySelector('#recommendations');
  out.replaceChildren();

  const matches = tools
    .map(t => ({ tool: t, profile: profiles[t.id] }))
    .filter(x =>
      x.profile &&
      x.profile.tasks.includes(task) &&
      x.profile.levels.includes(level)
    );

  // Free means a documented no-cost entry point,
  // not guaranteed zero total cost.

const eligible = (budget === 'free'
  ? matches.filter(x =>
      ['free', 'free-tier'].includes(x.profile.budget)
    )
  : matches
).sort((a, b) => {
  if (task === 'agent') {
    const priority = {
      langgraph: 0,
      ollama: 1
    };
    return (priority[a.tool.id] ?? 99) -
           (priority[b.tool.id] ?? 99);
  }
  return 0;
});

  if (!eligible.length) {
    out.append(el(
      'p',
      'muted',
      `No verified ${level}-friendly match in our current catalog for ${taskNames[task] || 'this task'} under the selected budget.`
    ));

    if (matches.length && budget === 'free') {
      out.append(el(
        'p',
        'muted',
        'Some relevant tools have variable model/provider costs. Try a different budget setting.'
      ));
    } else {
      out.append(el(
        'p',
        'muted',
        'Try Intermediate or a different task to explore other options.'
      ));
    }
    return;
  }

  // Editorial order, not a performance score.
  eligible.forEach((x, i) => {
    const t = x.tool;
    const p = x.profile;
    const box = el('article', 'match');

    box.append(
      el('span', 'pill', i === 0
        ? 'Suggested starting point'
        : 'Also relevant'),
      el('h3', '', t.name),
      el('p', '', p.reasons[task]),
      el('p', 'muted', 'Requirements: ' + p.needs)
    );

    if (budget === 'free') {
      box.append(el(
        'p',
        'muted',
        'Free entry point: ' +
        (t.pricing || 'Verify vendor pricing') +
        '. Limits, model fees, and hardware costs may apply.'
      ));
    } else {
      box.append(el(
        'p',
        'muted',
        'Pricing: ' + (t.pricing || 'Verify vendor pricing')
      ));
    }

    box.append(linkTo(t));
    out.append(box);
  });
}

function populateComparison() {
  const a = document.querySelector('#compare-a');
  const b = document.querySelector('#compare-b');

  for (const sel of [a, b]) {
    sel.replaceChildren();

    tools.forEach(t => {
      const o = document.createElement('option');
      o.value = t.id;
      o.textContent = t.name;
      sel.append(o);
    });
  }

  if (tools.length > 1) b.selectedIndex = 1;
  renderComparison();
}

function renderComparison() {
  const out = document.querySelector('#comparison');
  out.replaceChildren();

  const a = tools.find(t =>
    t.id === document.querySelector('#compare-a').value
  );
  const b = tools.find(t =>
    t.id === document.querySelector('#compare-b').value
  );

  if (!a || !b) return;

  if (a.id === b.id) {
    out.append(el(
      'p',
      'muted',
      'Choose two different tools to compare.'
    ));
    return;
  }

  const pairs = {
    'langgraph|ollama':
      'These tools complement each other: LangGraph orchestrates agent workflows, while Ollama can provide locally served models.',
    'aider|continue':
      'Both help with coding. Continue is designed around editor workflows; Aider focuses on terminal-based pair programming.'
  };

  const key = [a.id, b.id].sort().join('|');

  out.append(el(
    'p',
    'comparison-insight',
    pairs[key] ||
    'Compare the tools’ stated purposes, pricing, and setup requirements; no performance winner is claimed.'
  ));

  for (const t of [a, b]) {
    const card = el('article', 'match');
    const p = profiles[t.id];

    card.append(
      el('h3', '', t.name),
      el('p', '', t.summary),
      el('p', 'muted', 'Category: ' + t.category),
      el('p', 'muted', 'Cost notes: ' +
        (t.pricing || 'Verify with vendor')),
      el('p', 'muted', 'Setup: ' +
        (p?.needs || 'Check official documentation')),
      el('p', 'muted', 'Tags: ' + (t.tags || []).join(', ')),
      linkTo(t, 'Official source ↗')
    );

    out.append(card);
  }
}

['task', 'level', 'budget'].forEach(id =>
  document.getElementById(id).addEventListener(
    'change', renderFinder
  )
);

['compare-a', 'compare-b'].forEach(id =>
  document.getElementById(id).addEventListener(
    'change', renderComparison
  )
);

fetch('tools.json')
  .then(r => {
    if (!r.ok) throw Error('Failed to load tool database');
    return r.json();
  })
  .then(data => {
    if (!Array.isArray(data)) throw Error('Invalid tool database');
    tools = data.filter(t => t.status === 'approved');
    render();
    populateComparison();
    renderFinder();
  })
  .catch(() => {
    count.textContent = 'Unavailable';
    empty.hidden = false;
    empty.textContent =
      'Unable to load tools. Serve the site through a local web server.';
  });
