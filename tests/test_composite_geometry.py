import pytest

from core.gmd import equivalent_gmd, mutual_gmd
from core.gmr import composite_gmr
from core.models import Conductor


def _wire(phase, x, y=0.0, radius=0.02, gmr=0.015):
    return Conductor(phase, x, y, radius, gmr)


def test_two_wire_composite_gmr_matches_bundle_shortcut():
    bundle = [_wire("A", -1), _wire("A", 1)]
    assert composite_gmr(bundle) == pytest.approx((0.015 * 2) ** 0.5)
    assert composite_gmr(bundle, capacitance=True) == pytest.approx((0.02 * 2) ** 0.5)


def test_mutual_gmd_is_geometric_mean_for_composite_phases():
    first = [_wire("A", 0), _wire("A", 2)]
    second = [_wire("B", 10), _wire("B", 14)]
    expected = (10 * 14 * 8 * 12) ** 0.25
    assert mutual_gmd(first, second) == pytest.approx(expected)


def test_equivalent_gmd_for_horizontal_three_phase_line():
    phases = {
        "A": [_wire("A", 0)],
        "B": [_wire("B", 10)],
        "C": [_wire("C", 20)],
    }
    gmd, d_ab, d_bc, d_ca = equivalent_gmd(phases)
    assert (d_ab, d_bc, d_ca) == pytest.approx((10, 10, 20))
    assert gmd == pytest.approx((2000) ** (1 / 3))


def test_conductor_rejects_nonfinite_coordinates():
    with pytest.raises(ValueError, match="finite"):
        _wire("A", float("inf"))
