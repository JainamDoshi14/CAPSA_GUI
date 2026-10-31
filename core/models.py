"""Typed models shared by the calculation engine and the user interface."""

from dataclasses import dataclass, field
import math


@dataclass(frozen=True)
class Conductor:
    phase: str
    x: float
    y: float
    r: float
    gmr_s: float

    def __post_init__(self) -> None:
        if self.phase not in {"A", "B", "C"}:
            raise ValueError("phase must be A, B, or C")
        if not all(math.isfinite(value) for value in (self.x, self.y, self.r, self.gmr_s)):
            raise ValueError("conductor coordinates, radius, and self GMR must be finite")
        if self.r <= 0 or self.gmr_s <= 0:
            raise ValueError("conductor radius and self GMR must be positive")


@dataclass(frozen=True)
class LineModel:
    conductors: list[Conductor]
    length_km: float = 1.0
    freq_hz: float = 50.0
    name: str = "Custom line"

    def __post_init__(self) -> None:
        if not math.isfinite(self.length_km) or self.length_km <= 0:
            raise ValueError("line length must be positive")
        if not math.isfinite(self.freq_hz) or self.freq_hz <= 0:
            raise ValueError("frequency must be positive")


@dataclass(frozen=True)
class PhaseResult:
    n: int
    gmr_l: float
    gmr_c: float


@dataclass(frozen=True)
class Result:
    gmd: float
    gmd_ab: float
    gmd_bc: float
    gmd_ca: float
    gmr_l: float
    gmr_c: float
    L_mH_per_km: float
    C_uF_per_km: float
    L_total_mH: float
    C_total_uF: float
    X_L_ohm_per_km: float
    X_C_ohm_per_km: float
    per_phase: dict[str, PhaseResult] = field(default_factory=dict)
