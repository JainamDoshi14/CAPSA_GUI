# Known issues

- The GUI launch criterion has been checked for the composite and line-parameters tabs. Interactive table-cell editing was implemented but has not been manually exercised in a user session.
- No `geometry.py` existed in the supplied folder, despite the Phase 0 instruction to move existing math from it.
- The double-circuit Q5/Q6 presets encode the figure dimensions and phase arrangements from the reference; their regression values are within 1% of the published rounded outputs. The source's own rounding/layout conventions cause small differences within that tolerance.
- The Neubrutalism pass and startup/rendering fixes have passed Python compilation and module import, but the desktop GUI has not yet been visually rechecked at 1200×720. Home loads immediately; Composite and Line build on first visit, so their first-open render will still take longer than subsequent visits.
