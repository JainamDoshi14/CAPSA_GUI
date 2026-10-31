# AI Upgrade: Upload an Image, Get the Result (Gemini)

**Goal:** the user clicks **Upload image**, picks a screenshot or photo of a transmission-line problem (like Questions 1 to 6), and the app fills the conductor table. The user checks it, presses Compute, and gets the answer.

**Rule:** Gemini only *reads* the problem. The app's own `core/` engine does all calculations. This keeps answers exact and testable.

```
image → Gemini (JSON) → validate (pydantic) → review dialog → LineModel → core engine → results
```

---

## Step 1: Get a Gemini API key
1. Go to **https://aistudio.google.com/apikey** and sign in with a Google account.
2. Click **Create API key** and copy it.
3. Keep it private. Never paste it in code, screenshots, or chat.

## Step 2: Install packages
```bash
pip install google-genai pydantic python-dotenv Pillow
```
Add to `requirements.txt`:
```
google-genai
pydantic>=2
python-dotenv
Pillow
```

## Step 3: Store the key safely
Create `.env` in the project root:
```
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash
```
Create `.env.example` (safe to commit):
```
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash
```
Add to `.gitignore`:
```
.env
```
> Model names change over time. If `gemini-2.5-flash` is rejected, check the current list at https://ai.google.dev/gemini-api/docs/models and update `GEMINI_MODEL` in `.env`. No code change needed.

## Step 4: Define the output schema: `ai/schema.py`
```python
from typing import Literal, Optional
from pydantic import BaseModel, Field

class ConductorSpec(BaseModel):
    phase: Literal["A", "B", "C"]
    x: float = Field(description="horizontal position in the unit given in `unit`")
    y: float = Field(description="vertical position in the unit given in `unit`")

class ProblemSpec(BaseModel):
    problem_type: Literal["stranded_gmr", "single_circuit", "double_circuit"]
    # stranded conductor problems
    num_strands: Optional[int] = None
    # line problems
    conductors: list[ConductorSpec] = []
    unit: Literal["m", "ft", "in", "cm"] = "m"
    conductor_diameter: Optional[float] = None
    diameter_unit: Optional[Literal["in", "cm", "m", "mm"]] = None
    gmr_s: Optional[float] = None
    gmr_unit: Optional[Literal["in", "cm", "m", "mm"]] = None
    bundle_count: int = 1
    bundle_spacing: Optional[float] = None
    bundle_unit: Optional[Literal["in", "cm", "m"]] = None
    frequency_hz: Optional[float] = None
    line_length_km: Optional[float] = None
    confidence: Literal["high", "medium", "low"] = "medium"
    notes: str = ""
```

## Step 5: Gemini client: `ai/gemini_client.py`
```python
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from .schema import ProblemSpec

load_dotenv()

PROMPT = """You are reading a transmission-line textbook problem from an image.
Extract ONLY the data needed to build the conductor layout. Do NOT calculate anything.

Rules:
- problem_type: "stranded_gmr" if it is about GMR of a stranded conductor (give num_strands);
  "single_circuit" for one three-phase circuit; "double_circuit" if two circuits share a tower
  (phases a,b,c and a',b',c').
- For double circuit, give BOTH conductors of each phase in `conductors` (same phase letter for a and a').
- Convert phase names to capital A, B, C (a' -> A, b' -> B, c' -> C).
- Give conductor positions (x right, y up) using the spacings in the figure. Place phase a at x=0,
  y=0 (single circuit) or build coordinates from the labelled distances (D12, D23, H12, S11, ...).
- If a bundle is described (e.g. two conductors 18 in apart), list EVERY sub-conductor separately.
- Keep the unit that appears in the figure (ft, in, cm, m) in `unit`; do not convert.
- Fill diameter and GMR if stated. Leave unknown fields null.
- Set confidence to "low" if any dimension is unreadable and explain in `notes`.
"""

class GeminiError(Exception):
    pass

def extract_problem(image_bytes: bytes, mime_type: str = "image/png") -> ProblemSpec:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise GeminiError("No API key found. Add GEMINI_API_KEY to your .env file.")
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    try:
        client = genai.Client(api_key=key)
        resp = client.models.generate_content(
            model=model,
            contents=[types.Part.from_bytes(data=image_bytes, mime_type=mime_type), PROMPT],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ProblemSpec,
                temperature=0,
            ),
        )
        spec = resp.parsed
        if spec is None:
            raise GeminiError("The model returned no usable data. Try a clearer image.")
        return spec
    except GeminiError:
        raise
    except Exception as e:  # network, quota, invalid key...
        raise GeminiError(f"Gemini request failed: {e}") from e
```

