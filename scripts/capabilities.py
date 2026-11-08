#!/usr/bin/env python3
"""capabilities.py [--check] : the capability model of spec/capabilities, checked,
and its tables written into the pages.

The model is four files in spec/capabilities/:
  areas.csv         the areas, each with its part, depth and chapter
  capabilities.csv  one row a capability: who, where each app and face has it,
                    what serves it, its settings, where the spec says it, its changes
  settings.csv      one row a setting: who changes it, where, its default, a proposal
  inventory.csv     what the code offers, written by scripts/inventory.py

It checks, and fails on the first kind of problem it finds in each row:
  - every value is one the model allows, every key is unique and well formed;
  - every id in screens, served_by and ids is in the inventory (a trailing * names a
    family), and of a kind that belongs in that column;
  - every route, GraphQL operation, screen, tab and command of the inventory is
    claimed by a capability, and every resource field, environment variable and
    catalog setting by exactly one setting;
  - every reference into the spec leads to a page and a heading that exist, every
    change named is a numbered change of the spec;
  - the pages' generated blocks are what the model says (--check), else they are
    written. A block is the text between "<!-- generated: name -->" and
    "<!-- end: name -->"; everything outside the blocks is written by hand.
Numbers on the pages come from here, never typed."""
import csv
import glob
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
CAP = os.path.join(ROOT, 'spec', 'capabilities')
SPEC = os.path.join(ROOT, 'spec')
DOCS = os.path.join(ROOT, 'docs')

APPS = [('web', 'Web'), ('phone', 'Phone'), ('androidtv', 'Android TV'), ('samsung', 'Samsung TV')]
FACES = [('portal', 'Portal'), ('catalog', 'Catalog console'), ('cli', 'CLI'), ('resource', 'Resource')]
STATUS = ['built', 'partial', 'no', '—', '?']
WHO = ['person', 'admin', 'operator', 'addon', 'system']
PARTS = [('chino', 'chino', 'chino.md'), ('portal', 'the portal', 'portal.md'),
         ('catalog', 'the catalog and the pipeline', 'catalog.md'),
         ('platform', 'the platform', 'platform.md'), ('later', 'later products', 'platform.md')]
DEPTH = ['deep', 'working', 'stub']
SET_KIND = ['choice', 'wiring']
SET_WHO = ['operator', 'admin', 'person', 'nobody']
SET_WHERE = ['resource', 'env', 'catalog', 'registry', 'app', 'code']
PROPOSAL = ['', 'keep', 'setting', 'shared', 'person', 'constant']
CLAIMED_BY_CAPABILITY = {'route', 'graphql', 'screen', 'tab', 'command'}
CLAIMED_BY_SETTING = {'field', 'env', 'setting'}
SCREEN_KINDS = {'screen', 'tab'}
SERVE_KINDS = {'route', 'graphql', 'command', 'field'}
SETTING_KINDS = {'field', 'env', 'setting', 'constant'}
KEY = re.compile(r'^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$')
CAP_COLS = ['key', 'area', 'capability', 'who'] + [a for a, _ in APPS] + [f for f, _ in FACES] + \
    ['screens', 'served_by', 'settings', 'spec', 'changes', 'note']
SET_COLS = ['key', 'capability', 'setting', 'kind', 'who', 'where', 'ids', 'default', 'values', 'proposal', 'note']
AREA_COLS = ['key', 'part', 'area', 'depth', 'spec', 'intro']

problems = []


def problem(where, what):
    problems.append(f'{where}: {what}')


def read(name, cols):
    path = os.path.join(CAP, name)
    if not os.path.exists(path):
        problem(name, 'missing')
        return []
    with open(path, encoding='utf-8', newline='') as fh:
        r = csv.DictReader(fh)
        if r.fieldnames != cols:
            problem(name, f'columns are {r.fieldnames}, not {cols}')
        return [{k: (v or '').strip() for k, v in row.items() if k} for row in r]


def split(v):
    return [x.strip() for x in v.split(';') if x.strip()]


def slug(text):
    """the anchor GitHub and the site give a heading (as scripts/check-docs.py)"""
    kept = ''.join(ch for ch in text.lower() if ch in ' -' or unicodedata.category(ch)[0] in 'LMN'
                   or unicodedata.category(ch) == 'Pc')
    return kept.replace(' ', '-')


