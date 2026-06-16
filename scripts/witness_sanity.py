#!/usr/bin/env python3
"""witness_sanity.py — Δ-A2: the witness-sanity CONTRACT for jea_*/el-atlas pilot scripts.

The recurring class (G9 escalation, ≥4x): a pilot prints PASS while a COMPARISON or DEPENDENCY is rigged.
The provenance measure (jea_provenance.md) fires on INPUTS only; it did NOT catch these, because they are
failures of the witness/comparison STRUCTURE, not of an input's value:
  - Δ-A1 / fstar=0     : a ratio compared two quantities in DIFFERENT UNITS (PCIe GB/s vs iMC bytes/s).
  - Δ-F1               : a binding-edge probe relaxed a SUPERSET edge (iMC ⊇ PCIe) -> incomparable gains.
  - Δ-F2 / circular W3 : a "prediction" witness equalled its own calibration input (an identity, not a test).

This module is a callable contract, not a static linter (the failures are semantic). Pilots IMPORT it and
assert in their witness sections; the assertions raise WitnessViolation on a rigged witness, so a rigged
PASS cannot print. It is ADVISORY (a pilot may opt out with a documented reason) -- the binding layer for
pilot scripts, one rung below a pre-commit gate, per the G9 ladder.

The three helpers map 1:1 to the three historical bugs; __main__ is a REGRESSION that reconstructs each bug
and proves the gate fires (and passes the fixed form).
"""
import math


class WitnessViolation(AssertionError):
    pass


def same_scale(name_a, a, name_b, b, max_decades=4):
    """Two quantities combined in a RATIO (a/(a+b), a vs b) must share units -- within max_decades orders
    of magnitude. Catches the Δ-A1 unit mismatch (g_gpu~15.75 GB/s vs g_cpu~30e9 bytes/s -> fstar≈0).
    max_decades=4 is a JUSTIFIED net-positive GUARD (Δ-J5 audit), not a magic perf constant: two same-unit
    quantities meaningfully combined in a ratio rarely span >10^4 (the Δ-A1 bug was 10^9); the cost of a rare
    false-positive on a genuinely wide-dynamic-range ratio is far less than the unit-bug it catches. Pluggable."""
    if a <= 0 or b <= 0:
        return
    d = abs(math.log10(a) - math.log10(b))
    if d > max_decades:
        raise WitnessViolation(
            f"scale mismatch: {name_a}={a:.3g} vs {name_b}={b:.3g} differ by {d:.1f} decades "
            f"(>{max_decades}) -- a units bug? (the Δ-A1 fstar=0 trap: GB/s vs bytes/s)")
    return d


def single_edge_gains(base_value, base_state, edge_overrides, eval_fn):
    """Build a sensitivity/binding-edge gains dict where each edge's gain comes from relaxing EXACTLY ONE
    state key -- disjoint BY CONSTRUCTION, so no relaxation can be a SUPERSET of another (the Δ-F1 bug:
    'iMC' relaxed dma AND igpu while 'PCIe' relaxed only dma, so iMC could never lose). Each override must
    touch exactly one key, else WitnessViolation. Returns {edge: eval_fn(state⊕override) - base_value}."""
    gains = {}
    for name, ov in edge_overrides.items():
        if len(ov) != 1:
            raise WitnessViolation(
                f"edge '{name}' relaxes {len(ov)} keys {list(ov)}; a comparable binding-edge probe relaxes "
                f"exactly ONE edge per candidate (the Δ-F1 superset bug). Split into single-edge candidates.")
        st = dict(base_state); st.update(ov)
        gains[name] = eval_fn(st) - base_value
    return gains


def not_calibration_identity(witness, calibration, label, eps=1e-9):
    """A witness presented as a PREDICTION must not be numerically equal to its own calibration input.
    Catches the Δ-F2 circular W3 (total_time reconstructed == measured because tau:=measured-launch at
    gnorm=1 -- an identity, not a prediction). If they're equal, the caller must either hold out a real
    test point or LABEL the witness an identity (and call this with the identity intentionally absent)."""
    if abs(witness - calibration) <= eps:
        raise WitnessViolation(
            f"{label}: witness {witness:.6g} == calibration {calibration:.6g} within {eps:g} -> this is an "
            f"IDENTITY, not a prediction. Use a held-out point, or label it an identity (don't claim a match).")


if __name__ == "__main__":
    print("Δ-A2 witness-sanity contract -- REGRESSION against the 3 historical bugs it must catch\n")
    results = []

    # Bug 1 (Δ-A1): ratio across units. Fire on mixed units; pass on consistent units.
    try:
        same_scale("g_gpu(GB/s)", 15.75, "g_cpu(bytes/s)", 30.4e9); fired = False
    except WitnessViolation:
        fired = True
    ok1 = fired and (same_scale("g_gpu", 15.75e9, "g_cpu", 30.4e9) is not None)
    results.append(("same_scale catches GB/s-vs-bytes/s (Δ-A1), passes consistent units", ok1))

    # Bug 2 (Δ-F1): superset perturbation. The OLD binding_edge relaxed 2 keys for 'iMC', 1 for 'PCIe'.
    base_state = dict(dma=True, igpu=True, T=90.0, link=1.0)
    eval_fn = lambda st: -(st['T']) + (0 if st['dma'] else 8) + (0 if st['igpu'] else 13) + (0 if st['link'] < 1 else 0)
    try:  # buggy: 'iMC' relaxes BOTH dma and igpu -> superset of 'PCIe' (dma only)
        single_edge_gains(0.0, base_state, {"iMC": {"dma": False, "igpu": False}, "PCIe": {"dma": False}}, eval_fn)
        fired = False
    except WitnessViolation:
        fired = True
    fixed = single_edge_gains(0.0, base_state,
                              {"iMC/iGPU": {"igpu": False}, "PCIe": {"dma": False}, "thermal": {"T": 46.0}}, eval_fn)
    ok2 = fired and set(fixed) == {"iMC/iGPU", "PCIe", "thermal"}
    results.append(("single_edge_gains catches the superset relaxation (Δ-F1), builds disjoint gains", ok2))

    # Bug 3 (Δ-F2): circular witness. total_time(gnorm=1) reconstructs measured exactly.
    measured = 3.30; tau = measured - 0.05; total_time_gnorm1 = 0.05 + tau / 1.0   # == measured by construction
    try:
        not_calibration_identity(total_time_gnorm1, measured, "W3 deep-narrow"); fired = False
    except WitnessViolation:
        fired = True
    # a genuine held-out prediction (gnorm=0.4) is NOT an identity -> must pass
    held_out = 0.05 + tau / 0.4
    try:
        not_calibration_identity(held_out, measured, "W3 held-out"); passed = True
    except WitnessViolation:
        passed = False
    ok3 = fired and passed
    results.append(("not_calibration_identity catches the circular W3 (Δ-F2), passes a held-out point", ok3))

    for desc, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {desc}")
    allok = all(ok for _, ok in results)
    print(f"\n  {'PASS' if allok else 'FAIL'} — the contract fires on all 3 historical rigged-witness bugs")
    print(f"  and passes their fixed forms. Pilots import {{same_scale, single_edge_gains,")
    print(f"  not_calibration_identity}} and assert in their witness sections; a rigged PASS then cannot print.")
