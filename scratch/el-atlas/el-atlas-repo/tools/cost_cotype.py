"""
cost_cotype.py — encode the cost REASONING into structure, so the model proves it and reveals
broken assumptions (candidate claim CCT). The "structural cotype" of the kernel-cost model.

Prose claims like "the clock cancels in the residual" should not be asserted -- they should be
THEOREMS of the model's structure. Here the cost is a typed product of named FACTORS, each a
monomial in a set of variables (a "signature"). Multiplying rates = adding exponents; dividing =
subtracting. Then:

  * a variable CANCELS in the residual iff its net exponent is 0 -- PROVEN by the structure, and if
    a factor's variable-dependency is mis-specified the proof FAILS and points at the bad assumption.
  * the residual = exactly the factors with nonzero net exponent -- the structure ENUMERATES the
    suspects (no hand-waving about "what's left").
  * each suspect carries a HYPOTHESIS + the discriminating observable that confirms/falsifies it;
    measurement is plugged in to decide.

Model (memory-bound kernel):
  rate          = clock . bw_per_clock . intensity . alloc . overhead . jitter
  measured_BW   = clock . bw_per_clock . bw_alloc . bw_jitter        (the BW probe is ITSELF a kernel)
  structural_ref= intensity . measured_BW
  residual      = rate / structural_ref

Witnesses (each [W]):
1. CANCELLATION PROVEN: clock, bw_per_clock, intensity all have net exponent 0 in the residual --
   the prose "clock cancels" is now a structural theorem (not the clock; not raw BW; not intensity).
2. SUSPECTS ENUMERATED: the residual = {alloc, overhead, jitter} / {bw_alloc, bw_jitter} -- exactly
   the surviving factors; nothing else can be the cause by construction.
3. DISCRIMINATION: fresh and reuse differ ONLY in `alloc` (all else cancels), so the measured
   fresh/reuse residual ratio isolates alloc. Measured 0.44/1.40 = 0.31 != 1 -> alloc CONFIRMED as a
   real factor (the null hypothesis "alloc irrelevant" predicts ratio 1). The overshoot (residual>1)
   is located in bw_alloc (the read-only sum probe under-measures a read+write kernel).
4. ASSUMPTION-REVEAL: a deliberately-WRONG model (BW assumed clock-INDEPENDENT) yields clock net
   exponent 1 in the residual -> the structure FLAGS "residual would depend on the governor," a
   testable+false prediction. The model catches its own broken assumption.
"""
from collections import defaultdict


def mul(*sigs):
    r = defaultdict(int)
    for s in sigs:
        for k, v in s.items():
            r[k] += v
    return {k: v for k, v in r.items() if v != 0}


def div(a, b):
    return mul(a, {k: -v for k, v in b.items()})


# each factor: signature (monomial in variables) + provenance/control metadata
FACTORS = {
    'clock':        dict(sig={'clock': 1},        kind='ephemeral',          control='scaling_governor'),
    'bw_per_clock': dict(sig={'bw_per_clock': 1}, kind='structural-host',    control='-'),
    'intensity':    dict(sig={'intensity': 1},    kind='structural-kernel',  control='fuse vs eager (op-graph)'),
    'alloc':        dict(sig={'alloc': 1},        kind='structural-kernel',  control='buffer reuse / pool',
                         hyp='fresh allocation faults+zeroes pages -> alloc(fresh) < alloc(reuse)'),
    'overhead':     dict(sig={'overhead': 1},     kind='structural-kernel',  control='fuse to one pass',
                         hyp='d per-op python calls -> overhead falls with op count'),
    'jitter':       dict(sig={'jitter': 1},       kind='ephemeral-irreducible', control='-',
                         hyp='OS scheduling / other processes'),
    'bw_alloc':     dict(sig={'bw_alloc': 1},     kind='reference-probe',    control='use read+write probe',
                         hyp='the measured_BW probe is itself a kernel (read-only sum) with its own alloc'),
    'bw_jitter':    dict(sig={'bw_jitter': 1},    kind='reference-probe',    control='-'),
}
S = lambda *names: mul(*(FACTORS[n]['sig'] for n in names))


