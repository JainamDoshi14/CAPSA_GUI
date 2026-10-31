# Memory Rules

Rules for any AI coding assistant (Claude, Cursor, Copilot, Gemini CLI, etc.) working on this project, so context survives between sessions. Copy this file's contents into the assistant's rules file (`CLAUDE.md`, `.cursorrules`, etc.) if it supports one.

## 1. Memory files
Keep a `memory/` folder in the repo root:

```
memory/
├── project_brief.md     # one-paragraph summary + links to docs/ (rarely changes)
├── active_context.md    # what is being worked on right now, next step, open questions
├── progress.md          # checklist per phase from PHASES.md, with dates
├── decisions.md         # numbered decision log (what, why, date)
└── known_issues.md      # bugs, textbook mismatches, TODOs
```

## 2. Session start (always)
1. Read `docs/PRD.md`, `docs/ARCHITECTURE.md`, `docs/DESIGN.md` only if the task touches them.
2. Always read `memory/active_context.md` and `memory/progress.md`.
3. State in one sentence which phase and task you are on before writing code.

## 3. Session end (always)
1. Update `progress.md`: tick finished items, add date.
2. Rewrite `active_context.md`: current state, exact next step, anything half-done.
3. Add any non-obvious choice to `decisions.md` as `D-00X: decision. Reason. Date.`
4. Add found bugs to `known_issues.md`.

## 4. What to store
- Decisions and the reason behind them.
- Verified textbook answers (question, expected GMR/GMD/L/C, source example number).
- Conventions (units, naming, file locations).

## 5. What NOT to store
- Secrets: API keys, tokens, passwords. Never in memory files, code, logs, or chat.
- Large code dumps (link to the file path instead).
- Guesses presented as facts. Mark uncertain items `[unverified]`.

## 6. Project conventions the assistant must follow
- **Units:** SI internally (metres, H, F). Convert only at the UI edge.
- **Separation:** nothing in `core/` may import `tkinter`, `ai/`, or network libraries.
- **AI boundary:** AI extracts inputs only. All calculations use `core/`. Never ask the AI model to compute GMR, GMD, L, or C.
- **Testing:** any change in `core/` needs a test; run `pytest` before declaring done.
- **Naming:** `snake_case` functions, `PascalCase` classes, constants in `theme.py` / `core/constants.py`.
- **Phase discipline:** do not start work from a later phase unless asked; mention it instead.
- **Design:** Neubrutalism, light theme only (no dark mode). Use tokens from `theme.py` (3 px black borders, hard +4 px shadows, flat colours, no gradients or blur); no hard-coded colours in tabs or widgets.
- **Minimal diffs:** change only what the task needs; do not reformat unrelated files.

## 7. Conflict rule
If code and docs disagree, stop and ask which is right, then update the other. Record the outcome in `decisions.md`.

## 8. Verified reference values (seed `decisions.md` with these)
| Item | Value | Source |
|------|-------|--------|
| 7-strand GMR | 2.1767 r | Q1 |
| Q2 conductor | diameter 1.345 in, GMR 0.5328 in | Example 4.2 |
| Textbook final L, C for Q2 to Q6 | `[unverified]` fill in from the book and tick off once tests pass | Examples 4.2 to 4.6 |

## 9. In-app history (optional, later)
If a "recent calculations" list is added, store it in `history.json` in the user's app-data folder, max 50 entries, input model + result only, never the API key.