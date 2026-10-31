# PRD: Transmission Line Studio

**Version:** 1.0  **Platform:** Desktop (Python + Tkinter)  **Course context:** CAPSA / Power System Analysis (Examples 4.1 to 4.6 style problems)

## 1. Problem
Textbook transmission-line problems (stranded conductors, bundled conductors, single and double circuit lines) need repetitive hand calculation of GMR, GMD, inductance and capacitance. It is slow and error-prone, and students cannot easily see *why* an answer comes out the way it does.

## 2. Goal
A desktop app where a student enters (or later uploads a picture of) a problem and gets:
1. Correct final values (GMR, GMD, L, C, optionally X_L, X_C).
2. A step-by-step working they can copy into a lab report.
3. A live geometry view of the conductor layout.

## 3. Target users
- Primary: undergraduate EEE students doing CAPSA / Power System Analysis labs.
- Secondary: instructors verifying answers.

## 4. Problem types in scope (from the reference questions)
| # | Type | Example |
|---|------|---------|
| Q1 | Stranded conductor GMR (n identical strands, radius r) | 7-strand, GMR = 2.1767 r |
| Q2 | Single-circuit, single conductor per phase, horizontal | Ex 4.2 (500 kV, ACSR 45/7) |
| Q3 | Single-circuit, 2-conductor bundle, horizontal | Ex 4.3 (18 in spacing) |
| Q4 | Single-circuit, 4-conductor bundle, horizontal | Ex 4.4 (735 kV, 46 cm spacing) |
| Q5 | Double-circuit, 2-conductor bundle, vertical | Ex 4.5 (345 kV) |
| Q6 | Double-circuit, 1 conductor per phase, horizontal | Ex 4.6 (345 kV) |

## 5. Functional requirements
### 5.1 Composite conductor tab
- FR1: Choose a standard strand count (1, 3, 7, 19, 37, 61, 91) or enter a custom whole-number count from 1 to 200, plus strand radius `r` (numeric or symbolic).
- FR2: Output GMR as multiple of `r` and in absolute units.

### 5.2 Line parameters tab
- FR3: Editable table of every physical sub-conductor: Phase, X, Y, r, GMR_s.
- FR4: "Add conductor", "Add bundle..." (n sub-conductors, spacing, orientation), "Remove selected", "Clear all".
- FR5: Preset examples dropdown covering Q2 to Q6, loaded with one click.
- FR6: Unit handling: accept ft, in, cm, m, mil, cmil; convert internally to metres.
- FR7: Inputs for line length (km) and frequency (Hz).
- FR8: Compute: equivalent GMD, GMR_L, GMR_C, total L (mH/phase), total C (uF/phase), plus per-km values, X_L and X_C.
- FR9: Auto-detect phases, bundles and parallel circuits (same phase label = parallel).
- FR10: Geometry canvas redraws live; phases colour-coded A red, B orange, C blue.
- FR11: Details panel shows per-phase intermediate values.

### 5.3 Step-by-step solution
- FR12: "Show working" produces the formula chain with numbers substituted (for lab report use).
- FR13: Export working and results to `.md` and `.txt` (PDF optional later).

### 5.4 AI upgrade (see `AI_UPGRADE.md`)
- FR14: Upload a picture of a problem, AI extracts the parameters, user reviews/edits, then app computes.
- FR15: Works fully offline with AI disabled.

## 6. Non-functional requirements
- NFR1: Results match textbook answers within 1% (rounding differences only).
- NFR2: Compute time under 100 ms for up to 200 conductors.
- NFR3: Runs on Windows 10/11, Python 3.10+; no admin rights.
- NFR4: The calculation engine never depends on AI. AI only fills inputs.
- NFR5: API keys never stored in source or committed.

## 7. Out of scope (v1)
Sag/tension, corona, line models (short/medium/long), unsymmetrical spacing without transposition correction, cloud sync.

## 8. Success metrics
- All six reference questions reproduce textbook answers.
- A new user solves a problem in under 2 minutes without reading docs.
- AI extraction correct on at least 90% of clean textbook images (after user review step).

## 9. Assumptions and risks
| Risk | Mitigation |
|------|-----------|
| Ambiguous problem figures (units like 35' vs m) | Unit field per input, AI flags low confidence |
| AI misreads figure | Mandatory review screen before compute |
| Textbook rounds intermediate values | Show both full-precision and rounded display |
| Double circuit geometry misinterpreted | Geometry canvas + preset tests |
