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


def inside_tiled(leaves, tags, s=9):
    """M1.5: fold the bottom `s` levels in shared memory (one launch, no global spill of
    internal values), then finish the small top on the host. Returns (root, bytes_global)."""
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
    d_leaves = cp.asarray(leaves); d_btags = cp.asarray(btags)
    d_partial = cp.empty(nblk, cp.int8)
    cp.cuda.Stream.null.synchronize(); t0 = time.perf_counter()
    _fold_subtree_f2((nblk,), (SEG // 2,),
                     (d_leaves, d_btags, d_partial, np.int32(SEG)),
                     shared_mem=SEG)                  # SEG int8 of shared per block
    cp.cuda.Stream.null.synchronize(); gpu_ms = (time.perf_counter() - t0) * 1e3
    # global traffic of the tiled launch: leaves in + tags in + partials out (internal
    # bottom-s values stayed in shared, never global).
    bytes_global = d_leaves.nbytes + d_btags.nbytes + d_partial.nbytes
    # finish the top (levels s+1..h) on host — it is tiny (nblk values).
    top = _host_fold_tree(d_partial.get(), tags[s:])
    return top, bytes_global, gpu_ms


def demo_tiled(h=22, s=9, seed=3):
    """M1.5 spit-take: balanced 2^h-leaf F₂ tree, bottom s levels folded in shared memory."""
    leaves, tags = build_balanced(h, seed)
    M = leaves.size
    # M1 baseline (per-level global fold) traffic: every level's children are read and the
    # result written back to global — ~3 value-bytes per internal node + the tags.
    n_internal = M - 1
    m1_global = leaves.nbytes + 3 * n_internal + n_internal           # rough: 2 reads+1 write + tag
    root, tiled_global, gpu_ms = inside_tiled(leaves, tags, s)
    assert root == _host_fold_tree(leaves, tags), "tiled ≠ host fold"
    saved = 100 * (1 - tiled_global / m1_global)
    print(f"tiled h={h} (2^{h}={M:,} leaves), bottom s={s} levels in shared: root={root}, "
          f"verified vs host. global traffic ≈ {tiled_global/1e6:.1f} MB vs per-level "
          f"≈ {m1_global/1e6:.1f} MB ({saved:.0f}% less, analytic); bottom-{s} intermediates "
          f"never left shared mem. GPU fold {gpu_ms:.2f} ms (host btags layout extra, "
          f"vectorizable).")
    # recompute-from-residue crossover, stated honestly for F₂:
    print(f"  recompute-vs-fetch: an F₂ value is 1 byte = its residue, so FETCH wins here "
          f"(nothing to save by recomputing). The recompute-from-residue WIN scales with "
          f"value/residue size ratio → it earns its keep in M2 (exact ℚ: a reduced "
          f"fraction ≫ its EEA-trace residue; recompute the reduction in-SM, don't move it).")


if __name__ == "__main__":
    print("Just Enough Agda on GPU — M1: SPPF inside-fold over F₂ (branchless, resident)\n")
    demo_chain(40)
    demo_wide()
    print()
    demo_tiled()
