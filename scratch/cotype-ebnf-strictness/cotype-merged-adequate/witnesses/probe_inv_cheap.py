# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
# PRICE-IS-RIGHT compute: Φ_p multiplicity = dim ker(Φ_p(T)) = nullity, NOT full symbolic factorization.
# Pay for the ONE number, not the whole degree-91 spectrum. Reach the points behind the old "wall".
#
# PUMP-COMPATIBLE (paperkit liveness protocol): exposes initial/pump/parse/serialize/deserialize so the
# paperkit driver can run the (p,c) sweep in resumable increments under a budget — one (p,c) per pump().
# The heavy object T is rebuilt INSIDE pump and never crosses the serialization boundary; state is just a
# cursor + accumulated scalar results (JSON-able). Run bare (python3 probe_inv_cheap.py) it still does the
# full sweep and prints — the cold cmd: fallback. Graceful degradation: both interfaces, one file.
import os,sys; sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import species_np as snp
import numpy as np
import json

# ── the actual computation (unchanged, the price-is-right nullity) ────────────────────────────────
def phi_mult_cheap(perm,nv,p):
    edges,eidx,C,Cpinv=snp.cyc_setup(nv)
    Tn=snp.rep(perm,edges,eidx,C,Cpinv).astype(complex)
    coeffs,phi=snp.phi_coeffs_prime(p)
    d=len(coeffs)-1
    powers=[np.eye(Tn.shape[0],dtype=complex)]
    for i in range(d): powers.append(powers[-1]@Tn)
    M=sum(coeffs[i]*powers[d-i] for i in range(d+1))
    nullity=M.shape[0]-np.linalg.matrix_rank(M, tol=1e-6)
    return (nullity//phi if phi else nullity), nullity, phi

def build_c(c,p,nv):
    perm=list(range(nv))
    for j in range(c):
        cyc=list(range(j*p,(j+1)*p))
        for i in range(p): perm[cyc[i]]=cyc[(i+1)%p]
    return tuple(perm)

# the sweep, and the known-good values that make this a CHECK (not just a computation)
CASES=[(2,2),(2,3),(2,4),(3,1),(3,2),(3,3),(3,4),(5,1),(5,2),(5,3),(7,1),(7,2)]
import json as _json, os as _os
_gp=_os.path.join(_os.path.dirname(_os.path.realpath(__file__)),"..","data","inv_cheap_gold.json")
try:
    GOLD={tuple(int(x) for x in k.split(",")): v for k,v in _json.load(open(_gp)).items()}
except (FileNotFoundError, OSError):
    GOLD={}  # prose-bound checks supply their own gold from the claim; the file is now redundant

# ── pump protocol: one (p,c) per increment; T rebuilt inside, never serialized ────────────────────
def initial():
    return {"cursor": 0, "results": []}   # results: list of [p, c, mult]

def pump(state):
    i = state["cursor"]
    if i >= len(CASES):
        return state                      # done; idempotent past the end
    p, c = CASES[i]
    nv = c * p
    mult, _, _ = phi_mult_cheap(build_c(c, p, nv), nv, p)   # heavy T built & discarded here
    return {"cursor": i + 1, "results": state["results"] + [[p, c, int(mult)]]}

def parse(state):
    done = state["cursor"] >= len(CASES)
    # verdict: every computed mult matches GOLD. Counterexample fails fast (caller policy).
    bad = [r for r in state["results"] if GOLD.get((r[0], r[1])) != r[2]]
    out = {"done": done, "results": state["results"],
           "progress": f'{state["cursor"]}/{len(CASES)}'}
    if bad:
        out["verdict"] = "FAIL"; out["counterexample"] = bad[0]
    elif done:
        out["verdict"] = "PASS"
    return out

def serialize(state): return json.dumps(state, sort_keys=True)
def deserialize(blob): return json.loads(blob)

# ── cold fallback: bare run does the full sweep and prints (the existing cmd: contract) ────────────
if __name__ == "__main__":
    st = initial()
    while not parse(st)["done"]:
        st = pump(st)
    m = parse(st)
    print("PRICE-IS-RIGHT: Φ_p mult via nullity(Φ_p(T))/φ(p) — pay for ONE number, reach behind the wall.")
    print(f"{'p':>3} {'c':>3} {'Φ_p mult':>9}")
    for p, c, mult in m["results"]:
        flag = "" if GOLD.get((p, c)) == mult else f"  != GOLD {GOLD.get((p,c))}"
        print(f"{p:>3} {c:>3} {mult:>9}{flag}")
    print(f"verdict: {m.get('verdict','?')}")
    sys.exit(0 if m.get("verdict") == "PASS" else 1)
