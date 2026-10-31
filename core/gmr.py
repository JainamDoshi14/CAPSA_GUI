"""Geometric mean radius calculations for stranded and composite conductors."""

from collections.abc import Sequence
from math import atan2, exp, log, sqrt

from .models import Conductor


def stranded_gmr_ratio(num_strands: int) -> float:
    """Return GMR/r for the displayed compact hexagonally packed layout.

    Custom counts fill concentric hexagonal rings from the centre outwards.
    An incomplete final ring is filled clockwise in a stable order. The
    documented three-strand arrangement is an equilateral triangle.
    """
    points = stranded_layout(num_strands)
    if num_strands == 1:
        return exp(-0.25)
    if num_strands == 3:
        return exp(-0.25) ** (1.0 / 3.0) * (2.0 ** (2.0 / 3.0))

    log_product = 0.0
    for i, p in enumerate(points):
        for j in range(i + 1, len(points)):
            dx = p[0] - points[j][0]
            dy = p[1] - points[j][1]
            distance_over_r = sqrt(dx * dx + dy * dy)
            log_product += 2.0 * log(distance_over_r)
    log_product += num_strands * log(exp(-0.25))
    return exp(log_product / (num_strands * num_strands))


def stranded_layout(num_strands: int) -> list[tuple[float, float]]:
    """Return strand centre coordinates in units of the strand radius.

    The layout matches ``stranded_gmr_ratio``: 1 strand is centred, 3 form an
    equilateral triangle, and other counts fill the hexagonal lattice outward.
    Custom counts are limited to 200 to keep the pairwise GMR calculation
    responsive in the UI.
    """
    if not isinstance(num_strands, int) or isinstance(num_strands, bool) or not 1 <= num_strands <= 200:
        raise ValueError("strand count must be a whole number from 1 to 200")
    if num_strands == 1:
        return [(0.0, 0.0)]
    if num_strands == 3:
        return [(0.0, -2 / sqrt(3)), (-1.0, 1 / sqrt(3)), (1.0, 1 / sqrt(3))]

    points = [(0.0, 0.0)]
    remaining = num_strands - 1
    layer = 1
    while remaining:
        ring: list[tuple[float, float]] = []
        for q in range(-layer, layer + 1):
            for r in range(-layer, layer + 1):
                if max(abs(q), abs(r), abs(-q - r)) == layer:
                    ring.append((2 * q + r, sqrt(3) * r))
        ring.sort(key=lambda point: atan2(point[1], point[0]))
        selected = ring[:remaining]
        points.extend(selected)
        remaining -= len(selected)
        layer += 1
    return points


def stranded_gmr(num_strands: int, strand_radius: float) -> float:
    if strand_radius <= 0:
        raise ValueError("strand radius must be positive")
    return stranded_gmr_ratio(num_strands) * strand_radius


def composite_gmr(conductors: Sequence[Conductor], *, capacitance: bool = False) -> float:
    """Equivalent phase GMR using the full conductor-to-conductor product."""
    if not conductors:
        raise ValueError("at least one conductor is required")
    n = len(conductors)
    log_product = 0.0
    for i, first in enumerate(conductors):
        for j, second in enumerate(conductors):
            if i == j:
                distance = first.r if capacitance else first.gmr_s
            else:
                distance = sqrt((first.x - second.x) ** 2 + (first.y - second.y) ** 2)
                if distance <= 0:
                    raise ValueError("conductors in the same phase cannot occupy the same point")
            log_product += log(distance)
    return exp(log_product / (n * n))
