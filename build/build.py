#!/usr/bin/env python3
"""Stage 2: render the static site (dist/) from src/ + site.config.json.

Run `python3 build/extract.py` first (or `make build`, which does both). Everything here is a
deterministic transform of the approved 5_14_0_2_1 design: the design, artwork and layout are
carried over unchanged, and only the changes recorded in docs/AUDIT_AND_FIXES.md and
docs/COPY_CHANGES.md are applied.
"""
import re, os, sys, json, hashlib, pathlib, html as htmlmod, datetime, io
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC, DIST, BUILD = ROOT / 'src', ROOT / 'dist', ROOT / 'build'
sys.path.insert(0, str(BUILD))
import copy_edits

CFG = json.loads((ROOT / 'site.config.json').read_text())
ORIGIN = CFG['origin'].rstrip('/')
if re.search(r'localhost|127\.0\.0\.1|staging|\.local\b|^http:', ORIGIN):
    raise SystemExit(f'refusing to build with a non-production origin: {ORIGIN}')
LAUNCH = CFG['launch']
STATE = copy_edits.STATE_COPY[LAUNCH['weekly']]
BUILD_TIME = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

# ----------------------------------------------------------------------------- routes + metadata
PAGES = {
 'home':      dict(path='/', title='Full Plate Intelligence | Restaurant Financial Insights for Independent Restaurants',
                   desc='Full Plate Intelligence (Full Plate Intel) helps independent restaurant owners see their numbers the way top operators do: a free weekly newsletter on food cost, labor, cash flow and profitability, with restaurant research and benchmarking tools on the way.',
                   og='og-home.png', anchor='#signup', type='WebPage'),
 'weekly':    dict(path='/weekly/', title='Full Plate Weekly | Free Restaurant Financial Newsletter',
                   desc='Full Plate Weekly is a free restaurant newsletter with practical financial insights for independent owners: food cost, labor cost, cash flow, occupancy and profitability, in one short email a week.',
                   og='og-weekly.png', anchor='#weekly-join', type='WebPage'),
 'show':      dict(path='/show/', title='The Full Plate Show | Restaurant Business Conversations',
                   desc='The Full Plate Show is an upcoming restaurant podcast: practical conversations with owners, chefs, investors, lenders and technologists about the decisions that shape a restaurant business.',
                   og='og-show.png', anchor='#show-join', type='WebPage'),
 'index':     dict(path='/restaurant-intelligence-index/', title='Restaurant Intelligence Index | Independent Restaurant Industry Report',
                   desc='The Restaurant Intelligence Index is a planned twice-yearly restaurant industry report built from independent restaurant data: sales and profitability, food and beverage costs, labor and productivity, operator sentiment and technology. Paid per edition.',
                   og='og-index.png', anchor='#index-join', type='WebPage'),
 'benchmark': dict(path='/benchmark/', title='Full Plate Benchmark | Restaurant Financial Benchmarking',
                   desc='Full Plate Benchmark is a planned restaurant benchmarking tool: compare food cost, labor, prime cost and profitability against restaurants like yours by concept, cuisine, revenue and market. Paid Quick Calculator and Full Benchmark Report.',
                   og='og-benchmark.png', anchor='#benchmark-join', type='WebPage'),
 'steve':     dict(path='/steve/', title='Steve Dillberg | Founder of Full Plate Intelligence',
                   desc='Meet Steve Dillberg, restaurant accountant and advisor, founder of Full Plate Intelligence and founding partner of Schofer Dillberg & Company, with more than 25 years advising restaurant owners and operators.',
                   og='og-steve.png', anchor='#signup-steve', type='ProfilePage'),
 'privacy':   dict(path='/privacy/', title='Privacy Policy | Full Plate Intelligence', desc='How Full Plate Intelligence collects and uses your email address and what happens when you join the Full Plate Weekly list.', og='og-home.png', anchor='/#signup', type='WebPage'),
 'terms':     dict(path='/terms/', title='Terms of Use | Full Plate Intelligence', desc='Terms of use for the Full Plate Intelligence website and Full Plate Weekly newsletter.', og='og-home.png', anchor='/#signup', type='WebPage'),
 'contact':   dict(path='/contact/', title='Contact | Full Plate Intelligence', desc='Questions, feedback or ideas for Full Plate Intelligence? Email Steve directly.', og='og-home.png', anchor='/#signup', type='WebPage'),
}
LEGACY = {'#/show': '/show/', '#/weekly': '/weekly/', '#/index': '/restaurant-intelligence-index/', '#/benchmark': '/benchmark/',
          '#/steve': '/steve/', '#/privacy': '/privacy/', '#/terms': '/terms/', '#/contact': '/contact/', '#/home': '/'}