_headings = {}


def headings(path):
    if path not in _headings:
        out, fence = [], False
        for line in open(path, encoding='utf-8'):
            if line.lstrip().startswith(('```', '~~~')):
                fence = not fence
                continue
            m = None if fence else re.match(r'^(#{1,6})\s+(.*?)\s*$', line)
            if m:
                out.append((len(m.group(1)), m.group(2)))
        _headings[path] = out
    return _headings[path]


def resolve_spec(ref):
    """chino/playback#11.7 | chino/playback | portal/home#Spaces | docs/adr/0015-…
    -> (link from spec/capabilities/, label) or None"""
    page, _, sec = ref.partition('#')
    if page.startswith('docs/'):
        path = os.path.join(ROOT, page + '.md')
        rel = '../../' + page + '.md'
        label = page[len('docs/'):].split('/')[-1].replace('-', ' ')
    else:
        path = os.path.join(SPEC, page + '.md')
        rel = '../' + page + '.md'
        label = page.split('/')[0] + ' ' + page.split('/')[-1].replace('-', ' ')
    if not os.path.exists(path):
        return None
    if not sec:
        if page.startswith('chino/'):
            first = headings(path)[0][1] if headings(path) else ''
            m = re.match(r'(\d+)\s', first)
            label = f'chapter {m.group(1)}' if m else label
        return rel, label
    for level, h in headings(path):
        if re.match(rf'^{re.escape(sec)}\s', h) or h.lower() == sec.lower():
            # a page's own title is its page: the site shows the H1 as the title, with no anchor
            return (rel if level == 1 else f'{rel}#{slug(h)}'), (sec if re.match(r'^\d', sec) else h)
    return None


def spec_changes():
    out = {}
    for path in glob.glob(os.path.join(SPEC, '*', '*.md')):
        for line in open(path, encoding='utf-8'):
            m = re.match(r'^\|\s*((?:\d+|[A-Z])\.C\d+)\s*\|.*\|\s*([a-z]+)\s*\|\s*$', line)
            if m:
                out[m.group(1)] = m.group(2)
    return out


def match(ids, inventory, kinds, where, column):
    """the inventory rows each id names; a problem for an id that names none"""
    hit = []
    for i in ids:
        # an id is itself first (a route's path may hold * and [ ]), else a family
        rows = [r for r in inventory if r['id'] == i]
        if not rows and '*' in i:
            family = re.compile('^' + re.escape(i).replace(r'\*', '.*') + '$')  # only * is a wildcard
            rows = [r for r in inventory if family.match(r['id'])]
        if not rows:
            problem(where, f'{column}: {i} is not in the inventory')
            continue
        wrong = sorted({r['kind'] for r in rows} - kinds)
        if wrong:
            problem(where, f'{column}: {i} is a {"/".join(wrong)}, which does not belong in {column}')
        hit.extend(rows)
    return hit


