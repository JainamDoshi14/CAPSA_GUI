"""Plain-language and exam-style explanations for calculated line results."""

from .models import LineModel, Result


_CONTENT = {
    "gmd": (
        "Average phase-to-phase spacing across the three phases, using a geometric average.",
        "Think of it as one representative phase-to-phase distance for the whole line.",
        "More phase spacing generally lowers the electric-field coupling and changes L and C.",
        "GMD = (D_AB · D_BC · D_CA)^(1/3)",
    ),
    "gmr_l": (
        "Effective conductor radius used in the inductance calculation.",
        "A bundle of wires behaves magnetically like one conductor with an equivalent radius.",
        "A larger inductive GMR lowers the line's inductance.",
        "GMR_L = (GMR_LA · GMR_LB · GMR_LC)^(1/3)",
    ),
    "gmr_c": (
        "Effective conductor radius used in the capacitance calculation.",
        "It is the electrical size of each phase when calculating its electric field.",
        "It sets the logarithmic spacing term used to find capacitance.",
        "GMR_C = (GMR_CA · GMR_CB · GMR_CC)^(1/3)",
    ),
    "inductance": (
        "Inductance per phase per kilometre, caused by the magnetic field around the conductors.",
        "It measures how strongly current changes oppose changes in current.",
        "Inductance affects voltage drop and inductive reactance in AC operation.",
        "L = 2 × 10^-7 ln(GMD / GMR_L) H/m",
    ),
    "capacitance": (
        "Capacitance per phase per kilometre, caused by charge stored between conductors.",
        "The conductors and the space between them act like a long distributed capacitor.",
        "Capacitance creates charging current, even when the line has little load.",
        "C = 2π ε0 / ln(GMD / GMR_C) F/m",
    ),
    "reactance": (
        "The AC opposition associated with the line's inductance and capacitance.",
        "XL is the magnetic part; XC is the electric-field part.",
        "Reactance helps describe current flow and voltage behaviour on an AC line.",
        "XL = 2πfL;  XC = 1 / (2πfC)",
    ),
}


def explain_result(metric: str, model: LineModel, result: Result, digits: int = 5) -> dict[str, str]:
    """Return explanation copy plus the formula with this result's values."""
    if metric not in _CONTENT:
        raise ValueError(f"unknown result metric: {metric}")
    what, analogy, why, formula = _CONTENT[metric]
    q = lambda value: f"{value:.{digits}g}"
    substitutions = {
        "gmd": f"GMD = ({q(result.gmd_ab)} × {q(result.gmd_bc)} × {q(result.gmd_ca)})^(1/3) = {q(result.gmd)} m",
        "gmr_l": f"GMR_L = ({q(result.per_phase['A'].gmr_l)} × {q(result.per_phase['B'].gmr_l)} × {q(result.per_phase['C'].gmr_l)})^(1/3) = {q(result.gmr_l)} m",
        "gmr_c": f"GMR_C = ({q(result.per_phase['A'].gmr_c)} × {q(result.per_phase['B'].gmr_c)} × {q(result.per_phase['C'].gmr_c)})^(1/3) = {q(result.gmr_c)} m",
        "inductance": f"L = 2 × 10^-7 ln({q(result.gmd)} / {q(result.gmr_l)}) = {q(result.L_mH_per_km)} mH/km; total for {q(model.length_km)} km = {q(result.L_total_mH)} mH",
        "capacitance": f"C = 2π × 8.8541878128 × 10^-12 / ln({q(result.gmd)} / {q(result.gmr_c)}) = {q(result.C_uF_per_km)} μF/km; total = {q(result.C_total_uF)} μF",
        "reactance": f"XL = 2π × {q(model.freq_hz)} × L = {q(result.X_L_ohm_per_km)} Ω/km; XC = 1/(2π × {q(model.freq_hz)} × C) = {q(result.X_C_ohm_per_km)} Ω/km",
    }
    return {"title": metric.replace("_", " ").upper(), "what": what, "analogy": analogy,
            "why": why, "formula": formula, "substitution": substitutions[metric]}


def story_steps(model: LineModel, result: Result, digits: int = 5) -> list[dict[str, str]]:
    """Build the five short explanation cards for a completed calculation."""
    q = lambda value: f"{value:.{digits}g}"
    return [
        {"title": "Your setup", "body": f"You entered {len(model.conductors)} conductors across phases A, B and C, with a {q(model.length_km)} km line at {q(model.freq_hz)} Hz.", "formula": f"Phases: A={result.per_phase['A'].n}, B={result.per_phase['B'].n}, C={result.per_phase['C'].n}"},
        {"title": "Each phase gets an effective radius", "body": "The bundle wires combine into one equivalent GMR for inductance and one for capacitance.", "formula": f"GMR_L = {q(result.gmr_l)} m;  GMR_C = {q(result.gmr_c)} m"},
        {"title": "The phase spacing is averaged", "body": "The three mutual phase distances combine into one equivalent GMD.", "formula": f"({q(result.gmd_ab)} × {q(result.gmd_bc)} × {q(result.gmd_ca)})^(1/3) = {q(result.gmd)} m"},
        {"title": "Inductance", "body": "The ratio of phase spacing to inductive GMR determines magnetic energy storage.", "formula": f"L = 2 × 10^-7 ln({q(result.gmd)} / {q(result.gmr_l)}) = {q(result.L_mH_per_km)} mH/km"},
        {"title": "Capacitance", "body": "The same spacing compared with capacitive GMR determines electric charge storage.", "formula": f"C = 2π ε0 / ln({q(result.gmd)} / {q(result.gmr_c)}) = {q(result.C_uF_per_km)} μF/km"},
    ]
