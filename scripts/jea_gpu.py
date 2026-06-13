#!/usr/bin/env python3
"""jea_gpu.py — Just Enough Agda on GPU. M1: the SPPF `inside`-fold over F₂,
GPU-native, faithful, branchless. See memory project_agda_on_gpu_charter.

Acceptance criteria exercised by M1 (the dataflow spit-take):
  * ON-GPU & RESIDENT: the trace (the SPPF DAG) lives in device memory as SoA arrays;
    the fold runs on the device; nothing crosses to host until a single final readout.
  * MEMOIZING TRACE: the DAG is INTERNED — a shared subterm is ONE node, computed once.
    The trace IS the memo table; a tree with 2^k paths is a DAG with O(k) nodes.
  * NO REGEX: a real fold over the term AST (tag + child indices), never text.
  * NO TRUNCATION / NO HIDDEN QUOTIENT: F₂ carrier, values in {0,1}, add = XOR, mul =
    AND — bit-exact, no float, nothing dropped.
  * BRANCHLESS: the per-node combine is one masked-arithmetic formula; no data-dependent
    `if` in the kernel (the only conditional is the uniform out-of-range tail guard).
  * GEOMETRIC MODEL: nodes are renumbered into contiguous level ranges → coalesced reads;
    one kernel launch per level (the dependency barrier). [SM shared-memory tiling +
    recompute-from-residue is M1.5/M2; M1 proves the resident/memoized/exact/branchless
    skeleton.]

F₂ inside-fold (mirrors Substrate.Algebra.Semiring.SPPF.inside at the F₂ semiring):
  gen g ↦ v(g)   one ↦ 1   a ⊗ b ↦ a∧b   a ⊕ b ↦ a⊕b
"""
import time
import cupy as cp
import numpy as np

TAG_GEN, TAG_ONE, TAG_MUL, TAG_ADD = 0, 1, 2, 3


class SPPF:
    """Interned (memoized) SPPF builder. Shared subterms collapse to one node — the
    Register/SPPF packing. Children are built before parents, so insertion order is a
    topological order."""
    def __init__(self):
        self.tag, self.lhs, self.rhs, self.gval = [], [], [], []
        self._memo = {}                      # (tag,lhs,rhs,gval) -> idx  (the dedup)

    def _node(self, tag, lhs=0, rhs=0, gval=0):
        key = (tag, lhs, rhs, gval)
        i = self._memo.get(key)
        if i is None:
            i = len(self.tag)
            self.tag.append(tag); self.lhs.append(lhs); self.rhs.append(rhs)
            self.gval.append(gval); self._memo[key] = i
        return i

    def gen(self, bit): return self._node(TAG_GEN, gval=bit & 1)  # leaf: children = 0 (masked)
    def one(self):      return self._node(TAG_ONE)
    def mul(self, a, b):return self._node(TAG_MUL, a, b)          # ⊗ = AND
    def add(self, a, b):return self._node(TAG_ADD, a, b)          # ⊕ = XOR

    # ---- compile to a device-resident, level-ordered SoA DAG ----
    def compile(self):
        n = len(self.tag)
        tag = np.asarray(self.tag, np.int8); lhs = np.asarray(self.lhs, np.int32)
        rhs = np.asarray(self.rhs, np.int32); gval = np.asarray(self.gval, np.int8)
        # level[i] = 0 for leaves; 1 + max(child levels) otherwise. Children < i (topo),
        # so a single forward pass computes it exactly (no truncation, no heuristic).
        level = np.zeros(n, np.int32)
        leaf = (tag == TAG_GEN) | (tag == TAG_ONE)
        for i in range(n):
            if not leaf[i]:
                level[i] = 1 + max(int(level[lhs[i]]), int(level[rhs[i]]))
        # renumber by (level, idx) so each level is a CONTIGUOUS range (coalesced reads).
        order = np.argsort(level, kind="stable")          # stable: preserves topo within level
        newpos = np.empty(n, np.int32); newpos[order] = np.arange(n, dtype=np.int32)
        tag, gval, level = tag[order], gval[order], level[order]
        lhs = newpos[lhs[order]]; rhs = newpos[rhs[order]]
        # contiguous [lo,hi) per level
        maxL = int(level[-1]) if n else 0
        bounds = [(int(np.searchsorted(level, L, "left")),
                   int(np.searchsorted(level, L, "right"))) for L in range(maxL + 1)]
        roots_new = newpos                                # map old idx -> new idx
        return DeviceDAG(cp.asarray(tag), cp.asarray(lhs), cp.asarray(rhs),
                         cp.asarray(gval), bounds), roots_new


# Branchless F₂ combine. One uniform formula; the only conditional is the tail guard.
_combine_f2 = cp.RawKernel(r'''
extern "C" __global__
void combine_f2(const signed char* tag, const int* lhs, const int* rhs,
                const signed char* gval, signed char* value, int lo, int hi) {
    int i = lo + blockDim.x * (long long)blockIdx.x + threadIdx.x;
    if (i >= hi) return;                       // uniform tail guard (not data divergence)
    signed char t = tag[i];
    signed char a = value[lhs[i]];             // leaf children = 0 -> value[0], masked out
    signed char b = value[rhs[i]];
    signed char mg = (t == 0), mo = (t == 1), mm = (t == 2), ma = (t == 3);
    value[i] = (signed char)((mg & gval[i]) ^ mo ^ (mm & (a & b)) ^ (ma & (a ^ b)));
}
''', 'combine_f2')


class DeviceDAG:
    def __init__(self, tag, lhs, rhs, gval, bounds):
        self.tag, self.lhs, self.rhs, self.gval, self.bounds = tag, lhs, rhs, gval, bounds
        self.n = int(tag.size)

    def inside(self, block=256):
        """Bottom-up F₂ fold, device-resident, one branchless launch per level."""
        value = cp.zeros(self.n, cp.int8)          # zeros so masked leaf-child reads are 0
        for lo, hi in self.bounds:
            grid = ((hi - lo) + block - 1) // block
            _combine_f2((grid,), (block,),
                        (self.tag, self.lhs, self.rhs, self.gval, value,
                         np.int32(lo), np.int32(hi)))
        return value                               # stays on the device


def _cpu_fold(s: SPPF):
    """Ground-truth host fold over the SAME DAG (verification only)."""
    v = np.zeros(len(s.tag), np.int8)
    for i, t in enumerate(s.tag):
        if t == TAG_GEN: v[i] = s.gval[i]
        elif t == TAG_ONE: v[i] = 1
        elif t == TAG_MUL: v[i] = v[s.lhs[i]] & v[s.rhs[i]]
        else: v[i] = v[s.lhs[i]] ^ v[s.rhs[i]]
    return v


