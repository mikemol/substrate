#!/usr/bin/env python3
"""jea_onegraph.py — Δ-Ω-onegraph (brick 1): the HARDWARE operating-point solve is the SAME graded-ℚ graph reduction
as the term eval. The navigator solves a conductance network by a Kron reduction (Schur-eliminate internal nodes ->
equivalent conductance -> f*, binding-edge). That is a GRAPH reduced by combining nodes via RATIONAL arithmetic --
the EXACT graded-ℚ carrier the term evaluator uses (+, ×, and reciprocal = num/den swap; the field ops Schur needs).

Branchless + exact-ℚ + the graph's own elimination order = NO pivot branch = the IDENTICAL uniform fold the evaluator
runs (Δ-Ω-branchless is the prereq: the decision logic is arithmetic, not control flow). So the operating point is a
TERM the same evaluator reduces -- self-hosting: the system that schedules the eval is computed BY the eval.

Brick 1 (this file): the 2-conductance operating point f* = g_gpu/(g_cpu+g_gpu) -- a parallel current-divider -- as
a graded-ℚ DAG on the carrier (q_combine = jea_graded.combine_batch; q_recip = swap), matching live_dispatcher.decide
EXACTLY; the bottleneck = a BRANCHLESS argmax over the ℚ relaxation gains. Circuit-state-RELAXATION = re-eval on new
telemetry leaves (the drain, reactive). Brick 2 (next): fold compute_bw's full iMC/iGPU Kron/Schur into the ℚ graph.

Witnesses ([W], __main__):
1. f* PARALLEL REDUCTION on the carrier == gg/(gc+gg) exact (the Kron parallel-combine is graded-ℚ arithmetic).
2. == live_dispatcher.decide (f* matches the real solver within float ε; bottleneck matches via the branchless ℚ argmax).
3. RELAXATION = RE-EVAL: change the telemetry (cool->hot), re-run the SAME graph -> f*/bottleneck MOVE (reactive).
"""
import os, sys
os.environ.setdefault("CUDA_PATH", "/usr")
from fractions import Fraction
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jea_graded as GR, jea_branchless as BL, jea_divstr as DV     # DV: ÷ IS the ℚ wedge quotient (Δ-Ω-divstr)
_TOOLS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scratch", "el-atlas", "el-atlas-repo", "tools"))
sys.path.insert(0, _TOOLS)
from live_dispatcher import decide, binding_edge, _PCIE_MAX_BW, _TRIP   # the el-atlas reference (the Kron solve)
from perf_graph_integrated import compute_bw                          # reference: the iMC/iGPU conductance net + g_eff
from kron_reduction import g_eff                                      # reference: the ONE Kron operator
from thermal_gate import gate

_EDGES = ("iMC/iGPU", "thermal", "PCIe/link")                         # the 3 relaxation edges (binding_edge order)
def _Q(x): return Fraction(x).limit_denominator(10**12)               # rationalize a measured conductance -> exact ℚ


def q_combine(op, a, b):
    """ONE graded-ℚ carrier combine (the SAME op as the eval: jea_graded.combine_batch, batch size 1). op 1=×, 0=+."""
    n, d = GR.combine_batch(op, [a.numerator], [a.denominator], [b.numerator], [b.denominator])[0]
    return Fraction(n, d)

def q_recip(a): return DV.Q_DIV.wedge(Fraction(1), a)[0]              # reciprocal = the ℚ WEDGE quotient (Δ-Ω-divstr: the live ÷ IS recon's q)


def series_schur(a, b):
    """SCHUR-eliminate the shared middle node of a 2-edge series path -> equivalent conductance a·b/(a+b). THE Kron
    reduction step, as a graded-ℚ WEDGE on the carrier: mul (a·b), add (a+b), recip (swap), mul. Commutative +
    associative -> FOLD a series path of conductances by the same combine (Schur = recon with a ℚ quotient -> the
    generic-Quot Wedge; AI-Q's Wedge generalization and Δ-Ω-onegraph meet here)."""
    return q_combine(1, q_combine(1, a, b), q_recip(q_combine(0, a, b)))


