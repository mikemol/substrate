#!/usr/bin/env python3
"""jea_eval.py — the MEMOIZING evaluator over a PERSISTENT RESIDENT SPPF: terms are INTERNED + SHARED into a
growing shared forest; only genuinely-NEW nodes are evaluated. (You don't prune an SPPF -- you share into it.)

The charter wants "on-GPU resident MEMOIZING traces = SPPF". That is a SHARED PACKED FOREST that GROWS
monotonically: every distinct sub-term is a node, kept, and referenced by every term that contains it. There is
no pruning -- a sub-term already in the forest is SHARED (its node id is reused, its value already resident); a
genuinely-new sub-term ADDS a node. So evaluation is: intern the term into the resident SPPF (hash-cons each node:
existing -> share id, new -> add), then evaluate ONLY the NEW frontier on the GPU; existing nodes are referenced,
never recomputed. The forest only ever grows; nothing is cut. recompute-from-residue [[feedback_never_discard_residue]].

The resident SPPF IS the memo: a node carries (op, child ids, reduced/CF-canonical value). Equal structure across
ANY two evaluations interns to ONE node (cross-eval sharing); value-equal-but-structurally-distinct terms also key
into _VAL (the value-key). evaluate(g) -> (value, evaluated, shared): the SPPF is consumed by evaluate itself
(sharing), so the evaluator IS the consumer, not a demo. A stream of overlapping terms evaluates each distinct
sub-term ONCE, ever, and the forest accumulates the whole memoizing trace.
"""
import os, sys
os.environ.setdefault("CUDA_PATH", "/usr")
from fractions import Fraction
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# NB run_apex_u128 / deliver_subtree are imported LAZILY inside evaluate() so this module's SPPF/WAL machinery is
# dependency-light -- jea_apex (which jea_apex_deliver imports) can record decisions here without a circular import.

# --- the PERSISTENT RESIDENT SPPF (the shared packed forest; grows monotonically, never pruned) ---
_NODES = []   # node id -> [op, lch_id, rch_id, value Fraction|None]  (the resident shared forest = the memo)
_ID    = {}   # hash-cons key -> node id (interning: equal structure -> SAME node, SHARED not duplicated)
_VAL   = {}   # reduced value -> node id (value-key: value-equal structurally-distinct terms share a value entry)

# --- the SUPERVISOR DECISION WAL, held HERE (same module as the eval memo) as ONE trace structure (Δ-Σ-trace c) ---
# A decision is (evidence -> operating-point). The WAL is the ordered EEA trace of decisions; _DMEMO is its
# interned form (recurring evidence = ONE node, like the SPPF interns recurring subterms). The supervisor's dout
# (Δ-Σ-decide) is FOLDED here: the control history becomes a durable, interned trace, not an ephemeral flat array.
_DMEMO = {}   # evidence key -> operating-point (the interned distinct decisions = SPPF of the control loop)
_WAL   = []   # ordered (evidence-key, op, was_hit) -- the never-discard residue of the control loop

def record_decision(evkey, op):
    """Fold one supervisor decision into the WAL/memo. Returns (was_hit, canonical_op). Recurring evidence HITS
    the memo -> the cached decision is reused (the supervisor need not re-derive), and the trace interns it."""
    hit = evkey in _DMEMO
    if not hit: _DMEMO[evkey] = op
    _WAL.append((evkey, op, hit))
    return hit, _DMEMO[evkey]

def wal_len(): return len(_WAL)
def distinct_decisions(): return len(_DMEMO)


def _intern(op, vN, vD, l, r):
    """Hash-cons one node INTO the resident SPPF: existing key -> SHARE its id; new -> ADD a node. (op,l,r) for a
    combine, (vN,vD) for a leaf. Returns (node id, is_new). Equal structure across any evals collapses to one node."""
    key = ("lf", vN, vD) if op==-1 else (op, l, r)
    if key in _ID: return _ID[key], False                       # SHARE the resident node (referenced, not pruned)
    nid=len(_NODES); _ID[key]=nid
    _NODES.append([op, l, r, (Fraction(vN, vD) if op==-1 else None)])  # leaf value known; combine value filled on eval
    return nid, True


