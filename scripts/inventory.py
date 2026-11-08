#!/usr/bin/env python3
"""inventory.py : what the code of zaentrum offers, listed from the main branch of
every repository, one row a thing (spec/capabilities/inventory.csv).

  python3 scripts/inventory.py --src DIR [--fetch] [--check]

DIR holds a clone of each repository under its own name (git@github.com or
https://github.com/zaentrum/<name>); --fetch clones what is missing and fetches
main, --check compares with the committed list and exits 1 when they differ.
Each repository is read at origin/main (HEAD where there is no origin), never
the working tree, so local changes don't count.

Kinds:
  route     an HTTP route a service answers: METHOD /path (chi routers, a
            ServeMux pattern); health and metrics routes too
  graphql   a query or mutation of a GraphQL schema
  screen    a screen of an app or a console: a component file named …Page,
            …Screen, …Section, …Console, …View, …Panel, …Wizard, …Card, …Bell,
            …Launchpad, …Shell, …Host
  tab       a tab of a console (an item of a Tabs list)
  command   a command of the zae CLI
  field     a field of the operator's resources (spec.…), with its default
  env       an environment variable a service or an app reads
  setting   a setting of the catalog's settings table
  constant  a number, a duration, a switch or a list fixed in the code

The specification's capability model (spec/capabilities) claims every row
of the kinds route, graphql, screen, tab, command, field, env and setting;
scripts/capabilities.py checks that. Constants are listed, not claimed yet."""
import argparse
import csv
import io
import os
import re
import subprocess
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'spec', 'capabilities', 'inventory.csv')
SOURCES = os.path.join(ROOT, 'spec', 'capabilities', 'inventory-sources.csv')
GITHUB = 'https://github.com/zaentrum'

# the repositories whose main branch is the product, and what each is
REPOS = [
    'zaentrum-portal', 'zaentrum-operator', 'zae',
    'chino-api', 'chino-stream', 'chino-web', 'chino-mobile', 'chino-androidtv', 'chino-tizen',
    'katalog-manager', 'katalog-manager-ui', 'katalog-api', 'katalog-ingest',
    'analyzer', 'transcoder', 'packager', 'subtitler', 'live-worker',
]

SCREEN_FILE = re.compile(r'(?:^|/)((?:[A-Z]\w*?)?(?:Page|Screen|Section|Console|View|Panel|Wizard|Card|Bell|Launchpad|Shell|Host))(?:\.(?:android|ios))?\.(?:tsx|kt)$')
TEST_PATH = re.compile(r'(?:^|/)\w*(?:test|fake)/|(?:^|/)(?:test|tests|testdata|__tests__|e2e|harness|preview|mocks?|fixtures?|androidTest|commonTest|androidUnitTest|iosTest|jvmTest|testFixtures)(?:/|$)|_test\.go$|\.(?:test|spec)\.[jt]sx?$|Test\.kt$|(?:^|/)test_[^/]*\.py$|_test\.py$|conftest\.py$')
# not the product: tooling, benchmarks; in the operator's repository only operator/ is the
# platform (apps/ and deploy/ are the older, unsupported profiles)
TOOLING = re.compile(r'(?:^|/)(?:bench|benchmarks?|tools|hack|scripts)/')
ONLY = {'zaentrum-operator': ('operator/',)}
UPPER = re.compile(r'^[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+$|^(?:PORT|ADDR|HOST|DEBUG)$')


def git(repo_dir, *args):
    r = subprocess.run(['git', '-C', repo_dir, *args], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f'git -C {repo_dir} {" ".join(args)}: {r.stderr.strip()}')
    return r.stdout


class Repo:
    def __init__(self, src, name):
        self.name = name
        self.dir = os.path.join(src, name)
        refs = git(self.dir, 'for-each-ref', '--format=%(refname)', 'refs/remotes/origin/main')
        self.ref = 'origin/main' if refs.strip() else 'HEAD'
        self.commit = git(self.dir, 'rev-parse', self.ref).strip()
        self.files = [f for f in git(self.dir, 'ls-tree', '-r', '--name-only', self.ref).split('\n')
                      if f and not TOOLING.search(f) and f.startswith(ONLY.get(name, ''))]
        self._cache = {}

    def text(self, path):
        if path not in self._cache:
            self._cache[path] = git(self.dir, 'show', f'{self.commit}:{path}')
        return self._cache[path]

    def code(self, *exts):
        return [f for f in self.files if f.endswith(exts) and not TEST_PATH.search(f)
                and not f.startswith(('vendor/', 'node_modules/', 'dist/', 'build/'))]


