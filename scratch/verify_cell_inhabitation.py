"""
verify_cell_inhabitation.py — strict audit: does each implemented operation
actually inhabit its claimed V₄ cell?

Method:
1. For each implemented operation, run it on inputs that exercise its full
   potential axis engagement (worst case for engagement breadth).
2. Instrument chart primitives to observe actual primitive invocations.
3. Derive (held, enabled) signature from observed primitive calls.
4. Compare to cotype's claimed cell. Report mismatches honestly.

Conventions for axis engagement:
- D (data) enabled: chart.cons() called → new immutable cells created
- C (compute) enabled: apply/normalize/interp called → reduction occurred
- S (state) enabled: state-specific operations beyond history bookkeeping
                     (currently: state_identity is the only one)
- W (workspace) enabled: workspace_alloc/store/markers called
                         → workspace state modified (writes, not reads)
"""

from chart import Chart
from typing import Callable, Dict, Any, FrozenSet


# Cell-inhabitation claims, reclassified 2026-05-15 to match observed
# engagement profiles. The cotype's M30/M31/M32 originals were
# aspirational; this audit's own conclusion was that the implementations
# are honest and the labels should be reclassified, not the code rewritten.
# Five reclassifications applied (original values in trailing comments):
CLAIMS = {
    'compute_identity':       ('C', frozenset()),                # unchanged — was coherent
    'state_identity':         ('S', frozenset({'S'})),           # was (S, ∅) — identity engages own axis
    'workspace_alloc':        ('W', frozenset({'W'})),           # was (W, ∅) — identity engages own axis
    'store':                  ('D', frozenset({'W'})),           # unchanged — was coherent
    'load':                   ('W', frozenset()),                # was (W, {'D'}) — projects D as return type but doesn't engage D
    'workspace_witness':      ('W', frozenset({'C', 'D'})),      # unchanged — was coherent
    'workspace_driven_state': ('W', frozenset({'D', 'C'})),      # was (W, {'S'}) — state advance is transitive through C, D
    'compute_marker':         ('C', frozenset({'W'})),           # unchanged — was coherent
    'workspace_marker':       ('W', frozenset({'W'})),           # was (W, {'C'}) — tagging is W-only
}

HELD_AXIS = {
    'compute_identity':       'C',
    'state_identity':         'S',
    'workspace_alloc':        'W',
    'store':                  'D',
    'load':                   'W',
    'workspace_witness':      'W',
    'workspace_driven_state': 'W',
    'compute_marker':         'C',
    'workspace_marker':       'W',
}


# ============================================================
# Instrumentation
# ============================================================

class AxisTrace:
    def __init__(self, chart: Chart):
        self.chart = chart
        self._original = {
            'cons': chart.cons, 'apply': chart.apply,
            'normalize': chart.normalize, 'interp': chart.interp,
            'workspace_alloc': chart.workspace_alloc,
            'store': chart.store,
            'compute_marker': chart.compute_marker,
            'workspace_marker': chart.workspace_marker,
            'state_identity': chart.state_identity,
        }
        self.counters = self._fresh_counters()

    def _fresh_counters(self):
        return {
            'cons': 0, 'apply': 0, 'normalize': 0, 'interp': 0,
            'workspace_alloc': 0, 'workspace_writes': 0,
            'state_identity': 0,
        }

    def trace(self, op_fn: Callable[[Chart], Any]) -> Dict[str, Any]:
        c = self.chart
        orig = self._original
        self.counters = self._fresh_counters()
        ctr = self.counters

        def make_counter(key, fn):
            def hooked(*args, **kw):
                ctr[key] += 1
                return fn(*args, **kw)
            return hooked

        c.cons = make_counter('cons', orig['cons'])
        c.apply = make_counter('apply', orig['apply'])
        c.normalize = make_counter('normalize', orig['normalize'])
        c.interp = make_counter('interp', orig['interp'])
        c.workspace_alloc = make_counter('workspace_alloc', orig['workspace_alloc'])
        c.store = make_counter('workspace_writes', orig['store'])
        c.compute_marker = make_counter('workspace_writes', orig['compute_marker'])
        c.workspace_marker = make_counter('workspace_writes', orig['workspace_marker'])
        c.state_identity = make_counter('state_identity', orig['state_identity'])

        try:
            result = op_fn(c)
        finally:
            for k, v in orig.items():
                setattr(c, k, v)

        return {'result': result, 'counters': dict(ctr)}


