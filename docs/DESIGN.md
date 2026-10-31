# Design: Transmission Line Studio (v5, Neubrutalism, light only)

> **Mood:** loud, playful, honest and impossible to get lost in. Thick black outlines, flat bright colours, hard offset shadows and chunky type make every element look like a sticker or a printed card stuck on a cream page. It feels fun, but the structure is strict, so users always know what to press and where to look.
>
> **Light theme only.** There is no dark mode, no theme switch and no theme setting.
>
> **Scope:** this document changes the *look and feel* only. All functionality in `PRD.md` stays exactly the same (stranded GMR, conductor table, bundles, presets, compute, tower view, results, explain system, step-by-step working, export, AI image upload).

---

## 1. Design philosophy

### 1.1 What Neubrutalism means here
Neubrutalism takes the raw, unpolished honesty of brutalist web design and adds friendly colour. Nothing is hidden or blended: borders are visible, shadows are solid blocks, colours are flat and saturated, and type is big and bold. The result is high contrast, very readable, and full of personality.

### 1.2 Six rules (the whole style)
1. **Every box has a 3 px solid black border.** Cards, buttons, inputs, chips, tiles, dialogs, the canvas.
2. **Every raised box has a hard shadow:** solid black, offset 4 px right and 4 px down, **no blur, no transparency**. Large cards use 6 px.
3. **Fills are flat and saturated** on a warm cream page. No gradients, no glow, no glass, no soft shadows.
4. **Corners are square or barely rounded.** One radius value is used everywhere (4 px recommended; 0 px is also valid). Never pill shaped. Only dots, the stepper numbers and toggle knobs are round.
5. **Type is heavy.** Large bold headings, monospace for all numbers.
6. **Interaction is physical.** Buttons lift on hover and push into their shadow on press, like real keys.

### 1.3 Supporting principles
- **Colour has a job.** Each phase and each result type keeps its colour everywhere, so users learn the code once.
- **Snap, solve, understand.** Three steps are always visible: Add, Check, Results.
- **Every number explains itself.** Tap any result to get plain English, then the formula, then the user's own numbers.
- **Punchy, friendly voice.** Short sentences, no jargon without a one-line translation.
- **Room for shadows.** Gaps between boxes are at least 20 px so hard shadows never touch the next element.

---

## 2. Design tokens (`theme.py`), light theme only

### 2.1 Colour
| Token | Value | Use |
|-------|-------|-----|
| `BG` | `#FFF6E0` | Page background (warm cream) |
| `SURFACE` | `#FFFFFF` | Cards, table, canvas, inputs |
| `INK` | `#111111` | All text, all borders, all shadows |
| `MUTED` | `#4A4A4A` | Helper text and captions (still strong contrast) |
| `YELLOW` | `#FFD93D` | Primary buttons, highlights, Phase B |
| `PINK` | `#FF6B9D` | Phase A, Capacitance tile |
| `BLUE` | `#4D96FF` | Phase C, Inductance tile |
| `MINT` | `#6BCB77` | Success, GMD tile, completed steps |
| `ORANGE` | `#FF9F1C` | Warnings, GMR tile |
| `LAVENDER` | `#C9B6FF` | Explain panel, hints, secondary accents |
| `RED` | `#FF4D4D` | Errors, danger hover |
| `HOVER_TINT` | `#FFF0B8` | Row hover, drop-zone drag-over |

Rules:
- Text is always `INK` on any fill. White text is never used on a bright colour.
- All fills pair with `INK` text at 7:1 contrast or better.
- Pure black (`INK`) is used for outlines; do not substitute greys for borders.
- No tints or opacity for shadows. Shadows are always full `INK`.

### 2.2 Phase and result colour code
| Meaning | Colour |
|---------|--------|
| Phase A | `PINK` |
| Phase B | `YELLOW` |
| Phase C | `BLUE` |
| Inductance (L) tile | `BLUE` |
| Capacitance (C) tile | `PINK` |
| GMD tile | `MINT` |
| GMR tile (L and C) | `ORANGE` |
| Explain panel and hints | `LAVENDER` |