rows = {}


def add(kind, repo, name, path, line, value='', note=''):
    rid = f'{kind}:{repo.name}:{name}'
    if rid in rows:
        old = rows[rid]
        if not old['value'] and value:
            old['value'] = value
        if not old['note'] and note:
            old['note'] = note
        return
    rows[rid] = {'id': rid, 'kind': kind, 'repo': repo.name, 'name': name, 'value': clean(value),
                 'note': clean(note), 'where': f'{path}:{line}'}


def clean(s):
    s = re.sub(r'\s+', ' ', str(s or '')).strip()
    return s if len(s) <= 160 else s[:157].rstrip() + '…'


def first_sentence(doc):
    doc = ' '.join(d.strip() for d in doc)
    m = re.match(r'(.+?[.])(?:\s|$)', doc)
    return (m.group(1) if m else doc).strip()


def strip_code(line):
    """the line without its strings and its // comment, for counting braces"""
    line = re.sub(r'"(?:\\.|[^"\\])*"|`[^`]*`|\'(?:\\.|[^\'\\])\'', '""', line)
    return line.split('//', 1)[0]


# ---------------------------------------------------------------- Go routes
def go_routes(repo):
    for f in repo.code('.go'):
        text = repo.text(f)
        if not re.search(r'chi\.(?:New)?Router|chi\.Mux|http\.NewServeMux|\.HandleFunc\(|\.Handle\(', text):
            continue
        stack, depth = [], 0
        for i, line in enumerate(text.split('\n'), 1):
            m = re.search(r'\.Route\(\s*"([^"]*)"\s*,\s*func\(\s*\w+\s+chi\.Router\s*\)\s*\{', line)
            g = re.search(r'\.Group\(\s*func\(\s*\w+\s+chi\.Router\s*\)\s*\{', line)
            prefix = ''.join(p for p, _ in stack)
            for mm in re.finditer(r'\.(Get|Post|Put|Patch|Delete|Head|Options)\(\s*"(/[^"]*)"', line):
                add('route', repo, f'{mm.group(1).upper()} {prefix}{mm.group(2)}', f, i)
            for mm in re.finditer(r'\.Method\(\s*(?:"(\w+)"|http\.Method(\w+))\s*,\s*"(/[^"]*)"', line):
                method = (mm.group(1) or mm.group(2)).upper()
                add('route', repo, f'{method} {prefix}{mm.group(3)}', f, i)
            for mm in re.finditer(r'\.(?:Handle|HandleFunc|Mount)\(\s*"((?:[A-Z]+ )?/[^"]*)"', line):
                pat = mm.group(1)
                if ' ' in pat:
                    method, path = pat.split(' ', 1)
                    add('route', repo, f'{method.upper()} {prefix}{path}', f, i)
                else:
                    add('route', repo, f'ANY {prefix}{pat}', f, i)
            code = strip_code(line)
            opens, closes = code.count('{'), code.count('}')
            if m:
                stack.append((m.group(1), depth + 1))
            elif g:
                stack.append(('', depth + 1))
            depth += opens - closes
            while stack and depth < stack[-1][1]:
                stack.pop()


# -------------------------------------------------------------- GraphQL ops
def graphql_ops(repo):
    for f in repo.code('.graphql', '.graphqls'):
        kind_of, depth, paren, doc = None, 0, 0, False
        for i, line in enumerate(repo.text(f).split('\n'), 1):
            code = line.split('#', 1)[0]
            if code.count('"""') % 2:          # a block description opens or closes
                doc = not doc
                continue
            if doc or code.strip().startswith('"'):
                continue
            m = re.match(r'\s*(?:extend\s+)?type\s+(Query|Mutation|Subscription)\b', code)
            if m and depth == 0:
                kind_of = m.group(1).lower()
            elif depth == 1 and paren == 0 and kind_of:
                fm = re.match(r'\s*(\w+)\s*[(:]', code)
                if fm:
                    add('graphql', repo, f'{kind_of} {fm.group(1)}', f, i)
            depth += code.count('{') - code.count('}')
            paren += code.count('(') - code.count(')')
            if depth == 0:
                kind_of = None if not m else kind_of


