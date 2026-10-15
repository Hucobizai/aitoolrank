"""Dependency-free discovery bot. Only writes review candidates; never auto-approves."""
import datetime as dt
import json
import pathlib
import re
import urllib.request
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
ATOM = '{http://www.w3.org/2005/Atom}'


def read_json(name, default):
    path = DATA / name
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else default


def write_json(name, data):
    (DATA / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def parse_feed(xml, source):
    root = ET.fromstring(xml)
    entries = []
    if root.tag == ATOM + 'feed':
        for item in root.findall(ATOM + 'entry')[:12]:
            link = next((x.attrib.get('href', '') for x in item.findall(ATOM + 'link') if x.attrib.get('rel', 'alternate') == 'alternate'), '')
            entries.append((item.findtext(ATOM + 'id', default=link), item.findtext(ATOM + 'title', default='Untitled'), link, item.findtext(ATOM + 'updated', default='')))
    else:
        for item in root.findall('./channel/item')[:12]:
            entries.append((item.findtext('guid') or item.findtext('link') or '', item.findtext('title') or 'Untitled', item.findtext('link') or '', item.findtext('pubDate') or ''))
    result = []
    for identifier, title, link, published in entries:
        if not link.startswith('https://'):
            continue
        result.append({'id': source['name'] + ':' + (identifier or link), 'title': re.sub(r'\s+', ' ', title).strip()[:200], 'url': link, 'source': source['name'], 'category': source['category'], 'published': published, 'discovered': dt.datetime.now(dt.timezone.utc).date().isoformat(), 'status': 'pending', 'note': 'Release announcement only; verify claims before publication.'})
    return result


def fetch(url):
    if urlparse(url).scheme != 'https':
        raise ValueError('HTTPS feeds only')
    req = urllib.request.Request(url, headers={'User-Agent': 'AIToolRankResearch/0.1 (public feed reader)'})
    with urllib.request.urlopen(req, timeout=15) as response:
        return response.read(1_500_000)


def main():
    existing = read_json('review_queue.json', [])
    known = {item['id'] for item in existing}
    added = 0
    for source in read_json('sources.json', []):
        try:
            for candidate in parse_feed(fetch(source['url']), source):
                if candidate['id'] not in known:
                    existing.append(candidate)
                    known.add(candidate['id'])
                    added += 1
            print('OK', source['name'])
        except (OSError, ValueError, ET.ParseError) as exc:
            print('WARNING', source['name'], str(exc))
    write_json('review_queue.json', sorted(existing, key=lambda x: x['discovered'], reverse=True)[:500])
    print('New review candidates:', added)

if __name__ == '__main__':
    main()
