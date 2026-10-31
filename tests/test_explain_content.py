from core.explain_content import explain_result, story_steps
from core.parameters import calculate_line
from core.presets import PRESETS


def test_explanation_substitutes_q4_results_and_supports_both_core_metrics():
    model = PRESETS["Q4"].model
    result = calculate_line(model)

    gmd = explain_result("gmd", model, result)
    inductance = explain_result("inductance", model, result)
    assert "17.089" in gmd["substitution"]
    assert "0.88912" in inductance["substitution"]
    assert "phase-to-phase" in gmd["what"]
    assert "ln(" in inductance["formula"]


def test_story_has_five_reportable_steps():
    model = PRESETS["Q4"].model
    steps = story_steps(model, calculate_line(model))

    assert len(steps) == 5
    assert steps[0]["title"] == "Your setup"
    assert steps[-1]["title"] == "Capacitance"
    assert all(step["formula"] for step in steps)