def check(areas, caps, settings, inventory):
    area_keys = {}
    for a in areas:
        w = f'areas.csv {a.get("key")}'
        if not KEY.match(a['key']):
            problem(w, 'key is not kebab-case')
        if a['key'] in area_keys:
            problem(w, 'key twice')
        area_keys[a['key']] = a
        if a['part'] not in [p for p, _, _ in PARTS]:
            problem(w, f'part {a["part"]!r} is none of {[p for p, _, _ in PARTS]}')
        if a['depth'] not in DEPTH:
            problem(w, f'depth {a["depth"]!r} is none of {DEPTH}')
        if a['spec'] and not resolve_spec(a['spec']):
            problem(w, f'spec {a["spec"]} leads nowhere')
    set_keys = {s['key'] for s in settings}
    changes = spec_changes()
    claimed = defaultdict(list)
    cap_keys = set()
    for c in caps:
        w = f'capabilities.csv {c.get("key")}'
        if not KEY.match(c['key']) or len(c['key']) > 32:
            problem(w, 'key is not kebab-case of at most 32 characters')
        if c['key'] in cap_keys:
            problem(w, 'key twice')
        cap_keys.add(c['key'])
        if c['area'] not in area_keys:
            problem(w, f'area {c["area"]!r} is not in areas.csv')
        if c['who'] not in WHO:
            problem(w, f'who {c["who"]!r} is none of {WHO}')
        if not c['capability'] or len(c['capability']) > 90 or c['capability'].endswith('.'):
            problem(w, 'capability is empty, longer than 90 characters or ends with a full stop')
        for col, _ in APPS + FACES:
            if c[col] not in STATUS:
                problem(w, f'{col} is {c[col]!r}, none of {STATUS}')
        for r in match(split(c['screens']), inventory, SCREEN_KINDS, w, 'screens'):
            claimed[r['id']].append(c['key'])
        for r in match(split(c['served_by']), inventory, SERVE_KINDS, w, 'served_by'):
            claimed[r['id']].append(c['key'])
        for s in split(c['settings']):
            if s not in set_keys:
                problem(w, f'settings: {s} is not in settings.csv')
        for ref in split(c['spec']):
            if not resolve_spec(ref):
                problem(w, f'spec: {ref} leads to no page or heading')
        for ch in split(c['changes']):
            if ch not in changes:
                problem(w, f'changes: {ch} is no numbered change of the spec')
        if len(c['note']) > 140:
            problem(w, 'note is longer than 140 characters')
    set_claims = defaultdict(list)
    seen = set()
    for s in settings:
        w = f'settings.csv {s.get("key")}'
        if not KEY.match(s['key']) or len(s['key']) > 32:
            problem(w, 'key is not kebab-case of at most 32 characters')
        if s['key'] in seen:
            problem(w, 'key twice')
        seen.add(s['key'])
        if not split(s['capability']):
            problem(w, 'capability is empty')
        for k in split(s['capability']):
            if k not in cap_keys:
                problem(w, f'capability {k} is not in capabilities.csv')
        for col, allowed in (('kind', SET_KIND), ('who', SET_WHO), ('where', SET_WHERE), ('proposal', PROPOSAL)):
            if s[col] not in allowed:
                problem(w, f'{col} is {s[col]!r}, none of {allowed}')
        for r in match(split(s['ids']), inventory, SETTING_KINDS, w, 'ids'):
            set_claims[r['id']].append(s['key'])
        if len(s['note']) > 140:
            problem(w, 'note is longer than 140 characters')
    for r in inventory:
        if r['kind'] in CLAIMED_BY_CAPABILITY and not claimed.get(r['id']):
            problem(f'inventory.csv {r["id"]}', f'no capability claims it ({r["where"]})')
        if r['kind'] in CLAIMED_BY_SETTING:
            owners = sorted(set(set_claims.get(r['id'], [])))
            if not owners:
                problem(f'inventory.csv {r["id"]}', f'no setting claims it ({r["where"]})')
            elif len(owners) > 1:
                problem(f'inventory.csv {r["id"]}', f'claimed by {len(owners)} settings: {", ".join(owners)}')
    return area_keys, changes


# ------------------------------------------------------------------- pages
def cell(v):
    return str(v).replace('|', '\\|').replace('\n', ' ')


def code_list(ids, limit=3):
    names = []
    for i in ids:
        kind, repo, name = (i.split(':', 2) + ['', ''])[:3]
        names.append(f'`{repo} {name}`' if kind in ('route', 'graphql') else f'`{name}`' if kind == 'command' else f'`{name}`')
    more = len(names) - limit
    return ', '.join(names[:limit]) + (f' and {more} more' if more > 0 else '')


def spec_cell(c):
    out = []
    for ref in split(c['spec']):
        r = resolve_spec(ref)
        if r:
            out.append(f'[{r[1]}]({r[0]})')
    return ', '.join(out) or '—'


def table(rows, header):
    lines = ['| ' + ' | '.join(header) + ' |', '|' + '|'.join('---' for _ in header) + '|']
    lines += ['| ' + ' | '.join(cell(x) for x in r) + ' |' for r in rows]
    return '\n'.join(lines)


def faces_used(caps):
    return [(k, label) for k, label in APPS + FACES if any(c[k] != '—' for c in caps)]


