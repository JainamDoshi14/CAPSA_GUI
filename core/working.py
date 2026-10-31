"""Report-ready, substituted calculation steps for a calculated line model."""

from collections import defaultdict
import re
from .models import LineModel, Result


def _n(value: float, digits: int) -> str:
    return f"{value:.{digits}g}"


def generate_working_markdown(model: LineModel, result: Result, digits: int = 5) -> str:
    """Render the calculation path and substituted values as a Markdown report."""
    phases = defaultdict(list)
    for conductor in model.conductors:
        phases[conductor.phase].append(conductor)
    q = lambda value: _n(value, digits)
    lines = [
        f"# Line parameter calculation — {model.name}", "",
        "## Given data", "",
        f"- Line length: {q(model.length_km)} km",
        f"- Frequency: {q(model.freq_hz)} Hz",
        f"- Conductors: {len(model.conductors)} total; " + ", ".join(
            f"phase {phase}: {len(phases[phase])}" for phase in "ABC"
        ), "",
        "## 1. Mutual geometric mean distances", "",
        "For each phase pair, take the geometric mean of all conductor-to-conductor spacings:", "",
        f"- $D_{{AB}} = {q(result.gmd_ab)}$ m",
        f"- $D_{{BC}} = {q(result.gmd_bc)}$ m",
        f"- $D_{{CA}} = {q(result.gmd_ca)}$ m",
        f"- $GMD = (D_{{AB}}D_{{BC}}D_{{CA}})^{{1/3}} = ({q(result.gmd_ab)} × {q(result.gmd_bc)} × {q(result.gmd_ca)})^{{1/3}} = {q(result.gmd)}$ m", "",
        "## 2. Equivalent self GMR for each phase", "",
        "The composite self term is the geometric mean of the ordered self and mutual distances in that phase. For capacitance, conductor radius replaces self GMR on the diagonal.", "",
    ]
    for phase in "ABC":
        p = result.per_phase[phase]
        lines.append(
            f"- Phase {phase} ($n={p.n}$): $GMR_L={q(p.gmr_l)}$ m; "
            f"$GMR_C={q(p.gmr_c)}$ m"
        )
    lines.extend([
        "",
        f"- $GMR_L = (GMR_{{LA}}GMR_{{LB}}GMR_{{LC}})^{{1/3}} = ({q(result.per_phase['A'].gmr_l)} × {q(result.per_phase['B'].gmr_l)} × {q(result.per_phase['C'].gmr_l)})^{{1/3}} = {q(result.gmr_l)}$ m",
        f"- $GMR_C = (GMR_{{CA}}GMR_{{CB}}GMR_{{CC}})^{{1/3}} = ({q(result.per_phase['A'].gmr_c)} × {q(result.per_phase['B'].gmr_c)} × {q(result.per_phase['C'].gmr_c)})^{{1/3}} = {q(result.gmr_c)}$ m", "",
        "## 3. Inductance per phase", "",
        "$L = 2 × 10^{-7} ln(GMD/GMR_L)$ H/m", "",
        f"$L = 2 × 10^{{-7}} ln({q(result.gmd)}/{q(result.gmr_l)}) = {q(result.L_mH_per_km * 1e-6)}$ H/m = **{q(result.L_mH_per_km)} mH/km**", "",
        f"For {q(model.length_km)} km: $L_{{total}} = {q(result.L_mH_per_km)} × {q(model.length_km)} = **{q(result.L_total_mH)}$ mH**.", "",
        "## 4. Capacitance per phase", "",
        "$C = 2π ε_0 / ln(GMD/GMR_C)$ F/m, where $ε_0 = 8.8541878128 × 10^{-12}$ F/m.", "",
        f"$C = 2π × 8.8541878128 × 10^{{-12}} / ln({q(result.gmd)}/{q(result.gmr_c)}) = {q(result.C_uF_per_km * 1e-9)}$ F/m = **{q(result.C_uF_per_km)} μF/km**", "",
        f"For {q(model.length_km)} km: $C_{{total}} = {q(result.C_uF_per_km)} × {q(model.length_km)} = **{q(result.C_total_uF)}$ μF**.", "",
        "## 5. Reactance per kilometre", "",
        f"$X_L = 2πfL_{{1 km}} = 2π × {q(model.freq_hz)} × ({q(result.L_mH_per_km)} × 10^{{-3}}) = **{q(result.X_L_ohm_per_km)} Ω/km**$.", "",
        f"$X_C = 1/(2πfC_{{1 km}}) = 1/(2π × {q(model.freq_hz)} × ({q(result.C_uF_per_km)} × 10^{{-6}})) = **{q(result.X_C_ohm_per_km)} Ω/km**$.", "",
        "---", "Calculated by Transmission Line Studio.",
    ])
    return "\n".join(lines)


def generate_working_text(model: LineModel, result: Result, digits: int = 5) -> str:
    """Render a plain-text equivalent suitable for a .txt export."""
    markdown = generate_working_markdown(model, result, digits)
    text = markdown.replace("**", "").replace("$", "")
    text = re.sub(r"\^\{([^}]*)\}", r"^\1", text)
    text = re.sub(r"_\{([^}]*)\}", r"_\1", text)
    for old, new in (("\\times", " x "), ("×", " x "), ("π", " pi "),
                     ("ε_0", "epsilon_0"), ("μ", "u"), ("Ω", "ohm")):
        text = text.replace(old, new)
    text = re.sub(r"(?m)^#{1,6}\s*", "", text)
    return text