NAV_PAGE = {'show': 'show', 'weekly': 'weekly', 'index': 'index', 'benchmark': 'benchmark', 'steve': 'steve'}
FORM_IDS = {'homepage-hero': 'signup', 'homepage-bottom-cta': 'signup-bottom', 'show-page': 'signup-show', 'weekly-page-bottom': 'signup-weekly',
            'index-page': 'signup-index', 'benchmark-page': 'signup-benchmark', 'steve-page': 'signup-steve'}
FORM_PAGE = {'homepage-hero': '/', 'homepage-bottom-cta': '/', 'show-page': '/show/', 'weekly-page-bottom': '/weekly/',
             'index-page': '/restaurant-intelligence-index/', 'benchmark-page': '/benchmark/', 'steve-page': '/steve/'}
FORM_INTEREST = {'homepage-hero': 'newsletter', 'homepage-bottom-cta': 'newsletter', 'show-page': 'show', 'weekly-page-bottom': 'newsletter',
                 'index-page': 'index', 'benchmark-page': 'benchmark', 'steve-page': 'newsletter'}

def read(p): return (SRC / p).read_text(encoding='utf-8')
head_static = read('partials/head-static.html'); symbols = read('partials/symbols.html')
header = read('partials/header.html'); footer = read('partials/footer.html'); css = read('css/site.css')
pages = {k: read(f'pages/{k}.html') for k in PAGES}
manifest = json.loads((DIST / 'assets' / 'manifest.json').read_text())
favicon = next(i['path'] for i in manifest['images'] if '/favicon-' in i['path'])

# ----------------------------------------------------------------------------- copy
pages, copy_records = copy_edits.apply(pages, LAUNCH)

# ----------------------------------------------------------------------------- component overrides (RC5)
# Durable replacements for whole sections of the extracted templates. Each override file replaces exactly one
# region of a page, delimited by the ORIGINAL file's own section comments, so the change survives every
# extract.py + build.py run without touching the read-only ORIGINAL reference.
OVERRIDES = [
    # Steve: paired Founder & Partner / "Why I Started" component (owner-approved RC4_3 design; question cards
    # intentionally removed, coffee/notebook artwork, identity wording without the CPA credential).
    ('steve', '    <!-- ================= FOUNDER / WHY ================= -->', '    <!-- ================= THREE COLUMNS ================= -->', 'steve-founder-why.html'),
]
for pid, start_marker, end_marker, fname in OVERRIDES:
    html_in = pages[pid]
    assert html_in.count(start_marker) == 1 and html_in.count(end_marker) == 1, f'override region for {fname} not found exactly once'
    a, b = html_in.index(start_marker), html_in.index(end_marker)
    pages[pid] = html_in[:a] + (BUILD / 'overrides' / fname).read_text(encoding='utf-8') + html_in[b:]
    copy_records.append({'page': pid, 'original': f'section {start_marker.strip()} .. {end_marker.strip()}', 'replacement': f'build/overrides/{fname}', 'reason': 'Owner-approved RC4_3 Steve component (see docs/CHANGELOG_RC5.md).', 'approval': None})