def area_blocks(part, areas, caps, settings_by_key):
    out = []
    for a in [a for a in areas if a['part'] == part or (part == 'platform' and a['part'] == 'later')]:
        rows = [c for c in caps if c['area'] == a['key']]
        out.append(f'## {a["area"]}\n')
        bits = [a['intro']]
        r = resolve_spec(a['spec']) if a['spec'] else None
        bits.append(f'Specified in [{r[1]}]({r[0]}).' if r else 'Not specified yet.')
        bits.append(f'Depth: {a["depth"]}.')
        out.append(' '.join(bits) + '\n')
        if not rows:
            out.append('No capability yet.\n')
            continue
        faces = faces_used(rows)
        header = ['Capability', 'Who'] + [label for _, label in faces] + ['Spec']
        body = [[c['capability'], c['who']] + [c[k] for k, _ in faces] + [spec_cell(c)] for c in rows]
        out.append(table(body, header) + '\n')
        notes = [f'- {c["capability"]}: {c["note"]}' for c in rows if c['note']]
        if notes:
            out.append('\n'.join(notes) + '\n')
        body = [[f'`{c["key"]}`', ', '.join(split(c['changes'])) or '—', code_list(split(c['served_by'])) or '—',
                 ', '.join(f'`{s}`' for s in split(c['settings'])) or '—'] for c in rows]
        out.append(table(body, ['Key', 'Changes', 'Served by', 'Settings']) + '\n')
    return '\n'.join(out).rstrip() + '\n'


def overview(areas, caps, settings, inventory, changes):
    lines = []
    rows = []

    def described(sel):
        chapter = [c for c in sel if any(not r.startswith('docs/') for r in split(c['spec']))]
        docs = [c for c in sel if split(c['spec']) and c not in chapter]
        return [len(chapter), len(docs), len(sel) - len(chapter) - len(docs), sum(1 for c in sel if split(c['changes']))]
    for p, label, page in PARTS:
        part_caps = [c for c in caps if next(a['part'] for a in areas if a['key'] == c['area']) == p]
        if part_caps:
            rows.append([f'[{label}](./{page})', len(part_caps)] + described(part_caps))
    rows.append(['all', len(caps)] + described(caps))
    lines.append(table(rows, ['Part', 'Capabilities', 'In a chapter', 'Only in the docs', 'Nowhere', 'With a change']))
    lines.append('')
    rows = []
    for k, label in APPS + FACES:
        n = Counter(c[k] for c in caps)
        if sum(n[s] for s in STATUS if s != '—') == 0:
            continue
        rows.append([label] + [n[s] for s in STATUS])
    lines.append(table(rows, ['App or face'] + STATUS))
    lines.append('')
    mapped = {ch for c in caps for ch in split(c['changes'])}
    st = Counter(changes.values())
    lines.append(table([[len(changes), len(mapped), len(changes) - len(mapped)] + [st.get(s, 0) for s in ('proposed', 'approved', 'built', 'verified')]],
                       ['Numbered changes', 'Named by a capability', 'Not yet', 'Proposed', 'Approved', 'Built', 'Verified']))
    return '\n'.join(lines) + '\n'


def inventory_block(inventory, caps, settings):
    kinds = ['route', 'graphql', 'screen', 'tab', 'command', 'field', 'env', 'setting', 'constant']
    labels = {'route': 'HTTP routes', 'graphql': 'GraphQL operations', 'screen': 'screens', 'tab': 'tabs',
              'command': 'CLI commands', 'field': "fields of the operator's resources",
              'env': 'environment variables', 'setting': "the catalog's settings", 'constant': 'constants in the code'}
    in_settings = set()
    for s in settings:
        for r in match(split(s['ids']), inventory, SETTING_KINDS, 'inventory', 'ids'):
            in_settings.add(r['id'])
    n = Counter(r['kind'] for r in inventory)
    repos = len({r['repo'] for r in inventory})
    rows = []
    for k in kinds:
        claim = 'a capability' if k in CLAIMED_BY_CAPABILITY else 'a setting' if k in CLAIMED_BY_SETTING else 'listed'
        note = f'{sum(1 for r in inventory if r["kind"] == k and r["id"] in in_settings)} in a setting' if k == 'constant' else ''
        rows.append([labels[k], n[k], claim, note])
    return table(rows, ['What the code offers', 'Rows', 'Claimed by', '']) + \
        f'\n\nFrom the main branch of {repos} repositories, as [inventory-sources.csv](./inventory-sources.csv) names them.\n'


