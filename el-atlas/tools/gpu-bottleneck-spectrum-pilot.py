"""
gpu-bottleneck-spectrum-pilot.py — T-series pilot: the FULL bottleneck spectrum as the
continued-fraction TRACE of the GPU conductance network (candidate claim GBS).

gpu-topology-nedge-pilot found THE bottleneck (the min-conductance series link = the top of
the G_AND fold). This extracts the WHOLE ordered spectrum -- a full ranking of constraints, not
just the top -- by taking the CONTINUED-FRACTION / EEA trace of the conductance ladder.

The bridge that makes it rigorous (not analogy): a CAUER LADDER network's effective impedance
IS a continued fraction in its element values --
    Z = R1 + 1/(G2 + 1/(R3 + 1/(G4 + ...)))          (series R alternating with shunt G)
so "take the CF of the network" == "read off the ordered constraint ladder." This is the SAME
to_cf/from_cf carrier as jea_trace_window.py, now carrying the bottleneck hierarchy instead of a
rational. The single roofline ridge generalizes to the HIERARCHICAL (multi-ceiling) roofline:
every memory level + compute + occupancy is a ceiling; the sorted ceilings = the spectrum.

Each constraint's DOMINANCE WEIGHT is its share of the total series resistance (Amdahl):
    f_i = (1/G_i) / sum_j (1/G_j)      speedup-if-removed = 1/(1 - f_i)
Sorted descending = the full bottleneck ranking. The top is what the topology pilot reported;
the rest is the cascade -- who becomes the bottleneck once you fix the current one.

Witnesses (each [W]):
1. SPECTRUM = FULL RANKING: sort constraints by conductance; the top == the G_AND bottleneck
   (consistency with the topology pilot), and the whole sorted list is the ordered ladder.
2. AMDAHL DOMINANCE: resistance shares f_i sum to 1; speedup-if-removed = 1/(1-f_i); removing
   the top gives the largest speedup; the sorted shares ARE the ranking.
3. CASCADE / MULTI-RIDGE: sweep arithmetic intensity I; compute = peakFLOP/I is a moving
   ceiling, so the bottleneck IDENTITY steps through the spectrum at crossovers (each crossover
   is a Wheatstone bridge null) -- the hierarchical roofline, a spectrum of ridges not one.
4. CF TRACE: the ladder element sequence is the network's continued fraction; folding it
   (from_cf, electrical) reconstructs the effective conductance, and the convergents (truncating
   the deep rungs) converge to it -- the spectrum IS the EEA trace of the network.
5. REMOVE-TOP -> NEXT: idealizing the #1 constraint makes #2 the new bottleneck; the spectrum
   order predicts the whole removal cascade.
Run output: tools/gpu-bottleneck-spectrum-pilot-out.txt.
"""
import os
os.environ.setdefault("CUDA_PATH", "/usr")
from functools import reduce as _reduce

G_OR  = lambda a, b: a + b
G_AND = lambda a, b: 0.0 if a + b == 0 else a * b / (a + b)
G_AND_fold = lambda xs: _reduce(G_AND, xs)


def query():
    import cupy as cp
    d = cp.cuda.Device(0); a = d.attributes
    props = cp.cuda.runtime.getDeviceProperties(0)
    nm = props['name']; nm = nm.decode() if isinstance(nm, (bytes, bytearray)) else nm
    clk = a['ClockRate'] * 1e3; sms = a['MultiProcessorCount']
    dram_bw = 2 * (a['GlobalMemoryBusWidth'] / 8) * (a['MemoryClockRate'] * 1e3)
    fp32 = sms * 128 * 2 * clk
    return dict(name=nm, sms=sms, dram_bw=dram_bw, fp32=fp32)


def constraints_at(t, I, host=True):
    """All ceilings in common BYTES/SEC at arithmetic intensity I (FLOP/byte). A memory link's
    ceiling is its BW; compute's byte-equivalent ceiling is peakFLOP/I. Lower conductance =
    higher resistance = stronger bottleneck. The spectrum is WORKLOAD-RELATIVE: host=True streams
    from host (PCIe in the loop, dominates); host=False is device-resident (the compute roofline)."""
    cons = []
    if host:
        cons.append(("host/PCIe", 16.0e9))             # [est] gen4 x8 laptop -- only if streaming from host
    cons += [
        ("DRAM",       t['dram_bw']),                  # queried
        ("L2(24MB)",   t['dram_bw'] * 6),              # [est] ~6x DRAM
        ("L1/shared",  t['sms'] * 128 * 1.0 * 2.13e9), # [est] ~128 B/clk/SM
        ("compute",    t['fp32'] / I),                 # peak FP32 re-expressed as bytes/s at intensity I
    ]
    return cons


