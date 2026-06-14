"""
swar-boundary-nedge-pilot.py — T-series pilot: GPU SWAR carrier boundaries as a
nedge G-Value circuit (candidate claim SWB).

The jea SWAR carrier (substrate scripts/jea_swar*.py) packs N independent carriers
of width L into a 64-bit register, lane-isolated. This pilot models the SWAR
BOUNDARIES (lane boundary, room boundary, width-group boundary) as the nedge
electrical-evidence calculus and lets it weigh/rank the full op x width x layout
configuration space. The carrier is the el-atlas pair, NOT a quotient:

  E+ = sum_lanes L_i           operand/payload bits packed (parallel conductance, G_OR fold)
  E- = sum_lanes (W_i - L_i)   forced spatial expansion (product/headroom rooms)
  mass = E+ + E- = sum W_i     register occupancy
  bias = E+ - E-               packing efficiency (payload minus expansion)
  D    = #distinct (L,W) groups = divergent passes (temporal series resistance)

Maps SWAR onto the el-atlas crossbar and witnesses (each a [W] grounding):

1. MASS CONSERVATION: every valid tiling has mass = sum W_i = 64. The register is
   the conserved quantity; configs are pure bias + divergence variation (the mass
   axis is pinned, so all the signal lives in bias and D).
2. OP -> CROSSBAR REGION: the operation's room rule fixes its region.
   add (W=L) -> bias=+64 (T, all-payload); mul (W=2L) -> bias=0 (B, the bridge NULL,
   half the register is product headroom); bignum (W>2L) -> bias<0 (F, headroom-dominated).
3. LANE-ISOLATION = INSULATING BOUNDARY: config validity = series G_AND over the
   per-boundary insulation conductances; ONE leaky boundary (e.g. mul room W<2L, or
   non-pow2 broadcast room, or a bignum room below 2L+1+ceil(log2 K)) shorts G_valid
   to 0 -- series semantics, exactly as a short kills a series circuit.
4. DIVERGENCE = SERIES RESISTANCE: throughput conductance G_thru = E+/D (D equal
   passes in series, G_AND fold = E+/D); strictly monotone decreasing in D, so a
   mixed tiling (D>1) sits below the uniform one (D=1) at equal payload -- the
   warp-divergence Pareto axis, orthogonal to bias.
5. CONFLATION WITNESS: two configs with equal bias-shadow but different D have the
   same efficiency quotient yet different throughput -- the bias ratio cannot see
   divergence, only the (E+,E-,D) carrier can. Same shape as el-atlas: the quotient
   erases what the unquotiented pair retains.

Plus a DeMorgan check that the nedge ops used here are the spec's (NOT(AND)=OR).
The harness claim SWB re-encodes these at sample scale; this is the free-standing
witness. Run output: tools/swar-boundary-nedge-pilot-out.txt.
"""
from math import ceil, log2, isclose

# --- the nedge G-Value calculus (el-atlas-spec 5.7e; ngl-lift-pilot.py) -------------
G_OR  = lambda a, b: a + b                                   # parallel conductance
G_AND = lambda a, b: 0.0 if (a + b) == 0 else a * b / (a + b)  # series conductance
G_NOT = lambda g: float('inf') if g == 0 else 1.0 / g          # swap / reciprocal
def fold(op, xs, unit):
    acc = unit
    for x in xs: acc = op(acc, x)
    return acc
G_OR_fold  = lambda xs: fold(G_OR, xs, 0.0)                   # parallel: unit 0
G_AND_fold = lambda xs: xs[0] if len(xs) == 1 else fold(G_AND, xs[1:], xs[0])  # series

# --- SWAR room rules: room W as a function of (operation, lane value-width L) --------
def pow2_ceil(n):
    W = 1
    while W < n: W <<= 1
    return W

