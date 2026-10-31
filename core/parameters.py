"""Transmission-line inductance, capacitance, and reactance calculations."""

from collections import defaultdict
from math import log, pi

from .gmd import equivalent_gmd
from .gmr import composite_gmr
from .models import LineModel, PhaseResult, Result

EPSILON_0 = 8.8541878128e-12


def calculate_line(model: LineModel) -> Result:
    if not model.conductors:
        raise ValueError("add conductors before calculating")
    phases = defaultdict(list)
    for conductor in model.conductors:
        phases[conductor.phase].append(conductor)
    gmd, d_ab, d_bc, d_ca = equivalent_gmd(phases)
    phase_results = {
        name: PhaseResult(
            n=len(items),
            gmr_l=composite_gmr(items),
            gmr_c=composite_gmr(items, capacitance=True),
        )
        for name, items in phases.items()
    }
    # A transposed, balanced line uses the geometric mean of the three phase
    # self terms, including parallel circuits grouped by their phase label.
    gmr_l = (phase_results["A"].gmr_l * phase_results["B"].gmr_l * phase_results["C"].gmr_l) ** (1.0 / 3.0)
    gmr_c = (phase_results["A"].gmr_c * phase_results["B"].gmr_c * phase_results["C"].gmr_c) ** (1.0 / 3.0)
    if gmd <= gmr_l or gmd <= gmr_c:
        raise ValueError("phase spacing must exceed equivalent phase radius")

    l_h_per_m = 2e-7 * log(gmd / gmr_l)
    c_f_per_m = 2 * pi * EPSILON_0 / log(gmd / gmr_c)
    l_mh_per_km = l_h_per_m * 1e6
    c_uf_per_km = c_f_per_m * 1e9
    return Result(
        gmd=gmd,
        gmd_ab=d_ab,
        gmd_bc=d_bc,
        gmd_ca=d_ca,
        gmr_l=gmr_l,
        gmr_c=gmr_c,
        L_mH_per_km=l_mh_per_km,
        C_uF_per_km=c_uf_per_km,
        L_total_mH=l_mh_per_km * model.length_km,
        C_total_uF=c_uf_per_km * model.length_km,
        X_L_ohm_per_km=2 * pi * model.freq_hz * l_h_per_m * 1000,
        X_C_ohm_per_km=1 / (2 * pi * model.freq_hz * c_f_per_m * 1000),
        per_phase=phase_results,
    )