assert 'class="stickies"' not in pages['steve'] and 'ms-why' in pages['steve'] and 'Why isn' not in pages['steve']
# extra artwork shipped by the build (not part of the ORIGINAL data URIs): bytes copied verbatim, recorded in the manifest
EXTRA_IMG = sorted((BUILD / 'assets' / 'img').glob('*'))
manifest['additional_images'] = []
for f in EXTRA_IMG:
    (DIST / 'assets' / 'img' / f.name).write_bytes(f.read_bytes())
    with Image.open(f) as im: w_, h_ = im.size
    manifest['additional_images'].append({'path': f'/assets/img/{f.name}', 'bytes': f.stat().st_size, 'sha256': hashlib.sha256(f.read_bytes()).hexdigest(), 'type': f'image/{im.format.lower()}', 'width': w_, 'height': h_, 'source': f'build/assets/img/{f.name}'})
(DIST / 'assets' / 'manifest.json').write_text(json.dumps(manifest, indent=1), encoding='utf-8')
for rec_ in manifest['additional_images']:
    assert rec_['path'] in pages['steve'], f'{rec_["path"]} is shipped but not referenced'

# legal pages: replace the policy bodies with the revised text; headings become h1/h2
legal_vars = dict(policy_revision_date=CFG['policy_revision_date'], contact_email=CFG['contact_email'],
                  analytics_paragraph=('We do not run analytics, advertising pixels, or session recording on this site, and we set no cookies for those purposes. The signup form keeps campaign values in your browser&rsquo;s session storage, which clears when you close the tab; the copy sent with your signup is kept in our operational signup logs alongside the technical information described above, and nowhere else.'
                                       if not CFG['analytics']['provider'] else
                                       'This site uses a privacy-configured analytics tool to count page views and signup events. Analytics events never include your email address. See the runbook for the exact events sent.'))
for pid in ('privacy', 'terms'):
    body = (BUILD / 'legal' / f'{pid}.html').read_text(encoding='utf-8').format(**legal_vars)
    a = pages[pid].index('<div class="legal-body">') + len('<div class="legal-body">')
    b = pages[pid].rindex('</div>\n  </section>')
    pages[pid] = pages[pid][:a] + '\n' + body + '    ' + pages[pid][b:]
for pid in ('privacy', 'terms', 'contact'):
    pages[pid] = pages[pid].replace('<h2 class="section-title">', '<h1 class="section-title">', 1).replace('</span></h2>', '</span></h1>', 1)
pages['contact'] = pages['contact'].replace('<a href="#signup">Join Full Plate Weekly</a>', '<a href="/#signup">Join Full Plate Weekly</a>')

# ----------------------------------------------------------------------------- links
def rewrite_links(s, pid):
    for old, new in LEGACY.items():
        s = s.replace(f'href="{old}"', f'href="{new}"')
    s = s.replace('href="#" ', 'href="/" ')
    if pid != 'home':
        s = s.replace('href="#signup"', 'href="/#signup"')
    return s

# ----------------------------------------------------------------------------- header per page
def render_header(pid):
    # header CTA reaches this page's own signup block (before generic link rewriting)
    h = header.replace('<a class="btn" href="#signup">', f'<a class="btn" href="{PAGES[pid]["anchor"]}" data-cta="header-subscribe">')
    h = rewrite_links(h, pid)
    h = h.replace('<header class="wrap">', '<header class="wrap site-header">')
    # aria-current on the active nav item
    cur = NAV_PAGE.get(pid)
    if cur:
        h = h.replace(f'<a class="nav-item" href="{LEGACY["#/"+cur]}">', f'<a class="nav-item active" aria-current="page" href="{LEGACY["#/"+cur]}">')
    # newsletter pill follows the launch state
    h = h.replace('<span class="label">Full Plate<br>Weekly</span>\n        <span class="pill">COMING SOON</span>',
                  f'<span class="label">Full Plate<br>Weekly</span>\n        <span class="pill">{STATE["weekly_pill"]}</span>')
    return h

