"""Reference problems Q2-Q6 represented as explicit SI conductor layouts."""

from dataclasses import dataclass
from .models import Conductor, LineModel
from .units import to_metres


@dataclass(frozen=True)
class Preset:
    key: str
    title: str
    model: LineModel
    reference: str


def _conductor(phase: str, x: float, y: float, diameter: float, gmr: float, unit: str, conductor_unit: str) -> Conductor:
    return Conductor(phase, to_metres(x, unit), to_metres(y, unit), to_metres(diameter / 2, conductor_unit), to_metres(gmr, conductor_unit))


def _line(key: str, title: str, specs: list[tuple[str, float, float, float, float]], unit: str, reference: str, freq_hz: float = 60.0, conductor_unit: str | None = None) -> Preset:
    conductor_unit = conductor_unit or unit
    conductors = [_conductor(phase, x, y, diameter, gmr, unit, conductor_unit) for phase, x, y, diameter, gmr in specs]
    return Preset(key, title, LineModel(conductors, length_km=1.0, freq_hz=freq_hz, name=title), reference)


def _square_bundle(phase: str, x: float, y: float, spacing: float, diameter: float, gmr: float, unit: str) -> list[tuple[str, float, float, float, float]]:
    half = spacing / 2
    return [
        (phase, x - half, y - half, diameter, gmr),
        (phase, x - half, y + half, diameter, gmr),
        (phase, x + half, y - half, diameter, gmr),
        (phase, x + half, y + half, diameter, gmr),
    ]


def get_presets() -> dict[str, Preset]:
    """Return fresh Q2-Q6 preset models; all stored coordinates are converted to SI."""
    result: dict[str, Preset] = {}

    # Examples 4.2-4.3 use 35 ft adjacent spacing and 70 ft outer spacing.
    result["Q2"] = _line("Q2", "Example 4.2 — 500 kV Bittern", [
        ("A", 0, 0, 1.345, 0.5328), ("B", 35, 0, 1.345, 0.5328), ("C", 70, 0, 1.345, 0.5328),
    ], "ft", "Example 4.2; textbook values: L≈1.38 mH/km, C≈0.0083 μF/km", conductor_unit="in")

    # Rook two-wire bundles sit on a vertical line through each phase center.
    q3: list[tuple[str, float, float, float, float]] = []
    for phase, x in (("A", 0.0), ("B", 35.0), ("C", 70.0)):
        q3.extend(((phase, x, -9 / 12, 0.977, 0.3924), (phase, x, 9 / 12, 0.977, 0.3924)))
    result["Q3"] = _line("Q3", "Example 4.3 — two-conductor Rook bundles", q3, "ft", "Example 4.3; textbook values: L≈1.0588 mH/km, C≈0.0107 μF/km", conductor_unit="in")

    # Rail four-conductor square bundles, 44.5 ft phase-center spacing.
    q4 = []
    for phase, x in (("A", 0.0), ("B", 44.5), ("C", 89.0)):
        q4.extend(_square_bundle(phase, x, 0, 46 / 30.48, 2.959 / 30.48, 1.173 / 30.48, "ft"))
    result["Q4"] = _line("Q4", "Example 4.4 — 735 kV Rail bundles", q4, "ft", "Example 4.4; textbook values: L≈0.8892 mH/km, C≈0.01267 μF/km")

    # Example 4.5: mirrored vertical double circuit; phase-center gaps are
    # S11/S22/S33 horizontally and H12/H23 vertically, as printed in Fig. 4.22.
    q5 = []
    sites = (("A", 0.0, 13.5), ("B", 0.0, 6.5), ("C", 0.0, 0.0),
             ("C", 11.0, 13.5), ("B", 16.5, 6.5), ("A", 12.5, 0.0))
    for phase, x, y in sites:
        q5.extend(((phase, x - 0.2286, y, 1.427, 0.564), (phase, x + 0.2286, y, 1.427, 0.564)))
    result["Q5"] = _line("Q5", "Example 4.5 — double-circuit Bobolink bundles", q5, "m", "Example 4.5; dimensions transcribed from Fig. 4.22", conductor_unit="in")

    # Example 4.6 uses the abc-a'b'c' arrangement in Fig. 4.23.
    # The 9 m gap is between the two circuits; no bundle is described in PRD.
    result["Q6"] = _line("Q6", "Example 4.6 — double-circuit Dove", [
        ("A", 0.0, 0, 0.927, 0.3768), ("B", 8.0, 0, 0.927, 0.3768), ("C", 16.0, 0, 0.927, 0.3768),
        ("A", 25.0, 0, 0.927, 0.3768), ("B", 33.0, 0, 0.927, 0.3768), ("C", 41.0, 0, 0.927, 0.3768),
    ], "m", "Example 4.6; phase order interpreted from Fig. 4.23", conductor_unit="in")
    return result


PRESETS = get_presets()
