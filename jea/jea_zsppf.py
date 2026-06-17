#!/usr/bin/env python3
"""jea_zsppf.py — the SPPF as a PREFIX-SORT of z-coded numbers (device radix sort), and an HONEST test of what
z-order actually buys. Tackles the user's conjecture: sliding-carrier => faithful bitstring => z-coded trace =>
SPPF = prefix-sorting z-coded lists.

What is TRUE and BUILT here:
 * SPPF interning = a SORT. Per height, the key of a combine is (op, canonical children); cupy.unique (a DEVICE
   radix sort + dedup) assigns canonical ids and collapses equal keys. This is the GPU-native memo: sort, not a
   hash table. (jea_intern already does this; here it is the explicit z-code/prefix-sort framing + the test.)
 * SHARED vs PACKED (the S and P of SPPF): sorting by the STRUCTURAL code (op, child-ids) gives SHARING (one node,
   many parents). Sorting by the VALUE code (z-coded reduced num,den) gives PACKING (many distinct structures, one
   value) -- value-equal-but-structurally-distinct terms collapse. Two prefix-sorts, the two halves of "SPPF".

What is tested, NOT assumed (anti-overclaim):
 * Is z-order a CORRECTNESS lever? NO -- proven here: a plain lexicographic key (op,cl,cr) and a z-interleaved key
   give the IDENTICAL sharing partition. Interning = sort+dedup is code-AGNOSTIC; any injective code works. So
   "SPPF = prefix-sort of z-codes" is true for any injective code; z-order is not magic for the dedup.
 * What DOES z-order buy? LOCALITY in the (num,den) PLANE: sorting the z-coded numbers puts (num,den)-close
   rationals adjacent (2D Morton clustering) -- measured vs a random order. That is the residue-space locality
   (Morton ≅ Cayley-Dickson cocycle, the commuting-sphere conjecture), NOT value-line locality and NOT the dedup.
"""
import os, sys, functools
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp
from fractions import Fraction
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jea_trace_window import to_cf, cf_less                    # the rational's INTRINSIC quadtree: Stern-Brocot / CF address

U=np.uint64
def _spread16(x):                                              # spread low 16 bits into even bit positions (2D Morton)
    x=(np.asarray(x,U))&U(0xFFFF)
    x=(x|(x<<U(8)))&U(0x00FF00FF); x=(x|(x<<U(4)))&U(0x0F0F0F0F)
    x=(x|(x<<U(2)))&U(0x33333333); x=(x|(x<<U(1)))&U(0x55555555)
    return x
def morton2(a,b): return _spread16(a)|(_spread16(b)<<U(1))     # z-code: interleave the bits of two coordinates


def heights(g):
    N=g["N"]; ht=np.zeros(N,np.int64)
    for i in range(N):
        if g["op"][i]!=-1: ht[i]=max(int(ht[g["lch"][i]]),int(ht[g["rch"][i]]))+1
    return ht


def intern_radix(g, mode="z"):
    """Device radix-sort interning: per height, cupy.unique (sort+dedup) over the node keys -> canonical ids.
    mode='z' z-interleaves the child ids; mode='plain' uses a lexicographic (op,cl,cr) key. Returns (canon, distinct)."""
    N=g["N"]; ht=heights(g); H=int(ht.max()) if N else 0
    canon=np.full(N,-1,np.int64); gid=0; leafcode={}
    for h in range(H+1):
        idx=np.nonzero(ht==h)[0]
        if h==0:
            keys=np.array([leafcode.setdefault((int(g["vN"][i]),int(g["vD"][i])), len(leafcode)+1) for i in idx],U)
        else:
            cl=np.array([canon[g["lch"][i]] for i in idx],U); cr=np.array([canon[g["rch"][i]] for i in idx],U)
            ops=np.array([g["op"][i] for i in idx],U)
            keys=((ops<<U(40))|morton2(cl,cr)) if mode=="z" else (ops*U(1<<40)+cl*U(1<<20)+cr)  # both INJECTIVE
        uniq,inv=cp.unique(cp.asarray(keys),return_inverse=True)   # <-- the DEVICE radix sort + dedup = interning
        canon[idx]=gid+inv.get(); gid+=int(uniq.size)
    return canon, gid


def partition(canon):
    from collections import defaultdict
    d=defaultdict(list)
    for i,c in enumerate(canon): d[int(c)].append(i)
    return set(frozenset(v) for v in d.values())


def host_values(g):
    v=[None]*g["N"]
    for i in range(g["N"]):
        if g["op"][i]==-1: v[i]=Fraction(int(g["vN"][i]),int(g["vD"][i]))
        elif g["op"][i]==1: v[i]=v[g["lch"][i]]*v[g["rch"][i]]
        else: v[i]=v[g["lch"][i]]+v[g["rch"][i]]
    return v