## Step 6: Convert the spec into the app model: `ai/mapper.py`
```python
from core.models import Conductor, LineModel
from core.units import to_metres

def spec_to_model(spec) -> LineModel:
    conductors = []
    r = 0.0
    if spec.conductor_diameter and spec.diameter_unit:
        r = to_metres(spec.conductor_diameter, spec.diameter_unit) / 2
    gmr = to_metres(spec.gmr_s, spec.gmr_unit) if spec.gmr_s and spec.gmr_unit else 0.7788 * r
    for c in spec.conductors:
        conductors.append(Conductor(
            phase=c.phase,
            x=to_metres(c.x, spec.unit),
            y=to_metres(c.y, spec.unit),
            r=r,
            gmr_s=gmr,
        ))
    return LineModel(
        conductors=conductors,
        length_km=spec.line_length_km or 1.0,
        freq_hz=spec.frequency_hz or 50.0,
    )
```
For `stranded_gmr`, skip the mapper and send `num_strands` straight to the Composite conductor tab.

## Step 7: Hook into the UI (`tabs/line_tab.py`)
Run Gemini in a background thread so the window does not freeze.

```python
import threading
from tkinter import filedialog, messagebox
from ai.gemini_client import extract_problem, GeminiError
from ai.mapper import spec_to_model

def on_upload_image(self):
    path = filedialog.askopenfilename(
        title="Select problem image",
        filetypes=[("Images", "*.png *.jpg *.jpeg *.webp")])
    if not path:
        return
    with open(path, "rb") as f:
        data = f.read()
    mime = "image/png" if path.lower().endswith(".png") else "image/jpeg"
    self.set_busy(True, "Reading image...")

    def work():
        try:
            spec = extract_problem(data, mime)
            self.after(0, lambda: self.show_review(spec, path))
        except GeminiError as e:
            self.after(0, lambda: messagebox.showerror("AI error", str(e)))
        finally:
            self.after(0, lambda: self.set_busy(False))

    threading.Thread(target=work, daemon=True).start()

def show_review(self, spec, image_path):
    # Open the AI review dialog (image on the left, editable table on the right).
    # On "Use these values":
    model = spec_to_model(spec)
    self.table.load_model(model)      # fills the table
    self.canvas.redraw(model)         # updates tower view
    # The user then presses "Compute Line Parameters".
```
Button in the layout (next to *Load example*):
```python
ttk.Button(row, text="📷 Upload image (AI)", command=self.on_upload_image)
```
Disable it with a tooltip if no key is set:
```python
if not os.getenv("GEMINI_API_KEY"):
    self.ai_button.state(["disabled"])
```

## Step 8: Optional in-app key entry
Add a **Settings** dialog with a masked entry. Save to `.env` with `python-dotenv`:
```python
from dotenv import set_key
set_key(".env", "GEMINI_API_KEY", key_value)
os.environ["GEMINI_API_KEY"] = key_value
```
Include a **Test connection** button that sends a tiny text prompt and shows OK or the error.

## Step 9: Test it
1. Put the screenshots of Questions 1 to 6 in `tests/images/`.
2. For each, run `extract_problem` and compare the result with the preset in `core/presets.py` (conductor count, phases, spacings, within 1%).
3. Check at least: Q5 and Q6 (double circuit, a' b' c' mapped to A B C), Q4 (4-conductor bundle), Q1 (`num_strands = 7`).
4. Save passing examples as golden JSON files for `tests/test_mapper.py`.

## Step 10: Safety and limits
- Always show the **review dialog**. Never compute straight from AI output.
- If `confidence` is `low`, highlight the notes and affected rows in amber.
- Keep the key in `.env` only; never commit it; rotate it if exposed.
- Free-tier limits and model availability change; handle errors (429 quota, 401 key) with friendly messages.
- Image data is sent to Google's servers. Mention this in the app's About dialog.
- App must keep working fully with AI off.

## Troubleshooting
| Problem | Fix |
|---------|-----|
| "No API key found" | `.env` missing or wrong folder; it must sit next to `main.py` |
| 400 or 404 model error | Update `GEMINI_MODEL` to a current model name |
| 429 error | Quota hit; wait or use a different key/project |
| Wrong coordinates | Image too blurry or figure ambiguous; crop to the figure and question text and retry; correct in review dialog |
| Window freezes | The call is on the main thread; use the thread pattern in Step 7 |

## Future ideas
Let Gemini also read the *question text* for line length and frequency; add paste-from-clipboard; add a "Explain this result" button that sends the computed numbers to Gemini for a plain-English explanation (the numbers still come from `core/`).