### 2.3 Typography
| Role | Font | Fallback | Size |
|------|------|----------|------|
| App title | **Space Grotesk Bold** (or Archivo Black) | Arial Black | 28 |
| Section title | Space Grotesk Bold | Arial Bold | 18 |
| Body | Space Grotesk Medium | Segoe UI | 12 |
| Caption / helper | Space Grotesk Medium | Segoe UI | 10 |
| Button label | Space Grotesk Bold | Arial Bold | 12 |
| Numbers, table, formulas, working | **Space Mono Bold** | Consolas | 12 |
| Big result number | Space Mono Bold | Consolas | 30 |

Notes: bundle the font files with the app. Section labels and sticker tags may be UPPERCASE. Body text stays in sentence case.

### 2.4 Shape, spacing and motion
| Item | Value |
|------|-------|
| Border | 3 px `INK` (2 px for dividers inside tables) |
| Shadow, normal | offset (+4, +4), solid `INK`, no blur |
| Shadow, large cards and dialogs | offset (+6, +6) |
| Hover (buttons, cards) | element moves (-2, -2); shadow grows to (+6, +6) |
| Pressed | element moves (+4, +4) onto its shadow; shadow hidden |
| Radius | one value everywhere: 4 px (or 0) |
| Spacing grid | 8 px |
| Card padding | 20 px |
| Gap between boxes | 20 px |
| Window margin | 28 px |
| Minimum click target | 40 x 40 px |
| Motion | 100 ms linear for lift and press; 500 ms count-up on results; 200 ms slide for side sheet; no fades or springs |
All motion is skipped when "Reduce motion" is on in Settings.

### 2.5 Icons
Chunky icons with a 3 px stroke in `INK`, flat colour fills where used, drawn square-ended. Always paired with a label on buttons. Set: camera, puzzle, bolt, microscope, plus, trash, layers (bundle), question mark, lightbulb, copy, download, gear, check, alert, info, arrow left/right.

---

## 3. Components (detailed specs)

### 3.1 Button (`NeoButton`)
**Primary (one main action per step, e.g. "CALCULATE")**
- Fill `YELLOW`, `INK` bold label, 3 px border, shadow (+4, +4), height 48, side padding 28.
- Hover: lifts (-2, -2), shadow (+6, +6). Pressed: moves (+4, +4), shadow hidden.
- Disabled: fill `SURFACE`, label `MUTED`, border stays, **no shadow** (flat).
- Loading: label becomes "CRUNCHING THE NUMBERS..." with an animated dot trail.

**Secondary (Add conductor, Add bundle, Load, Copy, Export)**
- Fill `SURFACE`, `INK` bold label with an icon on the left, height 44, same lift and press.
- Hover fill changes to `HOVER_TINT`.

**Danger (Remove selected, Clear all)**
- Same as secondary; on hover the fill becomes `RED`. A confirm dialog appears for Clear all.

**Icon button (? help, gear, close)**
- 40 x 40 square, 3 px border, shadow (+3, +3), icon centred. The **?** on tiles is 32 x 32 with a `LAVENDER` fill.

### 3.2 Inputs and dropdowns (`NeoInput`)
- Fill `SURFACE`, 3 px border, height 44, radius as global, text in Space Mono Bold.
- Placeholder in `MUTED`.
- Focus: the shadow appears (+3, +3) in `INK` and the fill turns `HOVER_TINT`.
- Error: border stays black, fill turns a light `RED` tint (`#FFD6D6`), a small alert icon at the right, message in bold under the field.
- Dropdown: arrow in a small bordered square on the right side.
- Unit text (m, ft, in) sits inside the right edge in `MUTED`.

### 3.3 Segmented control (units m / ft / in / cm, Simple / Exam, strand counts)
- A row of bordered boxes sharing 3 px borders (no gaps).
- Selected segment: filled `YELLOW`, bold label. Unselected: `SURFACE`.
- Whole control has the (+4, +4) shadow.

### 3.4 Toggle (Show distances, Show GMD, Reduce motion)
- Square-ish track 56 x 28 with 3 px border; knob is a round bordered circle.
- Off: knob left, track `SURFACE`. On: knob right, track `MINT`, a check inside the knob.
- Label on the right in body text.

### 3.5 Phase chips (A, B, C)
- 44 x 44 bordered squares with shadow (+3, +3), bold letter, filled with the phase colour (A `PINK`, B `YELLOW`, C `BLUE`).
- Active chip: pressed in (moved onto its shadow) with a thicker 4 px border.
- Clicking chooses the phase for the next conductor added.

