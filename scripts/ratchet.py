#!/usr/bin/env python3
"""ratchet.py — the shared SET-based paydown-only ratchet (single-source).

A recurring gate over ACCUMULATING DEBT — a census that should trend to 0 or
hold — is a RATCHET over a MATERIALIZED census: a baseline that pays down
monotonically. This is the SET form, shared by the sibling gates:
  · check_carrier_locality.py  — the live sanctioned-exemption set.
  · check_sumtype_ratchet.py   — the duplicate type-declaration set.
(set1_ratchet_cores.py is the COUNT form — count + denominator guard + a
census read from catalog.db; it keeps its specialised gate. This helper is the
factored core for the set-valued ratchets, per the rule of three.)

Semantics (identical to set1_ratchet_cores.census_gate's baseline compare):
  · no baseline yet   → record the current set, pass.
  · a NEW key         → REFUSE (debt may only be paid down, not grown).
  · a paid-down key   → AUTO-LOWER: rewrite the baseline, pass.
  · unchanged         → frozen at baseline, pass.
A SET (not a bare count) baseline also catches swap-gaming (remove one, add
another — the added key is refused).
"""
import os


def _write(path, keys):
    with open(path, "w") as fh:
        fh.write("".join(k + "\n" for k in sorted(keys)))


def _read(path):
    with open(path) as fh:
        return {ln.strip() for ln in fh if ln.strip()}


def set_ratchet(cur, baseline_path, label, quiet=False,
                noun="entries", refuse_hint=None):
    """Run the paydown-only ratchet over the census SET `cur` (str keys).
    Returns a process exit code: 0 = pass (frozen / recorded / paid down),
    1 = a NEW key appeared (debt grew). Writes/rewrites `baseline_path`."""
    cur = set(cur)
    if not os.path.exists(baseline_path):
        _write(baseline_path, cur)
        print(f"{label}: baseline recorded = {len(cur)} {noun}")
        return 0
    base = _read(baseline_path)
    added = cur - base
    if added:
        print(f"{label}: BROKEN — {len(added)} NEW {noun} "
              f"(this census is DEBT; it may only be PAID DOWN, not grown):")
        for k in sorted(added):
            print(f"    + {k}")
        if refuse_hint:
            print(f"  {refuse_hint}")
        return 1
    paid = base - cur
    if paid:
        _write(baseline_path, cur)
        print(f"{label}: baseline LOWERED {len(base)} -> {len(cur)} "
              f"({len(paid)} {noun} paid down)")
        for k in sorted(paid):
            print(f"    - {k}")
        return 0
    if not quiet:
        print(f"{label}: at baseline {len(base)} {noun} (frozen)")
    return 0