# ----------------------------------------------------------------------------- forms
FORM_RE = re.compile(r'<form class="signup"([^>]*)data-source="([^"]+)"[^>]*>\s*<input[^>]*>\s*<button class="([^"]+)" type="submit">([^<]+)</button>\s*</form>')
def render_form(m):
    source = m.group(2); fid = FORM_IDS[source]; btncls = m.group(3); label = m.group(4)
    help_txt = copy_edits.FORM_HELP[source]
    describedby = 'signup-help' if source == 'homepage-hero' else f'{fid}-help'
    help_html = f'  <p class="signup-help" id="{fid}-help">{help_txt}</p>\n' if help_txt else ''
    return (f'<form class="signup" id="{fid}" action="{CFG["subscribe_endpoint"]}" method="post" data-source="{source}" novalidate>\n'
            f'  <label class="sr-only" for="{fid}-email">Email address</label>\n'
            f'  <input id="{fid}-email" type="email" name="email" autocomplete="email" inputmode="email" maxlength="254" required placeholder="Enter your email" aria-describedby="{describedby}">\n'
            f'  <input type="hidden" name="source" value="{source}">\n'
            f'  <input type="hidden" name="interest" value="{FORM_INTEREST[source]}">\n'
            f'  <input type="hidden" name="page" value="{FORM_PAGE[source]}">\n'
            f'  <div class="hp" aria-hidden="true"><label for="{fid}-hp">Leave this field empty</label><input id="{fid}-hp" type="text" name="fpi_ref" tabindex="-1" autocomplete="off"></div>\n'
            f'  <button class="{btncls}" type="submit">{label}</button>\n'
            + help_html +
            f'  <p class="signup-error" id="{fid}-error" role="alert" hidden></p>\n'
            f'  <p class="signup-status" id="{fid}-status" role="status" aria-live="polite"></p>\n'
            f'  <p class="signup-status-help" id="{fid}-status-help" hidden></p>\n'
            f'</form>')
for pid in pages:
    pages[pid], n = FORM_RE.subn(render_form, pages[pid])
# the "You own your data" panel is nested inside <main>; a complementary landmark must be top-level, so it becomes a plain group
pages['benchmark'] = pages['benchmark'].replace('<aside class="bm-own">', '<div class="bm-own" role="group" aria-labelledby="bm-own-h">').replace('</aside>', '</div>').replace('<h3>You own your data.', '<h3 id="bm-own-h">You own your data.')
assert 'bm-own-h' in pages['benchmark']
assert sum(p.count('<form class="signup"') for p in pages.values()) == 7, 'expected seven signup forms'
assert 'id="signup-steve"' in pages['steve']   # the Steve form keeps its original anchor id

# ----------------------------------------------------------------------------- images: dimensions + lazy loading
dims = {}
for rec in manifest['images']:
    with Image.open(DIST / rec['path'].lstrip('/')) as im:
        dims[rec['path']] = im.size
IMG_RE = re.compile(r'<img\b[^>]*>')
def fix_img(tag, eager):
    src = re.search(r'src="([^"]+)"', tag).group(1)
    if src in dims and 'width=' not in tag:
        w, h = dims[src]; tag = tag.replace('<img', f'<img width="{w}" height="{h}"', 1)
    if 'loading=' in tag:
        tag = re.sub(r'\s*loading="[^"]*"', '', tag)
    if eager:
        if 'fetchpriority' not in tag: tag = tag.replace('<img', '<img fetchpriority="high"', 1)
    else:
        tag = tag.replace('<img', '<img loading="lazy"', 1)
    if 'decoding=' not in tag: tag = tag.replace('<img', '<img decoding="async"', 1)
    return tag
def process_images(s, hero_count=1):
    # first <section> of a page is above the fold: keep its first image eager (LCP), the rest lazy
    first_section_end = s.find('</section>')
    n = [0]
    def rep(m):
        eager = m.start() < first_section_end and n[0] < hero_count
        if m.start() < first_section_end: n[0] += 1
        return fix_img(m.group(0), eager)
    return IMG_RE.sub(rep, s)
for pid in pages:
    pages[pid] = process_images(pages[pid])
# header: logo + nav icons stay eager (above the fold everywhere); footer logo lazy
header = IMG_RE.sub(lambda m: fix_img(m.group(0), True).replace(' fetchpriority="high"', ''), header)
footer = IMG_RE.sub(lambda m: fix_img(m.group(0), False), footer)

