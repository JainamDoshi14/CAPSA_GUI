"""Length unit conversion helpers. Engine values are always in metres."""

import math

METRES_PER_UNIT = {
    "m": 1.0,
    "ft": 0.3048,
    "in": 0.0254,
    "cm": 0.01,
    "mm": 0.001,
    "mil": 0.0000254,
}


def to_metres(value: float, unit: str) -> float:
    """Convert a length to metres; ``cmil`` input is circular area.

    A circular-mil area corresponds to a diameter of sqrt(value) mils.
    For example, 1,272,000 cmil has a circular-equivalent diameter of
    sqrt(1,272,000) mil. This is useful for unit-entry fields but is not a
    substitute for a stranded conductor's measured outside diameter.
    """
    unit = unit.strip().lower()
    if unit == "cmil":
        if value < 0:
            raise ValueError("cmil area cannot be negative")
        return math.sqrt(value) * METRES_PER_UNIT["mil"]
    try:
        factor = METRES_PER_UNIT[unit]
    except KeyError as exc:
        raise ValueError(f"unsupported length unit: {unit}") from exc
    return value * factor


def from_metres(value: float, unit: str) -> float:
    """Convert metres to a length unit or equivalent circular mil area.

    For ``cmil``, the returned number is the area of a circle whose diameter
    equals the converted length. This is a convenience for conductor fields.
    """
    unit = unit.strip().lower()
    if unit == "cmil":
        return (value / METRES_PER_UNIT["mil"]) ** 2
    try:
        factor = METRES_PER_UNIT[unit]
    except KeyError as exc:
        raise ValueError(f"unsupported length unit: {unit}") from exc
    return value / factor