# ------------------------------------------------------------------ screens
def screens(repo):
    for f in repo.files:
        if TEST_PATH.search(f):
            continue
        m = SCREEN_FILE.search(f)
        if m and f.startswith(('src/', 'app/src/main/', 'shared/src/')):
            add('screen', repo, m.group(1), f, 1)


def tabs(repo):
    for f in repo.code('.tsx'):
        text = repo.text(f)
        if '<Tabs' not in text:
            continue
        comp = os.path.splitext(os.path.basename(f))[0]
        for i, line in enumerate(text.split('\n'), 1):
            for mm in re.finditer(r"\{\s*value:\s*'([a-z][\w-]*)'\s*,\s*label:", line):
                add('tab', repo, f'{comp} {mm.group(1)}', f, i)


# ---------------------------------------------------------------- zae CLI
def zae_commands(repo):
    top = {}
    text = repo.text('main.go')
    in_switch = False
    for i, line in enumerate(text.split('\n'), 1):
        if re.search(r'switch\s+os\.Args\[1\]\s*\{', line):
            in_switch = True
            continue
        if in_switch:
            m = re.match(r'\s*case\s+"([a-z][\w-]*)"', line)
            if m and m.group(1) not in ('help', 'version'):
                top[m.group(1)] = i
            if re.match(r'\s*default:', line) or re.match(r'^\t\}', line):
                in_switch = False
    for name, i in top.items():
        add('command', repo, name, 'main.go', i)
    for f in repo.code('.go'):
        parts = f.split('/')
        if len(parts) != 3 or parts[0] != 'internal' or parts[1] not in top:
            continue
        sw = None
        for i, line in enumerate(repo.text(f).split('\n'), 1):
            s = re.search(r'\bswitch\b\s*(.*?)\s*\{\s*$', line)
            if s:
                sw = s.group(1)
                continue
            if sw and re.fullmatch(r'(?:\w+\.)?[aA]rgs\[\d\]|sub|verb|cmd|os\.Args\[2\]', sw):
                m = re.match(r'\s*case\s+"([a-z][\w-]*)"', line)
                if m and m.group(1) not in ('help',):
                    add('command', repo, f'{parts[1]} {m.group(1)}', f, i)


def doc_default(doc, enum=''):
    """the default a doc comment states, where it says so plainly: "Default 7.",
    "Default "@daily", at midnight.", "(default: X)", "Default: X"; "X, the default" or
    "X (the default)" only for one of the field's values; "Empty: …" when it is short"""
    text = ' '.join(d.strip() for d in doc)
    for pat in (r'\bDefault(?:s to|:)?\s+("[^"]*"|[^\s,.;:]+)[.,;]',
                r'\(default:?\s+([^()]+?)\)'):
        m = re.search(pat, text)
        if m:
            return m.group(1).strip('"').strip()
    values = [v for v in enum.split(';') if v] or ['true', 'false', 'on', 'off']
    for pat in (r'(\S+?)\s+\(the default\)', r'\b(\S+?),\s+the default\b'):
        for m in re.finditer(pat, text):
            v = m.group(1).strip('"\'(').lower()
            if v in [x.lower() for x in values]:
                return v
    m = re.search(r'\b(?:Unset|Empty)(?: or empty)?:\s+([^.;:]+)[.;:]', text)
    if m and len(m.group(1)) <= 60:
        return m.group(1).strip()
    return ''