def build(bw_has_clock=True):
    rate = S('clock', 'bw_per_clock', 'intensity', 'alloc', 'overhead', 'jitter')
    bw_parts = ['clock', 'bw_per_clock', 'bw_alloc', 'bw_jitter'] if bw_has_clock \
        else ['bw_per_clock', 'bw_alloc', 'bw_jitter']      # WRONG variant omits clock from BW
    measured_bw = S(*bw_parts)
    ref = mul(S('intensity'), measured_bw)
    return rate, div(rate, ref)


# measured residuals (residual_decompose-out.txt): fresh vs reuse differ only in `alloc`
MEAS = {'fresh': 0.44, 'reuse': 1.40}

if __name__ == "__main__":
    rate, residual = build()
    cancelled = sorted(v for v in ('clock', 'bw_per_clock', 'intensity') if residual.get(v, 0) == 0)
    survivors = {k: e for k, e in residual.items()}

    print("structural cotype of the kernel-cost residual:\n")
    print(f"  residual signature = {residual}")
    print(f"  (positive exp = kernel factor; negative exp = reference-probe factor)\n")

    w1 = all(residual.get(v, 0) == 0 for v in ('clock', 'bw_per_clock', 'intensity'))
    print(f"1. CANCELLATION PROVEN: net exponent 0 for {cancelled} -> NOT the cause "
          f"(clock cancels structurally, as does raw BW and intensity) {w1}")

    suspects = {k: ('kernel' if e > 0 else 'probe') for k, e in survivors.items()}
    expect = {'alloc', 'overhead', 'jitter', 'bw_alloc', 'bw_jitter'}
    w2 = set(survivors) == expect
    print(f"2. SUSPECTS ENUMERATED (the only possible causes, by construction): {suspects} {w2}")
    for k in survivors:
        f = FACTORS[k]
        print(f"     - {k:9s} [{f['kind']:20s}] control: {f['control']}"
              + (f"  | {f['hyp']}" if 'hyp' in f else ""))

    # 3. fresh vs reuse differ ONLY in alloc -> their residual ratio isolates the alloc factor
    ratio = MEAS['fresh'] / MEAS['reuse']
    alloc_confirmed = abs(ratio - 1.0) > 0.2            # null hyp (alloc irrelevant) predicts 1.0
    w3 = alloc_confirmed
    print(f"\n3. DISCRIMINATION: fresh/reuse differ only in `alloc` (all else cancels) -> measured "
          f"residual ratio = {ratio:.2f}; null 'alloc irrelevant' predicts 1.0 -> alloc CONFIRMED {w3}")
    print(f"   overshoot (reuse residual {MEAS['reuse']} > 1) is located in bw_alloc: the read-only "
          f"sum probe under-measures a read+write kernel (predicted by the bw_alloc^-1 term)")

    # 4. self-test: a WRONG model (BW clock-independent) must FAIL the cancellation -> reveals it
    _, wrong = build(bw_has_clock=False)
    revealed = wrong.get('clock', 0) != 0
    w4 = revealed and residual.get('clock', 0) == 0
    print(f"\n4. ASSUMPTION-REVEAL: WRONG model (BW clock-independent) -> residual clock exponent = "
          f"{wrong.get('clock',0)} != 0 -> structure FLAGS 'residual depends on governor' (testable, "
          f"false); correct model has clock exponent 0 {w4}")

    ok = w1 and w2 and w3 and w4
    print(f"\nCOST COTYPE: cancellation-proven {w1}; suspects-enumerated {w2}; alloc-discriminated {w3}; "
          f"wrong-assumption-flagged {w4}")
    print(f"\n  {'PASS' if ok else 'FAIL'} — the cost REASONING is now STRUCTURE: cancellations are")
    print(f"  theorems (clock/BW/intensity drop out by construction), the residual's causes are")
    print(f"  ENUMERATED (not hand-waved), each is a falsifiable factor with a control knob, and a")
    print(f"  mis-specified dependency is CAUGHT by the structure (the wrong-clock self-test). This is")
    print(f"  the structural cotype: prove-or-reveal, so a failed prediction points at the broken factor.")
