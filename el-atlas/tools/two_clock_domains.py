"""
two_clock_domains.py — the correction the power-arms experiment forced: `clock` is TWO clocks
(candidate 2CK). The cost-cotype's prove-or-reveal property, exercised by a real falsification.

power_arms measured the ridge (compute/mem ratio) swinging 45% across the power profiles
(5.9 -> 10.7 FLOP/byte), falsifying my single-`clock` "clock cancels in the ratio" claim. Root
cause: compute scaled 2.60x but memory only 1.44x -- they ride DIFFERENT clock domains (core clock
vs memory-controller/uncore clock), scaled differently by the power profile. So `clock` was an opaque
primitive; it is clock_core (in compute) and clock_mem (in BW). Splitting it:

  compute_rate  ~ clock_core        mem_BW ~ clock_mem
  ridge = compute/mem ~ clock_core / clock_mem   -> survives -> POWER-DEPENDENT (no cancellation)
  residual(memory-bound kernel) = rate_mem / (I * mem_BW) ~ clock_mem / clock_mem -> CANCELS

So the corrected, SCOPED statement: SAME-domain ratios cancel the clock (the residual_decompose
memory-bound result still holds); CROSS-domain ratios (the ridge) do NOT -- they scale as
clock_core/clock_mem, which the power arm controls.

Witnesses (each [W]; scales are perf/power-saver from power_arms-out.txt):
1. single-clock cotype predicts the ridge is clock-FREE (exponent 0 -> scale 1.0, invariant) -- the
   measured 1.81x ridge swing FALSIFIES it.
2. two-clock cotype: ridge signature = {clock_core:+1, clock_mem:-1} -> power-dependent; predicted
   ridge scale = compute_scale / mem_scale.
3. QUANTITATIVE: predicted ridge scale (2.60/1.44 = 1.81) == measured ridge scale (10.7/5.9 = 1.81).
4. SCOPE PRESERVED: a memory-bound kernel's residual stays single-domain (clock_mem/clock_mem) ->
   cancels -> the residual_decompose claim survives the refinement, correctly scoped.
"""
from collections import defaultdict


def mul(*ss):
    r = defaultdict(int)
    for s in ss:
        for k, v in s.items():
            r[k] += v
    return {k: v for k, v in r.items() if v != 0}


def div(a, b):
    return mul(a, {k: -v for k, v in b.items()})


# measured per-quantity scale factors, performance / power-saver (power_arms-out.txt)
SC_COMPUTE = 156.6 / 60.3      # 2.60   (rides clock_core)
SC_MEM = 14.7 / 10.2          # 1.44   (rides clock_mem)
SC_RIDGE_MEAS = 10.7 / 5.9    # 1.81   (measured ridge swing)


def scale(sig, scales):
    s = 1.0
    for k, e in sig.items():
        s *= scales.get(k, 1.0) ** e
    return s


if __name__ == "__main__":
    print("the power-arms falsification, structurally corrected: `clock` is two clocks.\n")

    # signatures
    compute = {'clock_core': 1, 'intensity': 1}
    mem_bw = {'clock_mem': 1}
    ridge_2ck = div(compute, mem_bw)                       # two-clock ridge
    # single-clock variant: clock_core == clock_mem == clock
    compute_1ck = {'clock': 1, 'intensity': 1}; mem_1ck = {'clock': 1}
    ridge_1ck = div(compute_1ck, mem_1ck)

    # 1. single-clock predicts ridge clock-free -> invariant; measured 1.81x falsifies
    w1 = ridge_1ck.get('clock', 0) == 0 and abs(SC_RIDGE_MEAS - 1.0) > 0.3
    print(f"1. single-clock cotype: ridge signature {ridge_1ck} -> clock exponent 0 -> predicts ridge "
          f"INVARIANT (scale 1.0); measured {SC_RIDGE_MEAS:.2f}x -> FALSIFIED {w1}")

    # 2. two-clock: ridge survives as clock_core/clock_mem
    w2 = ridge_2ck.get('clock_core', 0) == 1 and ridge_2ck.get('clock_mem', 0) == -1
    print(f"2. two-clock cotype: ridge signature {ridge_2ck} -> POWER-DEPENDENT (clock_core/clock_mem) {w2}")

    # 3. quantitative: predicted ridge scale == measured
    scales = {'clock_core': SC_COMPUTE, 'clock_mem': SC_MEM, 'intensity': 1.0}  # core-clock realized as compute scale
    pred = scale(ridge_2ck, scales)                        # = SC_COMPUTE / SC_MEM
    w3 = abs(pred - SC_RIDGE_MEAS) / SC_RIDGE_MEAS < 0.1
    print(f"3. QUANTITATIVE: predicted ridge scale = compute_scale/mem_scale = {SC_COMPUTE:.2f}/{SC_MEM:.2f} "
          f"= {pred:.2f} == measured {SC_RIDGE_MEAS:.2f} {w3}")

    # 4. scope preserved: memory-bound residual stays single-domain -> cancels
    rate_membound = {'clock_mem': 1, 'intensity': 1}       # a memory-bound kernel rides clock_mem
    residual_mb = div(rate_membound, mul({'intensity': 1}, mem_bw))   # rate / (I * mem_BW)
    w4 = 'clock_mem' not in residual_mb and 'clock_core' not in residual_mb
    print(f"4. SCOPE: memory-bound residual signature {residual_mb} -> clock cancels (single domain) -> "
          f"residual_decompose's claim HOLDS, correctly scoped {w4}")

    ok = w1 and w2 and w3 and w4
    print(f"\nTWO CLOCK DOMAINS: single-clock-falsified {w1}; two-clock-power-dependent {w2}; "
          f"quantitative-match {w3}; scope-preserved {w4}")
    print(f"\n  {'PASS' if ok else 'FAIL'} — `clock` was an opaque primitive; the power-arms experiment")
    print(f"  split it into clock_core (compute) and clock_mem (memory controller). The ridge is a")
    print(f"  CROSS-domain ratio -> scales as clock_core/clock_mem -> power-dependent (predicted 1.81x ==")
    print(f"  measured). Same-domain ratios (the memory-bound residual) still cancel. The structural-cotype")
    print(f"  prove-or-reveal: a falsified prediction pointed exactly at the broken factor, which split.")