# ------------------------------------------------- the operator's resources
def operator_fields(repo):
    types, docs = {}, {}
    for f in repo.code('.go'):
        if '/api/' not in f or not f.endswith('_types.go'):
            continue
        cur, doc, marks = None, [], []
        for i, line in enumerate(repo.text(f).split('\n'), 1):
            st = re.match(r'type\s+(\w+)\s+struct\s*\{', line)
            if st:
                cur, doc, marks = st.group(1), [], []
                types[cur] = []
                continue
            if cur is None:
                continue
            if re.match(r'^\}', line):
                cur = None
                continue
            c = re.match(r'\s*//\s?(.*)', line)
            if c:
                (marks if c.group(1).startswith('+') else doc).append(c.group(1))
                continue
            fm = re.match(r'\s*(\w+)?\s*([\*\[\]\w\.]+)\s+`json:"([^"]*)"', line)
            if fm:
                jname = fm.group(3).split(',')[0]
                inline = 'inline' in fm.group(3)
                default = next((m[len('+kubebuilder:default='):] for m in marks if m.startswith('+kubebuilder:default=')), '')
                enum = next((m[len('+kubebuilder:validation:Enum='):] for m in marks if m.startswith('+kubebuilder:validation:Enum=')), '')
                types[cur].append({'name': jname, 'type': fm.group(2), 'inline': inline, 'doc': doc,
                                   'default': default, 'enum': enum, 'where': (f, i)})
            doc, marks = [], []
    def walk(tname, path, seen):
        for fld in types.get(tname, []):
            base = re.sub(r'^[\*\[\]]+', '', fld['type']).split('.')[-1]
            sub = path if fld['inline'] else (f"{path}.{fld['name']}" if fld['name'] else path)
            if fld['type'].startswith('[]') and base in types:
                sub += '[]'
            if base in types and base not in seen:
                walk(base, sub, seen | {base})
            elif fld['name'] or fld['inline']:
                value = fld['default'] or doc_default(fld['doc'], fld['enum'])
                note = first_sentence(fld['doc'])
                if fld['enum']:
                    note = (note + f" One of: {fld['enum'].replace(';', ', ')}.").strip()
                add('field', repo, sub, fld['where'][0], fld['where'][1], value, note)
    for kind, spec in (('Zaentrum', 'ZaentrumSpec'), ('ZaentrumAddon', 'ZaentrumAddonSpec')):
        if spec in types:
            walk(spec, f'{kind}.spec', {spec})


# ----------------------------------------------- environment variables
def env_vars(repo):
    comment_default = re.compile(r'\b([A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+)\b[^()]*\(default ([^)]*)\)')
    for f in repo.code('.go', '.py', '.ts', '.tsx', '.mjs'):
        text = repo.text(f)
        is_config = 'config' in f.lower() or 'settings' in f.lower()
        lines = text.split('\n')
        for i, line in enumerate(lines, 1):
            for mm in re.finditer(r'import\.meta\.env\.([A-Z][A-Z0-9_]+)', line):
                add('env', repo, mm.group(1), f, i)
            # a call of an env helper: env("A", "B"), envDefault("8080", "PORT"), _env_int("X", 4);
            # in a config file any call whose argument is a name: _require("X"), r.int("X", 4)
            code = line.split('//', 1)[0]
            for mm in re.finditer(r'\b([\w.]+)\(', code):
                fn = mm.group(1).split('.')[-1]
                if fn in ('Getenv', 'LookupEnv', 'getenv', 'Environ', 'environ', 'get', 'Errorf', 'Sprintf', 'New', 'Error', 'print', 'Printf', 'Println', 'append'):
                    continue
                env_fn = re.search(r'env', fn, re.I)
                if not env_fn and not is_config:
                    continue
                rest = code[mm.end():]
                lits = [a or b for a, b in re.findall(r'"([^"]*)"|\'([^\']*)\'', rest)]
                if env_fn:
                    names = [x for x in lits if UPPER.match(x)]
                else:  # a config file's own helper: its first argument is the name
                    first = re.match(r'\s*["\']([A-Z][A-Z0-9_]+)["\']', rest)
                    names = [first.group(1)] if first and UPPER.match(first.group(1)) else []
                others = [x for x in lits if not UPPER.match(x)]
                num = re.match(r'\s*["\'][A-Z][A-Z0-9_]+["\']\s*,\s*([-\d_.]+|True|False|true|false|None)\b', rest)
                for n in names:
                    add('env', repo, n, f, i, value=others[0] if others else (num.group(1) if num else ''))
        # os.environ.get("X", "default") and os.Getenv("X"), also across lines
        for mm in re.finditer(r'(?:os\.(?:Getenv|LookupEnv|getenv)|os\.environ\.get|os\.environ\[|environ\.get)\(?\s*["\']([A-Z][A-Z0-9_]+)["\'](?:\s*,\s*["\']([^"\']*)["\'])?', text):
            add('env', repo, mm.group(1), f, text.count('\n', 0, mm.start()) + 1, value=mm.group(2) or '')
    # a web image's entrypoint script: ${BASE_PATH:-/}
    for f in repo.files:
        if not re.search(r'(?:^|/)docker-entrypoint\.d/[^/]+\.sh$|(?:^|/)[\w-]*entrypoint[\w-]*\.sh$', f):
            continue
        for i, line in enumerate(repo.text(f).split('\n'), 1):
            if line.lstrip().startswith('#'):
                continue
            for mm in re.finditer(r'\$\{([A-Z][A-Z0-9]*_[A-Z0-9_]+)(?::?-([^}]*))?\}', line):
                if mm.group(1) not in ('PATH', 'HOME', 'PWD', 'USER', 'SHELL', 'HOSTNAME', 'IFS', 'TMPDIR'):
                    add('env', repo, mm.group(1), f, i, value=mm.group(2) or '')
    for f in repo.code('.go', '.py', '.ts', '.tsx', '.mjs'):
        text = repo.text(f)
        is_config = 'config' in f.lower() or 'settings' in f.lower()
        lines = text.split('\n')
        for i, line in enumerate(lines, 1):
            if is_config:
                for mm in comment_default.finditer(line):
                    if f'env:{repo.name}:{mm.group(1)}' in rows:
                        r = rows[f'env:{repo.name}:{mm.group(1)}']
                        if not r['value']:
                            r['value'] = clean(mm.group(2))
    # a default stated in a comment of a config file: "Port string // PORT (default 8080)"
    for f in repo.code('.go', '.py'):
        if 'config' not in f.lower():
            continue
        for line in repo.text(f).split('\n'):
            comment = line.split('//', 1)[1] if '//' in line else (line.split('#', 1)[1] if line.lstrip().startswith('#') else '')
            for mm in comment_default.finditer(comment):
                rid = f'env:{repo.name}:{mm.group(1)}'
                if rid in rows and not rows[rid]['value']:
                    rows[rid]['value'] = clean(mm.group(2))


