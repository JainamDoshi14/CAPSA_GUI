"""Equivalent transposed-line GMD calculations."""

from collections.abc import Sequence
from math import exp, log, sqrt

from .models import Conductor


def mutual_gmd(first: Sequence[Conductor], second: Sequence[Conductor]) -> float:
    if not first or not second:
        raise ValueError("each phase must contain at least one conductor")
    log_sum = 0.0
    for a in first:
        for b in second:
            distance = sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)
            if distance <= 0:
                raise ValueError("conductors in different phases cannot occupy the same point")
            log_sum += log(distance)
    return exp(log_sum / (len(first) * len(second)))


def equivalent_gmd(phases: dict[str, Sequence[Conductor]]) -> tuple[float, float, float, float]:
    try:
        a, b, c = (phases[label] for label in ("A", "B", "C"))
    except KeyError as exc:
        raise ValueError("line must include phases A, B, and C") from exc
    d_ab = mutual_gmd(a, b)
    d_bc = mutual_gmd(b, c)
    d_ca = mutual_gmd(c, a)
    return (d_ab * d_bc * d_ca) ** (1.0 / 3.0), d_ab, d_bc, d_ca