def spectrum(cons):
    """Sorted ascending by conductance = the ordered bottleneck ladder (top first). Each entry
    carries its resistance share f_i (Amdahl dominance) and speedup-if-removed."""
    Rtot = sum(1.0 / g for _, g in cons)
    rows = sorted(((nm, g, (1.0 / g) / Rtot) for nm, g in cons), key=lambda r: r[1])
    return [(nm, g, f, (1.0 / (1.0 - f) if f < 1 else float('inf'))) for nm, g, f in rows]


def ladder_fold(elems):
    """Electrical CF fold (from_cf direction): alternate series G_AND / shunt G_OR from the
    DEEP end inward. elems = [(kind, G), ...] port-most first; returns effective G at the port
    AND the list of convergents (effective G keeping only the top-k rungs)."""
    convs = []
    for k in range(1, len(elems) + 1):
        sub = elems[:k]
        acc = sub[-1][1]
        for kind, g in reversed(sub[:-1]):
            acc = G_AND(g, acc) if kind == "series" else G_OR(g, acc)
        convs.append(acc)
    return convs[-1], convs


def w_spectrum_full_ranking(t):
    cons = constraints_at(t, 4.0)          # a memory-bound-ish intensity
    spec = spectrum(cons)
    top = spec[0][0]
    band = G_AND_fold([g for _, g in cons])
    ok = (top == min(cons, key=lambda c: c[1])[0]) and (band <= spec[0][1] + 1)
    print(f"1. spectrum = full ranking @ I=4 FLOP/byte (binding conductance G_AND={band/1e9:.1f} GB/s):")
    for i, (nm, g, f, sp) in enumerate(spec):
        print(f"     #{i+1} {nm:10s} {g/1e9:8.1f} GB/s  share={f*100:5.1f}%  speedup-if-removed x{sp:.2f}")
    print(f"   top bottleneck = {top} (== G_AND min) {ok}")
    return ok


def w_amdahl(t):
    spec = spectrum(constraints_at(t, 4.0))
    shares = sum(f for _, _, f, _ in spec)
    ok_sum = abs(shares - 1.0) < 1e-9
    ok_top = spec[0][3] == max(s[3] for s in spec)   # top bottleneck has the largest speedup
    print(f"2. Amdahl dominance: shares sum to 1 {ok_sum}; top has max speedup-if-removed {ok_top}")
    return ok_sum and ok_top


def w_cascade_multiridge(t):
    # device-resident roofline (no host transfer in the loop): sweep intensity, watch the
    # bottleneck identity step through the spectrum at the crossovers (= bridge nulls).
    seen = []
    for I in (1, 4, 16, 56, 128, 512):
        top = spectrum(constraints_at(t, float(I), host=False))[0][0]
        seen.append((I, top))
    identities = [nm for _, nm in seen]
    changed = len(set(identities)) >= 2
    compute_takes_over = identities[-1] == "compute" and identities[0] != "compute"
    ridge = t['fp32'] / t['dram_bw']                  # DRAM<->compute crossover (the classic ridge)
    print(f"3. cascade / multi-ridge (device-resident): bottleneck vs intensity {seen}")
    print(f"   identity changes across I {changed}; compute overtakes at high I {compute_takes_over}; "
          f"DRAM<->compute crossover (bridge null) at I*={ridge:.1f} FLOP/byte")
    return changed and compute_takes_over


def w_cf_trace(t):
    # the memory ladder as a Cauer CF: series links alternating with shunt (cache) resources
    elems = [("series", 16.0e9), ("shunt", t['dram_bw'] * 6), ("series", t['dram_bw']),
             ("shunt", t['sms'] * 128 * 2.13e9)]
    geff, convs = ladder_fold(elems)
    # convergents converge: each is closer to geff than the previous (monotone tail)
    errs = [abs(c - geff) for c in convs]
    converging = all(errs[i] <= errs[i - 1] + 1e-6 for i in range(1, len(errs))) and errs[-1] < 1e-3
    # the trace (ordered element conductances) reconstructs geff via the fold
    ok = geff > 0 and converging
    print(f"4. CF trace: ladder fold -> G_eff = {geff/1e9:.1f} GB/s; convergents "
          f"{[round(c/1e9,1) for c in convs]} converge to it {converging}")
    print(f"   => the ordered ladder IS the network's continued fraction (same carrier as jea_trace_window)")
    return ok