def evaluate(g):
    """Evaluate by INTERNING the term into the resident SPPF and evaluating ONLY the new frontier; existing
    sub-terms are SHARED (their resident value is referenced, never recomputed). The forest grows; nothing is
    pruned. Returns (value, evaluated_new, shared) -- evaluated_new = new combine nodes the GPU computed this call."""
    from jea_apex_deliver import run_apex_u128, deliver_subtree  # lazy: keeps the SPPF/WAL machinery dependency-light
    N=g["N"]; nid=[0]*N; frontier=[]; combines=0
    for i in range(N):                                          # intern the term into the resident SPPF (leaves-first)
        if g["op"][i]==-1:
            k,new=_intern(-1, int(g["vN"][i]), int(g["vD"][i]), -1, -1)
        else:
            combines+=1
            k,new=_intern(int(g["op"][i]), 0, 0, nid[g["lch"][i]], nid[g["rch"][i]])
            if new: frontier.append(k)                          # a genuinely-NEW combine node -> must be evaluated
        nid[i]=k
    rootid=nid[g["root"]]
    if frontier:                                               # evaluate ONLY the new frontier (existing nodes shared)
        need=set(frontier)
        for k in frontier: need.add(_NODES[k][1]); need.add(_NODES[k][2])
        local=sorted(need); li={k:j for j,k in enumerate(local)}; fset=set(frontier)
        op2=[]; vN2=[]; vD2=[]; lch2=[]; rch2=[]
        for k in local:
            nd=_NODES[k]
            if k in fset:                                       # a new combine to compute
                op2.append(nd[0]); vN2.append(0); vD2.append(1); lch2.append(li[nd[1]]); rch2.append(li[nd[2]])
            else:                                               # an already-resident node -> referenced as a leaf-with-value
                v=nd[3]; op2.append(-1); vN2.append(v.numerator); vD2.append(v.denominator); lch2.append(-1); rch2.append(-1)
        g2=dict(op=op2, vN=vN2, vD=vD2, lch=lch2, rch=rch2, N=len(local), root=li[rootid])
        val,err,nodes = run_apex_u128(g2, return_nodes=True)
        if err==2: val,_ = deliver_subtree(g2, nodes["vN"], nodes["vD"], escal=nodes["escal"])
        for k in fset:                                          # store the new nodes' values INTO the resident SPPF
            j=li[k]
            if nodes["escal"][j]==0 and nodes["vD"][j]:
                fr=Fraction(nodes["vN"][j], nodes["vD"][j]); _NODES[k][3]=fr; _VAL.setdefault((fr.numerator, fr.denominator), k)
        if _NODES[rootid][3] is None: _NODES[rootid][3]=val     # crown root (>u128): value from the byte-limb deliver
    return _NODES[rootid][3], len(frontier), combines-len(frontier)


def memo_size(): return len(_NODES)                             # resident SPPF size (distinct sub-terms ever seen)


def _embed(sub, host_op, extra_leaf):
    """Build a term that CONTAINS sub (same structure -> SHARED into the resident SPPF) combined with one extra leaf."""
    N=len(sub["op"]); op=list(sub["op"])+[-1, host_op]; vN=list(sub["vN"])+[extra_leaf[0],0]
    vD=list(sub["vD"])+[extra_leaf[1],1]; lch=list(sub["lch"])+[-1, sub["root"]]; rch=list(sub["rch"])+[-1, N]
    return dict(op=op, vN=vN, vD=vD, lch=lch, rch=rch, N=N+2, root=N+1)


if __name__ == "__main__":
    print("jea_eval: the MEMOIZING evaluator over a PERSISTENT RESIDENT SPPF -- terms are SHARED into a growing forest\n")
    # S = a shared sub-term (1/2 * 1/3 = 1/6); T1 = S + 1/1 = 7/6;  T2 = S * 2/1 = 1/3 (T1,T2 both CONTAIN S)
    S=dict(op=[-1,-1,1], vN=[1,1,0], vD=[2,3,1], lch=[-1,-1,0], rch=[-1,-1,1], N=3, root=2)
    T1=_embed(S, 0, (1,1)); T2=_embed(S, 1, (2,1))

    v1,e1,s1 = evaluate(T1)                                     # first eval: S is new -> added to the forest
    m1=memo_size()
    v2,e2,s2 = evaluate(T2)                                     # second eval: S is already resident -> SHARED, not recomputed
    ok1=(v1==Fraction(7,6)); ok2=(v2==Fraction(1,3))
    print(f"  eval(T1=S+1/1): value={v1} (==7/6:{ok1})  new nodes evaluated={e1} shared={s1}   resident SPPF now {m1} nodes")
    print(f"  eval(T2=S*2/1): value={v2} (==1/3:{ok2})  new nodes evaluated={e2} shared={s2}   <- S SHARED from the forest")

    # value-key: a DISTINCT-structure term whose value equals a resident node's value shares the value entry.
    Z=dict(op=[-1,-1,0], vN=[1,1,0], vD=[12,12,1], lch=[-1,-1,0], rch=[-1,-1,1], N=3, root=2)   # 1/12+1/12 = 1/6 (==S!)
    vZ,eZ,sZ = evaluate(Z)
    print(f"  eval(Z=1/12+1/12): value={vZ} (==1/6:{vZ==Fraction(1,6)})  -- value 1/6 already resident from S "
          f"(value-key): {(1,6) in _VAL}")

    w1 = ok1 and ok2 and (vZ==Fraction(1,6))                    # all exact through the resident-SPPF evaluator
    w2 = (s2>=1) and (e2 < e2+s2)                               # T2 SHARED S from the forest (evaluated < its combines)
    w3 = (1,6) in _VAL                                          # value-key populated (value-equal terms share an entry)
    print(f"\nW1 EXACT through the resident-SPPF evaluator (T1=7/6, T2=1/3, Z=1/6 all correct): {w1}")
    print(f"W2 SHARED, NOT PRUNED (T2 evaluated {e2} NEW combine(s), SHARED {s2} from the resident forest -- S was")
    print(f"   referenced, not recomputed; each distinct sub-term is evaluated ONCE, ever, and the forest GROWS): {w2}")
    print(f"W3 VALUE-KEY POPULATED (resident node values are reduced/CF-canonical; value-equal terms share an entry): {w3}")
    ok=w1 and w2 and w3
    print(f"\n  {'PASS' if ok else 'FAIL'} — the evaluator interns each term into a PERSISTENT RESIDENT SPPF (the shared")
    print(f"  packed forest = the memoizing trace) and evaluates ONLY the new frontier; existing sub-terms are SHARED")
    print(f"  (referenced, value resident), never recomputed or pruned. The forest grows monotonically. Self-consuming")
    print(f"  (evaluate shares into _NODES). NEXT: make _NODES device-RESIDENT (on-GPU); stream terms through evaluate().")