# --------------------------------------------------- the catalog's settings
VALUE_LIKE = re.compile(r'^(?:\d+(?:\.\d+)?[a-zA-Z]*|\d\d:\d\d(?:-\d\d:\d\d)?|on|off|true|false|keep|legacy|full|chain|v2|none)$')


def catalog_settings(repo):
    """the settings table's keys: SettingX = "a.b", settingY = "c.d_e", and lists of keys
    (secretSettingKeys = []string{"tmdb.api_key", …})"""
    decl = re.compile(r'^\s*(?:const\s+|var\s+)?(\w*[sS]etting\w*)\s*=\s*"([a-z]+(?:\.[a-zA-Z0-9_]+)+)"')
    listed = re.compile(r'^\s*(?:var\s+)?(\w*[sS]ettings?\w*)\s*=\s*\[\]string\{([^}]*)\}')
    for f in repo.code('.go'):
        doc = []
        for i, line in enumerate(repo.text(f).split('\n'), 1):
            c = re.match(r'\s*//\s?(.*)', line)
            if c:
                doc.append(c.group(1))
                continue
            m = decl.match(line)
            if m:
                text = ' '.join(d.strip() for d in doc)
                # "is legacy (the default) or v2", "full (every file's hash, the default)",
                # "is on or off (the default)", "… at most (30).", "… (24h); 0 unlinks"
                dm = (re.search(r'(\S+)\s+\((?:[^()]*,\s*)?the default\)', text)
                      or re.search(r'\(([^()]{1,24})\)\s*[.;:]', text))
                value = dm.group(1).strip('",') if dm else ''
                if not VALUE_LIKE.match(value):
                    value = ''
                note = re.sub(r'^\w+ (?:is )?', '', first_sentence(doc))
                add('setting', repo, m.group(2), f, i, value, note[:1].upper() + note[1:])
            lm = listed.match(line)
            if lm:
                for key in re.findall(r'"([a-z]+(?:\.[a-zA-Z0-9_]+)+)"', lm.group(2)):
                    add('setting', repo, key, f, i, '', first_sentence(doc))
            doc = []


# ----------------------------------------------------------------- constants
NUMERIC = re.compile(r'^[-+]?[\d_.]+(?:[eE][-+]?\d+)?[LfFuU]?$|^[\d_.\s*+/()\-]+(?:\*\s*time\.\w+|time\.\w+)?$|^(?:true|false)$|^[\d_.\s*+/()\-]*\s*(?:\*\s*)?(?:time\.)?(?:Nanosecond|Microsecond|Millisecond|Second|Minute|Hour)$|^(?:[\d_.]+\s*\*\s*)*(?:time\.)?(?:Second|Minute|Hour|Millisecond)s?$|^\d+\.(?:seconds|minutes|hours|milliseconds)$')