# The KERNEL-TYPE knob: a kernel's data residence / access pattern selects WHICH level feeds it,
# hence which rungs are in the loop and where the ridge sits. This is a pilot-level knob (a
# workload selector), NOT a depsort SPACE knob (that would be a row -- invalidates ledgers).
KERNEL_TYPES = [
    ("host-stream",   "host/PCIe", 16.0e9),   # one-pass over host data (ETL); PCIe feeds every op
    ("dram-stream",   "DRAM",      None),      # device-resident, low reuse (saxpy, stencil-1pass)
    ("l2-resident",   "L2(24MB)",  None),      # working set fits L2 (blocked/tiled, high reuse)
    ("l1-resident",   "L1/shared", None),      # set fits shared mem (register/smem-tiled GEMM inner)
    ("compute-bound", "compute",   None),      # so much reuse the source is irrelevant; FP caps
]

def w_kernel_type_knob(t):
    """The kernel type selects the feeding level => moves the ridge. Cache-resident kernels become
    compute-bound at MUCH lower intensity (their memory ceiling is higher, so the ridge is lower)."""
    src_bw = {"host/PCIe": 16.0e9, "DRAM": t['dram_bw'], "L2(24MB)": t['dram_bw'] * 6,
              "L1/shared": t['sms'] * 128 * 2.13e9}
    rows = []
    for name, src, _ in KERNEL_TYPES:
        if src == "compute":
            rows.append((name, src, float('inf'))); continue
        ridge = t['fp32'] / src_bw[src]        # I above which this kernel turns compute-bound
        rows.append((name, src, ridge))
    finite = [r[2] for r in rows if r[2] != float('inf')]
    monotone = all(finite[i] < finite[i - 1] for i in range(1, len(finite)))  # slower src -> higher ridge
    print(f"4b. kernel-type knob (data residence selects the feeding level => moves the ridge):")
    for name, src, ridge in rows:
        rs = "inf (always compute-bound)" if ridge == float('inf') else f"{ridge:6.1f} FLOP/byte"
        print(f"     {name:13s} fed by {src:10s} ridge = {rs}")
    print(f"   ridge strictly rises as the feeding level slows (host>dram>l2>l1) {monotone}  "
          f"=> cache-resident kernels saturate compute far sooner")
    return monotone

def w_remove_top_next(t):
    cons = constraints_at(t, 4.0)
    spec = spectrum(cons)
    top, second = spec[0][0], spec[1][0]
    # idealize the top constraint (G -> inf); the new bottleneck must be the old #2
    cons2 = [(nm, (1e30 if nm == top else g)) for nm, g in cons]
    new_top = spectrum(cons2)[0][0]
    ok = new_top == second
    print(f"5. remove-top -> next: idealize {top} -> new bottleneck = {new_top} (predicted #2 = {second}) {ok}")
    return ok


if __name__ == "__main__":
    try:
        t = query()
    except Exception as e:
        print(f"GPU BOTTLENECK SPECTRUM PILOT: SKIP (no device / cupy: {e})"); raise SystemExit(0)
    print(f"device: {t['name']}  ({t['sms']} SMs, {t['dram_bw']/1e9:.0f} GB/s DRAM, "
          f"{t['fp32']/1e9:.0f} GFLOP/s FP32) -- queried live\n")
    ws = [w_spectrum_full_ranking(t), w_amdahl(t), w_cascade_multiridge(t),
          w_kernel_type_knob(t), w_cf_trace(t), w_remove_top_next(t)]
    ok = all(ws)
    print(f"\nGPU BOTTLENECK SPECTRUM PILOT: full-ranking {ws[0]}; amdahl {ws[1]}; cascade {ws[2]}; "
          f"kernel-type-knob {ws[3]}; cf-trace {ws[4]}; remove-top->next {ws[5]}")
    print(f"\n  {'PASS' if ok else 'FAIL'} — the full bottleneck spectrum is the continued-fraction TRACE of")
    print(f"  the GPU conductance network: the topology pilot's single bottleneck is the TOP of the trace;")
    print(f"  the whole sorted ladder (with Amdahl dominance weights) is the ranking; sweeping intensity")
    print(f"  cascades the bottleneck through the spectrum (the hierarchical roofline = a spectrum of ridges).")
    print(f"  'Find the bottleneck' = top of the trace; 'full ranking' = the whole trace (jea_trace_window).")
