#!/usr/bin/env python3
"""capabilities.py [--check] : the capability model of spec/capabilities and the
architecture of spec/architecture, checked, and their tables written into the pages.

The capability model is four files in spec/capabilities/:
  areas.csv         the areas, each with its part, depth and chapter
  capabilities.csv  one row a capability: who, where each app and face has it,
                    what serves it, its settings, where the spec says it, its changes
  settings.csv      one row a setting: who changes it, where, its default, a proposal
  inventory.csv     what the code offers, written by scripts/inventory.py

The architecture is three files in spec/architecture/, on the same inventory:
  components.csv    one row a component: its layer, kind and status, its code, and
                    the workloads and volumes of the operator's chart it runs as
  connections.csv   one row a connection: from, to, its kind, what it is on (a path,
                    a database, topics), and what in the code makes it (via)
  decisions.csv     one row a decision record: the components and capabilities it governs
It checks that every repository of the organisation is a component's code, every
workload and volume of the chart one component's; that every wire of the chart that
leads to another component, and every address an environment variable names, is a
connection's via; that every via is in the inventory and belongs to the connection's
ends; and that where a decision record amends, supersedes or extends another, the
other says so. What the model finds against the decisions is listed, never failed.

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
Numbers on the pages come from here, never typed.

capabilities.py --json PATH writes the model instead, resolved, for the site's map
and fact sheets: each reference into the spec with its file and heading, each change
with its row, each id with its row of the inventory. It changes no page, and it
writes the file even when the check finds problems: they are in it, under problems."""
import csv
import fnmatch
import glob
import json
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
CAP = os.path.join(ROOT, 'spec', 'capabilities')
ARCH = os.path.join(ROOT, 'spec', 'architecture')
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


def read(name, cols, base=CAP):
    path = os.path.join(base, name)
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


def resolve_ref(ref):
    """chino/playback#11.7 | chino/playback | portal/home#Spaces | docs/adr/0015-…
    -> {file, kind, page, heading, level, anchor, label} or None. file is the page's
    path in the repository; heading is None for a whole page, and so is anchor for a
    page's own title (the site shows the H1 as the title, with no anchor)."""
    page, _, sec = ref.partition('#')
    if page.startswith('docs/'):
        file, kind = page + '.md', 'docs'
        label = page[len('docs/'):].split('/')[-1].replace('-', ' ')
    else:
        file, kind = 'spec/' + page + '.md', 'chapter'
        label = page.split('/')[0] + ' ' + page.split('/')[-1].replace('-', ' ')
    path = os.path.join(ROOT, file)
    if not os.path.exists(path):
        return None
    hs = headings(path)
    title = hs[0][1] if hs and hs[0][0] == 1 else ''
    out = {'ref': ref, 'file': file, 'kind': kind, 'page': title, 'heading': None, 'level': None, 'anchor': None}
    if not sec:
        if page.startswith('chino/'):
            m = re.match(r'(\d+)\s', title)
            label = f'chapter {m.group(1)}' if m else label
        return {**out, 'label': label}
    for level, h in hs:
        if re.match(rf'^{re.escape(sec)}\s', h) or h.lower() == sec.lower():
            return {**out, 'heading': h, 'level': level, 'anchor': None if level == 1 else slug(h),
                    'label': sec if re.match(r'^\d', sec) else h}
    return None


def resolve_spec(ref):
    """-> (link from spec/capabilities/, label) or None"""
    r = resolve_ref(ref)
    if not r:
        return None
    rel = '../../' + r['file'] if r['kind'] == 'docs' else '../' + r['file'][len('spec/'):]
    return (f'{rel}#{r["anchor"]}' if r['anchor'] else rel), r['label']


def spec_changes():
    out = {}
    for path in glob.glob(os.path.join(SPEC, '*', '*.md')):
        for line in open(path, encoding='utf-8'):
            m = re.match(r'^\|\s*((?:\d+|[A-Z])\.C\d+)\s*\|.*\|\s*([a-z]+)\s*\|\s*$', line)
            if m:
                out[m.group(1)] = m.group(2)
    return out


def cells(line):
    """a table row's cells; a \\| inside a cell is the cell's own"""
    parts = re.split(r'(?<!\\)\|', line.strip())
    return [p.strip().replace('\\|', '|') for p in parts[1:-1]]


def change_rows():
    """every numbered change of the spec, with its row and the heading over its table:
    {number: {file, heading, anchor, title, apps, today, target, status}}"""
    out = {}
    for path in sorted(glob.glob(os.path.join(SPEC, '*', '*.md'))):
        file = os.path.relpath(path, ROOT).replace(os.sep, '/')
        heading, fence = None, False
        for line in open(path, encoding='utf-8'):
            if line.lstrip().startswith(('```', '~~~')):
                fence = not fence
                continue
            if fence:
                continue
            m = re.match(r'^(#{1,6})\s+(.*?)\s*$', line)
            if m:
                heading = (len(m.group(1)), m.group(2))
                continue
            if not re.match(r'^\|\s*(?:\d+|[A-Z])\.C\d+\s*\|', line):
                continue
            row = cells(line)
            while len(row) < 6:
                row.insert(-1, '')
            number, title, apps, today, target, status = row[0], row[1], row[2], row[3], ' | '.join(row[4:-1]), row[-1]
            out[number] = {'file': file, 'heading': heading[1] if heading else None,
                           'anchor': slug(heading[1]) if heading and heading[0] > 1 else None,
                           'title': title, 'apps': apps, 'today': today, 'target': target, 'status': status}
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