def configuration_blocks(caps, settings, areas):
    cap_area = {c['key']: c['area'] for c in caps}
    part_of = {a['key']: a['part'] for a in areas}
    out = {}
    rows = []
    for where in SET_WHERE:
        sel = [s for s in settings if s['where'] == where]
        if sel:
            rows.append([where, len(sel)] + [sum(1 for s in sel if s['who'] == w) for w in SET_WHO] +
                        [sum(1 for s in sel if s['kind'] == 'wiring')])
    out['summary'] = table(rows, ['Changed in', 'Settings'] + SET_WHO + ['of them wiring']) + '\n'
    prop = Counter(s['proposal'] for s in settings if s['proposal'])
    out['proposals'] = table([[p, prop[p]] for p in PROPOSAL if p and prop[p]], ['Proposal', 'Settings']) + '\n' if prop else 'No proposal yet.\n'
    def name(s):
        return f'{s["setting"]} `{s["key"]}`, for ' + ', '.join(f'`{k}`' for k in split(s['capability']))

    def default(s):
        d, v = s['default'] or '—', s['values']
        return f'{d} ({v})' if v else d

    def rows_of(sel):
        return [[name(s), s['who'], s['where'], default(s), s['proposal'] or '—'] for s in sel]
    header = ['Setting', 'Who', 'Where', 'Default (values)', 'Proposal']

    def notes_of(sel):
        n = [f'- `{s["key"]}`: {s["note"]}' for s in sel if s['note']]
        return ('\n\n' + '\n'.join(n)) if n else ''
    for p, label, _ in PARTS:
        if p == 'later':
            continue
        sel = [s for s in settings if s['kind'] == 'choice' and s['where'] != 'code'
               and part_of.get(cap_area.get(split(s['capability'])[0] if split(s['capability']) else '', ''), '') == p]
        out[f'choices-{p}'] = (table(rows_of(sel), header) + notes_of(sel) if sel else 'None.') + '\n'
    sel = [s for s in settings if s['where'] == 'code']
    out['fixed'] = (table([[name(s), default(s), s['proposal'] or '—'] for s in sel],
                          ['Setting', 'Default in each app (values)', 'Proposal']) + notes_of(sel) if sel else 'None yet.') + '\n'
    sel = [s for s in settings if s['kind'] == 'wiring']
    out['wiring'] = (table([[f'{s["setting"]} `{s["key"]}`', s['where'], code_list(split(s['ids']), 4)] for s in sel],
                           ['Wiring', 'Where', 'Is']) if sel else 'None.') + '\n'
    return out


def fill(path, blocks, write):
    text = open(path, encoding='utf-8').read() if os.path.exists(path) else ''
    new = text
    for name, body in blocks.items():
        pat = re.compile(rf'(<!-- generated: {re.escape(name)} -->\n).*?(<!-- end: {re.escape(name)} -->)', re.S)
        if not pat.search(new):
            problem(os.path.relpath(path, ROOT), f'has no block "{name}"')
            continue
        new = pat.sub(lambda m: m.group(1) + body + m.group(2), new)
    if new != text:
        if write:
            open(path, 'w', encoding='utf-8').write(new)
        else:
            problem(os.path.relpath(path, ROOT), 'its generated blocks are not what the model says: run scripts/capabilities.py')


def main():
    write = '--check' not in sys.argv
    areas = read('areas.csv', AREA_COLS)
    caps = read('capabilities.csv', CAP_COLS)
    settings = read('settings.csv', SET_COLS)
    inventory = read('inventory.csv', ['id', 'kind', 'repo', 'name', 'value', 'note', 'where'])
    area_keys, changes = check(areas, caps, settings, inventory)
    settings_by_key = {s['key']: s for s in settings}
    fill(os.path.join(CAP, 'README.md'), {
        'overview': overview(areas, caps, settings, inventory, changes),
        'inventory': inventory_block(inventory, caps, settings),
    }, write)
    for p, _, page in PARTS:
        if p == 'later':
            continue
        fill(os.path.join(CAP, page), {'areas': area_blocks(p, areas, caps, settings_by_key)}, write)
    fill(os.path.join(CAP, 'configuration.md'), configuration_blocks(caps, settings, areas), write)
    for p in problems:
        print(p)
    print(f'{len(problems)} problems; {len(caps)} capabilities in {len(areas)} areas, {len(settings)} settings, '
          f'{len(inventory)} inventory rows')
    sys.exit(1 if problems else 0)


if __name__ == '__main__':
    main()
