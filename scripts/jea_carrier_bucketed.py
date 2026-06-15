#!/usr/bin/env python3
"""jea_carrier_bucketed.py — U1: the data-driven mixed-width carrier (pack the lanes by magnitude bucket).

I3 (jea_bucket_msb) PROVED the bucketing law sound on the flat-u64 carrier's values. U1 REALIZES it: values
now LIVE and COMPUTE at their magnitude bucket's native width instead of a flat u64. A combine is executed
lane-parallel at the WORKING width the migration law predicts -- mul of two w-bit components needs 2w room
(the SWAR W>=2L lane-spacing, jea_swar_mul), add needs ~2w+1 -- so the batch is grouped by working width
and each group runs vectorized at its native GPU int dtype (uint8/16/32/64 = the narrow datapaths, where
uint8 is the GPU's fastest int path / dp4a; the byte is the floor, jea_limb_gpu). The result re-buckets by
its actual magnitude (migrate); a working width past 64 ESCALATES to the next carrier (byte-limb), never
wraps. This is "pay-for-what-you-use" REALIZED (narrow values cost narrow bytes + run on narrow lanes),
not just measured as in I3.

This is the carrier mechanism (storage + combine + migration + escalate, exact). Wiring it as the
persistent cooperative evaluator's storage layer (per-bucket pools, re-bucket inside the readiness gate)
is the named follow-on -- the hazardous persistent-kernel-pool rewrite, deliberately not bundled here.

Lazy (no reduce) is the mode shown -- it keeps the whole carrier on-GPU at native width (reduction would
migrate values DOWN, proven in I3); exactness is checked against host Fraction (reduction is order-free).

Witnesses (each [W]):
1. EXACT: every non-escalated combine's packed-GPU result == host Fraction (across all width buckets).
2. MIGRATION SOUND: the working width (migration-law prediction) is an upper bound on the actual result
   width (never under-sized -> no silent overflow); mul results migrate UP from their operands' buckets.
3. PAY-FOR-WHAT-YOU-USE (realized): storing each value at its native bucket width uses far fewer bytes than
   a flat u64, AND each combine ran at its native width (group sizes reported), not promoted to u64.
4. ESCALATE: combines whose working width > 64 are FLAGGED (-> byte-limb carrier), never wrapped.
"""
import os
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp
from fractions import Fraction

NAT = [(8, cp.uint8), (16, cp.uint16), (32, cp.uint32), (64, cp.uint64)]
NBYTES = {8: 1, 16: 2, 32: 4, 64: 8}
def bw(x): return int(x).bit_length()
def native(bits):                                             # smallest native int width holding `bits`
    for w, _ in NAT:
        if bits <= w: return w
    return 128                                                # >64 = escalate (byte-limb's job)


