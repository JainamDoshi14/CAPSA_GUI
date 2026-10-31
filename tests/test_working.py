from core.parameters import calculate_line
from core.presets import PRESETS
from core.working import generate_working_markdown, generate_working_text


def test_q4_report_includes_substituted_calculation_and_final_values():
    model = PRESETS["Q4"].model
    result = calculate_line(model)
    report = generate_working_markdown(model, result)

    assert "Example 4.4" in report
    assert "D_{AB}" in report and "GMD" in report
    assert "0.889" in report
    assert "0.012" in report
    assert "Reactance" in report


def test_text_export_removes_markdown_and_keeps_plain_equations():
    model = PRESETS["Q4"].model
    result = calculate_line(model)
    report = generate_working_text(model, result)

    assert "#" not in report
    assert "**" not in report
    assert "ohm/km" in report
    assert "L_total" in report