def compute_bw_qgraph(imc, dma=False, igpu=False, T=46.0, link_state=1.0, dma_full=8e9, igpu_full=None):
    """Δ-Ω-onegraph brick 2: compute_bw's iMC/iGPU conductance net (CORES--IMC--DRAM, Schur-eliminate IMC, × thermal
    gate) computed as a graded-ℚ graph reduction on the SAME carrier (series_schur + a gate mul). The contender
    arithmetic (avail = imc - DMA·link - iGPU, clamp) is the leaf-conductance prep (host ℚ field); the KRON REDUCTION
    (the Schur) is the carrier. dma/igpu are scenario PRESENCE (which contenders), not value-knob branches."""
    igpu_full = igpu_full if igpu_full is not None else imc * 0.25
    steal = (dma_full * link_state if dma else 0.0) + (igpu_full if igpu else 0.0)   # contender steal (presence, leaf prep)
    avail = GR.q_sub(_Q(imc), _Q(steal))                            # imc - steal: the SUBTRACTION is now ON THE CARRIER (sign-on-carrier)
    avail = max(avail, _Q(imc * 0.01))                               # clamp (host ℚ max)
    g = series_schur(_Q(1e18), avail)                                # CORES--IMC(1e18)--DRAM(avail): Schur on the carrier
    return q_combine(1, g, _Q(gate(T, 100.0)))                       # × thermal gate (a carrier mul)


def fstar_qgraph(gc, gg):
    """f* = gg/(gc+gg): two parallel conductances' current-divider, as a graded-ℚ graph reduction on the carrier --
    add (gc+gg), reciprocal (swap), multiply (gg · 1/(gc+gg)). The Kron parallel-combine IS graded-ℚ arithmetic."""
    s = q_combine(0, gc, gg)                                          # gc + gg            (rat_add)
    return q_combine(1, gg, q_recip(s))                              # gg · 1/(gc + gg)    (rat_mul)


def operating_point_qgraph(imc, tel, pcie_eff=1.0, cpu_eff=1.0, ref_T=46.0):
    """The navigator's operating point (f*, bottleneck) ENTIRELY as graded-ℚ graph arithmetic + a BRANCHLESS argmax --
    the same logic+arithmetic as the term eval (Δ-Ω-onegraph), matching live_dispatcher.decide. f* = parallel
    current-divider (fstar_qgraph); the 3 relaxation gains are now computed via compute_bw_qgraph (the iMC/iGPU Kron
    Schur ON THE CARRIER -- brick 2 closes brick-1's 'gains from reference'); the binding edge = BL.argmax over them."""
    gc = _Q(imc * gate(tel["T"], _TRIP) * cpu_eff)                    # iMC ceiling × thermal gate × cpu_eff (a conductance)
    gg = _Q(_PCIE_MAX_BW * tel["link_state"] * pcie_eff)             # PCIe max × ASPM link × pcie_eff (a conductance)
    fstar = fstar_qgraph(gc, gg)
    T, ls = tel["T"], tel["link_state"]
    g_cpu = compute_bw_qgraph(imc, dma=True, igpu=True, T=T, link_state=ls)        # the bound net, on the carrier
    gains = [GR.q_sub(compute_bw_qgraph(imc, dma=True, igpu=False, T=T,     link_state=ls), g_cpu),  # iMC/iGPU (drop iGPU)
             GR.q_sub(compute_bw_qgraph(imc, dma=True, igpu=True,  T=ref_T, link_state=ls), g_cpu),  # thermal (gate->ref)
             GR.q_sub(_Q(_PCIE_MAX_BW * 1.0), _Q(_PCIE_MAX_BW * ls))]                                # PCIe/link (link->full)
    bottleneck = BL.pick(_EDGES, BL.argmax(gains))                   # binding edge = branchless argmax over the ℚ gains (carrier-subtracted)
    return fstar, bottleneck