### 3.6 Conductor table
- Container: `SURFACE`, 3 px border, shadow (+4, +4).
- Header row: `INK` fill with `SURFACE` bold text (the only place white text appears, always on black).
- Rows: height 44, 2 px `INK` dividers, alternating `SURFACE` and `#FFFBEF`.
- Phase cell shows a small bordered square sticker in the phase colour with the letter.
- Hover row: `HOVER_TINT`. Selected row: `YELLOW` fill with a 6 px `INK` bar on the left.
- Double-click a cell to edit (turns into an input). Invalid cell: light `RED` fill, alert icon, tooltip explaining.
- Empty state: a big icon sticker and "NOTHING HERE YET. Drop an image, load an example, or add a conductor."
- Scrollbar: 14 px wide, bordered, thumb filled `YELLOW`.

### 3.7 Stepper (Add, Check, Results)
- Three square-bordered number boxes joined by 3 px lines. Labels under them in bold.
- Active: filled `YELLOW`, shadow (+4, +4). Completed: filled `MINT` with a check. Upcoming: `SURFACE`.
- Each step is clickable and shows a tooltip.

### 3.8 Cards and panels (`NeoCard`)
- Fill `SURFACE` (or a colour for emphasis), 3 px border, shadow (+6, +6) for large cards.
- Title row: section title with a small coloured **sticker tag** (bordered label, e.g. "STEP 1") rotated -2 degrees where the toolkit allows it, otherwise straight.
- Helper text under the title in caption style.

### 3.9 Result tiles
The most important component. Five tiles: Inductance, Capacitance, GMD, GMR (L), GMR (C). X_L and X_C appear under a "MORE" toggle.
- Size about 200 x 140, filled with the result's colour (see 2.2), 3 px border, shadow (+5, +5).
- Top-left: the sticker label (e.g. "INDUCTANCE") on a white bordered tag.
- Top-right: the **?** button.
- Middle: the big value in Space Mono Bold 30, `INK`.
- Bottom: unit caption such as "mH per km", wrapping to two lines, **never clipped**.
- Hover: lifts. Click anywhere opens the Explain panel.
- States: empty "--". Computing: diagonal black stripe pattern animation on the tile. Done: count-up.

### 3.10 Tower / layout view
- Container: `SURFACE`, 3 px border, shadow (+6, +6), faint 1 px dotted grid (`#DDD`).
- Conductors are **round dots** (24 px) with a 3 px `INK` border, filled with the phase colour, and a bold letter label beside each (A, B, C), so colour is never the only cue.
- Hover a dot: it lifts with a small hard shadow; a tooltip shows phase and x, y. Drag to move; the table updates live.
- Bundle members of a phase are linked by a short solid 2 px line.
- "Show distances" draws dashed `INK` lines with small bordered labels (D12, D23, bundle spacing). "Show GMD" highlights the lines used in `ORANGE`, 3 px thick.
- Auto-fit with 12 percent margin. A bordered scale bar sits at the bottom-left.

### 3.11 Drop zone (image upload)
- `SURFACE`, 3 px **dashed** `INK` border, shadow (+4, +4), height 160.
- Content: camera icon sticker, "DROP AN IMAGE HERE", caption "or click to browse, or paste with Ctrl+V".
- Drag-over: fill `HOVER_TINT`, the border becomes solid, icon jumps up 4 px.
- Reading state: a bordered progress bar with a `YELLOW` fill that slides, text "READING YOUR IMAGE...".
- No key set: flat (no shadow), text "Add your Gemini key in Settings to turn this on" and a secondary button "OPEN SETTINGS".

### 3.12 Details panel and formula boxes
- `SURFACE` with 3 px border, Space Mono 11. Formula boxes use a `#FFFBEF` fill.
- Per-phase blocks separated by 2 px dividers. A copy icon button sits in the top-right corner.

### 3.13 Tooltips and glossary chips
- Tooltip: `LAVENDER` box, 3 px border, shadow (+3, +3), max width 260, text 11 bold, appears after 400 ms.
- Glossary terms are underlined with a 3 px `YELLOW` highlight; clicking opens a one-line explanation tooltip.

