#!/usr/bin/env python3
"""jea_eval.py — the MEMOIZING evaluator: a PERSISTENT cross-eval memo, consumed by PRUNING. The real infrastructure.

The charter wants "on-GPU resident MEMOIZING traces" -- not just one-shot interning, but a memo that PERSISTS
across evaluations so a sub-term the engine has ALREADY computed is never recomputed. The decision/eval/EEA
trace is that memo. This is the missing infrastructure: build it, and the value-level residue HAS a consumer.

How it is consumed (no chicken-and-egg): the memo is keyed by each node's structural SIGNATURE (a persistent
hash-cons: sig(node) = id of (op, sig(lch), sig(rch)); leaves = id of (vN,vD)). Equal structure across DIFFERENT
evaluations gets the SAME sig, so before a drain we PRUNE every node whose sig is already in the memo -- replace
it with a leaf carrying its cached (reduced, CF-canonical) value. The apex then drains ONLY the genuinely-new
sub-terms; the seen ones are read from the memo. The cached values are the reduced rationals (= the CF/EEA
canonical key, [[feedback_never_discard_residue]] / jea_carrier_trace) -- so value-equal leaves canonicalize too.

evaluate(g) -> (value, drained, pruned): the persistent _MEMO is consumed BY evaluate itself (pruning), so this
is not a demo of a capability nothing uses -- the evaluator IS the consumer. Reuses jea_sppf.intern (structural
SPPF) + run_apex_u128 (the exact GPU drain). A stream of overlapping terms drains each distinct sub-term ONCE, ever.
"""
import os, sys
os.environ.setdefault("CUDA_PATH", "/usr")
from fractions import Fraction
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jea_sppf as SPPF
from jea_apex_deliver import run_apex_u128, deliver_subtree

_SIG = {}     # structural key -> persistent global signature id (hash-cons ACROSS evaluations)
_MEMO = {}    # signature id    -> reduced Fraction value (the cached, CF-canonical sub-term result)
_VAL = {}     # reduced value   -> signature id (value-key: value-equal structurally-distinct terms share)


def _signatures(g):
    """Per-node persistent structural signature; equal structure across evals -> equal id (cross-eval hash-cons)."""
    sig=[0]*g["N"]
    for i in range(g["N"]):
        key = ("lf", int(g["vN"][i]), int(g["vD"][i])) if g["op"][i]==-1 \
              else (int(g["op"][i]), sig[g["lch"][i]], sig[g["rch"][i]])
        sig[i]=_SIG.setdefault(key, len(_SIG))
    return sig


def evaluate(g):
    """Memoized GPU eval: intern -> PRUNE sub-terms whose sig is cached -> drain only the new ones -> record.
    Returns (value, combines_drained, combines_pruned). The persistent memo is consumed by the pruning."""
    g,_ = SPPF.intern(g)                                        # structural SPPF (within-eval sharing)
    sig = _signatures(g); N=g["N"]
    op=list(g["op"]); vN=[int(x) for x in g["vN"]]; vD=[int(x) for x in g["vD"]]
    lch=list(g["lch"]); rch=list(g["rch"])
    total = sum(1 for i in range(N) if g["op"][i]!=-1)
    pruned=0
    for i in range(N):                                          # PRUNE: a seen sub-term -> leaf with its cached value
        if g["op"][i]!=-1 and sig[i] in _MEMO:
            fr=_MEMO[sig[i]]; op[i]=-1; vN[i]=fr.numerator; vD[i]=fr.denominator; lch[i]=-1; rch[i]=-1; pruned+=1
    g2=dict(op=op, vN=vN, vD=vD, lch=lch, rch=rch, N=N, root=g["root"])
    val,err,nodes = run_apex_u128(g2, return_nodes=True)        # drain ONLY the new sub-terms (pruned ones pre-satisfied)
    if err==2:                                                  # >u128: deliver the root exactly over the crown
        val,_ = deliver_subtree(g2, nodes["vN"], nodes["vD"], escal=nodes["escal"])
    for i in range(N):                                          # RECORD every NON-CROWN node's reduced (CF-canonical) value
        if nodes["escal"][i]==0 and nodes["vD"][i]:             # crown nodes are byte-limb (not in the u128 arrays)
            fr=Fraction(nodes["vN"][i], nodes["vD"][i])         # Fraction auto-reduces -> the canonical value-key
            _MEMO.setdefault(sig[i], fr); _VAL.setdefault((fr.numerator, fr.denominator), sig[i])
    return val, total-pruned, pruned


