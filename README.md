# Transmission Line Studio

Transmission Line Studio is a Python desktop application for exploring overhead transmission-line geometry and calculating geometric mean distance (GMD), geometric mean radius (GMR), inductance, capacitance, and line reactance. It is intended as a learning aid for power-system and transmission-line calculations: enter a layout, inspect the geometry, and review the intermediate calculation steps.

## Features

- Calculate stranded-conductor GMR for standard strand counts and custom layouts from 1 to 200 strands.
- Enter single conductors or two-, three-, and four-wire bundles for phases A, B, and C.
- Load built-in example layouts Q2–Q6, corresponding to textbook Examples 4.2–4.6.
- View and edit conductor coordinates, radius, and self-GMR; inspect the layout and distances in the geometry view.
- Calculate equivalent GMD, inductive and capacitive GMR, inductance, capacitance, and inductive and capacitive reactance.
- View calculation details and export the working as Markdown (`.md`) or plain text (`.txt`).
- Choose a strand radius symbolically (`r`) or enter a numeric radius with supported units.

The current application uses manual entry and built-in examples. Image-to-input extraction is not part of the implemented workflow.

## Requirements

- Python 3.10 or later
- Packages listed in [`requirements.txt`](requirements.txt)
- Tk support in the Python installation (included with most standard Windows Python installers)

## Installation and launch

From the project directory, create and activate a virtual environment in PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

On macOS or Linux, the equivalent commands are:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

## Using the application

### Stranded wire GMR

1. Open **Stranded wire GMR** from the Home screen or top tab.
2. Choose a standard strand count or select **Custom** and enter a whole number from 1 to 200.
3. Enter a strand radius and select its unit, or leave `r` for a symbolic result.
4. Read the resulting GMR factor and inspect the strand layout. **Show distances** displays the center-to-center spacing guides.

### Line parameters

1. Open **Line parameters**.
2. Either choose Q2–Q6 and select **Load example**, or build a layout with **+ Conductor** and **+ Bundle**.
3. Assign each conductor to phase A, B, or C. Set its coordinates, radius, and self-GMR. If self-GMR is left blank in an add dialog, the application uses `0.7788 × radius`.
4. Set the line length in kilometres and frequency in hertz.
5. Select **Calculate**. Use the geometry display, phase details, and **Show working** to review the result. Working can be exported as `.md` or `.txt`.

## Calculation method

All conductor lengths are converted to metres inside the calculation engine. For each pair of phases, the program takes the geometric mean of the conductor-to-conductor distances, then combines the three phase-pair means:

```text
GMD = (D_AB × D_BC × D_CA)^(1/3)
```

For each phase, the engine calculates separate equivalent self terms for inductance and capacitance. The diagonal self-distance is the conductor's supplied self-GMR for inductance and its physical radius for capacitance. For a transposed, balanced three-phase line, the phase values are combined geometrically and used in:

```text
L = 2 × 10^-7 × ln(GMD / GMR_L)             H/m
C = 2π × ε₀ / ln(GMD / GMR_C)               F/m
ε₀ = 8.8541878128 × 10^-12 F/m
X_L = 2πfL
X_C = 1 / (2πfC)
```

The interface reports inductance in mH/km, capacitance in μF/km, and reactance in Ω/km. Line length scales the total L and C values; frequency is used for reactance. Line voltage is not required by these calculations.

## Assumptions and scope

- The line-parameter equations use the balanced, transposed three-phase model implemented by the calculation engine.
- The result depends on the entered conductor coordinates, radii, self-GMR values, frequency, and line length.
- Unsymmetrical spacing without transposition correction, sag and tension, corona, short/medium/long line models, and cloud synchronization are outside the current scope.
- The project documentation notes an orientation ambiguity for the Example 4.3 layout. Check its preset geometry against the original textbook figure before treating it as a reference answer.

## Project architecture

```text
.
├── main.py                     # Application entry point
├── app.py                      # Root window, tabs, and navigation
├── theme.py                    # Shared visual tokens
├── core/                        # Calculation engine and data models
│   ├── models.py                # Conductor, LineModel, PhaseResult, Result
│   ├── units.py                 # Length-unit conversion
│   ├── gmr.py                   # Stranded and composite GMR calculations
│   ├── gmd.py                   # Mutual and equivalent GMD calculations
│   ├── parameters.py            # L, C, X_L, and X_C calculations
│   ├── presets.py               # Built-in Q2–Q6 layouts
│   ├── working.py               # Step-by-step working and exports
│   └── explain_content.py       # Plain-language result explanations
├── tabs/
│   ├── home.py                  # Home screen
│   ├── composite_tab.py         # Stranded-conductor GMR workspace
│   └── line_tab.py              # Line geometry and parameter workspace
├── widgets/                     # Reusable interface components
│   ├── dialogs.py               # Conductor and bundle entry dialogs
│   ├── editable_table.py        # Editable conductor table
│   ├── geometry_canvas.py       # Transmission-line geometry diagram
│   ├── strand_diagram.py        # Stranded-conductor cross-section
│   ├── explain_sheet.py         # Contextual explanations
│   ├── story_cards.py           # Step-by-step calculation display
│   ├── glossary.py              # Engineering term definitions
│   ├── neo.py                   # Shared styled controls
│   └── neu.py                   # Neumorphic widgets
├── tests/                       # Unit and calculation behavior tests
├── docs/                        # Requirements, design, architecture, and notes
├── memory/                      # Project context and progress notes
├── .env.example                 # Example environment configuration
├── .gitignore                   # Excludes local environments and secrets
└── requirements.txt             # Python package dependencies
```

The calculation engine is kept in `core/`; the Tkinter interface gathers input and presents its results. The main data flow is:

```text
manual input or preset → LineModel → GMD and GMR → line parameters → results and working
```

## Tests

Run the project test suite from the project directory with:

```powershell
python -m pytest
```

## Project documents

- [Product requirements](docs/PRD.md)
- [Architecture notes](docs/ARCHITECTURE.md)
- [Design notes](docs/DESIGN.md)
- [Development phases](docs/PHASES.md)
- [AI upgrade notes](docs/ai_upgrade.md) — describes possible future work, not an active image-solving feature
- [Project report](Transmission_Line_Studio_Project_Report.docx)

## License

No license file is currently included. Add a license if you intend to permit reuse or distribution of this project.
