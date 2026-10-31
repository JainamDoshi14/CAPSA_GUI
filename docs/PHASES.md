# Phases: Transmission Line Studio

Each phase ends with a working, testable app. Do not start a phase until the previous exit criteria pass.

## Phase 0: Setup (0.5 day)
- Create folder structure from `ARCHITECTURE.md`, `requirements.txt`, `.gitignore` (include `.env`), `.env.example`.
- Move current maths from `geometry.py` into `core/` modules.
- **Exit:** `python main.py` opens an empty themed window.

## Phase 1: Core engine (1 to 2 days)
- `models.py`, `units.py`, `gmr.py`, `gmd.py`, `parameters.py`.
- Presets for Q1 to Q6 in `presets.py`.
- Unit tests, including regression tests against textbook answers.
- **Exit:** `pytest` passes; Q1 gives GMR = 2.1767 r; Q2 to Q6 match textbook within 1%.

## Phase 2: Composite conductor tab (0.5 day)
- Strand count + radius input, GMR result tile, strand diagram.
- **Exit:** Q1 solved in the UI.

## Phase 3: Line parameters tab (2 days)
- Editable table, Add conductor, Add bundle dialog, Remove, Clear.
- Preset loader, length and frequency inputs, Compute button.
- Geometry canvas, KPI tiles, Details panel.
- Validation and error banner.
- **Exit:** Q2 to Q6 solved end to end from presets and from manual entry.

## Phase 4: Step-by-step working and export (1 day)
- `working.py` generates formula chain with substituted numbers.
- "Show working" window, export to `.md` / `.txt`.
- **Exit:** Exported working for Q4 is readable and could go straight into a lab report.

## Phase 4b: Neubrutalism UI and Explain system (2 days)
- Build the Neubrutalism widget kit (`widgets/neo.py`: card, button with lift/press, input, segmented control, toggle, chip, tile, toast, dialog) using hard offset shadows.
- `theme.py` light-only tokens (colours, 3 px border, shadow offsets, radius), Space Grotesk + Space Mono fonts bundled.
- Home screen with 4 coloured start cards, stepper, phase chips, coloured result tiles.
- Result tiles with ? button, Explain sheet (Simple / Exam), story cards, glossary tooltips, smart hints.
- Draggable dots and "Show distances" on the tower view.
- **Exit:** a first-time user can solve Example 4.2 and understand every result without reading docs.

## Phase 5: Polish (1 day)
- Animations (button lift/press, count-up, toasts), reduce-motion setting, keyboard shortcuts (Ctrl+Enter = Compute).
- Number format toggle, unit selector (ft, in, cm, m).
- Window icon, About dialog.
- **Exit:** No clipped text at 1200 x 720 and at 1920 x 1080.

## Phase 6: AI upgrade (1 to 2 days), see `AI_UPGRADE.md`
- Settings dialog for API key, `ai/` package, upload button, review dialog.
- **Exit:** Screenshots of Q2 to Q6 extract correctly (after review) and compute the same as presets.

## Phase 7: Packaging (0.5 day)
- PyInstaller build, test on a clean Windows machine, README with install steps.
- **Exit:** Double-click .exe works, AI works after the user adds a key.

## Timeline summary
| Phase | Days | Cumulative |
|-------|------|-----------|
| 0 Setup | 0.5 | 0.5 |
| 1 Core | 2 | 2.5 |
| 2 Composite tab | 0.5 | 3 |
| 3 Line tab | 2 | 5 |
| 4 Working/export | 1 | 6 |
| 4b Neubrutalism UI + Explain | 2 | 8 |
| 5 Polish | 1 | 9 |
| 6 AI upgrade | 2 | 11 |
| 7 Packaging | 0.5 | 11.5 |

## Definition of done (every phase)
- Tests pass, no unhandled exceptions, docs updated, `memory/progress.md` updated (see `MEMORY_RULES.md`).