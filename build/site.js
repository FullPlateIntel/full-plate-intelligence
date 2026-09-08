/* Full Plate Intelligence site script (RC5: 12 s signup deadline now covers the response body; see docs/CHANGELOG_RC5.md). No dependencies. Plain ES5-compatible syntax for reach. */
(function () {
  'use strict';
  var cfgEl = document.getElementById('fpi-config');
  var CFG = {};
  try { CFG = JSON.parse(cfgEl ? cfgEl.textContent : '{}'); } catch (e) { CFG = {}; }
  var MSG = CFG.messages || {};
  var REDUCED = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ------------------------------------------------------------ legacy #/route compatibility
     The old single-file site used hash routes. Fragments never reach the server, so this small
     allowlisted map is the only way to carry old links to the new pages. Anything else in the
     hash (section anchors like #signup) is left alone. */
  var legacy = CFG.legacyRoutes || {};
  function migrateLegacyHash() {
    if (!location.hash) return false;
    var qi = location.hash.indexOf('?');
    var route = qi === -1 ? location.hash : location.hash.slice(0, qi);
    var tail = qi === -1 ? '' : location.hash.slice(qi);          /* tracking appended after the old hash */
    if (legacy.hasOwnProperty(route)) {
      location.replace(legacy[route] + (location.search || tail));
      return true;
    }
    return false;
  }
  if (migrateLegacyHash()) return;
  window.addEventListener('hashchange', migrateLegacyHash);

  /* ------------------------------------------------------------ campaign attribution (allowlisted, session only) */
  var ATTR_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content'];
  var SAFE = /^[A-Za-z0-9_.-]{1,64}$/;
  function readAttribution() {
    var stored = null;
    try { stored = JSON.parse(sessionStorage.getItem('fpi_attr') || 'null'); } catch (e) { stored = null; }
    if (stored) return stored;                      /* first touch within this browser session wins */
    var params = new URLSearchParams(location.search), out = {}, any = false;
    ATTR_KEYS.forEach(function (k) { var v = params.get(k); if (v && SAFE.test(v)) { out[k] = v; any = true; } });
    if (any) { try { sessionStorage.setItem('fpi_attr', JSON.stringify(out)); } catch (e) {} return out; }
    return null;
  }
  var attribution = readAttribution();

  /* ------------------------------------------------------------ analytics adapter (no-op unless configured) */
  function track(event, props) {
    var a = CFG.analytics || {};
    var payload = props || {};
    if (a.provider === 'ga4' && a.measurement_id && typeof window.gtag === 'function') {
      window.gtag('event', event, payload);     /* never contains an email address */
    }
    if (window.FPI_DEBUG_EVENTS) { window.FPI_DEBUG_EVENTS.push([event, payload]); }
  }
  window.fpiTrack = track;

  /* ------------------------------------------------------------ in-page CTAs: capture interest, then scroll */
  var INTERESTS = ['newsletter', 'show', 'index', 'benchmark', 'benchmark-calculator', 'benchmark-report'];
  Array.prototype.forEach.call(document.querySelectorAll('[data-scroll]'), function (btn) {
    btn.addEventListener('click', function () {
      var target = document.getElementById(btn.getAttribute('data-scroll'));
      if (!target) return;
      var interest = btn.getAttribute('data-interest');
      if (interest && INTERESTS.indexOf(interest) !== -1) {
        var field = target.querySelector('input[name="interest"]');
        if (field) field.value = interest;
        track('cta_select', { interest: interest, page: document.body.getAttribute('data-page') });
      }
      target.scrollIntoView({ behavior: REDUCED ? 'auto' : 'smooth', block: 'center' });
      var input = target.querySelector('input[name="email"]');
      if (input && !target.classList.contains('is-done')) {
        setTimeout(function () { input.focus({ preventScroll: true }); }, REDUCED ? 0 : 500);
      }
    });
  });
  /* Header SUBSCRIBE FREE: on pages that have a signup form the href is that page's own form/section anchor.
     With script, bring the email box into view and put the cursor in it (same behaviour as the in-page CTAs);
     the plain href still works without script and on the legal pages, whose href points at the homepage form. */
  Array.prototype.forEach.call(document.querySelectorAll('[data-cta="header-subscribe"]'), function (a) {
    a.addEventListener('click', function (e) {
      track('cta_select', { interest: 'newsletter', placement: 'header', page: document.body.getAttribute('data-page') });
      var href = a.getAttribute('href') || '';
      if (href.charAt(0) !== '#') return;                                   /* cross-page link: let the browser navigate */
      var target = document.getElementById(href.slice(1));
      if (!target || target.hidden || !target.offsetParent && getComputedStyle(target).position !== 'fixed') return;
      var form = target.matches('form.signup') ? target : target.querySelector('form.signup');
      var box = form || target;
      e.preventDefault();
      if (history.replaceState) { try { history.replaceState(null, '', href); } catch (err) {} }
      box.scrollIntoView({ behavior: REDUCED ? 'auto' : 'smooth', block: 'center' });
      var input = form && form.querySelector('input[name="email"]');
      if (input && !form.classList.contains('is-done')) {
        setTimeout(function () { input.focus({ preventScroll: true }); }, REDUCED ? 0 : 500);
      }
    });
  });

  /* ------------------------------------------------------------ signup forms */
  var EMAIL_RE = /^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]{1,64}@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$/;
  var TIMEOUT_MS = 12000;
  Array.prototype.forEach.call(document.querySelectorAll('form.signup'), function (form) {
    var input = form.querySelector('input[name="email"]');
    var btn = form.querySelector('button[type="submit"]');
    var errorEl = form.querySelector('.signup-error');
    var statusEl = form.querySelector('.signup-status');
    var hp = form.querySelector('input[name="fpi_ref"]');
    var helpId = input.getAttribute('aria-describedby') || '';
    var busy = false, label = btn.textContent, startedAt = Date.now(), attemptSeq = 0;

    function showError(text) {
      errorEl.textContent = text; errorEl.hidden = false;
      input.setAttribute('aria-invalid', 'true');
      input.setAttribute('aria-describedby', (errorEl.id + ' ' + helpId).trim());
      input.classList.add('oops');
    }
    function clearError() {
      errorEl.textContent = ''; errorEl.hidden = true;
      input.removeAttribute('aria-invalid');
      if (helpId) input.setAttribute('aria-describedby', helpId); else input.removeAttribute('aria-describedby');
      input.classList.remove('oops');
    }
    function setBusy(on) {
      busy = on; form.classList.toggle('is-busy', on);
      btn.disabled = on; input.readOnly = on;
      btn.textContent = on ? 'SENDING…' : label;
      if (on) form.setAttribute('aria-busy', 'true'); else form.removeAttribute('aria-busy');
    }
    var helpEl = form.querySelector('.signup-status-help');
    function done(text) {
      clearError();
      form.classList.add('is-done');
      statusEl.textContent = text;
      if (helpEl && MSG.generic_help) { helpEl.textContent = MSG.generic_help; helpEl.hidden = false; }
      statusEl.setAttribute('tabindex', '-1');
      statusEl.focus({ preventScroll: true });
    }
    function fail(text) {
      setBusy(false); showError(text); input.focus({ preventScroll: true });
    }
    input.addEventListener('input', clearError);

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (busy || form.classList.contains('is-done')) return;      /* duplicate-click protection */
      var email = input.value.trim();
      if (!EMAIL_RE.test(email) || email.length > 254) { showError(MSG.invalid || 'Please enter a valid email address.'); input.focus(); return; }
      clearError();
      var source = form.getAttribute('data-source') || 'website';
      var interest = (form.querySelector('input[name="interest"]') || {}).value || 'newsletter';
      if (hp && hp.value) {                                         /* honeypot filled: behave like success, send nothing */
        done(MSG.generic || 'Thanks.'); return;
      }
      setBusy(true);
      track('signup_submit', { source: source, interest: interest });
      /* One attempt token per submission. The 12 s deadline covers the whole request AND the body read/parse
         (res.json()). When it fires, the form is restored immediately; anything that arrives later for this
         attempt (late headers, late body, the AbortError from our own abort) is ignored so it can never
         overwrite the timeout state or a newer attempt. */
      var attempt = ++attemptSeq, settled = false, timedOut = false;
      var controller = ('AbortController' in window) ? new AbortController() : null;
      function isCurrent() { return attempt === attemptSeq && !settled; }
      function settle() { settled = true; clearTimeout(timer); }
      var timer = setTimeout(function () {
        if (!isCurrent()) return;
        timedOut = true; settle();
        track('signup_error', { source: source, code: 'timeout' });
        fail(MSG.timeout || MSG.network || 'That took too long. Please try again.');
        if (controller) controller.abort();
      }, TIMEOUT_MS);
      var pagePath = (form.querySelector('input[name="page"]') || {}).value || location.pathname;
      var body = { email: email, source: source, interest: interest, page: pagePath, path: pagePath,   /* `path` kept for the existing V3 function's contract */
                   elapsed_ms: Date.now() - startedAt, attribution: attribution || undefined };
      fetch(CFG.endpoint || '/api/subscribe', {
        method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(body), credentials: 'same-origin', signal: controller ? controller.signal : undefined
      }).then(function (res) {
        /* keep the deadline running while the body streams/parses; only a malformed body becomes {} —
           an abort during the body read stays an AbortError */
        return res.json().then(
          function (data) { return { res: res, data: data }; },
          function (err) { if (err && err.name === 'AbortError') throw err; return { res: res, data: {} }; }
        );
      }).then(function (r) {
        if (!isCurrent()) return;                                     /* late completion after timeout / newer attempt */
        settle();
        var res = r.res, data = r.data;
        if (res.ok && data && data.ok === true) {
          var status = data.status;                                  /* accepted | pending_confirmation | subscribed */
          var text = status === 'pending_confirmation' ? (MSG.pending || MSG.generic) : status === 'subscribed' ? (MSG.subscribed || MSG.generic) : (MSG.generic || 'Thanks.');
          setBusy(false); done(text);
          track('signup_accepted', { source: source, interest: interest, status: status || 'accepted' });
          return;
        }
        var code = (data && data.error) || ('http_' + res.status);
        track('signup_error', { source: source, code: String(code).slice(0, 40) });
        if (res.status === 400 && code === 'invalid_email') { fail(MSG.invalid); return; }
        if (res.status === 429) { fail(MSG.rate_limited); return; }
        fail(MSG.unavailable || 'Signups are temporarily unavailable. Please try again shortly.');
      }).catch(function (err) {
        if (!isCurrent()) return;                                     /* our own abort after timeout, or a stale attempt */
        settle();
        var aborted = timedOut || (err && err.name === 'AbortError');
        track('signup_error', { source: source, code: aborted ? 'timeout' : 'network' });
        fail(aborted ? (MSG.timeout || MSG.network) : (MSG.network || 'That did not go through. Please try again.'));
      });
    });
  });
})();