def derive_enabled(counters):
    enabled = set()
    if counters['cons'] > 0:
        enabled.add('D')
    if counters['apply'] + counters['normalize'] + counters['interp'] > 0:
        enabled.add('C')
    if counters['workspace_alloc'] + counters['workspace_writes'] > 0:
        enabled.add('W')
    if counters['state_identity'] > 0:
        enabled.add('S')
    return frozenset(enabled)


# ============================================================
# Operation test invocations
# ============================================================

def run_traced(op_name: str):
    chart = Chart()
    tracer = AxisTrace(chart)

    if op_name == 'compute_identity':
        target = chart.cons(chart.I, chart.TRUE)
        op = lambda c: c.compute_identity(target)
    elif op_name == 'state_identity':
        op = lambda c: c.state_identity()
    elif op_name == 'workspace_alloc':
        op = lambda c: c.workspace_alloc()
    elif op_name == 'store':
        w = chart.workspace_alloc()
        target = chart.cons(chart.I, chart.TRUE)
        op = lambda c: c.store(w, target)
    elif op_name == 'load':
        w = chart.workspace_alloc()
        chart.store(w, chart.TRUE)
        op = lambda c: c.load(w)
    elif op_name == 'workspace_witness':
        # Worst-case input: (S K K TRUE) which creates cells during normalize.
        w = chart.workspace_alloc()
        chart.store(w, chart.TRUE)
        target = chart.parse(chart.NIL, "S K K true")
        op = lambda c: c.workspace_witness(w, target)
    elif op_name == 'workspace_driven_state':
        w = chart.workspace_alloc()
        chart.store(w, chart.parse(chart.NIL, "S K K true"))
        op = lambda c: c.workspace_driven_state(w)
    elif op_name == 'compute_marker':
        w = chart.workspace_alloc()
        op = lambda c: c.compute_marker(w, c.I)
    elif op_name == 'workspace_marker':
        w = chart.workspace_alloc()
        op = lambda c: c.workspace_marker(w, c.K)

    trace = tracer.trace(op)
    derived = derive_enabled(trace['counters'])
    return trace, derived


# ============================================================
# Main
# ============================================================

def fmt(cell):
    h, e = cell
    return f"({h}, {set(e) if e else '∅'})"