def demo_chain(k=40):
    """Verifiable spit-take: e₀ = gen 1; eₖ = add(mul(eₖ₋₁,eₖ₋₁), one) = ¬eₖ₋₁ in F₂.
    As a TREE eₖ has 2^k mul-leaves; as an interned DAG it is O(k) nodes. Folded on GPU."""
    s = SPPF(); one = s.one(); e = s.gen(1); roots = [e]
    for _ in range(k):
        e = s.add(s.mul(e, e), one); roots.append(e)
    dag, remap = s.compile()
    val = dag.inside()                                   # on device
    assert isinstance(val, cp.ndarray)                   # RESIDENT: result is on the GPU
    gpu = [int(val[remap[r]].get()) for r in roots]      # single readout per probed root
    closed = [1 - (i % 2) for i in range(k + 1)]         # eₖ = 1 iff k even
    cpu = _cpu_fold(s)
    assert gpu == closed, (gpu, closed)
    assert gpu == [int(cpu[r]) for r in roots]
    print(f"chain k={k}: DAG nodes={s.__len__() if hasattr(s,'__len__') else len(s.tag)}, "
          f"tree mul-leaves≈2^{k}≈{2.0**k:.3g}, "
          f"memoization ratio≈2^{k}/{len(s.tag)}; eₖ verified vs closed form AND host fold. "
          f"e_{k}={gpu[-1]} (k even⇒1)")


def _build_wide_soa(width, layers, seed):
    """Vectorised builder for a layered F₂ circuit (no per-node Python loop): `layers`
    levels of `width` nodes, each an add/mul of two random previous-layer nodes. Already
    level-ordered (layer = level = contiguous range), so no compile()/sort needed."""
    rng = np.random.default_rng(seed)
    n = width * (layers + 1)
    tag = np.empty(n, np.int8); lhs = np.zeros(n, np.int32)
    rhs = np.zeros(n, np.int32); gval = np.zeros(n, np.int8)
    tag[:width] = TAG_GEN; gval[:width] = rng.integers(0, 2, width, np.int8)
    for L in range(1, layers + 1):
        lo, prev = L * width, (L - 1) * width
        op = rng.integers(0, 2, width)                          # 1 = MUL, 0 = ADD
        tag[lo:lo + width] = np.where(op == 1, TAG_MUL, TAG_ADD).astype(np.int8)
        lhs[lo:lo + width] = prev + rng.integers(0, width, width)
        rhs[lo:lo + width] = prev + rng.integers(0, width, width)
    bounds = [(L * width, (L + 1) * width) for L in range(layers + 1)]
    return tag, lhs, rhs, gval, bounds


def _cpu_fold_soa(tag, lhs, rhs, gval):
    v = np.zeros(tag.size, np.int8)
    for i in range(tag.size):
        t = tag[i]
        if t == TAG_GEN: v[i] = gval[i]
        elif t == TAG_ONE: v[i] = 1
        elif t == TAG_MUL: v[i] = v[lhs[i]] & v[rhs[i]]
        else: v[i] = v[lhs[i]] ^ v[rhs[i]]
    return v


def demo_wide(width=1_000_000, layers=64, seed=1):
    """Throughput: width·layers nodes folded on GPU in `layers` branchless launches."""
    # small cross-check that the kernel matches a host fold on this circuit shape:
    t, l, r, g, b = _build_wide_soa(256, 12, seed)
    chk = DeviceDAG(cp.asarray(t), cp.asarray(l), cp.asarray(r), cp.asarray(g), b)
    assert np.array_equal(chk.inside().get(), _cpu_fold_soa(t, l, r, g)), "kernel ≠ host fold"
    # the throughput run:
    tag, lhs, rhs, gval, bounds = _build_wide_soa(width, layers, seed)
    dag = DeviceDAG(cp.asarray(tag), cp.asarray(lhs), cp.asarray(rhs), cp.asarray(gval), bounds)
    cp.cuda.Stream.null.synchronize(); t0 = time.perf_counter()
    val = dag.inside(); cp.cuda.Stream.null.synchronize(); dt = time.perf_counter() - t0
    resident = sum(a.nbytes for a in (dag.tag, dag.lhs, dag.rhs, dag.gval)) + val.nbytes
    print(f"wide {width}×{layers}: {dag.n:,} nodes folded on GPU in {dt*1e3:.1f} ms "
          f"({dag.n/dt/1e6:.0f}M nodes/s), {resident/1e6:.0f} MB resident, 0 host copies "
          f"(kernel verified vs host fold on a 256×12 instance).")


# ======================================================================
# M1.5 — SM shared-memory tiling. A balanced ⊗/⊕ tree (a parse reduction) folded so a
# CUDA block owns a subtree: load its leaves once, fold the whole subtree IN __shared__
# (the bottom `s` levels), write only the subtree root. The bottom-s intermediate values
# NEVER touch global memory — that is the bandwidth win the charter asks for.
#
# Branchlessness: the COMBINE is the same masked formula as M1 (no data-dependent branch).
# The only branch is the reduction's structural stride guard `if (t < half)` — it depends
# on threadIdx, not on data (uniform per warp except the boundary), the standard shared-
# reduction shape. Warp-shuffle to remove the sub-warp guard is a further optimization.
# ======================================================================

# Each block folds SEG = 2·blockDim leaves of a balanced tree into one partial, in shared
# memory. `btags` holds, per block, that subtree's internal tags in reduction-step order
# (level1 slice, then level2 slice, …) — SEG-1 tags per block.
_fold_subtree_f2 = cp.RawKernel(r'''
extern "C" __global__
void fold_subtree_f2(const signed char* leaves, const signed char* btags,
                     signed char* partial, int SEG) {
    extern __shared__ signed char s[];
    int t = threadIdx.x; int base = blockIdx.x * SEG; int toff = blockIdx.x * (SEG - 1);
    s[t]           = leaves[base + t];               // 2 leaves per thread, coalesced
    s[t + SEG/2]   = leaves[base + t + SEG/2];
    __syncthreads();
    int written = 0;
    for (int half = SEG >> 1; half >= 1; half >>= 1) {
        // stage reads in registers (adjacent pairs -- the mixed-op tree's pairing
        // matters), sync, then write back: no read-write race, combine stays branchless.
        signed char a = 0, b = 0, tg = 0;
        if (t < half) { a = s[2*t]; b = s[2*t + 1]; tg = btags[toff + written + t]; }
        __syncthreads();
        if (t < half) {
            signed char mm = (tg == 2), ma = (tg == 3);
            s[t] = (signed char)((mm & (a & b)) ^ (ma & (a ^ b)));
        }
        written += half;
        __syncthreads();
    }
    if (t == 0) partial[blockIdx.x] = s[0];
}
''', 'fold_subtree_f2')