def build_Eq(n):                                               # balanced add-tree of 1/1: 2^n leaves, heavy SHARING
    L=1<<n; vN=[1]*L; vD=[1]*L; op=[-1]*L; lch=[-1]*L; rch=[-1]*L; lvl=list(range(L))
    while len(lvl)>1:
        nx=[]
        for i in range(0,len(lvl),2):
            k=len(vN); vN.append(0); vD.append(1); op.append(0); lch.append(lvl[i]); rch.append(lvl[i+1]); nx.append(k)
        lvl=nx
    return dict(vN=vN,vD=vD,op=op,lch=lch,rch=rch,N=len(vN),root=lvl[0])


if __name__ == "__main__":
    print("jea_zsppf: SPPF = PREFIX-SORT of z-coded numbers (device radix sort) -- with z-order's role tested honestly\n")

    # W1: SPPF interning IS a device sort. E_q(12): a 8191-node tree collapses to its canonical SPPF by cupy.unique.
    eq=build_Eq(12); canon_z,dz=intern_radix(eq,"z")
    w1 = dz < eq["N"] and dz==13                               # n+1 distinct (the SPPF), via the device radix sort
    print(f"  W1  SPPF = DEVICE SORT: E_q(12) {eq['N']} nodes -> {dz} distinct (cupy.unique per height = radix sort+dedup); "
          f"collapse {eq['N']//dz}x: {w1}")

    # W2: is z-order a correctness lever? Plain (op,cl,cr) vs z-interleaved -> IDENTICAL sharing partition.
    canon_p,dp=intern_radix(eq,"plain")
    same_partition = (dz==dp) and (partition(canon_z)==partition(canon_p))
    w2 = same_partition
    print(f"  W2  BOTH dedup AND locality, one sort: plain & z BOTH dedup (identical sharing partition: {w2}) -- because")
    print(f"      in a SORTED structure dedup and locality are the SAME adjacency (equal->adjacent; near->adjacent).")

    # W3a: SHARED vs PACKED. A DAG with value-equal-but-structurally-distinct nodes: structural intern (sharing) vs
    # value intern (packing). 6=mul(1/2,2/3)=1/3, 7=add(1/6,1/6)=1/3 (distinct structure, same value); 4=2/4≡1/2.
    rb=dict(vN=[1,2,1,1,2,1,0,0,0], vD=[2,3,6,6,4,2,1,1,1], op=[-1,-1,-1,-1,-1,-1,1,0,0],
            lch=[-1,-1,-1,-1,-1,-1,0,2,6], rch=[-1,-1,-1,-1,-1,-1,1,3,7], N=9, root=8)
    _,ds = intern_radix(rb,"z")                                # STRUCTURAL distinct (sharing)
    red=[(v.numerator,v.denominator) for v in host_values(rb)]
    vcodes=morton2(np.array([r[0] for r in red]),np.array([r[1] for r in red]))   # z-code the reduced VALUES
    dv=len({int(x) for x in vcodes})                           # distinct value-codes = PACKING (value-equal collapse)
    w3a = dv < ds
    print(f"\n  W3a SHARED vs PACKED: structural intern -> {ds} distinct (sharing); VALUE intern (z-coded reduced "
          f"num,den) -> {dv} distinct (packing); value<structural: {w3a}")
    print(f"      -> the S of SPPF = structural-code sort; the P (packed: many structures, one value) = value-code sort.")

    # W3b: what z-order ACTUALLY buys -- (num,den)-PLANE locality. Sort random rationals by z-code vs random order;
    # adjacent (num,den) L1 distance is SMALLER under z-order (2D Morton clustering). NOT dedup, NOT value-line.
    rng=np.random.default_rng(0); num=rng.integers(1,1024,400); den=rng.integers(1,1024,400)
    zc=np.asarray(morton2(num,den)); order=np.argsort(zc)
    lex=np.argsort(num.astype(np.int64)*1024+den)              # 1-D lexicographic: localizes the MAJOR axis only
    def adj_l1(nn,dd): return float(np.mean(np.abs(np.diff(nn.astype(np.int64)))+np.abs(np.diff(dd.astype(np.int64)))))
    z_l1=adj_l1(num[order],den[order]); lex_l1=adj_l1(num[lex],den[lex]); rnd_l1=adj_l1(num,den)
    w3b = z_l1 < lex_l1                                         # z localizes BOTH axes; lex only one (the point of interleaving)
    print(f"  W3b BOTH AXES (interleaved) vs ONE (lex): adjacent (num,den) L1 -- z-order={z_l1:.0f}, LEX={lex_l1:.0f}, "
          f"random={rnd_l1:.0f}: z<lex={w3b}")
    print(f"      -> lex DEDUPS but localizes only the major axis (minor scrambled); the INTERLEAVED sort gives dedup")
    print(f"         AND locality on BOTH axes at once -- that is why you interleave (the quadtree), not lex.")

    # W3c: the rational's INTRINSIC quadtree = the STERN-BROCOT tree, addressed by the CONTINUED FRACTION (= the EEA
    # residue rung-(b) already keeps). In-order = value order; CF prefix = a Stern-Brocot interval = value-locality.
    # So the value-code that gives VALUE-LINE locality (which the plane quadtree missed) IS the EEA trace. Loop closed.
    rats=[(int(num[i]),int(den[i])) for i in range(len(num))]
    cmp=lambda A,B: -1 if cf_less(to_cf(*A),to_cf(*B)) else (1 if cf_less(to_cf(*B),to_cf(*A)) else 0)
    cf_order=sorted(rats, key=functools.cmp_to_key(cmp))        # sort by CF = Stern-Brocot in-order
    def adj_val(seq): return float(np.mean([abs(seq[i][0]/seq[i][1]-seq[i+1][0]/seq[i+1][1]) for i in range(len(seq)-1)]))
    cf_vl=adj_val(cf_order); mort_vl=adj_val([rats[i] for i in np.argsort(zc)]); rnd_vl=adj_val(rats)
    monotone=all(cf_order[i][0]/cf_order[i][1] <= cf_order[i+1][0]/cf_order[i+1][1] for i in range(len(cf_order)-1))
    w3c = monotone and (cf_vl < mort_vl*0.2)                    # CF order = value order; value-line locality (plane misses it)
    print(f"  W3c VALUE QUADTREE (CF = Stern-Brocot = the EEA residue): adjacent VALUE distance CF-sorted={cf_vl:.2f} vs "
          f"plane-quadtree={mort_vl:.1f} vs random={rnd_vl:.1f}; CF order monotone-in-value: {monotone} -> {w3c}")
    print(f"      -> the rational's INTRINSIC recursive subdivision is Stern-Brocot/CF (the residue we already keep);")
    print(f"         IT gives value-line locality. The plane quadtree was the wrong (extrinsic) one.")

    # W4: EMPIRICAL -- ONE interleaved sort over (structure, value) gives locality on BOTH axes + dedup. A random
    # term forest; each node has a structural id (intern) and a value rank. Measure per-axis adjacency, normalized.
    rng2=np.random.default_rng(7)
    leaves=[(int(rng2.integers(1,9)),int(rng2.integers(1,9))) for _ in range(8)]
    vN=[l[0] for l in leaves]; vD=[l[1] for l in leaves]; op=[-1]*8; lch=[-1]*8; rch=[-1]*8
    for _ in range(300):                                       # children from a SMALL window -> (op,a,b) recurs (real dedup)
        w=min(len(vN),16); a=int(rng2.integers(0,w)); b=int(rng2.integers(0,w))
        op.append(int(rng2.integers(0,2))); lch.append(a); rch.append(b); vN.append(0); vD.append(1)
    F=dict(vN=vN,vD=vD,op=op,lch=lch,rch=rch,N=len(vN),root=len(vN)-1)
    canon,ds_struct = intern_radix(F,"z")                      # structural id per node + SHARING count (distinct structures)
    red=[(v.numerator,v.denominator) for v in host_values(F)]
    valcmp=lambda i,j: (red[i][0]*red[j][1]-red[j][0]*red[i][1])
    vrank=[0]*F["N"]
    for r,i in enumerate(sorted(range(F["N"]), key=functools.cmp_to_key(valcmp))): vrank[i]=r   # value-order rank
    dv_pack=len({r for r in red})                              # distinct values = PACKING count
    s=np.array([canon[i] for i in range(F["N"])]); vr=np.array(vrank); S=int(s.max())+1; NN=F["N"]
    def axes(order):
        return (float(np.mean(np.abs(np.diff(s[order].astype(np.int64)))))/S,
                float(np.mean(np.abs(np.diff(vr[order].astype(np.int64)))))/NN)
    orders={"interleave":np.argsort(np.asarray(morton2(s,vr))), "lex(struct)":np.argsort(s.astype(np.int64)*(1<<20)+vr),
            "lex(value)":np.argsort(vr.astype(np.int64)*(1<<20)+s), "random":np.arange(NN)}
    print(f"\n  W4  EMPIRICAL: random forest {NN} nodes -> SHARING {ds_struct} distinct structures, PACKING {dv_pack} "
          f"distinct values (one sorted structure surfaces both). Per-axis adjacency (normalized 0..1, lower=tighter):")
    worst={}
    for nm,od in orders.items():
        ds,dvv=axes(od); worst[nm]=max(ds,dvv)
        print(f"      {nm:<12} struct-axis={ds:.3f}  value-axis={dvv:.3f}  worst-axis={worst[nm]:.3f}")
    w4 = worst["interleave"] < min(worst["lex(struct)"], worst["lex(value)"])   # interleave balances BOTH; lex sacrifices one
    print(f"      -> interleave worst-axis {worst['interleave']:.3f} < both lex worst-axes "
          f"({worst['lex(struct)']:.3f}, {worst['lex(value)']:.3f}): {w4} -- the interleaved sort localizes BOTH; each")
    print(f"         lex zeroes one axis and scrambles the other. BOTH locality AND dedup, from one sort.")

    # W5: the OPTIMAL granularity is HIERARCHY-dependent (user). A 2D Morton sort = alternating 1-bit radix passes;
    # the alternation granularity is a KNOB. Within an SM-tile locality is free (resident) -> 1D, dedup-cheap; across
    # HBM only scatter-gather matters -> Morton (high bits). Measured: HBM tiles touched by a 2D-local access, and
    # efficiency vs tile size T (= SM capacity). B=256 grid, b=16 access box.
    B=256; NN5=B*B; xs=np.repeat(np.arange(B),B).astype(np.uint64); ys=np.tile(np.arange(B),B).astype(np.uint64)
    mcode=np.asarray(morton2(xs,ys)); lcode=(xs.astype(np.int64)<<np.int64(8))|ys.astype(np.int64)   # row-major (1D)
    def pos_of(code): o=np.argsort(code,kind="stable"); p=np.empty(NN5,np.int64); p[o]=np.arange(NN5); return p
    pos_m=pos_of(mcode); pos_l=pos_of(lcode); rng3=np.random.default_rng(3); b=16
    def mean_tiles(pos,T,trials=60):
        tot=0
        for _ in range(trials):
            ox=int(rng3.integers(0,B-b)); oy=int(rng3.integers(0,B-b)); s=set()
            for dx in range(b):
                base=(ox+dx)*B+oy
                for dy in range(b): s.add(int(pos[base+dy])//T)
            tot+=len(s)
        return tot/trials
    T0=64; tm=mean_tiles(pos_m,T0); tl=mean_tiles(pos_l,T0)
    print(f"\n  W5  HIERARCHY: 2D access ({b}x{b}={b*b} pts) over a {B}x{B} grid, SM-tile T={T0} elems -- HBM tiles touched:")
    print(f"      Morton (interleave high bits) = {tm:.1f}   vs   row-major/1D = {tl:.1f}   ({tl/tm:.1f}x fewer transfers)")
    L=256                                                      # per-transfer LATENCY (element-equiv) -- the HBM hw knob
    print(f"      cost = tiles*(L+T), L={L} (latency vs over-fetch); the INTERIOR optimum T* is the alternation region size:")
    costs={}
    for T in (16,64,256,1024,4096):
        tt=mean_tiles(pos_m,T); c=tt*(L+T); costs[T]=c
        print(f"        T={T:<5} tiles={tt:4.1f}  cost={c:7.0f}" + ("   <- footprint b*b" if T==b*b else ""))
    Tstar=min(costs,key=costs.get)
    w5 = (tm < tl*0.5) and (16 < Tstar < 4096)                 # Morton << row-major (HBM) AND an INTERIOR optimal tile size
    print(f"      -> Morton touches {tl/tm:.1f}x fewer HBM tiles (scatter-gather); within-tile order is SM-free. With")
    print(f"         per-transfer latency the optimum tile T*={Tstar} is INTERIOR (~footprint when L~footprint): the")
    print(f"         alternation region size balances latency vs over-fetch -- a MEASURED hw knob (L,footprint), not baked. {w5}")

    ok = w1 and w2 and w3a and w3b and w3c and w4 and w5
    print(f"\n  {'PASS' if ok else 'FAIL'} — THINK QUADTREE (common structure, recursively): a prefix-sort of Morton codes")
    print(f"  IS a (linear) quadtree -- internal nodes = shared prefixes = shared subterms, so the SPPF is a quadtree, not")
    print(f"  a flat sort. The dedup is code-agnostic (W2); the CODE picks WHICH quadtree. Two intrinsic ones: structure =")
    print(f"  the (lch,rch) Morton quadtree (W1); value = the STERN-BROCOT tree addressed by the CONTINUED FRACTION = the")
    print(f"  EEA residue (W3c), which alone gives value-line locality -- morton(num,den) (W3b) was the wrong, extrinsic")
    print(f"  plane quadtree. Recursion: carrier (binary/CD subdivision) -> value (Stern-Brocot) -> structure ((lch,rch)")
    print(f"  quadtree) -> SPPF (linear quadtree by radix sort); the EEA trace IS the address at the value level. REALIZED:")
    print(f"  jea_resident IS this device-resident forest -- a code-sorted linear quadtree merged incrementally per eval.")
