"""Build public JSON from manually approved tool records."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
records = json.loads((ROOT/'data/tools.json').read_text(encoding='utf-8'))
required = {'id','name','url','category','summary','status'}
ids = set()
approved = []
for record in records:
    if not required.issubset(record) or record['id'] in ids:
        raise ValueError('Missing fields or duplicate tool ID')
    ids.add(record['id'])
    if record['status'] == 'approved':
        approved.append(record)
(ROOT/'site/tools.json').write_text(json.dumps(approved, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
print(f'Built {len(approved)} approved listings')