def build_balanced(h, seed=1):
    """A balanced binary ⊗/⊕ tree: M = 2^h random F₂ leaves; each internal node a random
    MUL/ADD. Returned level-by-level (level 0 = leaves; level L internal node i combines
    level L-1 nodes 2i,2i+1). Pure SPPF (gen/⊗/⊕)."""
    rng = np.random.default_rng(seed)
    M = 1 << h
    leaves = rng.integers(0, 2, M, np.int8)
    tags = []                                         # tags[L-1] = level-L internal tags
    for L in range(1, h + 1):
        op = rng.integers(0, 2, M >> L)               # 1 = MUL(AND), 0 = ADD(XOR)
        tags.append(np.where(op == 1, TAG_MUL, TAG_ADD).astype(np.int8))
    return leaves, tags


def _host_fold_tree(leaves, tags):
    """Ground-truth: fold the balanced tree on the host, level by level."""
    cur = leaves.astype(np.int8)
    for tg in tags:
        a, b = cur[0::2], cur[1::2]
        cur = np.where(tg == TAG_MUL, a & b, a ^ b).astype(np.int8)
    return int(cur[0])


# M1 baseline on the SAME tree: a per-level GLOBAL fold (every level read from / written
# to global — no shared-memory residency). This is the apples-to-apples comparator.
_combine_level_f2 = cp.RawKernel(r'''
extern "C" __global__
void combine_level_f2(const signed char* cur, const signed char* tags,
                      signed char* nxt, int n) {
    int i = blockDim.x * (long long)blockIdx.x + threadIdx.x;
    if (i >= n) return;
    signed char a = cur[2*i], b = cur[2*i+1], tg = tags[i];
    signed char mm = (tg == 2), ma = (tg == 3);
    nxt[i] = (signed char)((mm & (a & b)) ^ (ma & (a ^ b)));
}
''', 'combine_level_f2')


