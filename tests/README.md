# Tests

`tests/run_tests.py` is the automated matrix (static checks, contrast tokens, backend contract
against the mock Kit server, the dependency-injected core checks in `core_unit_test.mjs`, the Netlify
entry point in `netlify_entry_test.mjs`, browser behaviour with Playwright/Chromium + axe-core 4.10 including
the RC5 signup-timeout regressions (stalled body / no headers / late response through a raw-socket stub on
:8791 and a second static server on :8766 started by the runner), the Steve word-spacing checks at
320/375/390/400/401 px, responsive and fallback-font sweeps, first-load transfer sizes). It needs three local processes:

```
node server/mock-kit.mjs                                         # fake Kit API on :8790
set -a; . ./tests/test.env; set +a; node server/dev-server.mjs   # subscribe handler on :8780
python3 tests/serve.py --port=8765 --api=http://127.0.0.1:8780 --xff-per-request   # static site + proxy on :8765
python3 tests/run_tests.py
```

Outputs: `tests/results/results.md` (table), `results.json`, and screenshots in `tests/results/shots/`
(`steve_section_1280.png` / `steve_section_390.png` are the RC5 Founder/Why captures).
Standalone extras: `node tests/core_unit_test.mjs` (no servers needed), `python3 tests/color_fidelity.py http://127.0.0.1:8765`,
`python3 tests/make_preview.py PREVIEW_single_file_NONPRODUCTION_RC5.html RC5` (review preview; not deployed).
The suite proves local behaviour only. It does not send real email, does not contact api.kit.com, and
is not a Core Web Vitals measurement; see docs/TEST_RESULTS.md for what remains NOT TESTED.

Python dependencies: `playwright` (Chromium installed), `Pillow`, `numpy`. Node 18+ (uses global fetch).