# ----------------------------------------------------------------------------- inline styles -> classes (so the CSP can drop 'unsafe-inline' for styles)
style_classes = {}
def declass(s):
    def rep(m):
        st = m.group(1).strip()
        if st not in style_classes: style_classes[st] = f'st-{len(style_classes)+1}'
        cls = style_classes[st]
        tag = m.group(0)
        if 'class="' in tag[:tag.index('style=')] or 'class="' in tag[tag.index('style='):]:
            tag = re.sub(r'\s*style="[^"]*"', '', tag)
            tag = re.sub(r'class="([^"]*)"', lambda c: f'class="{c.group(1)} {cls}"', tag, 1)
        else:
            tag = re.sub(r'style="[^"]*"', f'class="{cls}"', tag)
        return tag
    return re.sub(r'<[a-zA-Z][^>]*\sstyle="([^"]*)"[^>]*>', rep, s)
for pid in pages: pages[pid] = declass(pages[pid])
header, footer, symbols = declass(header), declass(footer), declass(symbols)

# ----------------------------------------------------------------------------- CSS
fonts_css = '''/* Self-hosted brand fonts (SIL Open Font License 1.1; see /assets/fonts/LICENSE-*.txt) */
@font-face{font-family:'Caveat';font-style:normal;font-weight:500;font-display:swap;src:url(/assets/fonts/caveat-latin-500-normal.woff2) format('woff2');}
@font-face{font-family:'Caveat';font-style:normal;font-weight:600;font-display:swap;src:url(/assets/fonts/caveat-latin-600-normal.woff2) format('woff2');}
@font-face{font-family:'Caveat';font-style:normal;font-weight:700;font-display:swap;src:url(/assets/fonts/caveat-latin-700-normal.woff2) format('woff2');}
@font-face{font-family:'Patrick Hand';font-style:normal;font-weight:400;font-display:swap;src:url(/assets/fonts/patrick-hand-latin-400-normal.woff2) format('woff2');}
'''
a11y_css = (BUILD / 'a11y.css').read_text(encoding='utf-8')
classes_css = '\n/* former inline style attributes (moved here so the CSP can omit unsafe-inline) */\n' + ''.join(f'.{c}{{{st}}}\n' for st, c in style_classes.items())
# RC5: the sticky-note rules only styled the replaced Steve markup; drop them so no dead selectors ship
css_main = css.replace('overflow-x:hidden;', '')
def drop_sticky_rules(text):
    out, skip = [], False
    for line in text.split('\n'):
        st = line.strip()
        if skip:
            if st == '}': skip = False
            continue
        if st.startswith('.stickies{') or st.startswith('.sticky'):
            if not st.endswith('}'): skip = True      # multi-line block: skip through its closing brace
            continue
        out.append(line)
    return '\n'.join(out)
css_main = drop_sticky_rules(css_main)
assert '.sticky' not in css_main and '.stickies' not in css_main, 'sticky rules still present'
override_css = ''.join('\n' + f.read_text(encoding='utf-8') for f in sorted((BUILD / 'overrides').glob('*.css')))
css_out = fonts_css + css_main + a11y_css + classes_css + override_css
assert 'overflow-x:hidden' not in css_out
(DIST / 'assets' / 'css').mkdir(parents=True, exist_ok=True)
(DIST / 'assets' / 'css' / 'site.css').write_text(css_out, encoding='utf-8')
(DIST / 'assets' / 'fonts').mkdir(exist_ok=True)
for f in (BUILD / 'fonts').iterdir():
    if f.suffix in ('.woff2', '.txt'):
        (DIST / 'assets' / 'fonts' / f.name).write_bytes(f.read_bytes())
(DIST / 'assets' / 'js').mkdir(exist_ok=True)
site_js = (BUILD / 'site.js').read_text(encoding='utf-8')
(DIST / 'assets' / 'js' / 'site.js').write_text(site_js, encoding='utf-8')
def vhash(p): return hashlib.sha256((DIST / p).read_bytes()).hexdigest()[:10]
CSS_URL = f'/assets/css/site.css?v={vhash("assets/css/site.css")}'
JS_URL = f'/assets/js/site.js?v={vhash("assets/js/site.js")}'