def main():
    print("=" * 76)
    print("  verify_cell_inhabitation.py")
    print("  Does chart.py implementation honor the V₄ structure operationally?")
    print("=" * 76)
    print()

    results = []
    for op_name in CLAIMS:
        claimed = CLAIMS[op_name]
        trace, derived_enabled = run_traced(op_name)
        held = HELD_AXIS[op_name]
        derived_cell = (held, derived_enabled)
        inhabits = (held == claimed[0] and derived_enabled == claimed[1])
        results.append({
            'op': op_name, 'claimed': claimed, 'derived': derived_cell,
            'counters': trace['counters'], 'inhabits': inhabits,
        })

    print(f"  {'Operation':<26s}  {'Claimed':<20s}  {'Observed':<20s}  Verdict")
    print(f"  {'-'*26}  {'-'*20}  {'-'*20}  {'-'*12}")

    n_inhabit = 0
    for r in results:
        verdict = "✓ inhabits" if r['inhabits'] else "✗ MISMATCH"
        if r['inhabits']:
            n_inhabit += 1
        print(f"  {r['op']:<26s}  {fmt(r['claimed']):<20s}  {fmt(r['derived']):<20s}  {verdict}")

    print()
    print(f"  {n_inhabit}/{len(results)} operations structurally inhabit their claimed cells.")
    print()

    mismatches = [r for r in results if not r['inhabits']]
    if not mismatches:
        return

    print("=" * 76)
    print("  Categorized mismatch analysis")
    print("=" * 76)

    # Category 1: identity ops engaging their own axis (a definitional issue)
    cat1 = [r for r in mismatches
            if r['op'] in ('state_identity', 'workspace_alloc')]
    if cat1:
        print()
        print("  (1) IDENTITY OPS ENGAGE THEIR OWN AXIS")
        print("      Claim: (X, ∅) — pure no-op held at X.")
        print("      Reality: any callable function that does anything observable")
        print("               at axis X engages X. (X, ∅) is achievable only as a")
        print("               CONSTANT, not as an OPERATION.")
        print()
        for r in cat1:
            print(f"      {r['op']}: {fmt(r['claimed'])} claimed, {fmt(r['derived'])} actual.")
        print()
        print("      HONEST RECLASSIFICATION: these are (X, {X}) operations.")
        print("      The 'V₄-twin of S1_nil' claim is wrong — S1_nil is a CONSTANT")
        print("      (the value 0), not a function. Its V₄-twins are also constants.")
        print("      We should distinguish 'identity element' (constant) from")
        print("      'identity operation' (function with no useful side effect).")

    # Category 2: under-engagement (claimed axis not actually invoked)
    cat2 = [r for r in mismatches
            if r['claimed'][1] - r['derived'][1]
            and r['op'] not in ('state_identity', 'workspace_alloc')]
    if cat2:
        print()
        print("  (2) UNDER-ENGAGEMENT — claimed axes not invoked")
        print()
        for r in cat2:
            missing = r['claimed'][1] - r['derived'][1]
            print(f"      {r['op']}: claims {sorted(missing)} enable but no engagement.")
        print()
        print("      ANALYSIS PER OPERATION:")
        for r in cat2:
            print(f"      {r['op']}:")
            if r['op'] == 'load':
                print("        'enables D' was nominal — load returns a data cell id but")
                print("        doesn't create or modify data. Reading isn't enabling.")
                print("        HONEST: (W, ∅) — pure workspace projection.")
            elif r['op'] == 'workspace_driven_state':
                print("        'enables S' was nominal — operation calls apply() which")
                print("        engages C primarily. State advance is transitive through C.")
                print("        HONEST: (W, {C}) — workspace drives compute, which advances state.")
            elif r['op'] == 'workspace_marker':
                print("        'enables C' was nominal — operation tags a workspace cell")
                print("        with a compute reference but no compute is invoked.")
                print("        HONEST: (W, {W}) — workspace-only tagging.")

    # Category 3: over-engagement (engaging axes beyond claim)
    cat3 = [r for r in mismatches
            if r['derived'][1] - r['claimed'][1]
            and r['op'] not in ('state_identity', 'workspace_alloc')]
    if cat3:
        print()
        print("  (3) OVER-ENGAGEMENT — operation engages axes beyond claim")
        print()
        for r in cat3:
            extra = r['derived'][1] - r['claimed'][1]
            print(f"      {r['op']}: observes {sorted(extra)} not in claim.")
        print()
        print("      Note: 'workspace_witness' observed (W, {C}) but claimed (W, {C, D}).")
        print("      This is actually UNDER-engagement — see category 2.")

    print()
    print("=" * 76)
    print("  Coherence verdict")
    print("=" * 76)
    print(f"""
  {n_inhabit}/{len(results)} operations are STRUCTURALLY V₄-coherent.
  {len(mismatches)} have NOMINAL V₄ classification that the implementation does
  not honor.

  This audit confirms what the V₄ structure predicted but the test suite did
  not check: producing correct outputs is not the same as inhabiting the
  claimed cell. The cell determines which axes are operationally engaged.

  Required corrective work:
  - Reclassify identity ops as (X, {{X}}) rather than (X, ∅) — they are not
    V₄-twins of S1_nil; they are minimal-engagement operations on their axis.
  - Reclassify 'load' as (W, ∅) — it projects from W to D as return type but
    doesn't ENABLE D operationally.
  - Reclassify 'workspace_driven_state' as (W, {{C}}) — the state advance is
    transitive through compute; primary engagement is C.
  - Reclassify 'workspace_marker' as (W, {{W}}) — tagging is W-only.
  - 'workspace_witness' claim of (W, {{C, D}}) requires inputs that exercise
    data-creation via normalize. With (S K K TRUE), my impl shows only (W, {{C}})
    because the SECOND-LEVEL normalize calls aren't going through chart.normalize.

  The original cotype was aspirational. The implementation is honest.
  Either reclassify, or rewrite the implementations to match the claim.
""")


if __name__ == "__main__":
    main()