def current_divider(d_self, others):
    """The share of current through d_self at a node it shares with `others` (parallel conductances/demands):
    d_self / (d_self + Σ others) -- pure {+, ÷-by-swap, ×}, NO subtraction (KCL current division). The shares of all
    branches at a node sum to 1 by construction (the denominator IS the sum)."""
    tot = d_self
    for o in others: tot = q_combine(0, tot, o)                      # Σ demands (carrier add)
    return q_combine(1, d_self, q_recip(tot))                       # d_self · 1/Σ   (× recip-swap)


def compute_bw_shunt(imc, dma=False, igpu=False, T=46.0, link_state=1.0, dma_full=8e9, igpu_full=None):
    """Δ-Ω-onegraph brick 3 (SUBTRACTION-FREE): contention modeled as SHUNTS sharing the iMC; the compute throughput
    is its CURRENT-DIVIDER share of the channel -- bw = imc · (d_c / (d_c + Σ contender demands)) · gate -- pure
    {+,×,÷}. The truer conductance-network form; diverges from el-atlas's fixed-slice avail=imc-steal subtraction
    stand-in (proportional share vs fixed subtraction). d_c = imc (compute demands the full channel)."""
    igpu_full = igpu_full if igpu_full is not None else imc * 0.25
    others = ([_Q(dma_full * link_state)] if dma else []) + ([_Q(igpu_full)] if igpu else [])
    share = current_divider(_Q(imc), others)                        # compute's share of the shared iMC channel
    return q_combine(1, q_combine(1, _Q(imc), share), _Q(gate(T, 100.0)))   # imc · share · gate -- no subtraction


def operating_point_shunt(imc, tel, pcie_eff=1.0, cpu_eff=1.0, ref_T=46.0):
    """Δ-Ω-onegraph brick 3: the operating point with ZERO subtraction. f* = the current-divider (already {+,×,÷});
    the binding edge ranks by RATIO sensitivity (relaxed/bound -- the native-quotient multiplicative sensitivity),
    argmax, no subtraction. The whole solve is {+, ×, ÷-by-swap} on the carrier -- bs_sub retired from this path."""
    gc = _Q(imc * gate(tel["T"], _TRIP) * cpu_eff); gg = _Q(_PCIE_MAX_BW * tel["link_state"] * pcie_eff)
    fstar = fstar_qgraph(gc, gg)                                     # current divider gg/(gc+gg) -- subtraction-free
    T, ls = tel["T"], tel["link_state"]
    bound = compute_bw_shunt(imc, dma=True, igpu=True, T=T, link_state=ls)
    ratios = [q_combine(1, compute_bw_shunt(imc, dma=True, igpu=False, T=T,     link_state=ls), q_recip(bound)),  # iMC/iGPU
              q_combine(1, compute_bw_shunt(imc, dma=True, igpu=True,  T=ref_T, link_state=ls), q_recip(bound)),  # thermal
              q_combine(1, _Q(_PCIE_MAX_BW * 1.0), q_recip(_Q(_PCIE_MAX_BW * ls)))]                               # PCIe/link
    return fstar, BL.pick(_EDGES, BL.argmax(ratios))                 # RATIO sensitivity argmax (native ÷, no subtraction)