# ----------------------------------------------------------------------------- share images (composed from existing approved artwork only)
(DIST / 'assets' / 'share').mkdir(exist_ok=True)
def asset(fragment):
    return next(i['path'] for i in manifest['images'] if fragment in i['path'])
ART = {'og-home.png': ('sketch-of-a-salmon-dinner-plate', 'See your restaurant the way top operators do.'),
       'og-weekly.png': ('illustration-of-a-stack-of-plates', 'Full Plate Weekly: practical restaurant financial insights.'),
       'og-show.png': ('illustration-of-a-vintage-microphone', 'The Full Plate Show: real operators, real numbers.'),
       'og-index.png': ('a-silver-cloche-lifted', 'Restaurant Intelligence Index: see what real restaurant data is saying.'),
       'og-benchmark.png': ('from-restaurant-data-to-benchmark', 'Full Plate Benchmark: know where your restaurant really stands.'),
       'og-steve.png': ('hand-drawn-portrait-of-steve-dillberg', 'Steve Dillberg. Founder of Full Plate Intelligence.')}
caveat = ImageFont.truetype(str(BUILD / 'fonts' / 'caveat-latin-700.ttf'), 58)
def compose_share(name, art_fragment, line):
    canvas = Image.new('RGB', (1200, 630), (247, 241, 231))
    logo = Image.open(DIST / asset('full-plate-intelligence-').lstrip('/')).convert('RGBA'); logo.thumbnail((360, 140))
    canvas.paste(logo, (60, 48), logo)
    art = Image.open(DIST / asset(art_fragment).lstrip('/')).convert('RGBA'); art.thumbnail((560, 470))
    canvas.paste(art, (1200 - art.width - 50, 630 - art.height - 40), art)
    d = ImageDraw.Draw(canvas)
    words, lines, cur = line.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=caveat) > 540: lines.append(cur); cur = w
        else: cur = t
    lines.append(cur)
    y = 250
    for ln in lines:
        d.text((62, y), ln, font=caveat, fill=(31, 31, 27)); y += 68
    d.text((62, 560), ORIGIN.replace('https://', ''), font=ImageFont.truetype(str(BUILD / 'fonts' / 'caveat-latin-700.ttf'), 34), fill=(191, 70, 18))
    canvas.save(DIST / 'assets' / 'share' / name, optimize=True)
for name, (frag, line) in ART.items():
    compose_share(name, frag, line)

# ----------------------------------------------------------------------------- head
def json_ld(pid):
    org = {'@type': 'Organization', '@id': f'{ORIGIN}/#organization', 'name': 'Full Plate Intelligence', 'alternateName': 'Full Plate Intel', 'url': f'{ORIGIN}/',
           'logo': f'{ORIGIN}{asset("full-plate-intelligence-")}', 'email': CFG['contact_email'],
           'founder': {'@id': f'{ORIGIN}/steve/#person'}, 'sameAs': [v for k, v in CFG['social'].items() if not k.startswith('_')]}
    person = {'@type': 'Person', '@id': f'{ORIGIN}/steve/#person', 'name': 'Steve Dillberg',
              'jobTitle': 'Founder', 'worksFor': {'@id': f'{ORIGIN}/#organization'}, 'url': f'{ORIGIN}/steve/',
              'affiliation': {'@type': 'Organization', 'name': 'Schofer Dillberg & Company'}, 'knowsAbout': ['restaurant accounting', 'restaurant finance', 'restaurant benchmarking']}
    p = PAGES[pid]
    page = {'@type': p['type'], '@id': f'{ORIGIN}{p["path"]}#webpage', 'url': f'{ORIGIN}{p["path"]}', 'name': p['title'], 'description': p['desc'],
            'isPartOf': {'@id': f'{ORIGIN}/#website'}, 'primaryImageOfPage': f'{ORIGIN}/assets/share/{p["og"]}', 'inLanguage': 'en'}
    if p['type'] == 'ProfilePage': page['mainEntity'] = {'@id': f'{ORIGIN}/steve/#person'}
    site = {'@type': 'WebSite', '@id': f'{ORIGIN}/#website', 'url': f'{ORIGIN}/', 'name': 'Full Plate Intelligence', 'publisher': {'@id': f'{ORIGIN}/#organization'}, 'inLanguage': 'en'}
    graph = [org, person, site, page]
    return json.dumps({'@context': 'https://schema.org', '@graph': graph}, indent=1)

