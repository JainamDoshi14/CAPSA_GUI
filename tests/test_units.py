import pytest

from core.units import from_metres, to_metres


@pytest.mark.parametrize("value,unit,expected", [
    (1, "m", 1), (1, "ft", 0.3048), (1, "in", 0.0254),
    (1, "cm", 0.01), (1, "mil", 0.0000254),
])
def test_length_conversion(value, unit, expected):
    assert to_metres(value, unit) == pytest.approx(expected)


def test_circular_mil_area_converts_as_equivalent_diameter():
    assert to_metres(1_000_000, "cmil") == pytest.approx(0.0254)


def test_cmil_round_trips_as_equivalent_circular_diameter():
    assert from_metres(to_metres(1_000_000, "cmil"), "cmil") == pytest.approx(1_000_000)


def test_unknown_unit_is_rejected():
    with pytest.raises(ValueError):
        to_metres(1, "yards")