### 3.14 Toast
- Bordered box, shadow (+4, +4), 320 px wide, bottom right, 24 px from edges.
- Left square sticker with an icon; fill by type: success `MINT`, warning `ORANGE`, error `RED`, info `LAVENDER`. Message in bold body text. Slides in over 150 ms linear, holds 4 s.

### 3.15 Dialog
- Overlay: a flat `BG` layer over the page (no transparency, no blur) so the thick bordered dialog stands out.
- Panel: `SURFACE`, 3 px border, shadow (+6, +6), padding 28, title bar filled with a colour that matches the dialog type.
- Primary button at the bottom right. Escape closes; clicking outside does not.

### 3.16 Confidence badges (AI review)
Small bordered stickers: "SURE" (`MINT`), "CHECK THIS" (`ORANGE`), "COULDN'T READ" (`RED`). Each table row also gets a coloured square at its left edge.

---

## 4. Screens

### 4.1 Home
Greeting at the top: "HI! WHAT ARE WE SOLVING TODAY?" in app title style. Small sticker tag "TRANSMISSION LINE STUDIO" above it.

Four large coloured cards in a 2 x 2 grid (each about 360 x 160, shadow (+6, +6)):

| Card | Fill | Icon | Title | Subtitle | Goes to |
|------|------|------|-------|----------|---------|
| 1 | `PINK` | camera | SNAP AND SOLVE | Upload a picture of your question | Drop zone, review |
| 2 | `BLUE` | puzzle | BUILD IT YOURSELF | Add conductors one by one | Empty workspace |
| 3 | `YELLOW` | bolt | TRY AN EXAMPLE | Textbook problems 4.2 to 4.6, ready to go | Example picker |
| 4 | `MINT` | microscope | STRANDED WIRE GMR | How many strands? Get the GMR | Composite tool |

Hover lifts the card; press pushes it in. Below the grid:
- **Recent**: a bordered list of the last 5 calculations (name, date, L and C values), click to reopen.
- A text button "HOW THIS WORKS IN 30 SECONDS" opening a three-card story (add, check, results).