def render_head(pid, noindex=False):
    p = PAGES[pid]; url = f'{ORIGIN}{p["path"]}'
    t = htmlmod.escape(p['title'], quote=True); d = htmlmod.escape(p['desc'], quote=True)
    robots = '<meta name="robots" content="noindex, nofollow">' if noindex else '<meta name="robots" content="index, follow, max-image-preview:large">'
    return f'''<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{t}</title>
<meta name="description" content="{d}">
{robots}
<link rel="canonical" href="{url}">
<meta property="og:site_name" content="Full Plate Intelligence">
<meta property="og:type" content="{'profile' if pid=='steve' else 'website'}">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:image" content="{ORIGIN}/assets/share/{p['og']}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{htmlmod.escape(ART.get(p['og'], ('', 'Full Plate Intelligence'))[1], quote=True)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{t}">
<meta name="twitter:description" content="{d}">
<meta name="twitter:image" content="{ORIGIN}/assets/share/{p['og']}">
<link rel="icon" type="image/png" href="{favicon}">
<link rel="preload" href="/assets/fonts/caveat-latin-700-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/patrick-hand-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{CSS_URL}">
<script type="application/ld+json">
{json_ld(pid)}
</script>
'''

client_config = json.dumps({'endpoint': CFG['subscribe_endpoint'], 'legacyRoutes': LEGACY, 'launch': LAUNCH,   # no build time here: pages stay byte-reproducible
                            'messages': {'generic': STATE['thanks_generic'], 'generic_help': STATE['thanks_help'], 'pending': STATE['thanks_pending'], 'subscribed': STATE['thanks_subscribed'],
                                         'invalid': 'Please enter a valid email address.', 'rate_limited': 'Too many attempts from this connection. Please wait a minute and try again.',
                                         'unavailable': 'Signups are temporarily unavailable. Please try again in a few minutes, or email ' + CFG['contact_email'] + '.',
                                         'timeout': 'That took too long. Please check your connection and try again.', 'network': 'That did not go through. Please check your connection and try again.'},
                            'analytics': CFG['analytics']})

def render_page(pid, body_html, noindex=False):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
{render_head(pid, noindex)}</head>
<body data-page="{pid}">
<a class="skip-link" href="#main">Skip to main content</a>
{symbols}

{render_header(pid)}

<main id="main" tabindex="-1">
<div id="page-{pid if pid in ('home','show','weekly','index','benchmark','steve') else 'legal'}">
{rewrite_links(body_html, pid)}
</div>
</main>

{rewrite_links(footer, pid)}