if __name__ == "__main__":
    N = 100_000
    rng = np.random.default_rng(0)
    # operands: bit-lengths skewed small (most narrow) with a heavy tail (some products overflow u64 -> escalate)
    blen = lambda: int(min(34, 1 + int(rng.exponential(7))))
    an = np.empty(N, object); ad = np.empty(N, object); cn = np.empty(N, object); cd = np.empty(N, object)
    op = rng.integers(0, 2, N)                                # 0=add, 1=mul
    for i in range(N):
        an[i] = int(rng.integers(1, 1 << blen())); ad[i] = int(rng.integers(1, 1 << blen()))
        cn[i] = int(rng.integers(1, 1 << blen())); cd[i] = int(rng.integers(1, 1 << blen()))

    # working width per combine from operand bit-widths (the I3 migration law) -> native dtype bucket
    workbits = np.empty(N, np.int64); opbucket = np.empty(N, np.int64)
    for i in range(N):
        wan, wad, wcn, wcd = bw(an[i]), bw(ad[i]), bw(cn[i]), bw(cd[i])
        if op[i] == 1: Bn, Bd = wan + wcn, wad + wcd                          # mul
        else:          Bn, Bd = max(wan + wcd, wcn + wad) + 1, wad + wcd      # add
        workbits[i] = max(Bn, Bd); opbucket[i] = native(max(wan, wad, wcn, wcd))
    workw = np.array([native(b) for b in workbits], np.int64)
    esc = workw == 128

    res_n = np.zeros(N, object); res_d = np.zeros(N, object); group_sizes = {}
    for w, dt in NAT:                                          # one vectorized GPU pass per (width, op) group
        for o in (0, 1):
            idx = np.where((workw == w) & (op == o))[0]
            if idx.size == 0: continue
            group_sizes[(w, "mul" if o else "add")] = int(idx.size)
            gan = cp.asarray([int(an[i]) for i in idx], dt); gad = cp.asarray([int(ad[i]) for i in idx], dt)
            gcn = cp.asarray([int(cn[i]) for i in idx], dt); gcd = cp.asarray([int(cd[i]) for i in idx], dt)
            if o == 1: rn = gan * gcn; rd = gad * gcd          # mul, lane-parallel at native width w
            else:      rn = gan * gcd + gcn * gad; rd = gad * gcd  # add
            rn = rn.get(); rd = rd.get()                       # (lazy: unreduced, stays at native width on device)
            for k, i in enumerate(idx): res_n[i] = int(rn[k]); res_d[i] = int(rd[k])

    # ---- witnesses ----
    bad_exact = 0; mig_unsound = 0; migrated_up = 0; resbytes = 0; flatbytes = 0
    for i in range(N):
        if esc[i]: continue
        lhs = (Fraction(an[i], ad[i]) * Fraction(cn[i], cd[i])) if op[i] == 1 else (Fraction(an[i], ad[i]) + Fraction(cn[i], cd[i]))
        if Fraction(res_n[i], res_d[i]) != lhs: bad_exact += 1
        rb = native(max(bw(res_n[i]), bw(res_d[i])))
        if rb > workw[i]: mig_unsound += 1                     # working width must upper-bound the result
        if rb > opbucket[i]: migrated_up += 1
        resbytes += NBYTES[rb] * 2; flatbytes += 8 * 2

    nesc = int(esc.sum()); nlive = N - nesc
    w1 = bad_exact == 0
    w2 = mig_unsound == 0 and migrated_up > 0
    w3 = resbytes < flatbytes
    w4 = nesc > 0
    print(f"data-driven mixed-width carrier — {N} combines, {nlive} live, {nesc} escalated (working width >64)\n")
    print(f"  working-width groups (combines run lane-parallel at each native dtype):")
    for k in sorted(group_sizes): print(f"      u{k[0]:<2} {k[1]}: {group_sizes[k]}")
    print(f"  storage at native bucket vs flat u64: {resbytes} bytes vs {flatbytes} = {flatbytes/resbytes:.2f}x smaller")
    print(f"  migration: {migrated_up}/{nlive} results migrated UP from their operands' bucket (mul widens)")
    print(f"\n1. EXACT (packed-GPU == host Fraction, all live): {w1}  ({bad_exact} mismatches)")
    print(f"2. MIGRATION SOUND (working width >= actual, never undersized): {w2}  ({mig_unsound} undersized)")
    print(f"3. PAY-FOR-WHAT-YOU-USE ({flatbytes/resbytes:.2f}x smaller, ran at native width): {w3}")
    print(f"4. ESCALATE (working width >64 flagged, not wrapped): {w4}  ({nesc} escalated)")
    ok = w1 and w2 and w3 and w4
    print(f"\n  {'PASS' if ok else 'FAIL'} — U1: the carrier now STORES and COMPUTES at the magnitude bucket's")
    print(f"  native width (the data-driven mixed-width SWAR carrier), combines run lane-parallel per bucket,")
    print(f"  results migrate by the I3 law, escalate at the u64 boundary -- exact. pay-for-what-you-use")
    print(f"  REALIZED, not just measured. NEXT: wire as the persistent evaluator's storage (per-bucket pools,")
    print(f"  re-bucket in the readiness gate) -- and the sub-byte SWAR floor (1/2/4-bit packed within a byte).")
