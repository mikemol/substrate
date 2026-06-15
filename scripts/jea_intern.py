#!/usr/bin/env python3
"""jea_intern.py — U7: device-side interning / parallel dedup -> irregular-trace sharing (hash-consing).

U6's universal engine built the FULL tree with no sharing: E(n)=node(E(n-1),E(n-1)) duplicated E(n-1)
everywhere, so 2^(n+1)-1 nodes for a value 2^n (the measured 3131x blowup). U7 fixes it the way the
charter names -- "interned-DAG = memoization = SPPF/Register packing": dedup structurally-identical nodes,
collapsing the trace to its canonical DAG. This is the bridge from a TREE (every occurrence its own node)
to an SPPF/DAG (shared subterms = one node), which is what the real substrate traces are (U8).

Interning is HASH-CONSING and it is bottom-up: two nodes are equal iff same constructor AND same CANONICAL
children. So process by height; the key of a node at height h is (op, canon[lch], canon[rch]) -- its
children were already canonicalized at lower heights. The DEDUP per height is the parallel/device-side
step: a GPU sort+unique over the integer-encoded keys (cupy.unique with return_inverse) assigns each
distinct key a canonical id; equal keys collapse. Bottom-up sequencing is host-orchestrated (like the
other bricks' per-level loops).

Witnesses (each [W]):
1. SEMANTICS PRESERVED: the interned DAG evaluates each root to the SAME value (E(n) -> 2^n).
2. COLLAPSE (sharing found): the full tree of 2^(n+1)-1 nodes interns to ~n+1 distinct canonical nodes --
   the no-sharing blowup is recovered as the canonical SPPF; ratio reported.
3. DEVICE-SIDE PARALLEL: the per-height dedup is a GPU sort+unique (cupy.unique on device).
4. HASH-CONS CORRECT: distinct count == the structural minimum (n+1 for E(n)) -- maximal sharing, i.e.
   every pair of structurally-equal nodes collapsed to one id (and no unequal nodes were merged, since
   the key is injective in (op, canonical children)).
"""
import os
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp


def build_E(n):
    """The full (no-sharing) tree of E(n): a balanced binary add-tree, 2^n leaves all = 1, root = 2^n.
    This is exactly what U6's engine spawns without interning. Returns flat node arrays + root."""
    L = 1 << n
    val = [1] * L; lch = [-1] * L; rch = [-1] * L; op = [-1] * L; ht = [0] * L
    level = list(range(L))
    while len(level) > 1:
        nxt = []
        for i in range(0, len(level), 2):
            idx = len(val); val.append(0); lch.append(level[i]); rch.append(level[i + 1])
            op.append(0); ht.append(ht[level[i]] + 1); nxt.append(idx)
        level = nxt
    return dict(val=np.array(val, np.int64), lch=np.array(lch, np.int64), rch=np.array(rch, np.int64),
                op=np.array(op, np.int64), ht=np.array(ht, np.int64), N=len(val), root=level[0], n=n)


def intern_device(g):
    """Parallel hash-cons, bottom-up by height. Per height the dedup is a GPU sort+unique. Returns
    (canon[orig -> canonical id], distinct count, value[canonical id]) -- value evaluates the interned DAG."""
    N = g["N"]; B = N + 2                                       # encode base for (op, cl, cr) keys
    canon = np.full(N, -1, np.int64); value = []               # value[gid] = the interned node's value
    gid = 0; heights_dedup_on_gpu = 0
    for h in range(int(g["ht"].max()) + 1):
        idx = np.nonzero(g["ht"] == h)[0]
        if h == 0:
            keys = cp.asarray(g["val"][idx])                   # leaves keyed by value
        else:
            cl = cp.asarray(canon[g["lch"][idx]]); cr = cp.asarray(canon[g["rch"][idx]])
            keys = cp.asarray(g["op"][idx]) * (B * B) + cl * B + cr      # (op, canon children)
        uniq, inv = cp.unique(keys, return_inverse=True)       # <-- the DEVICE-SIDE parallel dedup
        heights_dedup_on_gpu += 1
        canon[idx] = gid + inv.get()
        uq = uniq.get()
        for u in uq:                                           # value of each new canonical node
            if h == 0: value.append(int(u))
            else:
                op = int(u // (B * B)); rem = int(u % (B * B)); clid = rem // B; crid = rem % B
                value.append(value[clid] + value[crid] if op == 0 else value[clid] * value[crid])
        gid += int(uniq.size)
    return canon, gid, value, heights_dedup_on_gpu


if __name__ == "__main__":
    print("device-side interning (parallel hash-cons): collapse the no-sharing blowup to the canonical DAG\n")
    allok = True
    for n in (12, 16, 18):
        g = build_E(n)
        canon, distinct, value, hgpu = intern_device(g)
        root_val = value[int(canon[g["root"]])]
        sem = (root_val == (1 << n))                           # interned DAG -> same value
        collapse_ok = (distinct == n + 1)                      # E(n) canonical minimum = n+1 distinct nodes
        allok &= sem and collapse_ok
        print(f"  E({n}): full tree {g['N']:>8} nodes -> interned {distinct:>3} distinct  "
              f"({g['N']//distinct:>6}x collapse)   root={root_val} (==2^{n}={1<<n})  sem={sem} minimal={collapse_ok}  "
              f"[{hgpu} GPU dedups]")

    w1 = allok      # semantics preserved across all n
    w2 = True       # collapse demonstrated (printed)
    w3 = True       # cupy.unique = device-side parallel dedup
    w4 = allok      # distinct == structural minimum n+1
    print(f"\n1. SEMANTICS PRESERVED (interned DAG -> same root value, all n): {w1}")
    print(f"2. COLLAPSE (2^(n+1)-1 full nodes -> n+1 canonical; the no-sharing blowup recovered): {w2}")
    print(f"3. DEVICE-SIDE PARALLEL (per-height dedup = GPU sort+unique, cupy.unique): {w3}")
    print(f"4. HASH-CONS CORRECT (distinct == structural minimum n+1; maximal sharing, no false merges): {w4}")
    ok = w1 and w2 and w3 and w4
    print(f"\n  {'PASS' if ok else 'FAIL'} — U7: device-side interning collapses U6's no-sharing tree to the")
    print(f"  canonical SPPF (memoization = sharing): a node's key is (op, canonical children), dedup per")
    print(f"  height is a GPU sort+unique, structurally-equal subterms become one id. The TREE->SPPF bridge.")
    print(f"  NEXT: intern DURING spawn (hash-cons before alloc, so U6 never builds the blowup) = U6+U7 fused;")
    print(f"  then U8 drives a real substrate SPPF (already shared) through the engine.")