def const_value(v):
    v = v.split('//', 1)[0].strip().rstrip(';').strip()
    if v.endswith(','):
        v = v[:-1]
    return v


def constants(repo):
    for f in repo.code('.ts', '.tsx', '.kt', '.go', '.py'):
        text = repo.text(f)
        stem = os.path.splitext(os.path.basename(f))[0].replace('.android', '').replace('.ios', '')
        in_go_const = False
        for i, line in enumerate(text.split('\n'), 1):
            name = value = None
            if f.endswith(('.ts', '.tsx')):
                m = re.match(r'^(?:export\s+)?const\s+([A-Z][A-Z0-9_]+)\s*(?::[^=]+)?=\s*(.+)$', line)
                if m:
                    name, value = m.group(1), const_value(m.group(2))
            elif f.endswith('.kt'):
                m = re.match(r'^\s*(?:(?:private|internal|public)\s+)?const\s+val\s+([A-Z][A-Z0-9_]+)\s*(?::\s*\w+)?\s*=\s*(.+)$', line)
                if m:
                    name, value = m.group(1), const_value(m.group(2))
            elif f.endswith('.go'):
                if re.match(r'^const\s*\($', line):
                    in_go_const = True
                    continue
                if in_go_const and re.match(r'^\)', line):
                    in_go_const = False
                    continue
                m = re.match(r'^const\s+(\w+)\s*(?:\w+\s*)?=\s*(.+)$', line) or (in_go_const and re.match(r'^\t(\w+)\s*(?:[\w.]+\s*)?=\s*(.+)$', line))
                if m:
                    name, value = m.group(1), const_value(m.group(2))
            elif f.endswith('.py'):
                m = re.match(r'^([A-Z][A-Z0-9_]+)\s*(?::\s*\w+)?\s*=\s*(.+)$', line)
                if m:
                    name, value = m.group(1), const_value(m.group(2))
            if name and value is not None and NUMERIC.match(value.replace(' ', ' ')):
                add('constant', repo, f'{stem}.{name}', f, i, value)


def build(src):
    sources = []
    for name in REPOS:
        repo = Repo(src, name)
        sources.append({'repo': name, 'commit': repo.commit})
        if any(f.endswith('.go') for f in repo.files):
            go_routes(repo)
        graphql_ops(repo)
        screens(repo)
        tabs(repo)
        if name == 'zae':
            zae_commands(repo)
        if name == 'zaentrum-operator':
            operator_fields(repo)
        if name == 'katalog-manager':
            catalog_settings(repo)
        env_vars(repo)
        constants(repo)
    return sources


def write_csv(path, fields, items):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, lineterminator='\n')
    w.writeheader()
    for it in items:
        w.writerow(it)
    return path, buf.getvalue()


def fetch(src):
    os.makedirs(src, exist_ok=True)
    for name in REPOS:
        d = os.path.join(src, name)
        if not os.path.isdir(os.path.join(d, '.git')):
            subprocess.run(['git', 'clone', '-q', '--filter=blob:none', f'{GITHUB}/{name}.git', d], check=True)
        else:
            subprocess.run(['git', '-C', d, 'fetch', '-q', 'origin', 'main'], check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--src', default=os.environ.get('INVENTORY_SRC', os.path.expanduser('~/.cache/zaentrum-inventory')))
    ap.add_argument('--fetch', action='store_true')
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    if a.fetch:
        fetch(a.src)
    sources = build(a.src)
    items = sorted(rows.values(), key=lambda r: (r['kind'], r['repo'], r['name']))
    outputs = [write_csv(OUT, ['id', 'kind', 'repo', 'name', 'value', 'note', 'where'], items),
               write_csv(SOURCES, ['repo', 'commit'], sources)]
    if a.check:
        stale = [p for p, text in outputs if not os.path.exists(p) or open(p, encoding='utf-8').read() != text]
        for p in stale:
            print(f'{os.path.relpath(p, ROOT)} is not what the code says: run scripts/inventory.py')
        sys.exit(1 if stale else 0)
    for p, text in outputs:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'w', encoding='utf-8').write(text)
    counts = {}
    for r in items:
        counts[r['kind']] = counts.get(r['kind'], 0) + 1
    print(' '.join(f'{k} {v}' for k, v in sorted(counts.items())), f'= {len(items)} rows from {len(sources)} repositories')


if __name__ == '__main__':
    main()