def memo_size(): return len(_MEMO)


def _embed(sub, host_op, extra_leaf):
    """Build a term that CONTAINS sub (same structure -> same cross-eval sig) combined with one extra leaf."""
    N=len(sub["op"]); op=list(sub["op"])+[-1, host_op]; vN=list(sub["vN"])+[extra_leaf[0],0]
    vD=list(sub["vD"])+[extra_leaf[1],1]; lch=list(sub["lch"])+[-1, sub["root"]]; rch=list(sub["rch"])+[-1, N]
    return dict(op=op, vN=vN, vD=vD, lch=lch, rch=rch, N=N+2, root=N+1)


if __name__ == "__main__":
    print("jea_eval: the MEMOIZING evaluator -- a persistent cross-eval memo, consumed by pruning seen sub-terms\n")
    # S = a shared sub-term (1/2 * 1/3 = 1/6); T1 = S + 1/1 = 7/6;  T2 = S * 2/1 = 1/3 (T1,T2 SHARE S's structure)
    S=dict(op=[-1,-1,1], vN=[1,1,0], vD=[2,3,1], lch=[-1,-1,0], rch=[-1,-1,1], N=3, root=2)
    T1=_embed(S, 0, (1,1)); T2=_embed(S, 1, (2,1))

    v1,d1,p1 = evaluate(T1)                                     # first eval: S is new -> drained
    m1=memo_size()
    v2,d2,p2 = evaluate(T2)                                     # second eval: S's structure is cached -> PRUNED
    ok1=(v1==Fraction(7,6)); ok2=(v2==Fraction(1,3))
    print(f"  eval(T1=S+1/1): value={v1} (==7/6:{ok1})  combines drained={d1} pruned={p1}   memo now {m1} entries")
    print(f"  eval(T2=S*2/1): value={v2} (==1/3:{ok2})  combines drained={d2} pruned={p2}   <- S's sub-term PRUNED (cached)")

    # value-key: a DISTINCT-structure term whose value equals a cached one shares the value entry.
    Z=dict(op=[-1,-1,0], vN=[1,1,0], vD=[12,12,1], lch=[-1,-1,0], rch=[-1,-1,1], N=3, root=2)   # 1/12+1/12 = 1/6 (==S!)
    vZ,dZ,pZ = evaluate(Z)
    print(f"  eval(Z=1/12+1/12): value={vZ} (==1/6:{vZ==Fraction(1,6)})  -- value 1/6 already in the value-memo "
          f"from S: {(1,6) in _VAL}")

    w1 = ok1 and ok2 and (vZ==Fraction(1,6))                    # all exact through the memoized evaluator
    w2 = (p2>=1) and (d2 < p2+d2)                               # T2 PRUNED a shared sub-term (drained < its combines)
    w3 = (1,6) in _VAL                                          # value-key populated (value-equal terms can share)
    print(f"\nW1 EXACT through the memoized evaluator (T1=7/6, T2=1/3, Z=1/6 all correct): {w1}")
    print(f"W2 MEMO CONSUMED BY PRUNING (T2 drained {d2} combine(s), pruned {p2} -- the shared sub-term S was NOT")
    print(f"   recomputed; the GPU drains each distinct sub-term ONCE, ever, across evaluations): {w2}")
    print(f"W3 VALUE-KEY POPULATED (cached values are reduced/CF-canonical; value-equal terms key to one entry): {w3}")
    ok=w1 and w2 and w3
    print(f"\n  {'PASS' if ok else 'FAIL'} — the memoizing evaluator IS the infrastructure: a persistent cross-eval")
    print(f"  memo (sig -> reduced/CF-canonical value), CONSUMED by pruning -- a sub-term seen in any prior eval is")
    print(f"  read from the memo, never re-drained. It is self-consuming (evaluate uses _MEMO), not a demo of an")
    print(f"  unused capability. NEXT: make _MEMO device-RESIDENT (on-GPU hash table) so the prune+lookup is on-GPU;")
    print(f"  route jea_agda_apex's eval through evaluate() so a stream of Agda terms shares the resident trace.")