def export(areas, caps, settings, inventory, path, arch=None):
    """the model, resolved, as one JSON file (see the docstring)"""
    by_id = {r['id']: r for r in inventory}
    keep = ('id', 'kind', 'repo', 'name', 'value', 'note', 'where')

    def rows(ids):
        out = []
        for i in ids:
            hit = [by_id[i]] if i in by_id else []
            if not hit and '*' in i:
                family = re.compile('^' + re.escape(i).replace(r'\*', '.*') + '$')
                hit = [r for r in inventory if family.match(r['id'])]
            out.extend({k: r[k] for k in keep} for r in hit)
        return out

    def refs(v):
        return [r for r in (resolve_ref(x) for x in split(v)) if r]
    sources = {}
    path_sources = os.path.join(CAP, 'inventory-sources.csv')
    if os.path.exists(path_sources):
        with open(path_sources, encoding='utf-8', newline='') as fh:
            sources = {r['repo']: r['commit'] for r in csv.DictReader(fh)}
    named = {ch for c in caps for ch in split(c['changes'])}
    model = {
        'parts': [{'key': p, 'label': label, 'page': f'spec/capabilities/{page}'} for p, label, page in PARTS],
        'faces': [{'key': k, 'label': label, 'app': True} for k, label in APPS] +
                 [{'key': k, 'label': label, 'app': False} for k, label in FACES],
        'areas': [{**a, 'spec': resolve_ref(a['spec']) if a['spec'] else None} for a in areas],
        'capabilities': [{
            'key': c['key'], 'area': c['area'], 'capability': c['capability'], 'who': c['who'], 'note': c['note'],
            'status': {k: c[k] for k, _ in APPS + FACES},
            'screens': rows(split(c['screens'])), 'served_by': rows(split(c['served_by'])),
            'settings': split(c['settings']), 'spec': refs(c['spec']), 'changes': split(c['changes']),
        } for c in caps],
        'settings': [{**{k: s[k] for k in SET_COLS if k not in ('capability', 'ids')},
                      'capability': split(s['capability']), 'ids': rows(split(s['ids']))} for s in settings],
        'changes': [{'number': n, 'named': n in named, **row} for n, row in change_rows().items()],
        'sources': sources,
        'architecture': arch.export(rows) if arch else None,
        'problems': list(problems),
    }
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(model, fh, ensure_ascii=False, indent=1)
        fh.write('\n')
    return model


# =================================================================== the architecture
LAYERS = [('apps', 'the apps'), ('portal', 'the portal and its consoles'), ('chino', "chino's services"),
          ('catalog', 'the catalog'), ('pipeline', 'the pipeline'), ('bundled', 'bundled services'),
          ('runtime', 'running the platform'), ('outside', 'outside the platform'),
          ('beside', 'beside the platform'), ('later', 'later products'), ('retired', 'retired')]
COMP_KINDS = ['app', 'web', 'service', 'worker', 'job', 'operator', 'cli', 'database', 'cache', 'broker',
              'identity', 'volume', 'docs', 'contracts', 'addon']
COMP_STATUS = ['runs', 'ships', 'idle', 'outside', 'beside', 'later', 'retired']
CONN_KINDS = ['calls', 'signs in', 'manages', 'links', 'publishes', 'consumes', 'writes', 'reads']
COMP_COLS = ['key', 'component', 'layer', 'kind', 'status', 'code', 'runs', 'note']
CONN_COLS = ['from', 'to', 'kind', 'on', 'via', 'note']
DEC_COLS = ['adr', 'components', 'capabilities', 'note']
STORE_KINDS = {'database', 'cache', 'volume'}
# the components nobody has to connect to: a person or the operator uses them, or they
# take their work from the bus or a schedule
USED_KINDS = {'app', 'web', 'worker', 'job', 'operator', 'cli', 'docs', 'contracts', 'addon'}
# an environment variable of the code that names where something else is
ADDRESS = re.compile(r'(?:_URL|_URI|_BROKERS|_ISSUER|_SERVICE_HOST)$')
OWN_ADDRESS = {'BASE_URL', 'PUBLIC_BASE_URL'}
# a wire of the chart that can name a service: by its name, or by a URL in its value
WIRE_ADDRESS = re.compile(r'(?:URL|URI|HOST|BROKERS|SERVER|ISSUER|LISTENERS)$')
RELATIONS = [('amends', 'amended by'), ('supersedes', 'superseded by'), ('extends', 'extended by')]
INVERSE = {a: b for a, b in RELATIONS} | {b: a for a, b in RELATIONS}
GITHUB = 'https://github.com/zaentrum'


