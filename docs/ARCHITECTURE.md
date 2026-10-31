# Architecture: Transmission Line Studio

## 1. Principles
1. **Engine is pure.** All maths lives in `core/` with no Tkinter or network imports. Testable on its own.
2. **UI is thin.** Tabs read widgets, build a `LineModel`, call the engine, render the result.
3. **AI is optional and one-way.** AI produces a `ProblemSpec` (data). A human confirms it. The engine computes. AI never does the arithmetic.
4. **Everything in SI internally** (metres, henry, farad). Conversion only at the UI edge.

## 2. Folder structure
```
transmission_line_studio/
├── main.py                  # entry point
├── app.py                   # root window, tab container, theme apply
├── theme.py                 # light-only Neubrutalism tokens: colours, fonts, border width, shadow offset, radius
├── core/                    # pure calculation (evolves from geometry.py)
│   ├── models.py            # dataclasses: Conductor, Phase, LineModel, Result
│   ├── units.py             # ft/in/cm/mil/cmil -> m
│   ├── gmr.py               # stranded GMR, bundle GMR
│   ├── gmd.py               # equivalent GMD for transposed lines
│   ├── parameters.py        # L, C, X_L, X_C
│   ├── presets.py           # Q2..Q6 example layouts
│   ├── working.py           # step-by-step text generator
│   └── explain_content.py   # plain-English text per result (what/formula/why)
├── tabs/
│   ├── home.py              # 4 start cards + recent list
│   ├── composite_tab.py     # Composite conductor
│   └── line_tab.py          # Line parameters
├── widgets/
│   ├── neo.py               # Neubrutalism kit: NeoCard, NeoButton, NeoInput, NeoSegmented, NeoToggle, NeoChip, NeoTile, NeoToast, NeoDialog
│   ├── dialogs.py           # Add bundle dialog, AI review dialog
│   ├── editable_table.py
│   ├── geometry_canvas.py
│   ├── result_tile.py       # KPI tile with ? button and count-up
│   ├── explain_sheet.py     # tap-to-explain side panel (Simple / Exam)
│   ├── story_cards.py       # step-by-step swipeable working
│   └── dropzone.py          # drag/drop/paste image upload
├── ai/                      # optional, see AI_UPGRADE.md
│   ├── schema.py            # pydantic ProblemSpec
│   ├── gemini_client.py
│   └── mapper.py            # ProblemSpec -> LineModel
├── tests/
│   ├── test_gmr.py
│   ├── test_examples.py     # Q1..Q6 regression
│   └── test_mapper.py
├── docs/                    # these md files
├── .env.example
├── .gitignore               # includes .env
└── requirements.txt
```

## 3. Data flow
```
          manual entry / preset                image upload (optional)
                 │                                     │
                 ▼                                     ▼
          editable_table  ◄────── review dialog ◄── ai/gemini_client
                 │                                (ProblemSpec JSON)
                 ▼
            LineModel  (core/models.py)
                 │
                 ▼
   core.gmr → core.gmd → core.parameters
                 │
                 ▼
            Result (dataclass)
          ┌──────┼───────────────┐
          ▼      ▼               ▼
     KPI tiles  Details     working.py (step-by-step)
                panel          → export .md/.txt
```

## 4. Core data models
```python
@dataclass
class Conductor:
    phase: str          # "A" | "B" | "C"
    x: float            # m
    y: float            # m
    r: float            # outer radius, m
    gmr_s: float        # self GMR of the (stranded) conductor, m

@dataclass
class LineModel:
    conductors: list[Conductor]
    length_km: float = 1.0
    freq_hz: float = 50.0

@dataclass
class Result:
    gmd: float
    gmr_l: float            # equivalent GMR for inductance
    gmr_c: float            # equivalent GMR (radius based) for capacitance
    L_mH_per_km: float
    C_uF_per_km: float
    L_total_mH: float
    C_total_uF: float
    per_phase: dict         # phase -> {n, gmr_l, gmr_c}
```

## 5. Algorithms (core)
**Stranded conductor (Q1):** for 7 identical strands of radius r, GMR = 2.1767 r (from `r' = 0.7788 r` and the 49-term distance product).

**Custom stranded conductor counts:** counts from 1 to 200 use the displayed layout: one centre strand, followed by clockwise-filled concentric hexagonal rings; a partial outer ring is allowed. Three strands use the documented equilateral triangle. The diagram and GMR engine share the same layout coordinates, and the pair-distance product is calculated from those coordinates.

**Per-phase composite GMR (generalised, works for any bundle or parallel circuit):**
```
GMR_L(phase) = ( Π_i Π_j D_ij )^(1/n²)      D_ii = gmr_s,  D_ij = distance
GMR_C(phase) = same, but D_ii = r (not gmr_s)
```
**Equivalent GMD (transposed):**
```
GMD_AB = ( Π_i∈A Π_j∈B d_ij )^(1/(nA·nB)), likewise BC, CA
GMD    = ( GMD_AB · GMD_BC · GMD_CA )^(1/3)
```
**Line parameters:**
```
L  = 2e-7 · ln(GMD / GMR_L)          H/m   → ×1e6 for mH/km
C  = 2π ε0 / ln(GMD / GMR_C)         F/m   (ε0 = 8.854e-12) → ×1e9 for uF/km
X_L = 2π f L ,  X_C = 1 / (2π f C)
```
Because the general formula is used, bundles (2, 3, 4 sub-conductors) and double circuits need no special cases. The bundle shortcuts (`√(Ds·d)`, `∛(Ds·d²)`, `1.09 ⁴√(Ds·d³)`) are used only inside `working.py` to *explain* steps.

## 5.1 Note on conductor images
Per-strand GMR values (e.g. `GMR_s = 0.7788 r` for a solid round conductor) are the default when the user gives only a diameter; if a datasheet GMR is given (e.g. 0.5328 in), it overrides.

## 6. Error handling
| Case | Behaviour |
|------|-----------|
| Missing phase label | Inline red cell + message, compute disabled |
| Phases with unequal sub-conductor counts | Warning, still computes (flag in Details) |
| Zero or negative radius | Blocked with message |
| Coincident conductors (distance 0 between different conductors) | Blocked |
| AI timeout, bad key, bad JSON | Toast + fall back to manual entry |

## 7. Testing strategy
- Unit tests for each core function with hand-checked numbers.
- Regression tests for Q1 to Q6 against textbook answers (tolerance 1%).
- Mapper tests: golden `ProblemSpec` JSON → expected `LineModel`.
- UI smoke test: launch, load each preset, press Compute, no exception.

## 8. Tech stack
Python 3.10+, plain Tkinter with a custom Neubrutalism widget kit (`widgets/neo.py`, hard offset shadows, light theme only, see DESIGN.md), Tkinter Canvas for the tower view, `tkinterdnd2` (drag and drop), `pydantic` (AI schema), `google-genai` (AI), `python-dotenv`, `Pillow` (image preview), `pytest`.

## 9. Packaging
`pyinstaller --onefile --windowed main.py` for a Windows .exe. The `.env` file is *not* bundled; the user supplies their own key (see AI_UPGRADE.md).
