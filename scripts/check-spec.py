#!/usr/bin/env python3
"""check-spec.py [chino dir] : the structure of the chino specification, checked
(spec/chino by default).
One line per problem (chapter, what); exit 1 if there is any. Checks:
  H1 = "# <n> <title>" with n from the chapter order; ## n.k numbered 1, 2, 3 …;
  every image is followed by a caption "Figure n.m: …", m = 1, 2, 3 … in order;
  every figure is named in the text outside its caption;
  a figure drawn with marks (data-co / data-co-parts in img/*.html) has a legend
  (a numbered list right after the caption) with as many items as marks;
  every image file exists."""
import os
import re
import sys

d = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'spec', 'chino')
ORDER = ['README', 'frame', 'start', 'home', 'browse', 'title-actions', 'person', 'watchlist', 'search',
         'zap', 'playback', 'subtitles', 'downloads', 'casting', 'notifications', 'settings', 'errors', 'words']

# marks per figure id, from every drawing source
marks = {}
for name in sorted(os.listdir(os.path.join(d, 'img'))):
    if not name.endswith('.html'):
        continue
    html = open(os.path.join(d, 'img', name), encoding='utf-8').read()
    html = re.sub(r'<!--.*?-->', '', html, flags=re.S)  # a comment that shows a figure tag is not a figure
    for m in re.finditer(r'<figure class="shot" id="([^"]+)"[^>]*>(.*?)</figure>', html, re.S):
        if m.group(1) in marks:
            continue  # the first file wins, as when rendering (chNN before mockups.html)
        body = m.group(2)
        n = len(re.findall(r'\sdata-co="\d+"', body))
        for parts in re.findall(r'data-co-(?:parts|in)="([^"]+)"', body):
            n += len([p for p in parts.split(',') if p.strip()])
        marks[m.group(1)] = n

problems = []
for no, base in enumerate(ORDER, 1):
    path = os.path.join(d, base + '.md')
    if not os.path.exists(path):
        problems.append((no, f'{base}.md is missing'))
        continue
    lines = open(path, encoding='utf-8').read().split('\n')
    text = '\n'.join(lines)
    if not re.match(rf'# {no} \S', lines[0]):
        problems.append((no, f'H1 is "{lines[0]}", not "# {no} …"'))
    fence = False
    secs = []
    for line in lines:
        if line.lstrip().startswith(('```', '~~~')):
            fence = not fence
            continue
        if fence:
            continue
        m = re.match(r'^## (\d+)\.(\d+) ', line)
        if line.startswith('## ') and not m:
            problems.append((no, f'unnumbered section "{line}"'))
        elif m:
            if int(m.group(1)) != no:
                problems.append((no, f'section "{line}" has the wrong chapter number'))
            secs.append(int(m.group(2)))
    if secs and secs != list(range(1, len(secs) + 1)):
        problems.append((no, f'sections run {secs}'))
    caps = [int(m.group(1)) for m in re.finditer(rf'^Figure {no}\.(\d+): ', text, re.M)]
    if caps != list(range(1, len(caps) + 1)):
        problems.append((no, f'figures run {caps}'))
    for i, line in enumerate(lines):
        im = re.match(r'^!\[[^\]]*\]\(\./img/([^)]+)\)\s*$', line)
        if not im:
            continue
        file = im.group(1)
        if not os.path.exists(os.path.join(d, 'img', file)):
            problems.append((no, f'image img/{file} does not exist'))
        j = i + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        cap = re.match(rf'^Figure {no}\.(\d+): ', lines[j]) if j < len(lines) else None
        if not cap:
            problems.append((no, f'img/{file}: no caption "Figure {no}.n:" under it'))
            continue
        m_no = int(cap.group(1))
        label = f'Figure {no}.{m_no}'
        k = j
        while k < len(lines) and lines[k].strip():   # the caption, to the end of its paragraph
            k += 1
        caption = '\n'.join(lines[j:k])
        others = text.replace(caption, '').replace(line, '')
        if not re.search(rf'[Ff]igures? {no}\.{m_no}\b|{no}\.\d+ (to|and) {no}\.{m_no}\b|[Ff]igures {no}\.\d+(, {no}\.\d+)* and {no}\.{m_no}\b', others):
            problems.append((no, f'{label} is never named in the text'))
        fid = os.path.splitext(file)[0]
        if marks.get(fid):
            while k < len(lines) and not lines[k].strip():
                k += 1
            items = 0
            while k < len(lines) and (re.match(r'^\d+\. ', lines[k]) or lines[k].startswith('   ')):
                items += bool(re.match(r'^\d+\. ', lines[k]))
                k += 1
                while k < len(lines) and not lines[k].strip() and k + 1 < len(lines) and re.match(r'^\d+\. ', lines[k + 1]):
                    k += 1
            if items != marks[fid]:
                problems.append((no, f'{label} ({fid}): {marks[fid]} marks in the drawing, {items} in the legend'))

for no, what in problems:
    print(f'{no:>2}  {what}')
print(f'{len(problems)} problems in {len(ORDER)} chapters')
sys.exit(1 if problems else 0)
