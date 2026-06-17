#!/usr/bin/env python3
"""jea_branchless.py — the BRANCHLESS decision vocabulary: a choice is ARITHMETIC over a computed coefficient, never
control flow. A predicate is 0/1 (a setp, not a branch); a multi-corner knob is the COUNT of thresholds exceeded
(an index); the selection is a table load. No `if`/ternary on a knob -> no warp divergence on the GPU, and the
decision logic becomes DATA/ARITHMETIC that ports to the on-device supervisor and composes into the same graph-fold
as the eval (the Δ-Ω-onegraph prereq: the circuit/relaxation solve is the same arithmetic, not a separate branchy one).

[[feedback_judgement_is_demechanization]]: a branch is a FROZEN judgement; branchless is a corner-of-a-parameter
selected by an arithmetic index -- the [[feedback_coordinate_to_geometry]] / [[feedback_noise_floor_is_flat_region]]
form (the option set is the corners; the index is the live-solved coefficient).

Primitives (all pure arithmetic; each compiles to predicate/select, no control flow):
  step(p)              : a PREDICATE as 0/1.
  tier(v, ts)          : # thresholds in ts that v exceeds -> the corner index (e.g. carrier = tier(bits,(64,128))).
  pick(opts, i)        : corner select by arithmetic index (a load).
  corner3(a, b, noise) : 3-corner index over two MEASURED costs -> 0=first cheaper, 1=second cheaper, 2=tie(<=noise)
                         -- the flat-region-aware argmin as arithmetic (the g* / eval-strategy choice shape).
"""

def step(p):  return 1 if p else 0                      # predicate -> 0/1 (setp/predicate, not a branch)
def tier(v, ts):  return sum(step(v > t) for t in ts)   # corner index = # thresholds exceeded (monotone, branch-free)
def pick(opts, i):  return opts[i]                      # corner select by index (a table load)

def corner3(a, b, noise):
    """Flat-region-aware 2-cost argmin as an arithmetic index: 0=a cheaper, 1=b cheaper, 2=tie (|a-b|<=noise).
    tie selects corner 2; else step(b<a) selects 0/1. No control flow -- index = tie*2 + (1-tie)*step(b<a)."""
    tie = step(abs(a - b) <= noise); win = step(b < a)
    return tie * 2 + (1 - tie) * win

def argmax(vals):
    """Branchless argmax index over a fixed small set: a tournament of step/pick (predicate-select), no `if`.
    bi/bv updated by index-select each step; ties -> earlier. (The binding-edge sensitivity = argmax over relaxation
    gains; on the GPU a fixed-size argmax unrolls to predicated selects -- no divergence.)"""
    bi, bv = 0, vals[0]
    for j in range(1, len(vals)):
        t = step(vals[j] > bv); bi = pick((bi, j), t); bv = pick((bv, vals[j]), t)
    return bi


if __name__ == "__main__":
    print("jea_branchless: a choice is ARITHMETIC over a computed coefficient (predicate->index->table load), no branch\n")

    # W1: tier reproduces the carrier ternary over a sweep (u64/u128/byte-limb by bits), branch-free
    def carrier_branchy(bits): return "u64" if bits <= 64 else ("u128" if bits <= 128 else "byte-limb")
    C = ("u64", "u128", "byte-limb")
    w1 = all(pick(C, tier(b, (64, 128))) == carrier_branchy(b) for b in range(0, 400, 3))
    print(f"  W1  tier/pick == the carrier ternary across bits 0..400 (carrier = pick(C, tier(bits,(64,128)))): {w1}")

    # W2: step reproduces the bang-bang knobs (mode, repr) over a sweep
    def mode_branchy(Cc): return "eager" if 252.0*Cc > 216.0 else "lazy"
    def repr_branchy(f):  return "value" if (8-7*f) < (1+7*f) else "trace"
    MODE = ("lazy", "eager"); REPR = ("trace", "value")
    w2 = (all(pick(MODE, step(252.0*c > 216.0)) == mode_branchy(c) for c in [i/100 for i in range(101)])
          and all(pick(REPR, step((8-7*f) < (1+7*f))) == repr_branchy(f) for f in [i/100 for i in range(101)]))
    print(f"  W2  step/pick == the mode/repr bang-bang ternaries (knob = pick(OPTS, step(predicate))): {w2}")

    # W3: corner3 reproduces the flat-aware 2-cost argmin (the g* / eval-strategy choice) over samples
    def choose_branchy(a, b, noise):
        if abs(a-b) <= noise: return 2
        return 1 if b < a else 0
    import random
    rr = random.Random(3); samples = [(rr.uniform(0, 5), rr.uniform(0, 5), rr.uniform(0, 1)) for _ in range(2000)]
    w3 = all(corner3(a, b, n) == choose_branchy(a, b, n) for a, b, n in samples)
    print(f"  W3  corner3 == the flat-aware 2-cost argmin (0/1/2 = first/second/tie) over 2000 samples: {w3}")

    # W4: argmax (the binding-edge sensitivity select) == Python max over random gain-vectors, branch-free tournament
    rr2 = random.Random(4); w4 = True
    for _ in range(1000):
        v = [rr2.uniform(-5, 5) for _ in range(rr2.randint(2, 5))]
        w4 = w4 and (argmax(v) == max(range(len(v)), key=lambda i: v[i]))
    print(f"  W4  argmax (tournament of step/pick) == Python argmax over 1000 random gain-vectors (the binding-edge select): {w4}")

    ok = w1 and w2 and w3 and w4
    print(f"\n  {'PASS' if ok else 'FAIL'} — the branchless vocabulary: every selection is a predicate (0/1) summed into")
    print(f"  an index, then a table load -- arithmetic, no control flow (no GPU divergence). Reproduces the navigator's")
    print(f"  ternary/if knobs EXACTLY. Consumed by jea_navigator (carrier/mode/repr/g/eval-strategy) + jea_resident")
    print(f"  (eval_frontier dispatch). Ports verbatim to the on-device supervisor; composes into Δ-Ω-onegraph's fold.")