### 4.2 Workspace (main screen)
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ⚡ TRANSMISSION LINE STUDIO     [1 ADD]━[2 CHECK]━[3 RESULTS]  [⚙] ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓   ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ [STEP 1] Your conductors  ┃   ┃ [STEP 2] Your line (live view) ┃
┃ ┌ DROP AN IMAGE HERE ───┐ ┃   ┃ ┌────────────────────────────┐ ┃
┃ └───────────────────────┘ ┃   ┃ │   ●A         ●A            │ ┃
┃ ── or add by hand ──      ┃   ┃ │   ●B         ●B            │ ┃
┃ Phase [A][B][C]           ┃   ┃ │   ●C         ●C            │ ┃
┃ ┌ table ────────────────┐ ┃   ┃ └────────────────────────────┘ ┃
┃ │ Phase  X  Y  r  GMR_s │ ┃   ┃ [ ] SHOW DISTANCES  [ ] SHOW GMD┃
┃ └───────────────────────┘ ┃   ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
┃ [+CONDUCTOR] [+BUNDLE]    ┃   ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ [REMOVE]     [CLEAR]      ┃   ┃ [STEP 3] Results               ┃
┃ Example [4.2 ▼] [LOAD]    ┃   ┃ ┏━━━━┓ ┏━━━━┓ ┏━━━━┓ ┏━━━━┓   ┃
┃ Length [1] km Freq [50] Hz┃   ┃ ┃ L ?┃ ┃ C ?┃ ┃GMD?┃ ┃GMR?┃   ┃
┃ [      CALCULATE       ]  ┃   ┃ ┗━━━━┛ ┗━━━━┛ ┗━━━━┛ ┗━━━━┛   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛   ┃ [💡 EXPLAIN IT TO ME] [COPY]   ┃
                                ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```
- Left column 44 percent, right column 56 percent. Minimum window 1200 x 720.
- Below 1000 px width the right column stacks under the left.
- The "MORE" toggle reveals X_L, X_C and per-km versus total values.
- The Details panel opens as a drawer under Results via "SHOW DETAILS".

### 4.3 Composite conductor (stranded wire) screen
- Left card: standard strand-count segments plus a **Custom** option (whole-number count 1–200), radius input `r` (number or the symbol r), primary button "CALCULATE GMR". Custom counts fill concentric hexagonal rings outward; a partial final ring is allowed.
- Right card: bordered canvas with the **hex-packed strand diagram** drawn as numbered round dots (centre strand `YELLOW`, outer ring `BLUE`). It updates live with the strand count. "Show distances" draws the lines used. The GMR calculation uses the same displayed coordinates.
- Result tile (`ORANGE`): "GMR = 2.1767 r" for 7 strands, with **?** explaining the 0.7788 r factor.

### 4.4 Explain system (same functions, bold look)
**Tap-to-explain panel** (opens from any **?**)
- Slides in from the right: 420 px wide, `LAVENDER` header bar, `SURFACE` body, 3 px border, shadow (+6, +6). Simple / Exam segmented control at the top.
- Four stacked boxes, each with a sticker heading: **WHAT IS IT?**, **FORMULA**, **YOUR NUMBERS**, **WHY IT MATTERS**.
- "Your numbers" shows the formula with the values substituted; the final answer sits in a `YELLOW` highlighted box.
- Footer: COPY and CLOSE buttons.

**Story cards ("Explain it to me")**
- A big bordered card in a dialog, "STEP 2 OF 5", with five square progress boxes (current one `YELLOW`, done ones `MINT`).
- Each card: short title, one friendly sentence, formula box, answer box (`YELLOW`), and a mini tower view highlighting the relevant parts.
- Buttons: BACK (secondary), NEXT (primary), COPY STEP, COPY ALL FOR REPORT, EXPORT .MD.
- Steps: 1 Your setup, 2 GMR of each phase, 3 GMD between phases, 4 Inductance, 5 Capacitance.

**Smart hints**
Bordered `LAVENDER` notes under the relevant field with an icon, never blocking. Examples: "Heads up: phase B has 1 wire but A has 2. Intended?" and "You typed 35 and the unit is metres. Did you mean feet?" with a SWITCH TO FT button. Positive confirmation uses `MINT`: "Looks good, 6 conductors across 3 phases."

### 4.5 Image upload and review (AI)
1. Drop zone accepts drag, click or paste.
2. A thumbnail appears in a bordered frame with the sliding progress bar.
3. **Review dialog:** left, the image in a bordered frame. Right, a table of what was understood with confidence stickers per row.
4. Buttons: **LOOKS RIGHT, USE IT** (primary) and **EDIT FIRST** (secondary).
5. After confirming, the workspace opens with the tower view already drawn.

### 4.6 Settings
Bordered dialog with: default units (segmented), decimals (5 significant digits or "textbook rounding" 4), Gemini API key (masked input with a SHOW toggle and a **TEST CONNECTION** button), Reduce motion (toggle), About (notes that images are sent to Google when AI is used). **There is no theme option.**

### 4.7 Empty, loading and error states
| State | Look |
|-------|------|
| Empty table | Big icon sticker + "NOTHING HERE YET" helper text |
| Computing | Primary button shows "CRUNCHING THE NUMBERS...", result tiles show moving black stripes |
| AI reading | Sliding yellow progress bar + "READING YOUR IMAGE..." |
| Error | Toast plus inline message under the field; never a raw traceback |
| Offline | Info toast "You're offline. Manual mode still works." |

---

## 5. Microcopy and tone
Punchy, friendly, direct. Button labels are UPPERCASE; sentences are normal case.

| Situation | Copy |
|-----------|------|
| Empty table | "Nothing here yet. Drop an image, load an example, or add a conductor." |
| Primary button | "CALCULATE" |
| Computing | "Crunching the numbers..." |
| Success | "Done! Your line has L = 1.28 mH/km. Tap a result to see why." |
| Missing phase | "Which phase is this wire on? Pick A, B or C." |
| Zero radius | "A wire needs a radius bigger than 0." |
| AI failed | "Couldn't read that one. Try a clearer or cropped photo, or add it manually." |
| No key | "Add your Gemini key in Settings to turn this on." |

Glossary tooltips: **GMR** effective radius of the conductor for magnetic effects. **GMD** average distance between the phases. **Bundle** several wires per phase, spaced apart, to reduce losses. **Transposed** phases swap positions along the line so they average out. **Double circuit** two three-phase lines on one tower.

---

## 6. Accessibility
- Text is `INK` on every fill: contrast is 7:1 or better on all palette colours.
- Never colour alone: phases carry letters, statuses carry icons and words, selected rows carry a thick left bar.
- Keyboard focus: a 4 px `BLUE` outline (offset 2 px) on every focusable element, plus the focus shadow; Tab order follows the layout.
- Minimum target 40 x 40 px.
- Reduce-motion setting disables lift animation, count-up, stripes and slides.
- Font size control: Settings can scale all text to 100, 115 or 130 percent.

---

## 7. Do and don't
| Do | Don't |
|----|-------|
| Use 3 px black borders on every box | Use thin or grey borders |
| Use solid black offset shadows with no blur | Use blur, transparency or glow |
| Use flat saturated fills | Use gradients or glassy effects |
| Keep one radius value everywhere | Mix pill and sharp corners |
| Keep 20 px or more between boxes | Let a shadow touch the next element |
| Use `INK` text on every fill | Put white text on bright colours |
| Keep colour meaning consistent | Colour things at random |

---

## 8. Implementation notes (Python + Tkinter)
This style is easy in Tkinter because hard shadows need no image rendering.

1. **Widget kit:** `widgets/neo.py` provides `NeoCard`, `NeoButton`, `NeoInput`, `NeoSegmented`, `NeoToggle`, `NeoChip`, `NeoTile`, `NeoTooltip`, `NeoToast`, `NeoDialog`.
2. **Hard shadow technique:** wrap each widget in a container `Frame` whose background is `INK`. Inside, place the visible `Frame` (border via `highlightthickness=3`, `highlightbackground=INK`) at an offset so the black container peeks out on the bottom-right as the shadow. Simplest approach: a shadow `Frame` (bg `INK`) placed at (+4, +4) behind the main `Frame` using `place()`.
3. **Lift and press:** on `<Enter>` move the main frame by (-2, -2) and grow the shadow to (+6, +6); on `<ButtonPress>` move it to (+4, +4); on `<ButtonRelease>` or `<Leave>` restore. Each is a few `place(x=, y=)` calls, so it is instant.
4. **Canvas widgets:** the tower view, strand diagram, tiles' stripe animation and progress bar use `tk.Canvas` with `create_rectangle(width=3, outline=INK)`. Shadows on canvas are an extra filled rectangle offset by (+4, +4) drawn first.
5. **Table:** `ttk.Treeview` styled flat (`rowheight=44`, header background `INK`, foreground `SURFACE`), wrapped in a `NeoCard`. Row dividers via the style's borderwidth, or draw the table on a canvas if finer control is needed.
6. **Dashed border (drop zone):** draw a `create_rectangle(dash=(8, 6), width=3)` on a canvas.
7. **Fonts:** bundle Space Grotesk and Space Mono; load at startup (on Windows via `ctypes.windll.gdi32.AddFontResourceExW`) and fall back to Arial Black / Consolas.
8. **Count-up and stripes:** `after(16, step)` loops; 30 frames for count-up, a moving stripe offset for loading.
9. **Drag and drop:** `tkinterdnd2`. Paste: `PIL.ImageGrab.grabclipboard()`.
10. **Single source of truth:** every colour, border width, shadow offset, radius and font comes from `theme.py`. No hard-coded values in tabs or widgets.
11. **No extra libraries for the style:** plain Tkinter is enough. Pillow is only used for the image preview and the AI flow.

---

## 9. QA checklist (design)
- [ ] Every box has a 3 px `INK` border.
- [ ] Every raised box has a solid hard shadow (+4, +4), large cards (+6, +6); no blur anywhere.
- [ ] No gradients, glows or transparent shadows.
- [ ] One radius value used throughout.
- [ ] Text is `INK` on every fill; white text appears only on the black table header.
- [ ] Phase and result colours match section 2.2 on every screen.
- [ ] Buttons lift on hover and press into the shadow; disabled buttons are flat.
- [ ] No clipped text on result tiles at 1200 x 720 and 1920 x 1080.
- [ ] Gaps between boxes are at least 20 px.
- [ ] Hover, press, focus, disabled and error states exist for every interactive component.
- [ ] No dark theme or theme option anywhere.
- [ ] Reduce motion turns off all animations.
- [ ] Home, Workspace, Composite, Explain panel, Story cards, Review dialog and Settings all look consistent.

## 10. Number formatting
Default 5 significant digits (0.67027); "textbook rounding" shows 4. Units always sit next to numbers. Copy buttons copy plain text with units.