<script type="application/json" id="fpi-config">{client_config}</script>
<script src="{JS_URL}" defer></script>
</body>
</html>
'''

for pid, p in PAGES.items():
    out = DIST / p['path'].strip('/') / 'index.html' if p['path'] != '/' else DIST / 'index.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_page(pid, pages[pid]), encoding='utf-8')

# 404 + no-JavaScript subscription result pages (kept out of the index)
def simple_page(pid_for_chrome, title, h1, paragraphs, noindex=True):
    paras = ''.join('      <p>' + x + '</p>\n' for x in paragraphs)
    body = ('  <section class="wrap legal">\n    <h1 class="section-title"><span class="squig">' + h1 + '</span></h1>\n'
            '    <div class="legal-body">\n' + paras + '    </div>\n  </section>')
    saved = PAGES[pid_for_chrome]
    PAGES[pid_for_chrome] = dict(saved, title=title, desc=paragraphs[0].split('.')[0] + '.')
    html_out = render_page(pid_for_chrome, body, noindex=noindex)
    PAGES[pid_for_chrome] = saved
    return html_out
PAGES['notfound'] = dict(PAGES['contact'], path='/404.html', title='Page not found | Full Plate Intelligence', desc='That page does not exist.', anchor='/#signup')
(DIST / '404.html').write_text(simple_page('notfound', 'Page not found | Full Plate Intelligence', 'Page not found',
    ['That page does not exist or has moved. Try the <a href="/">homepage</a>, <a href="/weekly/">Full Plate Weekly</a>, <a href="/show/">The Full Plate Show</a>, <a href="/restaurant-intelligence-index/">Restaurant Intelligence Index</a>, <a href="/benchmark/">Full Plate Benchmark</a>, or <a href="/steve/">Meet Steve</a>.']), encoding='utf-8')
del PAGES['notfound']
PAGES['thanks'] = dict(PAGES['contact'], path='/subscribe/thanks/', title='Check your inbox | Full Plate Intelligence', desc='One more step to join the Full Plate Weekly list.', anchor='/#signup')
(DIST / 'subscribe' / 'thanks').mkdir(parents=True, exist_ok=True)
(DIST / 'subscribe' / 'thanks' / 'index.html').write_text(simple_page('thanks', PAGES['thanks']['title'], 'Check your inbox',
    [STATE['thanks_generic'], 'Back to the <a href="/">homepage</a>.']), encoding='utf-8')
del PAGES['thanks']
PAGES['suberr'] = dict(PAGES['contact'], path='/subscribe/error/', title='Signup did not go through | Full Plate Intelligence', desc='Your signup could not be completed.', anchor='/#signup')
(DIST / 'subscribe' / 'error').mkdir(parents=True, exist_ok=True)
(DIST / 'subscribe' / 'error' / 'index.html').write_text(simple_page('suberr', PAGES['suberr']['title'], 'That did not go through',
    ['Your signup could not be completed. Please check the email address and <a href="/#signup">try again</a>. If it keeps happening, email <a href="mailto:' + CFG['contact_email'] + '">' + CFG['contact_email'] + '</a> and we will add you by hand.']), encoding='utf-8')
del PAGES['suberr']

# ----------------------------------------------------------------------------- sitemap, robots, route map
public = [p['path'] for p in PAGES.values()]
(DIST / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    ''.join(f'  <url><loc>{ORIGIN}{path}</loc></url>\n' for path in public) + '</urlset>\n', encoding='utf-8')   # no fabricated lastmod
(DIST / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nDisallow: /api/\nDisallow: /subscribe/\n\nSitemap: {ORIGIN}/sitemap.xml\n', encoding='utf-8')
(ROOT / 'hosting' ).mkdir(exist_ok=True)
(ROOT / 'hosting' / 'robots.staging.txt').write_text('# Staging only. Use together with the X-Robots-Tag: noindex header and HTTP auth; a Disallow alone does not keep a page out of the index.\nUser-agent: *\nDisallow: /\n', encoding='utf-8')

# Netlify reads _headers and _redirects from the publish directory
import subprocess
subprocess.run([sys.executable, str(ROOT / 'hosting' / 'render-host-configs.py')], check=True, capture_output=True)
for name in ('_headers', '_redirects'):
    (DIST / name).write_text((ROOT / 'hosting' / 'candidates' / name).read_text(encoding='utf-8'), encoding='utf-8')

# build report consumed by the docs
report = {'build_time': BUILD_TIME, 'origin': ORIGIN, 'launch': LAUNCH, 'pages': {pid: {'path': p['path'], 'title': p['title'], 'description': p['desc'], 'og_image': f'/assets/share/{p["og"]}'} for pid, p in PAGES.items()},
          'legacy_routes': LEGACY, 'copy_changes': copy_records, 'inline_style_classes': len(style_classes), 'css_url': CSS_URL, 'js_url': JS_URL,
          'html_bytes': {str(f.relative_to(DIST)): f.stat().st_size for f in DIST.rglob('*.html')}}
(ROOT / 'build' / 'build-report.json').write_text(json.dumps(report, indent=1), encoding='utf-8')
print('built', BUILD_TIME); print({k: v for k, v in report['html_bytes'].items()})
