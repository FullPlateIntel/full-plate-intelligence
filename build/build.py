#!/usr/bin/env python3
"""Stage 2: render the static site (dist/) from src/ + site.config.json.

Run `python3 build/extract.py` first (or `make build`, which does both). Everything here is a
deterministic transform of the approved 5_14_0_2_1 design: the design, artwork and layout are
carried over unchanged, and only the changes recorded in docs/AUDIT_AND_FIXES.md and
docs/COPY_CHANGES.md are applied.
"""