def read_adrs():
    """the decision records of docs/adr: number -> {file, title, state, relations}; a
    relation is (amends|supersedes|extends|amended by|…, the other record's number), as
    the record's status line says it"""
    out = {}
    for path in sorted(glob.glob(os.path.join(DOCS, 'adr', '[0-9][0-9][0-9][0-9]-*.md'))):
        num = os.path.basename(path)[:4]
        title = status = ''
        for line in open(path, encoding='utf-8'):
            if not title and line.startswith('# '):
                title = re.sub(r'^ADR-\d{4}:\s*', '', line[2:].strip())
            if not status and line.startswith('**Status:**'):
                status = line[len('**Status:**'):].strip()
        relations = []
        for seg in status.split('·'):
            m = re.search(r'\b(amended by|superseded by|extended by|amends|supersedes|extends)\b', seg)
            if not m:
                continue
            for a, b in re.findall(r'\[ADR-(\d{4})\]|\((?:\./)?(\d{4})-[^)]*\.md\)', seg[m.end():]):
                n = a or b
                if n != num and (m.group(1), n) not in relations:
                    relations.append((m.group(1), n))
        state = re.match(r'([A-Za-z]+)', status)
        out[num] = {'number': num, 'file': os.path.relpath(path, ROOT).replace(os.sep, '/'), 'title': title,
                    'state': state.group(1) if state else '', 'relations': relations}
    return out


