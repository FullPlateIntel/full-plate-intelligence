#!/usr/bin/env python3
"""Build a single-file NON-PRODUCTION preview of dist/ for offline review.

Not part of the deployable output. It inlines every asset as a data: URI, stacks the
<main> block of each page into one document and adds a small hash router so the real
page links work inside the file. Forms are not connected (no /api/subscribe here).
"""
import base64, json, mimetypes, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'PREVIEW_single_file_NONPRODUCTION_RC5.html'
LABEL = sys.argv[2] if len(sys.argv) > 2 else 'RC5'

ROUTES = [('/', 'home', 'index.html'), ('/show/', 'show', 'show/index.html'), ('/weekly/', 'weekly', 'weekly/index.html'),
          ('/restaurant-intelligence-index/', 'index', 'restaurant-intelligence-index/index.html'),
          ('/benchmark/', 'benchmark', 'benchmark/index.html'), ('/steve/', 'steve', 'steve/index.html'),
          ('/privacy/', 'privacy', 'privacy/index.html'), ('/terms/', 'terms', 'terms/index.html'),
          ('/contact/', 'contact', 'contact/index.html')]
MIME = {'.woff2': 'font/woff2', '.webp': 'image/webp', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.ico': 'image/x-icon'}


def data_uri(path):
    p = DIST / path.lstrip('/').split('?')[0]
    if not p.is_file():
        return path  # e.g. a wildcard mentioned in a CSS comment
    mime = MIME.get(p.suffix.lower()) or mimetypes.guess_type(p.name)[0] or 'application/octet-stream'
    return 'data:%s;base64,%s' % (mime, base64.b64encode(p.read_bytes()).decode('ascii'))


def inline_assets(text):
    return re.sub(r'(?<![\w/])/assets/[A-Za-z0-9_./-]+(?:\?v=[0-9a-f]+)?', lambda m: data_uri(m.group(0)), text)


def main_block(html):
    m = re.search(r'<main id="main" tabindex="-1">(.*)</main>', html, re.S)
    if not m:
        raise SystemExit('no <main> in page')
    inner = m.group(1)
    # Each page has exactly one page wrapper: <div id="page-X">...</div>
    return inner.strip()


home = (DIST / 'index.html').read_text(encoding='utf-8')
head = re.search(r'<head>(.*?)</head>', home, re.S).group(1)
body_open = re.search(r'<body[^>]*>', home).group(0)
body = home[home.find(body_open) + len(body_open):home.rfind('</body>')]

# Replace head: drop canonical/OG/JSON-LD (they would describe the wrong page) and inline css
css = (DIST / 'assets/css/site.css').read_text(encoding='utf-8')
js = (DIST / 'assets/js/site.js').read_text(encoding='utf-8')
cfg = re.search(r'<script type="application/json" id="fpi-config">(.*?)</script>', home, re.S).group(1)
# Preview-only: the standalone file must not try to leave itself. site.js migrates legacy #/route hashes to real
# URLs (location.replace), which would navigate away from this single file, so the preview's copy of the
# configuration carries no legacyRoutes; the preview router below handles #/route hashes inside the file instead.
cfg_obj = json.loads(cfg); cfg_obj['legacyRoutes'] = {}; cfg_obj['_preview'] = 'NON-PRODUCTION single-file preview; signup forms are not connected'
cfg = json.dumps(cfg_obj)
head_new = ('<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            '<meta name="robots" content="noindex, nofollow">\n'
            '<title>NON-PRODUCTION PREVIEW | Full Plate Intelligence %s</title>\n'
            '<style>%s\n.preview-banner{background:#1F1F1B;color:#fff;font:14px/1.4 system-ui,sans-serif;padding:8px 14px;text-align:center}</style>\n'
            '<script type="application/json" id="fpi-config">%s</script>\n' % (LABEL, inline_assets(css), cfg))
head_new += '<link rel="icon" href="%s">\n' % data_uri('/assets/img/' + re.search(r'/assets/img/(favicon-[0-9a-f]+\.png)', home).group(1))

# Body: keep header/nav/footer from the home page; stack all page blocks in <main>
pages = []
for path, name, file in ROUTES:
    html = (DIST / file).read_text(encoding='utf-8')
    block = main_block(html)
    block = block.replace('<div id="page-legal"', '<div id="page-%s" class="page-legal"' % name, 1)  # legal pages share a wrapper id
    if name != 'home':
        block = re.sub(r'^<div id="page-%s"' % name, '<div id="page-%s" hidden' % name, block)
    pages.append(block)
main_re = re.compile(r'<main id="main" tabindex="-1">.*</main>', re.S)
body_new = main_re.sub(lambda m: '<main id="main" tabindex="-1">\n' + '\n'.join(pages) + '\n</main>', body)
body_new = re.sub(r'<script src="[^"]*site\.js[^"]*" defer></script>', '', body_new)
# exactly one configuration block in the file: the copy in <head>; drop the page's own copy from the body
body_new, n_cfg = re.subn(r'<script type="application/json" id="fpi-config">.*?</script>\n?', '', body_new, flags=re.S)
assert n_cfg == 1, n_cfg
body_new = inline_assets(body_new)

banner = ('<div class="preview-banner">NON-PRODUCTION PREVIEW of FPI_SUBSCRIBER_LAUNCH_%s. Single file for review only: '
          'signup forms are not connected here (submitting shows the "did not go through" error; no request is sent anywhere). '
          'The deployable site is dist/ in the package.</div>\n' % LABEL)

router = r'''
<script>
// preview-only router: maps the real page URLs back onto the page blocks in this single file
(function(){
  var routes={'/':'home','/show/':'show','/weekly/':'weekly','/restaurant-intelligence-index/':'index','/benchmark/':'benchmark','/steve/':'steve','/privacy/':'privacy','/terms/':'terms','/contact/':'contact'};
  var ctaAnchor={home:'#signup',weekly:'#weekly-join',show:'#show-join',index:'#index-join',benchmark:'#benchmark-join',steve:'#signup-steve'};
  function show(name,anchor){
    Object.keys(routes).forEach(function(p){var el=document.getElementById('page-'+routes[p]); if(el) el.hidden=(routes[p]!==name);});
    document.body.setAttribute('data-page',name);
    // the header is the homepage's; point SUBSCRIBE FREE at the visible page's own form (legal pages -> homepage form), as each built page does
    document.querySelectorAll('[data-cta="header-subscribe"]').forEach(function(a){a.setAttribute('href', ctaAnchor[name]||'/#signup');});
    document.querySelectorAll('.nav-item').forEach(function(a){var on=routes[a.getAttribute('href')]===name; a.classList.toggle('active',on); if(on) a.setAttribute('aria-current','page'); else a.removeAttribute('aria-current');});
    if(anchor){var t=document.getElementById(anchor.slice(1)); if(t) t.scrollIntoView(); else window.scrollTo(0,0);} else window.scrollTo(0,0);
  }
  document.addEventListener('click',function(e){
    var a=e.target.closest('a[href]'); if(!a) return; var href=a.getAttribute('href');
    if(!href||href.indexOf('http')===0||href.indexOf('mailto')===0) return;
    var m=href.match(/^(\/[a-z-]*\/?)?(#.*)?$/); if(!m) return;
    var path=m[1]||null, anchor=m[2]||'';
    if(path && routes.hasOwnProperty(path)){ e.preventDefault(); show(routes[path],anchor); }
  });
  var legacy={'/index/':'/restaurant-intelligence-index/','/home/':'/'};
  var h=location.hash.replace('#/','/'); if(h && h!=='/' ){ h=h.endsWith('/')?h:h+'/'; h=legacy[h]||h; if(routes[h]) show(routes[h]); }
})();
</script>
'''
site_js = '<script>\n' + js.replace('</script', '<\\/script') + '\n</script>\n'

out = ('<!DOCTYPE html>\n<html lang="en">\n<head>\n' + head_new + '</head>\n' + body_open + '\n' + banner + body_new.strip() + '\n' + router + site_js + '</body>\n</html>\n')
assert out.count('id="fpi-config"') == 1, 'preview must carry exactly one fpi-config block'
assert 'name="robots" content="noindex, nofollow"' in out
OUT.write_text(out, encoding='utf-8')
leftovers = re.findall(r'(?<![\w/])/assets/[A-Za-z0-9_./-]+', out)
print('wrote', OUT, len(out.encode()), 'bytes; unresolved asset refs:', len(leftovers))
