import pytest

from core.parameters import calculate_line
from core.presets import get_presets


@pytest.mark.parametrize(
    "key,expected_l,expected_c",
    [
        ("Q2", 1.38, 0.0083),
        ("Q3", 1.0588, 0.0107),
        ("Q4", 0.8892, 0.01267),
        ("Q5", 0.4491, 0.0254),
        ("Q6", 0.6836, 0.0168),
    ],
)
def test_published_single_circuit_regression_values(key, expected_l, expected_c):
    result = calculate_line(get_presets()[key].model)
    assert result.L_mH_per_km == pytest.approx(expected_l, rel=0.01)
    assert result.C_uF_per_km == pytest.approx(expected_c, rel=0.01)


@pytest.mark.parametrize("key", ["Q2", "Q3", "Q4", "Q5", "Q6"])
def test_every_preset_is_a_valid_three_phase_line(key):
    preset = get_presets()[key]
    result = calculate_line(preset.model)
    assert result.gmd > 0
    assert result.gmr_l > 0
    assert result.gmr_c > 0
    assert result.L_mH_per_km > 0
    assert result.C_uF_per_km > 0
    assert set(result.per_phase) == {"A", "B", "C"}


def test_total_parameters_scale_with_line_length():
    preset = get_presets()["Q2"]
    base = calculate_line(preset.model)
    from dataclasses import replace

    long_line = calculate_line(replace(preset.model, length_km=125.0))
    assert long_line.L_total_mH == pytest.approx(base.L_mH_per_km * 125)
    assert long_line.C_total_uF == pytest.approx(base.C_uF_per_km * 125)
