# Package note (RC5)

Complete FPI_SUBSCRIBER_LAUNCH_RC5 release candidate: the RC3 production project plus the closeout changes in docs/CHANGELOG_RC5.md. One project root: `FPI_SUBSCRIBER_LAUNCH_RC5/`. Start with `START_HERE.md`.

- `src/` (generated templates) is omitted from the ZIP; `make build` (or the exact `netlify.toml` command `python3 build/extract.py && python3 build/build.py`) regenerates it and `dist/` byte-for-byte from the read-only ORIGINAL file plus `build/overrides`, `build/assets`, `build/copy_edits.py`, `build/legal` and `build/site.js`. Two clean builds were compared: identical hashes (RELEASE_MANIFEST.json).
- `tests/results/shots/` and `evidence/` screenshots are PNG captures from the final test run. Site images in `dist/assets/img/` are untouched originals plus the two RC5 artwork files (byte-identical to `build/assets/img/`).
- The standalone review preview (`PREVIEW_single_file_NONPRODUCTION_RC5.html`) is generated from this same `dist/`, is `noindex`, carries a NON-PRODUCTION banner and is not inside the publish directory. It is delivered next to the ZIP, not inside `dist/`.

Status: IMPLEMENTATION COMPLETE, LOCALLY VERIFIED. Not DEPLOYMENT VERIFIED, not SUBSCRIBER LAUNCH READY (account-dependent checks in START_HERE.md part B).