def room(op, L, K=3):
    if op == "add":    return L                              # carry stays in top bit, no expansion
    if op == "mul":    return 2 * L                          # product doubles the width
    if op == "bignum": return pow2_ceil(2 * L + 1 + (ceil(log2(K)) if K > 1 else 0))  # +carry headroom
    raise ValueError(op)

# --- a config: a list of lanes [(L, W)] (offsets irrelevant to the electrical model) -
def uniform(op, L, K=3):
    W = room(op, L, K); n = 64 // W
    return [(L, W)] * n if n >= 1 and 64 % W == 0 else None  # must tile 64

def analyze(op, lanes, K=3):
    """Compute the nedge quantities + OP-AWARE validity gate for a lane list. Boundary
    insulation is op-dependent: a room insulating for an add (W=L) leaks for a mul (needs W>=2L)."""
    Eplus  = sum(L for L, W in lanes)                         # payload bits (parallel G_OR fold)
    Eminus = sum(W - L for L, W in lanes)                     # forced expansion
    mass = Eplus + Eminus                                     # = sum W
    bias = Eplus - Eminus
    D = len(set(lanes))                                       # distinct (L,W) = divergent passes
    needs_pow2 = op in ("mul", "bignum")                      # only broadcast ops need pow2 rooms
    # per-boundary insulation conductances (series G_AND gate): 1.0 satisfied, 0.0 leaky
    cons = [1.0 if mass == 64 else 0.0,                                            # tiling boundary
            1.0 if (not needs_pow2 or all(W & (W - 1) == 0 for _, W in lanes)) else 0.0,  # pow2 broadcast
            1.0 if all(W >= room(op, L, K) for L, W in lanes) else 0.0]            # room sufficiency (no spill/bleed)
    g_valid = G_AND_fold(cons)                                # one leaky boundary -> 0
    g_thru = (Eplus / D) if D else 0.0                        # series of D equal payload conductances
    g_config = g_thru if g_valid > 0 else 0.0
    return dict(lanes=lanes, Eplus=Eplus, Eminus=Eminus, mass=mass, bias=bias,
                D=D, g_valid=g_valid, g_thru=g_thru, g_config=g_config)

def region(bias):
    return "T(payload)" if bias > 0 else ("B(null/contention)" if bias == 0 else "F(headroom)")