if __name__ == "__main__":
    print("jea_onegraph: Δ-Ω-onegraph (bricks 1-3) -- the hardware operating point is a graded-ℚ graph reduction (the SAME carrier)\n")
    imc = 100e9                                                      # a representative iMC ceiling (decide takes it as input)
    cool = dict(T=46, link_state=1.0, gov="powersave"); hot = dict(T=120, link_state=0.50, gov="performance")

    # W1: f* parallel reduction on the carrier == gg/(gc+gg) exact
    gc, gg = Fraction(3, 7), Fraction(5, 11)
    fq = fstar_qgraph(gc, gg); w1 = (fq == gg / (gc + gg))
    print(f"  W1  f* on the graded-ℚ carrier (add, recip-swap, mul) == gg/(gc+gg) exact: {fq} == {gg/(gc+gg)}: {w1}")

    # W2: == live_dispatcher.decide (the real Kron solver) -- f* within float ε; bottleneck via the branchless ℚ argmax
    f_c, bn_c = operating_point_qgraph(imc, cool); ref_c = decide(imc, cool)
    f_h, bn_h = operating_point_qgraph(imc, hot);  ref_h = decide(imc, hot)
    fmatch = abs(float(f_c) - ref_c["fstar"]) < 1e-9 and abs(float(f_h) - ref_h["fstar"]) < 1e-9
    bmatch = (bn_c == ref_c["bottleneck"]) and (bn_h == ref_h["bottleneck"])
    w2 = fmatch and bmatch
    print(f"  W2  == live_dispatcher.decide: f* cool {float(f_c):.4f} vs {ref_c['fstar']:.4f}, hot {float(f_h):.4f} vs "
          f"{ref_h['fstar']:.4f} (Δ<1e-9: {fmatch}); bottleneck {bn_c}/{bn_h} == ref {ref_c['bottleneck']}/{ref_h['bottleneck']}: {bmatch}")

    # W3: relaxation = RE-EVAL the SAME graph on new telemetry leaves (reactive) -> operating point MOVES
    w3 = (f_c != f_h) or (bn_c != bn_h)
    print(f"  W3  RELAXATION = RE-EVAL (cool->hot re-runs the SAME graded-ℚ graph): f* {float(f_c):.3f}->{float(f_h):.3f}, "
          f"bottleneck {bn_c}->{bn_h} -- moved: {w3}")

    # W4 (brick 2): the SCHUR reduction itself on the carrier == the el-atlas Kron operator g_eff (2-edge series)
    schur_ok = True
    for av in (51.2e9, 80e9, 8e9, 1e9):
        q = float(series_schur(_Q(1e18), _Q(av))); ref = g_eff([(0, 1, 1e18), (1, 2, av)], 0, 2)
        schur_ok = schur_ok and abs(q - ref) / ref < 1e-9
    w4 = schur_ok
    print(f"\n  W4  SCHUR on the carrier == el-atlas g_eff (Kron operator): series_schur(1e18,avail) == g_eff(2-edge series) "
          f"across avail: {w4}  (the Kron reduction IS a graded-ℚ wedge)")

    # W5 (brick 2): compute_bw_qgraph == el-atlas compute_bw across the composition scenarios (idle/+dma/+both/hot/aspm)
    scen = [dict(), dict(dma=True), dict(dma=True, igpu=True), dict(dma=True, igpu=True, T=130.0), dict(dma=True, link_state=0.5)]
    bw_ok = all(abs(float(compute_bw_qgraph(imc, **s)) - compute_bw(imc, **s)) / compute_bw(imc, **s) < 1e-9 for s in scen)
    w5 = bw_ok
    print(f"  W5  compute_bw_qgraph == el-atlas compute_bw across {len(scen)} scenarios (idle/+dma/+both/+hot/+aspm), "
          f"the iMC/iGPU net Schur-reduced on the carrier: {w5}")

    # W6 (brick 2): the FULL operating point -- f* AND the gains via the carrier -- == decide; bottleneck == binding_edge
    w6 = True
    for tel in (cool, hot):
        f_q, bn_q = operating_point_qgraph(imc, tel); ref = decide(imc, tel); ref_bn, _ = binding_edge(imc, tel)
        w6 = w6 and abs(float(f_q) - ref["fstar"]) < 1e-9 and bn_q == ref["bottleneck"] == ref_bn
    print(f"  W6  FULL operating point on the carrier (f* + gains via compute_bw_qgraph) == decide + binding_edge "
          f"(cool & hot): {w6}  (brick 1's 'gains from reference' deferral CLOSED)")

    # W7 (brick 3): KCL -- the current-divider shares of all branches at the iMC node sum to EXACTLY 1, computed
    # SUBTRACTION-FREE ({+,×,÷}). Conservation without a single subtraction.
    ds = [_Q(imc), _Q(8e9), _Q(imc*0.25)]                            # demands: compute, DMA, iGPU
    shares = [current_divider(ds[i], ds[:i]+ds[i+1:]) for i in range(3)]
    kcl = sum(shares, Fraction(0)) == 1
    w7 = kcl
    print(f"\n  W7  KCL (brick 3, SUBTRACTION-FREE): the 3 current-divider shares sum to EXACTLY {sum(shares, Fraction(0))} "
          f"== 1 (conservation via {{+,×,÷}}, no subtraction): {w7}")

    # W8 (brick 3): monotone contention -- idle >= +dma >= +both (more shunts -> less compute), via the divider
    b_idle = compute_bw_shunt(imc); b_dma = compute_bw_shunt(imc, dma=True); b_both = compute_bw_shunt(imc, dma=True, igpu=True)
    w8 = (b_idle >= b_dma >= b_both) and (b_idle == _Q(imc))         # idle = full channel; contention monotone
    print(f"  W8  MONOTONE contention (brick 3 divider): idle {float(b_idle)/1e9:.1f} >= +dma {float(b_dma)/1e9:.1f} >= "
          f"+both {float(b_both)/1e9:.1f} GB/s (subtraction-free; idle = full imc): {w8}")

    # W9 (brick 3): the operating point with ZERO subtraction -- ratio sensitivity + reactive
    fs_c, bn_sc = operating_point_shunt(imc, cool); fs_h, bn_sh = operating_point_shunt(imc, hot)
    w9 = (fs_c == f_c) and (fs_h == f_h) and ((fs_c, bn_sc) != (fs_h, bn_sh))   # f* same divider as brick1; reactive
    print(f"  W9  SUBTRACTION-FREE operating point (brick 3): f* = the current divider (== brick 1: {fs_c==f_c}); binding")
    print(f"      edge by RATIO sensitivity (native ÷); reactive cool->hot {bn_sc}->{bn_sh}: {w9}  -- solve is {{+,×,÷}} only")

    ok = w1 and w2 and w3 and w4 and w5 and w6 and w7 and w8 and w9
    print(f"\n  {'PASS' if ok else 'FAIL'} — Δ-Ω-onegraph bricks 1-3: the hardware operating-point solve is ENTIRELY a")
    print(f"  graded-ℚ graph reduction on the SAME carrier as the term eval -- f* (parallel current-divider) AND the")
    print(f"  iMC/iGPU net (the SCHUR/Kron reduction == series_schur, a graded-ℚ WEDGE: a·b/(a+b)) AND the binding edge")
    print(f"  (branchless ℚ argmax over the gains), matching el-atlas g_eff/compute_bw/binding_edge/decide. Circuit-state-")
    print(f"  RELAXATION = re-eval on new telemetry leaves. The supervisor solve IS a term the evaluator reduces --")
    print(f"  self-hosting. Bricks 1-2 reproduce el-atlas EXACTLY (incl. its avail=imc-steal subtraction stand-in, via")
    print(f"  q_sub). Brick 3 is the SUBTRACTION-FREE truer model: contention = current-divider shunts, binding edge =")
    print(f"  RATIO sensitivity -- {{+,×,÷-by-swap}} ONLY, validated by KCL (shares sum to 1) + monotonicity (it diverges")
    print(f"  from the fixed-slice stand-in by construction). bs_sub retires from this path (a grade-axis primitive only).")
    print(f"  NEXT: Schur = recon-with-a-ℚ-quotient -> AI-Q's generic-Quot Wedge; + run the solve ON-DEVICE.")
