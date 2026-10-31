# Phase progress

Dates use Asia/Calcutta. Last updated: 2026-10-20.

- [x] Phase 0 — Setup: scaffold, dependency/environment files, and themed window added; app launch confirmed on 2026-10-18.
- [x] Phase 1 — Core engine: SI models, units, stranded/composite GMR, mutual/equivalent GMD, line parameters, and Q2-Q6 presets implemented. Q1 ratio is 2.1767; Q2-Q6 regressions pass within 1%. `python -m pytest -q`: 32 passed.
- [x] Phase 2 — Composite conductor tab: standard strand selector plus a custom 1–200 count, numeric/symbolic radius, live GMR result, responsive shared-layout diagram, hover labels, and distance overlay. Custom counts fill center-out hexagonal rings; 3 strands retain the triangle.
- [x] Phase 3 — Line parameters tab: editable conductor table, manual conductor and bundle dialogs, Q2-Q6 preset loader, unit selector, length/frequency inputs, live layout and distances, result tiles, validation, and phase details. App preset flow Q2-Q6 and manual two-wire bundle flow confirmed on 2026-10-18. `python -m pytest -q`: 33 passed.
- [x] Phase 4 — Step-by-step working and export: pure report generator, substituted formula chain for GMD/GMR/L/C/reactance, on-screen working, clipboard copy, and Markdown/plain-text export. Q4 report generation and text readability are covered by tests; 35 tests pass (2026-10-18).
- [x] Phase 4b — Neubrutalism UI and Explain system: home screen and four start cards, recent list, light-only design tokens, coloured phase chips/result tiles, per-result Simple/Exam explain sheets, five story cards with copy/export, glossary hover tips, inline smart hints, and draggable geometry dots that update the table. Visual alignment follows DESIGN.md v5. Per the user's explicit design request, the 30-second option and top Start/Add/Check/Results navigation are omitted (2026-10-20).
- [x] Phase 5 — Polish: count-up result animation, success toasts, reduce-motion control, Ctrl+Enter compute shortcut, 4/5 significant-digit toggle, existing unit selector retained, window icon, and About dialog. GUI smoke completed at 1200x720 and 1920x1080 (2026-10-18).
- [ ] Phase 6 — AI upgrade: not started.
- [ ] Phase 7 — Packaging: not started.

Design alignment update (2026-10-20): updated the palette, typography, home spacing, table, strand diagram, and distance labels to Neubrutalism v5; calculation logic remains unchanged. Python compile and app import checks pass. GUI visual review remains outstanding.

Custom stranded-conductor update (2026-10-20): added a custom count field and apply action; shared layout coordinates drive the diagram and GMR product. The UI accepts whole-number counts 1–200.

Startup/rendering fix (2026-10-20): deferred Composite and Line tab widget construction until first visit, removed `lift()` from shadow syncing, and selected CustomTkinter polygon drawing to avoid its optional shape-font fallback. Compile and import succeeded; live GUI review remains outstanding.

Verified regression outputs (per km, rounded): Q2 L=1.38018 mH, C=0.008343 μF; Q3 L=1.05884 mH, C=0.010730 μF; Q4 L=0.88912 mH, C=0.012680 μF; Q5 L=0.45147 mH, C=0.025304 μF; Q6 L=0.68357 mH, C=0.016786 μF. Q2-Q4 source values: 1.38/0.0083, 1.0588/0.0107, 0.8891/0.0127. Q5-Q6 source values: 0.4491/0.0254, 0.6836/0.0168. All L values are mH/km and C values are μF/km.