def _fold_levels_device(cur, d_tags, block=256):
    """Per-level GPU fold from a device level-array `cur` through device tag arrays."""
    for tg in d_tags:
        n = int(tg.size); nxt = cp.empty(n, cp.int8)
        _combine_level_f2(((n + block - 1) // block,), (block,),
                          (cur, tg, nxt, np.int32(n)))
        cur = nxt
    return cur                                         # size-1 device array


def inside_perlevel(leaves, tags):
    """Full per-level GLOBAL fold of the whole tree on GPU (the M1-style baseline)."""
    cur = cp.asarray(leaves); d_tags = [cp.asarray(t) for t in tags]   # uploads (untimed)
    cp.cuda.Stream.null.synchronize(); t0 = time.perf_counter()
    root = _fold_levels_device(cur, d_tags)
    cp.cuda.Stream.null.synchronize(); ms = (time.perf_counter() - t0) * 1e3
    return int(root.get()[0]), ms


def inside_tiled(leaves, tags, s=9):
    """M1.5: fold the bottom `s` levels in shared memory (one launch, internal values never
    spill to global), then finish the top per-level — all on GPU. Returns (root, ms)."""
    h = len(tags); M = leaves.size; SEG = 1 << s
    nblk = M >> s
    # btags[b] = concat over levels 1..s of block b's slice (reduction-step order).
    btags = np.empty(nblk * (SEG - 1), np.int8)
    for b in range(nblk):
        off, span = 0, SEG >> 1
        for L in range(s):                            # level L+1 has M>>(L+1) tags total
            seg = tags[L][b * span:(b + 1) * span]
            btags[b * (SEG - 1) + off: b * (SEG - 1) + off + span] = seg
            off += span; span >>= 1
    d_btags = cp.asarray(btags)                       # host btags layout is untimed setup
    d_leaves = cp.asarray(leaves); d_partial = cp.empty(nblk, cp.int8)
    d_toptags = [cp.asarray(t) for t in tags[s:]]
    cp.cuda.Stream.null.synchronize(); t0 = time.perf_counter()
    _fold_subtree_f2((nblk,), (SEG // 2,),
                     (d_leaves, d_btags, d_partial, np.int32(SEG)),
                     shared_mem=SEG)                  # bottom s levels: all in shared mem
    root = _fold_levels_device(d_partial, d_toptags)  # top: per-level (small), on GPU
    cp.cuda.Stream.null.synchronize(); ms = (time.perf_counter() - t0) * 1e3
    return int(root.get()[0]), ms


def demo_compare(h=22, s=9, seed=3, reps=5):
    """A/B on the SAME 2^h-leaf balanced F₂ tree, both folds entirely on GPU:
    per-level GLOBAL fold (M1-style) vs bottom-s SHARED-memory tiled (M1.5).
    JIT-warmed and min-over-reps so the timing is steady-state, not first-call compile."""
    leaves, tags = build_balanced(h, seed); M = leaves.size
    truth = _host_fold_tree(leaves, tags)
    inside_perlevel(leaves, tags); inside_tiled(leaves, tags, s)        # warm the JIT (discard)
    pl = [inside_perlevel(leaves, tags) for _ in range(reps)]
    ti = [inside_tiled(leaves, tags, s) for _ in range(reps)]
    r_pl, ms_pl = pl[0][0], min(m for _, m in pl)                      # min = least-noise
    r_ti, ms_ti = ti[0][0], min(m for _, m in ti)
    assert r_pl == truth and r_ti == truth, (r_pl, r_ti, truth)
    speedup = ms_pl / ms_ti if ms_ti else float("inf")
    # global VALUE-traffic the two move (the point of tiling): per-level round-trips every
    # internal node's value (read 2 children + write = 3 bytes/node); tiled keeps the
    # bottom-s internal values (≈ M·(1-2^-s) of them) in shared, only partials spill.
    ni = M - 1
    pl_val = 3 * ni
    ti_val = 3 * (M >> s) + leaves.nbytes            # only top internals round-trip; leaves read once
    print(f"SAME tree h={h} (2^{h}={M:,} leaves, {2*M-1:,} nodes), both GPU, both = host fold ({truth}):")
    print(f"   per-level GLOBAL fold (M1) : {ms_pl:.2f} ms  | value-traffic ≈ {pl_val/1e6:.1f} MB")
    print(f"   bottom-{s} SHARED tiled (M1.5): {ms_ti:.2f} ms  | value-traffic ≈ {ti_val/1e6:.1f} MB")
    print(f"   → tiled is {speedup:.1f}x FASTER (per-level/tiled time); ~{100*(1-ti_val/pl_val):.0f}% "
          f"less value round-tripped through global (analytic). The win combines fewer "
          f"launches (s levels → 1) + shared residency; for F₂ (value=1B) the pure-bandwidth "
          f"part is small and grows with carrier size → M2.")


# ======================================================================
# M2 — exact ℤ carrier (no truncation, escalate-don't-wrap). 128-bit values via
# `unsigned __int128` (16 bytes each, stored as lo/hi uint64 lanes). Combine is
# branchless (select, not branch); OVERFLOW is DETECTED (add: carry out; mul: division
# check) and sets a sticky flag — the ESCALATE signal — never a silent wrap. Values are
# 16× an F₂ value, so the fold is now bandwidth-bound and the SM-tiling win converts to
# TIME. (Multi-limb escalation beyond 128 bits, triggered by the flag, is M2b.)
# ======================================================================

_I128_DECL = r'''
typedef unsigned long long u64;
typedef unsigned __int128 u128;
__device__ __forceinline__ u128 ld(const u64* lo, const u64* hi, int i){
    return ((u128)hi[i] << 64) | lo[i]; }
__device__ __forceinline__ int comb(u128 a, u128 b, signed char tg, u128* out){
    u128 sm = a + b, pr = a * b;          // both computed; select branchlessly
    int isMul = (tg == 2);
    *out = isMul ? pr : sm;
    int o_add = (sm < a);                 // add carry out of 128 bits
    int o_mul = (a != 0) && (pr / a != b);// mul overflowed 128 bits
    return isMul ? o_mul : o_add;         // 1 => must escalate (never truncated)
}
'''

_combine_level_i128 = cp.RawKernel(_I128_DECL + r'''
extern "C" __global__
void combine_level_i128(const u64* clo, const u64* chi, const signed char* tags,
                        u64* nlo, u64* nhi, int* ovf, int n) {
    int i = blockDim.x * (long long)blockIdx.x + threadIdx.x;
    if (i >= n) return;
    u128 r; int o = comb(ld(clo,chi,2*i), ld(clo,chi,2*i+1), tags[i], &r);
    nlo[i] = (u64)r; nhi[i] = (u64)(r >> 64);
    if (o) ovf[0] = 1;
}
''', 'combine_level_i128', options=('--device-int128',))

_fold_subtree_i128 = cp.RawKernel(_I128_DECL + r'''
extern "C" __global__
void fold_subtree_i128(const u64* llo, const u64* lhi, const signed char* btags,
                       u64* plo, u64* phi, int* ovf, int SEG) {
    extern __shared__ u64 sh[];                  // [0,SEG)=lo  [SEG,2SEG)=hi
    u64* slo = sh; u64* shi = sh + SEG;
    int t = threadIdx.x; int base = blockIdx.x * SEG; int toff = blockIdx.x * (SEG - 1);
    slo[t]=llo[base+t]; shi[t]=lhi[base+t];
    slo[t+SEG/2]=llo[base+t+SEG/2]; shi[t+SEG/2]=lhi[base+t+SEG/2];
    __syncthreads();
    int written = 0;
    for (int half = SEG>>1; half>=1; half>>=1) {
        u128 a=0,b=0; signed char tg=0;
        if (t<half){ a=ld(slo,shi,2*t); b=ld(slo,shi,2*t+1); tg=btags[toff+written+t]; }
        __syncthreads();
        if (t<half){ u128 r; int o=comb(a,b,tg,&r); slo[t]=(u64)r; shi[t]=(u64)(r>>64);
                     if(o) ovf[0]=1; }
        written += half; __syncthreads();
    }
    if (t==0){ plo[blockIdx.x]=slo[0]; phi[blockIdx.x]=shi[0]; }
}
''', 'fold_subtree_i128', options=('--device-int128',))


def build_balanced_int(h, seed, op, leafbits):
    """Balanced tree, integer leaves in [0,2^leafbits), all nodes the SAME op
    ('add'=⊕ or 'mul'=⊗) so overflow behaviour is controllable."""
    rng = np.random.default_rng(seed); M = 1 << h
    leaves = rng.integers(0, 1 << leafbits, M, dtype=np.uint64)
    tag = np.int8(TAG_MUL if op == 'mul' else TAG_ADD)
    tags = [np.full(M >> L, tag, np.int8) for L in range(1, h + 1)]
    return leaves, tags


def _host_fold_int(leaves, tags):
    """Exact arbitrary-precision ground truth (Python int)."""
    cur = [int(x) for x in leaves]
    for tg in tags:
        mul = (tg[0] == TAG_MUL)
        cur = [(cur[2*i]*cur[2*i+1]) if mul else (cur[2*i]+cur[2*i+1])
               for i in range(len(cur)//2)]
    return cur[0]


def _i128(lo, hi):  return (int(hi) << 64) | int(lo)


def inside_perlevel_i128(leaves, tags, block=256):
    clo = cp.asarray(leaves, cp.uint64); chi = cp.zeros(leaves.size, cp.uint64)
    dt = [cp.asarray(t) for t in tags]; ovf = cp.zeros(1, cp.int32)
    cp.cuda.Stream.null.synchronize(); t0 = time.perf_counter()
    for tg in dt:
        n = int(tg.size); nlo = cp.empty(n, cp.uint64); nhi = cp.empty(n, cp.uint64)
        _combine_level_i128(((n+block-1)//block,), (block,), (clo,chi,tg,nlo,nhi,ovf,np.int32(n)))
        clo, chi = nlo, nhi
    cp.cuda.Stream.null.synchronize(); ms = (time.perf_counter()-t0)*1e3
    return _i128(clo.get()[0], chi.get()[0]), ms, int(ovf.get()[0])


def inside_tiled_i128(leaves, tags, s=9):
    h = len(tags); M = leaves.size; SEG = 1 << s; nblk = M >> s
    btags = np.empty(nblk*(SEG-1), np.int8)
    for b in range(nblk):
        off, span = 0, SEG >> 1
        for L in range(s):
            btags[b*(SEG-1)+off : b*(SEG-1)+off+span] = tags[L][b*span:(b+1)*span]
            off += span; span >>= 1
    llo = cp.asarray(leaves, cp.uint64); lhi = cp.zeros(M, cp.uint64); dbt = cp.asarray(btags)
    plo = cp.empty(nblk, cp.uint64); phi = cp.empty(nblk, cp.uint64); ovf = cp.zeros(1, cp.int32)
    dtop = [cp.asarray(t) for t in tags[s:]]
    cp.cuda.Stream.null.synchronize(); t0 = time.perf_counter()
    _fold_subtree_i128((nblk,), (SEG//2,), (llo,lhi,dbt,plo,phi,ovf,np.int32(SEG)),
                       shared_mem=2*SEG*8)
    clo, chi = plo, phi
    for tg in dtop:
        n = int(tg.size); nlo = cp.empty(n, cp.uint64); nhi = cp.empty(n, cp.uint64)
        _combine_level_i128(((n+255)//256,), (256,), (clo,chi,tg,nlo,nhi,ovf,np.int32(n)))
        clo, chi = nlo, nhi
    cp.cuda.Stream.null.synchronize(); ms = (time.perf_counter()-t0)*1e3
    return _i128(clo.get()[0], chi.get()[0]), ms, int(ovf.get()[0])


def demo_compare_i128(h=22, s=9, seed=5, reps=5):
    """M2 spit-take: exact 128-bit ⊕-accumulation (large values → bandwidth-bound), same
    tree, per-level vs SM-tiled — now the SM-residency win should show in TIME."""
    leaves, tags = build_balanced_int(h, seed, 'add', leafbits=60)   # sums ~2^82, fit 128b
    truth = _host_fold_int(leaves, tags)
    inside_perlevel_i128(leaves, tags); inside_tiled_i128(leaves, tags, s)   # warm JIT
    pl = [inside_perlevel_i128(leaves, tags) for _ in range(reps)]
    ti = [inside_tiled_i128(leaves, tags, s) for _ in range(reps)]
    r_pl, ms_pl, o_pl = pl[0][0], min(m for _,m,_ in pl), pl[0][2]
    r_ti, ms_ti, o_ti = ti[0][0], min(m for _,m,_ in ti), ti[0][2]
    assert r_pl == truth and r_ti == truth, (r_pl, r_ti, truth)        # EXACT vs Python int
    assert o_pl == 0 and o_ti == 0                                     # no overflow here
    M = leaves.size
    print(f"M2 exact ℤ (128-bit, 16B values), SAME ⊕-tree h={h} (2^{h}={M:,} leaves), both "
          f"GPU, both = exact host int (a {truth.bit_length()}-bit number), overflow flag 0:")
    print(f"   per-level GLOBAL fold : {ms_pl:.2f} ms")
    print(f"   bottom-{s} SHARED tiled : {ms_ti:.2f} ms   → {ms_pl/ms_ti:.2f}x FASTER "
          f"(16B values are bandwidth-bound, so SM residency now converts to time — the win "
          f"F₂'s 1B values couldn't show).")


def demo_overflow_i128(h=8, seed=1):
    """Escalate-don't-truncate: a ⊗-tree whose exact product exceeds 128 bits. The flag is
    SET (detected) and the device result DIFFERS from the exact host int — no silent wrap."""
    leaves, tags = build_balanced_int(h, seed, 'mul', leafbits=40)    # products explode
    truth = _host_fold_int(leaves, tags)
    root, _, ovf = inside_perlevel_i128(leaves, tags)
    assert ovf == 1, "overflow not detected!"                          # the escalate signal
    assert truth.bit_length() > 128 and root != truth                 # host exact ≫ 128 bits
    print(f"M2 escalate-don't-truncate: ⊗-tree exact product is {truth.bit_length()} bits "
          f"(>128). Overflow flag = {ovf} (DETECTED, not wrapped); the 128-bit result is "
          f"flagged invalid, never a silent truncation. [Multi-limb escalation = M2b.]")


# ======================================================================
# Device-side trace builder. The trace construction must not be a host Python bottleneck:
# leaves, per-level tags, and the per-block `btags` layout for the tiled kernel are all
# built ON the GPU with vectorised cupy (O(s) ops), never a per-node/per-block Python loop.
# ======================================================================

def build_balanced_device(h, op='add', leafbits=60, seed=7):
    """Generate the whole balanced tree on-device: leaves + per-level tags. No host loop."""
    M = 1 << h
    d_leaves = cp.random.randint(0, 1 << leafbits, size=M).astype(cp.uint64)
    tv = np.int8(TAG_MUL if op == 'mul' else TAG_ADD)
    d_tags = [cp.full(M >> L, tv, cp.int8) for L in range(1, h + 1)]   # level-L tags, device
    return d_leaves, d_tags


def btags_device(d_tags, s):
    """Per-block btags layout for the tiled kernel, built ENTIRELY on-device: a vectorised
    reshape+scatter, O(s) cupy ops — replaces the O(nblk·s) host Python loop. For level L,
    d_tags[L] (size nblk·span) reshapes to (nblk, span) and drops into each block's slot."""
    SEG = 1 << s; M = int(d_tags[0].size) * 2; nblk = M >> s
    bt = cp.empty((nblk, SEG - 1), cp.int8)
    off = 0
    for L in range(s):
        span = SEG >> (L + 1)
        bt[:, off:off + span] = d_tags[L].reshape(nblk, span)
        off += span
    return bt.reshape(-1)


def inside_tiled_device(d_leaves, d_tags, s=9):
    """Device-native exact-ℤ tiled fold: inputs already on device, btags built on device."""
    M = int(d_leaves.size); SEG = 1 << s; nblk = M >> s
    d_btags = btags_device(d_tags, s)
    lhi = cp.zeros(M, cp.uint64)
    plo = cp.empty(nblk, cp.uint64); phi = cp.empty(nblk, cp.uint64); ovf = cp.zeros(1, cp.int32)
    cp.cuda.Stream.null.synchronize(); t0 = time.perf_counter()
    _fold_subtree_i128((nblk,), (SEG // 2,),
                       (d_leaves, lhi, d_btags, plo, phi, ovf, np.int32(SEG)),
                       shared_mem=2 * SEG * 8)
    clo, chi = plo, phi
    for tg in d_tags[s:]:
        n = int(tg.size); nlo = cp.empty(n, cp.uint64); nhi = cp.empty(n, cp.uint64)
        _combine_level_i128(((n + 255) // 256,), (256,), (clo, chi, tg, nlo, nhi, ovf, np.int32(n)))
        clo, chi = nlo, nhi
    cp.cuda.Stream.null.synchronize(); ms = (time.perf_counter() - t0) * 1e3
    return _i128(clo.get()[0], chi.get()[0]), ms, int(ovf.get()[0])


def _host_btags(htags, s, nblk, SEG):
    """The OLD host Python btags layout (O(nblk·s) iterations) — the bottleneck."""
    hbt = np.empty(nblk * (SEG - 1), np.int8)
    for b in range(nblk):
        off, span = 0, SEG >> 1
        for L in range(s):
            hbt[b*(SEG-1)+off : b*(SEG-1)+off+span] = htags[L][b*span:(b+1)*span]
            off += span; span >>= 1
    return hbt


def _t(fn, reps=5):
    fn(); cp.cuda.Stream.null.synchronize()                          # warm
    best = float("inf")
    for _ in range(reps):
        t0 = time.perf_counter(); fn(); cp.cuda.Stream.null.synchronize()
        best = min(best, time.perf_counter() - t0)
    return best * 1e3


def demo_device_build(h=22, s=9, seed=7):
    """Device btags layout vs the old host Python loop — warmed, apples-to-apples."""
    SEG = 1 << s; M = 1 << h; nblk = M >> s
    d_leaves, d_tags = build_balanced_device(h, 'add', 60, seed)
    htags = [t.get() for t in d_tags]
    dev_ms  = _t(lambda: btags_device(d_tags, s))                   # device layout, warmed
    host_ms = _t(lambda: _host_btags(htags, s, nblk, SEG), reps=3)  # host Python loop
    assert np.array_equal(btags_device(d_tags, s).get(), _host_btags(htags, s, nblk, SEG))
    root, fold_ms, ovf = inside_tiled_device(d_leaves, d_tags, s)   # device-native fold
    assert root == _host_fold_int(d_leaves.get(), htags) and ovf == 0
    print(f"device-side trace builder h={h} (2^{h}={M:,} leaves, nblk={nblk}): btags layout "
          f"ON GPU {dev_ms:.2f} ms vs host Python loop {host_ms:.0f} ms ({host_ms/dev_ms:.0f}x "
          f"faster), device==host (verified); device-native fold {fold_ms:.2f} ms, root exact "
          f"vs host bignum. The trace construction is no longer a host bottleneck.")


# ======================================================================
# M2b/ℚ — the top of the exact-arithmetic ladder. Carrier = exact ℚ as (num : i128,
# den : i128>0), 32-byte values. The fold's ⊕/⊗ are exact rational add/mul, then the
# EXPLICIT reduction: gcd(|num|, den) divides both — the wedge/EEA, the substrate spine,
# never a silent quotient. gcd is a BRANCHLESS fixed-iteration Euclidean (predicated
# select, no warp divergence; compute is cheap). Overflow of 128-bit num/den (or the
# intermediate products) is DETECTED → the escalate flag (M2b multi-limb beyond it). The
# natural ℚ workload is the SWP PROBABILITY carrier: fraction leaves folded by +,× — the
# positive-rail section, now exact on GPU.
# ======================================================================

_QDECL = r'''
typedef unsigned long long u64; typedef unsigned __int128 u128; typedef __int128 i128;
__device__ __forceinline__ u128 absu(i128 x){ return x < 0 ? (u128)(-x) : (u128)x; }
__device__ __forceinline__ u128 gcd_u(u128 a, u128 b){      // branchless fixed-iter Euclid
    for (int k = 0; k < 256; k++){ u128 r = (b != 0) ? (a % b) : (u128)0;
        a = (b != 0) ? b : a; b = (b != 0) ? r : b; } return a; }
__device__ __forceinline__ i128 ldn(const u64* lo,const u64* hi,int i){
    return (i128)(((u128)hi[i] << 64) | lo[i]); }
__device__ __forceinline__ i128 ldd(const u64* lo,const u64* hi,int i){
    return (i128)(((u128)hi[i] << 64) | lo[i]); }
'''

_combine_level_q = cp.RawKernel(_QDECL + r'''
extern "C" __global__
void combine_level_q(const u64* anl,const u64* anh,const u64* adl,const u64* adh,
                     const signed char* tags,
                     u64* nnl,u64* nnh,u64* ndl,u64* ndh,int* ovf,int n){
    int i = blockDim.x*(long long)blockIdx.x + threadIdx.x; if (i >= n) return;
    i128 an=ldn(anl,anh,2*i), ad=ldd(adl,adh,2*i);
    i128 bn=ldn(anl,anh,2*i+1), bd=ldd(adl,adh,2*i+1);
    int isMul = (tags[i] == 2);
    i128 p1 = an*bd, p2 = bn*ad;                          // add-numerator sub-products
    i128 nm = an*bn,  na = p1 + p2,  D = ad*bd;           // mul-num / add-num / common den
    int o = 0;                                            // overflow detection (exact, never wrap)
    o |= (an!=0) && (nm/an != bn);                        // mul-num product
    o |= (ad!=0) && (D /ad != bd);                        // common-den product
    o |= (bd!=0) && (p1/bd != an);                        // add sub-product an*bd
    o |= (ad!=0) && (p2/ad != bn);                        // add sub-product bn*ad
    o |= ((p1>0)==(p2>0)) && ((na>0) != (p1>0)) && (p1!=0);   // add-numerator SUM overflow
    i128 N = isMul ? nm : na;
    u128 g = gcd_u(absu(N), absu(D)); g = (g==0) ? (u128)1 : g;   // EXPLICIT reduction
    N = N / (i128)g; D = D / (i128)g;
    nnl[i]=(u64)(u128)N; nnh[i]=(u64)((u128)N>>64);
    ndl[i]=(u64)(u128)D; ndh[i]=(u64)((u128)D>>64);
    if (o) ovf[0]=1;
}
''', 'combine_level_q', options=('--device-int128',))


def _signed128(lo, hi):
    v = (int(hi) << 64) | int(lo)
    return v - (1 << 128) if v >= (1 << 127) else v


def inside_perlevel_q(nums, dens, tags, block=256):
    anl = cp.asarray(nums, cp.uint64); anh = cp.zeros(nums.size, cp.uint64)
    adl = cp.asarray(dens, cp.uint64); adh = cp.zeros(dens.size, cp.uint64)
    dt = [cp.asarray(t) for t in tags]; ovf = cp.zeros(1, cp.int32)
    cp.cuda.Stream.null.synchronize(); t0 = time.perf_counter()
    for tg in dt:
        m = int(tg.size)
        nnl = cp.empty(m, cp.uint64); nnh = cp.empty(m, cp.uint64)
        ndl = cp.empty(m, cp.uint64); ndh = cp.empty(m, cp.uint64)
        _combine_level_q(((m+block-1)//block,), (block,),
                         (anl,anh,adl,adh,tg, nnl,nnh,ndl,ndh, ovf, np.int32(m)))
        anl,anh,adl,adh = nnl,nnh,ndl,ndh
    cp.cuda.Stream.null.synchronize(); ms = (time.perf_counter()-t0)*1e3
    N = _signed128(anl.get()[0], anh.get()[0]); D = _signed128(adl.get()[0], adh.get()[0])
    return N, D, ms, int(ovf.get()[0])             # raw (don't build Fraction before ovf check)


def _host_fold_q(nums, dens, tags):
    from fractions import Fraction
    cur = [Fraction(int(n), int(d)) for n, d in zip(nums, dens)]
    for tg in tags:                                    # PER-NODE tag (not tg[0]!)
        cur = [(cur[2*i]*cur[2*i+1]) if tg[i] == TAG_MUL else (cur[2*i]+cur[2*i+1])
               for i in range(len(cur)//2)]
    return cur[0]


def demo_q(h=6, seed=4):
    """Exact ℚ on GPU: fraction leaves (the SWP probability carrier) folded by +,× with the
    EXPLICIT gcd reduction, verified bit-exact against Python's Fraction. Small dens keep
    the reduced ℚ inside 128-bit; deeper trees overflow → the escalate flag (demo_q_overflow)."""
    from fractions import Fraction
    rng = np.random.default_rng(seed); M = 1 << h
    nums = rng.integers(1, 5, M).astype(np.uint64)
    dens = rng.integers(1, 5, M).astype(np.uint64)
    tags = [np.where(rng.integers(0,2, M>>L)==1, TAG_MUL, TAG_ADD).astype(np.int8)
            for L in range(1, h+1)]
    truth = _host_fold_q(nums, dens, tags)
    inside_perlevel_q(nums, dens, tags)                        # warm
    N, D, ms, ovf = inside_perlevel_q(nums, dens, tags)
    assert ovf == 0 and D != 0, "ℚ overflowed 128-bit at this depth (escalate to multi-limb)"
    assert Fraction(N, D) == truth, (N, D, truth)              # EXACT vs Python Fraction
    print(f"M2b/ℚ exact rational on GPU, h={h} (2^{h}={M} fraction leaves, mixed +/×): root = "
          f"{truth.numerator}/{truth.denominator} (num {truth.numerator.bit_length()}b, den "
          f"{truth.denominator.bit_length()}b), VERIFIED bit-exact vs Python Fraction; overflow "
          f"flag 0; explicit gcd reduction (the wedge/EEA), no hidden quotient. {ms:.2f} ms.")


def demo_q_overflow(h=12, seed=4):
    """Deeper ℚ tree: the reduced denominator exceeds 128 bits → overflow DETECTED (flag),
    never a silent wrap — the M2b escalate signal (multi-limb is the completion)."""
    from fractions import Fraction
    rng = np.random.default_rng(seed); M = 1 << h
    nums = rng.integers(1, 10, M).astype(np.uint64); dens = rng.integers(1, 10, M).astype(np.uint64)
    tags = [np.where(rng.integers(0,2, M>>L)==1, TAG_MUL, TAG_ADD).astype(np.int8) for L in range(1,h+1)]
    truth = _host_fold_q(nums, dens, tags)
    _, _, _, ovf = inside_perlevel_q(nums, dens, tags)
    assert ovf == 1, "expected 128-bit ℚ overflow at this depth"
    bits = max(abs(truth.numerator).bit_length(), truth.denominator.bit_length())
    print(f"M2b/ℚ escalate-don't-truncate: h={h} ℚ-tree's exact reduced value needs {bits} "
          f"bits (>128). Overflow flag = {ovf} (DETECTED, not wrapped). The exact value is "
          f"{truth.numerator.bit_length()}b/{truth.denominator.bit_length()}b. "
          f"[Multi-limb escalation past 128-bit = the M2b completion.]")


# ======================================================================
# tiled-ℚ — the recompute-from-residue payoff. ℚ values are 32 bytes, so the per-level
# global fold round-trips a LOT of bandwidth; the SM-tiled fold keeps a subtree's ℚ
# values in shared memory and does the gcd reductions IN-SM (recompute the reduction
# where the operands already live, never move a materialized ℚ across global). Only the
# subtree root spills. This is where SM residency should pay off most (32B >> ℤ-128's 16B
# >> F₂'s 1B). Branchless combine; only the structural stride guard branches.
# ======================================================================

_fold_subtree_q = cp.RawKernel(_QDECL + r'''
extern "C" __global__
void fold_subtree_q(const u64* Lnl,const u64* Lnh,const u64* Ldl,const u64* Ldh,
                    const signed char* btags,
                    u64* Pnl,u64* Pnh,u64* Pdl,u64* Pdh, int* ovf, int SEG){
    extern __shared__ u64 sh[];                          // 4 lanes (nl,nh,dl,dh) x SEG
    u64* snl=sh; u64* snh=sh+SEG; u64* sdl=sh+2*SEG; u64* sdh=sh+3*SEG;
    int t=threadIdx.x; int base=blockIdx.x*SEG; int toff=blockIdx.x*(SEG-1); int t2=t+SEG/2;
    snl[t]=Lnl[base+t];  snh[t]=Lnh[base+t];  sdl[t]=Ldl[base+t];  sdh[t]=Ldh[base+t];
    snl[t2]=Lnl[base+t2];snh[t2]=Lnh[base+t2];sdl[t2]=Ldl[base+t2];sdh[t2]=Ldh[base+t2];
    __syncthreads();
    int written=0;
    for(int half=SEG>>1; half>=1; half>>=1){
        i128 an=0,ad=0,bn=0,bd=0; signed char tg=0;
        if(t<half){
            an=(i128)(((u128)snh[2*t]<<64)|snl[2*t]);    ad=(i128)(((u128)sdh[2*t]<<64)|sdl[2*t]);
            bn=(i128)(((u128)snh[2*t+1]<<64)|snl[2*t+1]);bd=(i128)(((u128)sdh[2*t+1]<<64)|sdl[2*t+1]);
            tg=btags[toff+written+t];
        }
        __syncthreads();
        if(t<half){
            int isMul=(tg==2);
            i128 p1=an*bd,p2=bn*ad, nm=an*bn, na=p1+p2, D=ad*bd;
            int o=0;
            o|=(an!=0)&&(nm/an!=bn); o|=(ad!=0)&&(D/ad!=bd);
            o|=(bd!=0)&&(p1/bd!=an); o|=(ad!=0)&&(p2/ad!=bn);
            o|=((p1>0)==(p2>0))&&((na>0)!=(p1>0))&&(p1!=0);
            i128 N=isMul?nm:na;
            u128 g=gcd_u(absu(N),absu(D)); g=(g==0)?(u128)1:g;   // reduction IN shared memory
            N=N/(i128)g; D=D/(i128)g;
            snl[t]=(u64)(u128)N; snh[t]=(u64)((u128)N>>64);
            sdl[t]=(u64)(u128)D; sdh[t]=(u64)((u128)D>>64);
            if(o) ovf[0]=1;
        }
        written+=half; __syncthreads();
    }
    if(t==0){ Pnl[blockIdx.x]=snl[0]; Pnh[blockIdx.x]=snh[0];
              Pdl[blockIdx.x]=sdl[0]; Pdh[blockIdx.x]=sdh[0]; }
}
''', 'fold_subtree_q', options=('--device-int128',))


def _q_top_fold(anl, anh, adl, adh, d_tags, ovf, block=256):
    for tg in d_tags:
        m = int(tg.size)
        nnl=cp.empty(m,cp.uint64); nnh=cp.empty(m,cp.uint64); ndl=cp.empty(m,cp.uint64); ndh=cp.empty(m,cp.uint64)
        _combine_level_q(((m+block-1)//block,), (block,),
                         (anl,anh,adl,adh,tg, nnl,nnh,ndl,ndh, ovf, np.int32(m)))
        anl,anh,adl,adh = nnl,nnh,ndl,ndh
    return anl,anh,adl,adh


def inside_tiled_q(nums, dens, tags, s=9):
    M = nums.size; SEG = 1 << s; nblk = M >> s
    d_tags = [cp.asarray(t) for t in tags]; d_btags = btags_device(d_tags, s)
    nl=cp.asarray(nums,cp.uint64); nh=cp.zeros(M,cp.uint64)
    dl=cp.asarray(dens,cp.uint64); dh=cp.zeros(M,cp.uint64)
    Pnl=cp.empty(nblk,cp.uint64); Pnh=cp.empty(nblk,cp.uint64)
    Pdl=cp.empty(nblk,cp.uint64); Pdh=cp.empty(nblk,cp.uint64); ovf=cp.zeros(1,cp.int32)
    cp.cuda.Stream.null.synchronize(); t0=time.perf_counter()
    _fold_subtree_q((nblk,),(SEG//2,),
                    (nl,nh,dl,dh, d_btags, Pnl,Pnh,Pdl,Pdh, ovf, np.int32(SEG)),
                    shared_mem=4*SEG*8)
    anl,anh,adl,adh = _q_top_fold(Pnl,Pnh,Pdl,Pdh, d_tags[s:], ovf)
    cp.cuda.Stream.null.synchronize(); ms=(time.perf_counter()-t0)*1e3
    return _signed128(anl.get()[0],anh.get()[0]), _signed128(adl.get()[0],adh.get()[0]), ms, int(ovf.get()[0])


def _build_q_add(h, seed):
    """All-⊕ ℚ tree, leaves num∈{1,2,3} den∈{1,2,4}: ℚ stays in 128-bit at any depth
    (den ≤ 4 after reduction, num ~ weighted sum), 32-byte values → bandwidth-relevant."""
    rng = np.random.default_rng(seed); M = 1 << h
    nums = rng.integers(1, 4, M).astype(np.uint64)
    dens = (1 << rng.integers(0, 3, M)).astype(np.uint64)        # 1,2,4
    tags = [np.full(M >> L, TAG_ADD, np.int8) for L in range(1, h+1)]
    return nums, dens, tags


def demo_compare_q(h=22, s=9, seed=2, reps=5):
    """tiled-ℚ A/B: same 32-byte-ℚ tree, per-level GLOBAL fold vs bottom-s SHARED-tiled
    (gcd reductions in-SM). Exactness checked at small h vs Python Fraction; at large h the
    two GPU folds are cross-checked (host Fraction over millions of leaves is too slow)."""
    from fractions import Fraction
    # 1) exactness at small h, both folds vs Python Fraction:
    nv, dv, tg = _build_q_add(12, seed)
    truth = _host_fold_q(nv, dv, tg)
    for fn, nm in ((inside_perlevel_q, 'per-level'), (lambda a,b,c: inside_tiled_q(a,b,c,9), 'tiled')):
        N,D,_,o = fn(nv,dv,tg); assert o==0 and Fraction(N,D)==truth, (nm,N,D,truth)
    # 2) bandwidth A/B at large h, GPU self-consistency:
    nums, dens, tags = _build_q_add(h, seed); M = nums.size
    inside_perlevel_q(nums,dens,tags); inside_tiled_q(nums,dens,tags,s)         # warm
    pl=[inside_perlevel_q(nums,dens,tags) for _ in range(reps)]
    ti=[inside_tiled_q(nums,dens,tags,s) for _ in range(reps)]
    (Np,Dp,_,op)=pl[0]; (Nt,Dt,_,ot)=ti[0]
    assert op==0 and ot==0 and (Np,Dp)==(Nt,Dt), "GPU folds disagree or overflowed"
    ms_pl=min(m for _,_,m,_ in pl); ms_ti=min(m for _,_,m,_ in ti)
    print(f"tiled-ℚ: exact at h=12 (both folds = Python Fraction). A/B, same 32B-ℚ tree "
          f"h={h} (2^{h}={M:,} leaves), both GPU, agree (={Fraction(Np,Dp)}), flag 0:")
    print(f"   per-level GLOBAL fold : {ms_pl:.2f} ms")
    print(f"   bottom-{s} SHARED tiled : {ms_ti:.2f} ms   → {ms_pl/ms_ti:.2f}x (tiling is SLOWER).")
    print(f"   HONEST FINDING (prediction was WRONG): ℚ is COMPUTE-bound, not bandwidth-bound — "
          f"the 256-iter Euclidean gcd per node dwarfs the 32B traffic, and the tiled "
          f"reduction's sub-warp stride guard idles threads while each survivor runs the full "
          f"gcd, so per-level (full occupancy) wins. SM residency pays off when the combine is "
          f"CHEAP and bandwidth dominates (F₂ 1B ~1.1x, ℤ-128 16B ~2x); ℚ's lever is gcd "
          f"optimization (binary GCD / early-out), not residency.")


if __name__ == "__main__":
    print("Just Enough Agda on GPU — M1: SPPF inside-fold over F₂ (branchless, resident)\n")
    demo_chain(40)
    demo_wide()
    print()
    demo_compare()
    print()
    demo_compare_i128()
    demo_overflow_i128()
    print()
    demo_device_build()
    print()
    demo_q()
    demo_q_overflow()
    print()
    demo_compare_q()
