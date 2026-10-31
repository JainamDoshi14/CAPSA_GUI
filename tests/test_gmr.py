import pytest

from core.gmr import stranded_gmr, stranded_gmr_ratio


def test_seven_strand_reference_ratio():
    assert stranded_gmr_ratio(7) == pytest.approx(2.1767, rel=1e-4)


@pytest.mark.parametrize("count", [1, 3, 7, 19, 37, 61, 91])
def test_supported_strand_count_returns_positive_gmr(count):
    assert stranded_gmr(count, 0.01) > 0


def test_invalid_strand_count_is_rejected():
    with pytest.raises(ValueError):
        stranded_gmr_ratio(0)


def test_nonpositive_strand_radius_is_rejected():
    with pytest.raises(ValueError):
        stranded_gmr(7, 0)