# ====================================================================================
if __name__ == "__main__":
    K = 3
    # ---- the many x many x many grid: operation x width-ladder x layout -------------
    grid = []   # (name, op, lanes)
    for op in ("add", "mul", "bignum"):
        for L in (32, 16, 8, 4, 2, 1):
            lanes = uniform(op, L, K)
            if lanes: grid.append((f"{op:6s} L={L:<2} uniform", op, lanes))
    # the real mixed configs we built (the "conclusions"):
    grid.append(("add    mixed 32/16/8/4/2/1/1", "add",
                 [(32, 32), (16, 16), (8, 8), (4, 4), (2, 2), (1, 1), (1, 1)]))
    grid.append(("mul    mixed 16/8/4/2/1/1", "mul",
                 [(16, 32), (8, 16), (4, 8), (2, 4), (1, 2), (1, 2)]))
    grid.append(("bignum mixed L4/L2/L1", "bignum",
                 [(4, 16), (2, 8), (2, 8), (1, 8), (1, 8), (1, 8), (2, 8)]))
    # a deliberately INVALID config: mul with product room too small (W < 2L) -> leaky boundary
    grid.append(("mul    L=8 room=8 (INVALID)", "mul", [(8, 8)] * 8))

    rows = [(name, op, analyze(op, lanes, K)) for name, op, lanes in grid]

    print("=" * 96)
    print("SWAR config space (op x width x layout) weighed by the nedge G-Value calculus")
    print("=" * 96)
    print(f"{'config':32s} {'N':>2} {'E+':>3} {'E-':>3} {'mass':>4} {'bias':>4} {'D':>2} "
          f"{'Gvalid':>6} {'G=E+/D':>7}  region")
    print("-" * 96)
    for name, op, a in sorted(rows, key=lambda r: -r[2]["g_config"]):
        print(f"{name:32s} {len(a['lanes']):>2} {a['Eplus']:>3} {a['Eminus']:>3} "
              f"{a['mass']:>4} {a['bias']:>4} {a['D']:>2} {a['g_valid']:>6.2f} "
              f"{a['g_config']:>7.2f}  {region(a['bias']) if a['g_valid']>0 else 'INVALID (shorted)'}")

    # ---- the five witnesses ---------------------------------------------------------
    valid = [(n, o, a) for n, o, a in rows if a["g_valid"] > 0]

    # 1. mass conservation
    w1 = all(a["mass"] == 64 for _, _, a in valid)

    # 2. op -> crossbar region
    reg = {}
    for _, op, a in valid:
        reg.setdefault(op, set()).add(region(a["bias"]))
    w2 = (reg.get("add") == {"T(payload)"} and reg.get("mul") == {"B(null/contention)"}
          and reg.get("bignum") == {"F(headroom)"})

    # 3. lane-isolation = insulating boundary: the INVALID config shorts to 0, valids don't
    inv = [a for n, o, a in rows if "INVALID" in n][0]
    w3 = (inv["g_valid"] == 0.0 and inv["g_config"] == 0.0 and all(a["g_valid"] > 0 for _, _, a in valid))

    # 4. divergence = series resistance: at EQUAL payload, more passes => lower G_thru
    a_uni = analyze("mul", [(4, 8)] * 8)             # uniform mul L=4: E+=32, D=1
    a_mix = analyze("mul", [(8, 16), (8, 16)] + [(4, 8)] * 4)  # E+=32 too, D=2
    w4 = (a_uni["Eplus"] == a_mix["Eplus"] and a_mix["D"] > a_uni["D"]
          and a_mix["g_thru"] < a_uni["g_thru"])

    # 5. conflation: equal bias-shadow, different D => same quotient, different throughput
    c1 = analyze("mul", [(8, 16)] * 4)                # mul L=8 uniform: bias 0, D=1
    c2 = analyze("mul", [(8, 16), (8, 16)] + [(4, 8)] * 4)  # bias 0 too, D=2
    same_bias = (c1["bias"] == c2["bias"] == 0)
    diff_thru = not isclose(c1["g_thru"], c2["g_thru"])
    w5 = same_bias and diff_thru and (c1["D"] != c2["D"])

    # DeMorgan sanity on the nedge ops (NOT(AND)=OR), a few samples
    import random; random.seed(0)
    demorgan = all(isclose(G_NOT(G_AND(x, y)), G_OR(G_NOT(x), G_NOT(y)), rel_tol=1e-9)
                   for x, y in ((random.uniform(.1, 9), random.uniform(.1, 9)) for _ in range(500)))

    print("-" * 96)
    print(f"SWAR-BOUNDARY NEDGE PILOT: "
          f"mass-conserved {w1}; op->region(T/B/F) {w2}; insulation-gate(short kills) {w3}; "
          f"divergence=series-R {w4}; conflation(bias blind to D) {w5}; DeMorgan {demorgan}")
    ok = all((w1, w2, w3, w4, w5, demorgan))
    print(f"\n  {'PASS' if ok else 'FAIL'} — SWAR boundaries model faithfully as a nedge G-Value circuit.")
    print(f"  mass=64 is the conserved register; add/mul/bignum land in crossbar T/B/F by their room rule;")
    print(f"  validity is a SERIES gate (one leaky lane boundary shorts it); divergence is series resistance")
    print(f"  (G=E+/D); and the bias quotient is blind to divergence exactly as el-atlas's quotient is blind")
    print(f"  to mass. The nedge calculus RANKS the config space (sorted G=E+/D column) -- the live")
    print(f"  symmetry-breaker weigher the kernel-performance control loop needs.")
