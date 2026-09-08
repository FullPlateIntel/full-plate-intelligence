# CHANGELOG — FPI_SUBSCRIBER_LAUNCH_RC3 (colour correction pass over RC2)

Only actual changes are listed. Everything else (pages, markup, copy, Kit V3 workflow, Netlify packaging, tests) is as in RC2.

## Colour: approved brand colours restored everywhere (owner direction, 2026-09-07)
- `build/a11y.css`: removed every colour re-pointing introduced in RC1/RC2. There are no more `--fpi-orange-text`, `--fpi-orange-text-lg`, `--fpi-gold-text`, `--fpi-gold-text-lg`, `--fpi-orange-control` or `--fpi-orange-control-hover` tokens, and no rules re-colouring `.orange`, `.gold`, `.pill`, `.rii-*`, `.bm-*`, `.legal a`, `.contact-email`, headings, card CTAs or buttons. The approved stylesheet's own tokens now apply unchanged: brand orange `#F26A21`, deep orange `#D9531E`, gold `#D8A441` / `#B8892F` (Index), and primary buttons `#F26A21` with white labels and the original hover (lift + shadow, no colour change).
- The only orange used by RC-added elements (`.signup-error`, invalid-input outline) is the reference's own `--fpi-orange-deep`, matching the original `.signup-msg`.
- Verification: `tests/color_fidelity.py` renders the reference file and every dist page in the same browser and compares computed `color`, `background-color`, border, `stroke` and `fill` for every class-bearing element: 1,961 properties compared, 0 brand-colour differences. Rendered primary buttons on home, Index and Benchmark: `rgb(242,106,33)` / `rgb(255,255,255)`. Shipped CSS contains none of `#B7420F`, `#866013`, `#9C7019`, `#E9611B` (new test).
- Consequence, recorded not hidden: the WCAG 1.4.3 contrast gaps of the brand palette (orange text 2.73:1, gold 2.01:1, white on orange 3.06:1) return. They are logged as INFO / accepted deviation (AUDIT_AND_FIXES.md B9, TEST_RESULTS.md "Contrast"); the axe `color-contrast` rule is reported per page as INFO, all other serious/critical axe rules still fail the build.

## Tests
- `tests/run_tests.py`: contrast group now records the brand ratios (INFO when below AA); button check expects white labels; axe `color-contrast` separated from the pass/fail gate; new "no darkened substitutes in shipped CSS" check. Run: **541 PASS, 0 FAIL, 35 INFO**.
- New `tests/color_fidelity.py` (above) and `tests/make_preview.py` (builds the single-file NON-PRODUCTION preview from `dist/`; not part of the deploy).

## Documentation
- AUDIT_AND_FIXES.md (B9, R4, §5 register), TEST_RESULTS.md (header, contrast table), LAUNCH_RUNBOOK.md, README.md updated; this changelog added.

Unchanged and still unverified: Netlify preview/production deployment, live Kit form/e-mail journey, operator details, sticky notes (not replaced), analytics (disabled). Not subscriber-launch-ready.