class Arch:
    """the architecture, read and checked, and what it derives from the inventory"""

    def __init__(self, comps, conns, decisions, inventory, caps, settings):
        self.comps, self.conns, self.decisions = comps, conns, decisions
        self.inventory, self.caps, self.settings = inventory, caps, settings
        self.by_id = {r['id']: r for r in inventory}
        self.comp = {c['key']: c for c in comps}
        self.runs = {}   # a workload's or a volume's id -> its component
        self.code = []   # (repository, path in it, component)
        for c in comps:
            if c['code']:
                repo, _, prefix = c['code'].partition('/')
                self.code.append((repo, prefix, c['key']))
            for i in split(c['runs']):
                self.runs.setdefault(i, c['key'])
        self.services = {r['name']: r['value'] for r in inventory if r['kind'] == 'service'}
        self.paths = {r['name']: r['value'] for r in inventory if r['kind'] == 'path'}
        prefixes = [r['value'] for r in inventory if r['kind'] == 'wire' and r['name'].endswith(' KAFKA_TOPIC_PREFIX') and r['value']]
        self.prefix = Counter(prefixes).most_common(1)[0][0] if prefixes else ''
        self.adrs = read_adrs()
        self.order = {k: i for i, (k, _) in enumerate(LAYERS)}

    # ----------------------------------------------------------- who owns what
    def rows(self, i):
        if i in self.by_id:
            return [self.by_id[i]]
        if '*' in i:
            family = re.compile('^' + re.escape(i).replace(r'\*', '.*') + '$')
            return [r for r in self.inventory if family.match(r['id'])]
        return []

    def owner(self, row):
        """the component a row of the inventory is part of"""
        k = row['kind']
        if k in ('workload', 'volume'):
            return self.runs.get(row['id'])
        if k == 'wire':
            return self.runs.get(f'workload:{row["repo"]}:{row["name"].split(" ", 1)[0]}')
        if k in ('path', 'service'):
            return self.runs.get(f'workload:{row["repo"]}:{row["value"]}')
        if k == 'repo':
            hits = [key for repo, prefix, key in self.code if repo == row['name'] and not prefix]
            return hits[0] if hits else None
        path = row['where'].rsplit(':', 1)[0]
        best = None
        for repo, prefix, key in self.code:
            if repo == row['repo'] and path.startswith(prefix) and (best is None or len(prefix) > len(best[0])):
                best = (prefix, key)
        return best[1] if best else None

    def topic(self, value):
        return value[len(self.prefix):] if self.prefix and value.startswith(self.prefix) else value

    def leads_to(self, row):
        """the components a wire of the chart leads to: a service by its name, a path of
        the public host, or a claim it mounts"""
        workload, _, env = row['name'].partition(' ')
        if env.startswith('volume '):
            k = self.runs.get(f'volume:{row["repo"]}:{env[len("volume "):]}')
            return {k} if k else set()
        v = row['value']
        if v.startswith(('secret ', 'configmap ', 'field ')) or not (WIRE_ADDRESS.search(env) or '://' in v or '@' in v):
            return set()
        out = set()
        for part in re.split(r'[\s,;]+', v):
            m = re.match(r'^(?:[A-Za-z][A-Za-z0-9+.-]*://)?(?:[^@/]*@)?([A-Za-z0-9.-]+)(?::\d+)?(/[^?#\s]*)?', re.sub(r'^jdbc:', '', part))
            if not m:
                continue
            host, path = m.group(1), m.group(2) or ''
            if host in self.services:
                out.add(self.runs.get(f'workload:{row["repo"]}:{self.services[host]}'))
            elif '.' in host:
                hit = max((p for p in self.paths if p != '/' and (path == p or path.startswith(p.rstrip('/') + '/'))),
                          key=len, default=None)
                if hit:
                    out.add(self.runs.get(f'workload:{row["repo"]}:{self.paths[hit]}'))
        return out - {None}

    # ------------------------------------------------------------------ check
    def check(self, cap_keys):
        layers, seen = [l for l, _ in LAYERS], set()
        claimed = Counter(i for c in self.comps for i in split(c['runs']))
        for c in self.comps:
            w = f'components.csv {c.get("key")}'
            if not KEY.match(c['key']) or len(c['key']) > 32:
                problem(w, 'key is not kebab-case of at most 32 characters')
            if c['key'] in seen:
                problem(w, 'key twice')
            seen.add(c['key'])
            for col, allowed in (('layer', layers), ('kind', COMP_KINDS), ('status', COMP_STATUS)):
                if c[col] not in allowed:
                    problem(w, f'{col} is {c[col]!r}, none of {allowed}')
            if not c['component'] or len(c['component']) > 90 or c['component'].endswith('.'):
                problem(w, 'component is empty, longer than 90 characters or ends with a full stop')
            if len(c['note']) > 140:
                problem(w, 'note is longer than 140 characters')
            if c['code']:
                repo, _, prefix = c['code'].partition('/')
                row = self.by_id.get(f'repo:{repo}:{repo}')
                if not row:
                    problem(w, f'code: {repo} is no repository of the organisation')
                elif (row['value'] == 'archived') != (c['status'] == 'retired'):
                    problem(w, f'status is {c["status"]}, and its repository is {row["value"]}')
                if prefix and not any(r['repo'] == repo and r['where'].startswith(prefix) for r in self.inventory):
                    problem(w, f'code: nothing the inventory lists is in {c["code"]}')
            for i in split(c['runs']):
                r = self.by_id.get(i)
                if not r:
                    problem(w, f'runs: {i} is not in the inventory')
                elif r['kind'] not in ('workload', 'volume'):
                    problem(w, f'runs: {i} is a {r["kind"]}, not a workload or a volume')
                elif claimed[i] > 1:
                    problem(w, f'runs: {i} is another component\'s too')
        for r in self.inventory:
            if r['kind'] == 'repo' and not any(repo == r['name'] and not prefix for repo, prefix, _ in self.code):
                problem(f'inventory.csv {r["id"]}', 'no component has it as its code')
            if r['kind'] in ('workload', 'volume') and r['id'] not in self.runs:
                problem(f'inventory.csv {r["id"]}', f'no component runs as it ({r["where"]})')
        wired, named, seen = defaultdict(set), set(), set()
        for n, x in enumerate(self.conns, 2):
            w = f'connections.csv line {n} ({x.get("from")} → {x.get("to")}, {x.get("kind")})'
            bad = [end for end in ('from', 'to') if x[end] not in self.comp]
            for end in bad:
                problem(w, f'{end} {x[end]!r} is not in components.csv')
            if x['kind'] not in CONN_KINDS:
                problem(w, f'kind is {x["kind"]!r}, none of {CONN_KINDS}')
                bad.append('kind')
            if bad:
                continue
            if x['from'] == x['to']:
                problem(w, 'leads from a component to itself')
            if (x['from'], x['to'], x['kind']) in seen:
                problem(w, 'twice: one row a connection, with every topic, database or path it is on')
            seen.add((x['from'], x['to'], x['kind']))
            to_kind = self.comp[x['to']]['kind']
            if x['kind'] in ('publishes', 'consumes'):
                if to_kind != 'broker':
                    problem(w, f'{x["kind"]} on {x["to"]}, which is no broker')
                if not split(x['on']):
                    problem(w, 'on: name the topics')
            if x['kind'] in ('writes', 'reads') and to_kind not in STORE_KINDS:
                problem(w, f'{x["kind"]} {x["to"]}, which is no store')
            if len(x['note']) > 140:
                problem(w, 'note is longer than 140 characters')
            vias = split(x['via'])
            if not vias:
                problem(w, 'via is empty: name what in the code makes the connection')
            for i in vias:
                r = self.by_id.get(i)
                if not r:
                    problem(w, f'via: {i} is not in the inventory')
                    continue
                if r['kind'] == 'path':
                    to = self.owner(r)
                    if to != x['to']:
                        problem(w, f'via: {i} leads to {to}, not to {x["to"]}')
                    continue
                if r['kind'] in ('repo', 'workload', 'volume', 'service'):
                    problem(w, f'via: {i} is a {r["kind"]}, which makes no connection')
                    continue
                of = self.owner(r)
                if of != x['from']:
                    problem(w, f'via: {i} is {of or "no component"}\'s, not {x["from"]}\'s')
                if r['kind'] == 'wire':
                    wired[i].add(x['to'])
                if r['kind'] == 'env':
                    named.add(i)
        for r in self.inventory:
            if r['kind'] == 'wire':
                of = self.owner(r)
                for to in sorted(self.leads_to(r) - {of}):
                    if to not in wired.get(r['id'], set()):
                        problem(f'inventory.csv {r["id"]}', f'leads to {to}, and no connection from {of} to {to} '
                                f'names it ({r["where"]})')
                env = r['name'].split(' ', 1)[1]
                if env.endswith(('CONSUME_TOPIC', 'PRODUCE_TOPIC')) and r['value']:
                    kind = 'consumes' if env.endswith('CONSUME_TOPIC') else 'publishes'
                    topic = self.topic(r['value'])
                    if not any(x['from'] == of and x['kind'] == kind and any(fnmatch.fnmatchcase(topic, t) for t in split(x['on']))
                               for x in self.conns):
                        problem(f'inventory.csv {r["id"]}', f'{kind} {topic}, and no connection of {of} says so')
            if r['kind'] == 'env' and ADDRESS.search(r['name']) and r['name'] not in OWN_ADDRESS and r['id'] not in named:
                problem(f'inventory.csv {r["id"]}', f'names an address, and no connection names it ({r["where"]})')
        seen = set()
        for d in self.decisions:
            w = f'decisions.csv {d.get("adr")}'
            if d['adr'] not in self.adrs:
                problem(w, 'is no decision record of docs/adr/')
            if d['adr'] in seen:
                problem(w, 'twice')
            seen.add(d['adr'])
            for k in split(d['components']):
                if k not in self.comp:
                    problem(w, f'components: {k} is not in components.csv')
            for k in split(d['capabilities']):
                if k not in cap_keys:
                    problem(w, f'capabilities: {k} is not in capabilities.csv')
            if len(d['note']) > 140:
                problem(w, 'note is longer than 140 characters')
        for num, a in self.adrs.items():
            if num not in seen:
                problem(a['file'], 'has no row in spec/architecture/decisions.csv')
            for verb, other in a['relations']:
                b = self.adrs.get(other)
                if not b:
                    problem(a['file'], f'{verb} ADR-{other}, which is no record')
                elif (INVERSE[verb], num) not in b['relations']:
                    problem(b['file'], f'ADR-{num} {verb} it, and its status line doesn\'t say "{INVERSE[verb]} ADR-{num}"')

    # ---------------------------------------------------------------- derived
    def derive(self):
        self.serves, self.built_by = defaultdict(list), defaultdict(list)
        for c in self.caps:
            for i in split(c['screens']) + split(c['served_by']):
                for r in self.rows(i):
                    k = self.owner(r)
                    if k and c['key'] not in self.serves[k]:
                        self.serves[k].append(c['key'])
                    if k and k not in self.built_by[c['key']]:
                        self.built_by[c['key']].append(k)
        self.configured = defaultdict(list)
        for s in self.settings:
            for i in split(s['ids']):
                for r in self.rows(i):
                    k = self.owner(r)
                    if k and s['key'] not in self.configured[k]:
                        self.configured[k].append(s['key'])
        self.offers, self.reached = defaultdict(list), defaultdict(list)
        for r in self.inventory:
            k = self.owner(r)
            if not k:
                continue
            if r['kind'] in ('route', 'graphql', 'command', 'field', 'screen', 'tab'):
                self.offers[k].append(r)
            if r['kind'] == 'path':
                self.reached[k].append(r)
        self.decided, self.cap_decided = defaultdict(list), defaultdict(list)
        for d in self.decisions:
            for k in split(d['components']):
                self.decided[k].append(d['adr'])
            for k in split(d['capabilities']):
                self.cap_decided[k].append(d['adr'])
        self.found = self.findings()

    def name_for(self, env):
        """the component, workload or service an environment variable is named for"""
        names = {}
        for c in self.comps:
            names[c['key']] = c['key']
        for i, k in self.runs.items():
            names[i.split(':', 2)[2]] = k
        for s, wl in self.services.items():
            names.setdefault(s, self.runs.get(f'workload:zaentrum-operator:{wl}'))
        for suffix in ('_BASE_URL', '_URL', '_URI'):
            if env.endswith(suffix):
                stem = env[:-len(suffix)]
                for cand in (stem, re.sub(r'_API$', '', stem)):
                    name = cand.lower().replace('_', '-')
                    if name in names:
                        return name, names[name]
                return None, None
        return None, None

    def findings(self):
        """what the model shows the code doing against its decisions or its own names:
        {kind, about: [components], what, via: [ids]}; listed, never failed"""
        out = []
        writers = defaultdict(list)
        for x in self.conns:
            if x['kind'] == 'writes' and self.comp[x['to']]['kind'] == 'database':
                for db in split(x['on']) or ['']:
                    writers[(x['to'], db)].append(x)
        for (store, db), xs in sorted(writers.items()):
            if len({x['from'] for x in xs}) > 1:
                who = sorted({x['from'] for x in xs})
                out.append({'kind': 'two writers', 'about': who + [store],
                            'what': f'the database {db} is written by {" and ".join(who)}; each database is one service\'s',
                            'via': [i for x in xs for i in split(x['via'])]})
        incoming = {x['to'] for x in self.conns}
        for c in self.comps:
            if c['status'] == 'runs' and c['kind'] not in USED_KINDS and c['key'] not in incoming:
                out.append({'kind': 'unconnected', 'about': [c['key']], 'what': f'{c["key"]} runs, and no component connects to it',
                            'via': split(c['runs'])[:1]})
        published, consumed = defaultdict(list), defaultdict(list)
        for x in self.conns:
            for t in split(x['on']):
                if x['kind'] == 'publishes':
                    published[t].append(x)
                elif x['kind'] == 'consumes' and t != '*':
                    consumed[t].append(x)
        for t, xs in sorted(published.items()):
            if not any(fnmatch.fnmatchcase(t, c) or fnmatch.fnmatchcase(c, t) for c in consumed):
                who = sorted({x['from'] for x in xs})
                out.append({'kind': 'unread topic', 'about': who, 'what': f'{" and ".join(who)} publishes {t}, and no component consumes it',
                            'via': [i for x in xs for i in split(x['via'])]})
        for t, xs in sorted(consumed.items()):
            if not any(fnmatch.fnmatchcase(t, p) or fnmatch.fnmatchcase(p, t) for p in published):
                who = sorted({x['from'] for x in xs})
                out.append({'kind': 'unpublished topic', 'about': who, 'what': f'{" and ".join(who)} consumes {t}, and no component publishes it',
                            'via': [i for x in xs for i in split(x['via'])]})
        seen = set()
        for x in self.conns:
            for i in split(x['via']):
                r = self.by_id.get(i)
                if not r or r['kind'] not in ('env', 'wire'):
                    continue
                env = r['name'].split(' ', 1)[1] if r['kind'] == 'wire' else r['name']
                name, comp = self.name_for(env)
                if name and comp != x['to'] and (x['from'], env) not in seen:
                    seen.add((x['from'], env))
                    retired = ' (retired)' if self.comp.get(comp, {}).get('status') == 'retired' else ''
                    out.append({'kind': 'named for another', 'about': [x['from'], x['to']],
                                'what': f'{x["from"]}\'s {env} is named for {name}{retired}, and leads to {x["to"]}', 'via': [i]})
        for r in self.inventory:
            if r['kind'] == 'env':
                for host in re.findall(r'([a-z0-9][a-z0-9-]*)\.[a-z0-9.-]*\.svc\b', r['value']):
                    if host not in self.services:
                        out.append({'kind': 'outside default', 'about': [self.owner(r)] if self.owner(r) else [],
                                    'what': f'{r["repo"]}\'s {r["name"]} defaults to {r["value"]}, a service the platform doesn\'t run',
                                    'via': [r['id']]})
        return out

    # ------------------------------------------------------------------ pages
    def code_link(self, c, rel=''):
        if not c['code']:
            return '—'
        repo, _, prefix = c['code'].partition('/')
        url = f'{GITHUB}/{repo}' + (f'/tree/main/{prefix.rstrip("/")}' if prefix else '')
        return f'[{c["code"]}]({url})'

    def runs_as(self, c):
        names = [i.split(':', 2)[2] for i in split(c['runs'])]
        return ', '.join(f'`{n}`' for n in names) or '—'

    def layer_comps(self, layer):
        return [c for c in self.comps if c['layer'] == layer]

    def state_block(self):
        rows = []
        for layer, label in LAYERS:
            sel = self.layer_comps(layer)
            if sel:
                n = Counter(c['status'] for c in sel)
                rows.append([label, len(sel)] + [n[s] or '' for s in COMP_STATUS])
        n = Counter(c['status'] for c in self.comps)
        rows.append(['all', len(self.comps)] + [n[s] for s in COMP_STATUS])
        out = [table(rows, ['Layer', 'Components'] + COMP_STATUS), '']
        rows = []
        for kind in CONN_KINDS:
            sel = [x for x in self.conns if x['kind'] == kind]
            chart = [x for x in sel if any(self.by_id.get(i, {}).get('kind') in ('wire', 'path') for i in split(x['via']))]
            rows.append([kind, len(sel), len(chart), len(sel) - len(chart)])
        rows.append(['all', len(self.conns), sum(r[2] for r in rows), sum(r[3] for r in rows)])
        out += [table(rows, ['Connections', 'Rows', "Made by the chart's wiring", 'Only in the code']), '']
        kinds = Counter(r['kind'] for r in self.inventory)
        leading = sum(1 for r in self.inventory if r['kind'] == 'wire' and self.leads_to(r) - {self.owner(r)})
        repos = Counter(r['value'] for r in self.inventory if r['kind'] == 'repo')
        out.append(table([
            ['workloads', kinds['workload'], 'a component'],
            ['volumes', kinds['volume'], 'a component'],
            ['services', kinds['service'], 'listed: each leads to a workload'],
            ['paths of the Ingress', kinds['path'], 'listed: each leads to a workload'],
            ['wires', kinds['wire'], f'{leading} lead to another component, each a connection\'s via'],
            ['repositories of the organisation', kinds['repo'], f'a component: {repos["active"]} active, {repos["archived"]} archived'],
        ], ['What the chart runs, and the code', 'Rows', 'Claimed by']))
        adrs = Counter(a['state'] for a in self.adrs.values())
        out.append('')
        out.append(table([[len(self.adrs)] + [adrs[s] for s in sorted(adrs)]],
                         ['Decision records'] + sorted(adrs)))
        return '\n'.join(out) + '\n'

    def findings_block(self):
        if not self.found:
            return 'Nothing.\n'
        rows = [[f['kind'], ', '.join(f'`{k}`' for k in f['about']), f['what'], code_list(f['via'], 2)] for f in self.found]
        return table(rows, ['Finding', 'Components', 'What the model shows', 'In the code']) + '\n'

    def components_block(self):
        out = []
        for layer, label in LAYERS:
            sel = self.layer_comps(layer)
            if not sel:
                continue
            out.append(f'## {label[:1].upper() + label[1:]}\n')
            body = [[f'`{c["key"]}`', c['component'], c['kind'], c['status'], self.code_link(c), self.runs_as(c),
                     len(self.serves.get(c['key'], [])) or '—', len(self.configured.get(c['key'], [])) or '—',
                     ', '.join(f'ADR-{a}' for a in self.decided.get(c['key'], [])) or '—'] for c in sel]
            out.append(table(body, ['Component', 'Is', 'Kind', 'Status', 'Code', 'Runs as', 'Capabilities', 'Settings',
                                    'Decisions']) + '\n')
            notes = [f'- `{c["key"]}`: {c["note"]}' for c in sel if c['note']]
            if notes:
                out.append('\n'.join(notes) + '\n')
        return '\n'.join(out).rstrip() + '\n'

    def connections_block(self):
        def key(x):
            return (self.order[self.comp[x['from']]['layer']], x['from'], CONN_KINDS.index(x['kind']), x['to'])
        out = ['## Requests\n']
        sel = sorted([x for x in self.conns if x['kind'] in ('calls', 'signs in', 'manages', 'links')], key=key)
        out.append(table([[f'`{x["from"]}`', x['kind'], f'`{x["to"]}`', ', '.join(split(x['on'])) or '—', x['note'] or '—']
                          for x in sel], ['From', 'Kind', 'To', 'On', 'Note']) + '\n')
        out.append('## Events\n')
        topics = defaultdict(lambda: ([], []))
        for x in self.conns:
            if x['kind'] in ('publishes', 'consumes'):
                for t in split(x['on']):
                    topics[t][0 if x['kind'] == 'publishes' else 1].append(x['from'])
        published = [t for t, (pub, _) in topics.items() if pub]
        # a topic a component publishes, and one it consumes that none publishes; a
        # pattern a consumer reads by ("catalog.item.*") counts for every topic it matches
        shown = sorted(t for t in topics if t != '*' and (topics[t][0] or not any(
            fnmatch.fnmatchcase(p, t) or fnmatch.fnmatchcase(t, p) for p in published)))
        rows = []
        for t in shown:
            pub, con = topics[t]
            readers = sorted(set(con) | {f for p, (_, cs) in topics.items() if p not in (t, '*')
                                         and (fnmatch.fnmatchcase(t, p) or fnmatch.fnmatchcase(p, t)) for f in cs})
            rows.append([f'`{t}`', ', '.join(f'`{k}`' for k in sorted(set(pub))) or '—',
                         ', '.join(f'`{k}`' for k in readers) or '—'])
        out.append(table(rows, ['Topic, after the prefix', 'Published by', 'Consumed by']) + '\n')
        every = sorted(set(topics['*'][1])) if '*' in topics else []
        if every:
            out.append(f'{" and ".join(f"`{k}`" for k in every)} {"reads" if len(every) == 1 else "read"} every topic.')
        out.append(f'Every topic carries the instance\'s prefix, `{self.prefix}` unless the resource says another.\n')
        out.append('## Stores\n')
        stores = defaultdict(lambda: ([], []))
        for x in self.conns:
            if x['kind'] in ('writes', 'reads'):
                for on in split(x['on']) or ['']:
                    stores[(x['to'], on)][0 if x['kind'] == 'writes' else 1].append(x['from'])
        rows = [[f'`{s}`', on or '—', ', '.join(f'`{k}`' for k in sorted(set(w))) or '—', ', '.join(f'`{k}`' for k in sorted(set(r))) or '—']
                for (s, on), (w, r) in sorted(stores.items(), key=lambda i: (self.order[self.comp[i[0][0]]['layer']], i[0]))]
        out.append(table(rows, ['Store', 'On', 'Written by', 'Read by']) + '\n')
        return '\n'.join(out).rstrip() + '\n'

    def decisions_block(self):
        rows = []
        for d in self.decisions:
            a = self.adrs.get(d['adr'])
            if not a:
                continue
            rel = '; '.join(f'{verb} ADR-{n}' for verb, n in a['relations']) or '—'
            rows.append([f'[ADR-{a["number"]}](../../{a["file"]})', a['title'], a['state'],
                         ', '.join(f'`{k}`' for k in split(d['components'])) or '—',
                         ', '.join(f'`{k}`' for k in split(d['capabilities'])) or '—', rel])
        return table(rows, ['Record', 'Decision', 'Status', 'Components', 'Capabilities', 'Relations']) + '\n'

    def routes_block(self):
        rows = []
        for r in sorted((r for r in self.inventory if r['kind'] == 'path'), key=lambda r: r['name']):
            k = self.owner(r)
            c = self.comp.get(k, {})
            rows.append([f'`{r["name"]}`', f'`{r["value"]}`' + (f' (`{k}`)' if k and k != r['value'] else ''), c.get('component', '—')])
        return table(rows, ['Path', 'Workload', 'What it is']) + '\n'

    def diagram_block(self):
        """the picture of docs/architecture.md: what the chart runs or ships, lane by lane,
        and how it reaches the rest; sign-in, the browser's links and the jobs left out.
        An edge every component of a lane has is drawn once, from the lane."""
        lanes = ['apps', 'portal', 'chino', 'catalog', 'pipeline', 'bundled', 'runtime']
        shown = [c for c in self.comps if c['layer'] in lanes and c['status'] in ('runs', 'ships') and c['kind'] != 'job']
        keys = {c['key'] for c in shown}
        nid = {c['key']: re.sub(r'[^a-zA-Z0-9]', '_', c['key']) for c in shown}
        out = ['```mermaid', 'flowchart LR']
        for layer in lanes:
            sel = [c for c in shown if c['layer'] == layer]
            if sel:
                out.append(f'  subgraph {layer}["{dict(LAYERS)[layer]}"]')
                out.append('    ' + '; '.join(f'{nid[c["key"]]}["{c["key"]}"]' for c in sel))
                out.append('  end')
        edges = {}
        for x in self.conns:
            if x['kind'] in ('signs in', 'links') or x['from'] not in keys or x['to'] not in keys:
                continue
            arrow = '-.->' if x['kind'] in ('publishes', 'consumes') else '-->'
            edges.setdefault((x['from'], x['to']), arrow)
        drawn = []
        for layer in lanes:
            members = {c['key'] for c in shown if c['layer'] == layer}
            if len(members) < 2:
                continue
            for (a, b), arrow in list(edges.items()):
                if a in members and b not in members and all(edges.get((m, b)) == arrow for m in members):
                    drawn.append(f'  {layer} {arrow} {nid[b]}')
                    for m in members:
                        edges.pop((m, b), None)
        out += drawn + [f'  {nid[a]} {arrow} {nid[b]}' for (a, b), arrow in edges.items()]
        out.append('```')
        return '\n'.join(out) + '\n'

    # ------------------------------------------------------------------- JSON
    def export(self, rows):
        def comp_json(c):
            repo, _, prefix = c['code'].partition('/') if c['code'] else ('', '', '')
            return {**{k: c[k] for k in ('key', 'component', 'layer', 'kind', 'status', 'code', 'note')},
                    'repo': repo, 'prefix': prefix,
                    'runs': rows(split(c['runs'])), 'reached': [{k: r[k] for k in ('id', 'name', 'value', 'note', 'where', 'repo', 'kind')} for r in self.reached.get(c['key'], [])],
                    'capabilities': self.serves.get(c['key'], []), 'settings': self.configured.get(c['key'], []),
                    'offers': [{k: r[k] for k in ('id', 'kind', 'repo', 'name', 'value', 'note', 'where')} for r in self.offers.get(c['key'], [])],
                    'decisions': self.decided.get(c['key'], [])}
        return {
            'layers': [{'key': k, 'label': label} for k, label in LAYERS],
            'kinds': COMP_KINDS, 'statuses': COMP_STATUS, 'connectionKinds': CONN_KINDS, 'prefix': self.prefix,
            'components': [comp_json(c) for c in self.comps],
            'connections': [{'from': x['from'], 'to': x['to'], 'kind': x['kind'], 'on': split(x['on']), 'note': x['note'],
                             'via': rows(split(x['via']))} for x in self.conns],
            'decisions': [{**self.adrs[d['adr']], 'relations': [list(r) for r in self.adrs[d['adr']]['relations']],
                           'components': split(d['components']), 'capabilities': split(d['capabilities']), 'note': d['note']}
                          for d in self.decisions if d['adr'] in self.adrs],
            'builtBy': dict(self.built_by), 'capabilityDecisions': dict(self.cap_decided),
            'findings': self.found,
        }


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
    arch = Arch(read('components.csv', COMP_COLS, ARCH), read('connections.csv', CONN_COLS, ARCH),
                read('decisions.csv', DEC_COLS, ARCH), inventory, caps, settings)
    arch.check({c['key'] for c in caps})
    arch.derive()
    if '--json' in sys.argv:
        at = sys.argv.index('--json') + 1
        if at >= len(sys.argv):
            sys.exit('--json needs the file to write')
        export(areas, caps, settings, inventory, sys.argv[at], arch)
        print(f'{len(problems)} problems; {len(caps)} capabilities, {len(settings)} settings, '
              f'{len(arch.comps)} components, {len(arch.conns)} connections written to {sys.argv[at]}')
        return
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
    fill(os.path.join(ARCH, 'README.md'), {'state': arch.state_block(), 'findings': arch.findings_block()}, write)
    fill(os.path.join(ARCH, 'components.md'), {'components': arch.components_block()}, write)
    fill(os.path.join(ARCH, 'connections.md'), {'connections': arch.connections_block()}, write)
    fill(os.path.join(ARCH, 'decisions.md'), {'decisions': arch.decisions_block()}, write)
    fill(os.path.join(DOCS, 'architecture.md'), {'diagram': arch.diagram_block(), 'routes': arch.routes_block()}, write)
    for p in problems:
        print(p)
    print(f'{len(problems)} problems; {len(caps)} capabilities in {len(areas)} areas, {len(settings)} settings, '
          f'{len(inventory)} inventory rows; {len(arch.comps)} components, {len(arch.conns)} connections, '
          f'{len(arch.decisions)} decisions, {len(arch.found)} findings')
    sys.exit(1 if problems else 0)


if __name__ == '__main__':
    main()
