#!/usr/bin/env python3
"""Stage 1: split the approved single-file website into source templates and assets.

ORIGINAL html  ->  src/partials/{head-static,symbols,header,footer}.html
                   src/pages/{home,show,weekly,index,benchmark,steve,privacy,terms,contact}.html
                   src/css/site.css   (the original <style> block, data-URI raster images replaced by asset paths)
                   src/js/original-scripts.js (kept for reference only; site.js is authored separately)
                   dist/assets/img/*  (deduplicated image bytes, preserved exactly; see assets/manifest.json)

Image bytes are never resampled or recompressed here: every file is the base64 payload decoded verbatim,
and manifest.json records the sha256 of each file so a deploy can be checked against it.
"""
import re, os, sys, json, base64, hashlib, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ORIG = next(ROOT.glob('ORIGINAL_*.html'))
SRC = ROOT / 'src'
ASSETS = ROOT / 'dist' / 'assets'

html = ORIG.read_text(encoding='utf-8')

# ------------------------------------------------------------------ images
DATA_RE = re.compile(r'data:image/(webp|png|jpeg|gif);base64,([A-Za-z0-9+/=]+)')
manifest = {}          # sha -> record
uri_to_path = {}       # full data uri -> /assets/img/... path
order = []

def slug(s):
    s = re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')
    return s[:48] or 'img'

# find a descriptive name for each occurrence from nearby alt / class / context
def context_name(pos):
    tag_start = html.rfind('<', 0, pos)
    tag_end = html.find('>', pos)
    tag = html[tag_start:tag_end + 1]
    alt = re.search(r'alt="([^"]{3,})"', tag)
    cls = re.search(r'class="([^"]+)"', tag)
    if alt:
        return slug(alt.group(1))
    if cls:
        return slug(cls.group(1).split()[-1])
    if 'rel="icon"' in tag:
        return 'favicon'
    # <source> inside <picture>: look at the following <img alt>
    nxt = html.find('alt="', tag_end, tag_end + 800)
    if nxt != -1:
        a = html[nxt + 5: html.find('"', nxt + 5)]
        if len(a) > 2:
            return slug(a) + '-alt'
    return 'img'

(ASSETS / 'img').mkdir(parents=True, exist_ok=True)
used_names = {}
for m in DATA_RE.finditer(html):
    uri = m.group(0)
    if uri in uri_to_path:
        continue
    ext = {'jpeg': 'jpg'}.get(m.group(1), m.group(1))
    raw = base64.b64decode(m.group(2))
    sha = hashlib.sha256(raw).hexdigest()
    if sha in manifest:                      # same bytes, different base64 text (should not happen, but dedupe anyway)
        uri_to_path[uri] = manifest[sha]['path']
        manifest[sha]['occurrences'] += 1
        continue
    base = context_name(m.start())
    n = used_names.get(base, 0) + 1
    used_names[base] = n
    name = f"{base}{'' if n == 1 else '-' + str(n)}-{sha[:8]}.{ext}"
    path = f"/assets/img/{name}"
    (ASSETS / 'img' / name).write_bytes(raw)
    manifest[sha] = {'path': path, 'bytes': len(raw), 'sha256': sha, 'type': f'image/{m.group(1)}', 'occurrences': 1}
    uri_to_path[uri] = path
    order.append(sha)

# count occurrences of each unique uri
for uri, path in uri_to_path.items():
    sha = next(k for k, v in manifest.items() if v['path'] == path)
    manifest[sha]['occurrences'] = html.count(uri)

def swap_uris(s):
    return DATA_RE.sub(lambda m: uri_to_path[m.group(0)], s)

(ASSETS / 'manifest.json').write_text(json.dumps({
    'source_file': ORIG.name,
    'source_sha256': hashlib.sha256(ORIG.read_bytes()).hexdigest(),
    'unique_images': len(manifest),
    'total_bytes': sum(v['bytes'] for v in manifest.values()),
    'images': [manifest[k] for k in order],
}, indent=1), encoding='utf-8')

# ------------------------------------------------------------------ split the document
head = html[html.index('<head>') + 6: html.index('</head>')]
style = head[head.index('<style>') + 7: head.index('</style>')]
head_static = head[: head.index('<style>')]                      # meta, ld+json, title, icon, font links
body = html[html.index('<body>') + 6: html.rindex('</body>')]

symbols = body[body.index('<svg xmlns'): body.index('</svg>', body.index('<svg xmlns')) + 6]
header = body[body.index('<header class="wrap">'): body.index('</header>') + 9]
footer = body[body.index('<footer>'): body.index('</footer>') + 9]
scripts = body[body.index('</footer>') + 9:]

pages = {}
ids = ['home', 'show', 'weekly', 'index', 'benchmark', 'steve', 'privacy', 'terms', 'contact']
for i, pid in enumerate(ids):
    start = body.index(f'<div id="page-{pid}"')
    # page block ends where the next page block (or the footer) begins
    nxt = body.index(f'<div id="page-{ids[i+1]}"') if i + 1 < len(ids) else body.index('<!-- ================= FOOTER')
    block = body[start:nxt]
    # strip the wrapper div: opening tag and its final closing </div>
    open_end = block.index('>') + 1
    inner = block[open_end: block.rindex('</div>')]
    pages[pid] = inner.strip('\n')

SRC.mkdir(exist_ok=True)
(SRC / 'partials').mkdir(exist_ok=True)
(SRC / 'pages').mkdir(exist_ok=True)
(SRC / 'css').mkdir(exist_ok=True)
(SRC / 'js').mkdir(exist_ok=True)
(SRC / 'partials' / 'head-static.html').write_text(swap_uris(head_static), encoding='utf-8')
(SRC / 'partials' / 'symbols.html').write_text(symbols, encoding='utf-8')
(SRC / 'partials' / 'header.html').write_text(swap_uris(header), encoding='utf-8')
(SRC / 'partials' / 'footer.html').write_text(swap_uris(footer), encoding='utf-8')
(SRC / 'css' / 'site.css').write_text(swap_uris(style), encoding='utf-8')
(SRC / 'js' / 'original-scripts.reference.html').write_text(scripts, encoding='utf-8')
for pid, inner in pages.items():
    (SRC / 'pages' / f'{pid}.html').write_text(swap_uris(inner), encoding='utf-8')

print(f"images: {len(manifest)} unique files, {sum(v['bytes'] for v in manifest.values())/1e6:.2f} MB")
print('pages:', {k: len(v) for k, v in pages.items()})
print('css bytes', len(style), 'remaining data uris in css:', len(DATA_RE.findall(style)))
