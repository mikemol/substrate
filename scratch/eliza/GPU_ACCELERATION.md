# GPU Acceleration via Speculative Parallel Execution

The codec is serial-by-nature in three specific spots; everything else
is parallelisable, and the speculative-execution discipline (compute
the branches, throw away the wrong ones) makes the serial spots cheap
because the branch we eventually pick is already in registers.

Compute is cheap when it stays in the SMs. The architecture below is
designed so that each input symbol's processing fits in ~64KB of
shared memory plus a few hundred bytes of registers — no off-SM
roundtrip per symbol, only at chunk boundaries.

## Where the serial-by-nature actually lives

Three operations have data dependencies between consecutive symbols:

1. **Arithmetic-coder state evolution.** Each `range_encode_sym` reads
   the current `(low, high)` and writes new `(low, high)`. The next
   symbol's encoding depends on the previous state.
2. **Predictor count update.** `predictor.update(ch)` writes a single
   cell in the count tensor; the next surprise lookup reads counts
   that include that update. So `predictor.surprise(ch+1)` is
   data-dependent on `predictor.update(ch)`.
3. **Sequitur grammar mutation.** A rule promotion at symbol `k`
   changes which subsequent symbols form known digrams. Promotion
   itself is rare per-symbol but can affect a long suffix.

Everything else — chamber walks, cocycle decomposition, holonomy,
rotation candidates, signature computation, gt-cost evaluation across
all 16 rotations — is **embarrassingly parallel** in the candidate
dimension.

## The speculative-execution discipline

For each operation downstream of a hot serial dependency, compute the
result for **every possible value** the dependency might take, in
parallel. When the actual value arrives, select the precomputed
result. Throw away the others.

This trades GPU FLOPs for sequential latency. The trade is favourable
when:

- The candidate set is small (typically `vocab_size` or 16 rotations).
- The per-candidate work fits in shared memory.
- The selection is a 1-D index, not a complex predicate.

Concretely, with vocab=256 and 256-byte windows:

- 256 speculative predictor lookups per symbol position → 256 SMs
  doing the cumfreq scan for one possible context each.
- 16 speculative rotation evaluations per window → 16 SMs doing
  one rotation each.
- 24 speculative chamber walks per step (one per possible group
  element) → all 24 in one warp.

The selection step is then an O(1) tensor index. The wasted compute
is the cost we pay for the parallelism.

## Per-brick acceleration plan

Each brick from the catalog with its GPU strategy. Bricks marked
**SM-resident** stay in shared memory + registers for the whole
window; **HBM-resident** uses global memory but with coalesced
access patterns; **persistent kernel** runs as a long-lived launch
that streams input in.

### Predictor (counts)

**Shape**: `counts : Tensor[256, 256, 256] int32` (16 MB). HBM-resident.

**cumfreqs**: prefix-sum along the last axis. `np.cumsum`/`cp.cumsum`
on a 256-vector. **SM-resident**: when we load the row for context
`(c1, c2)`, it stays in shared memory for the AC step.

**Speculative parallel**: per chunk, precompute cumfreqs for all
`256 × 256 = 65536` contexts that *might* be the current context
several symbols ahead. The actual context evolves serially; the
cumfreqs lookup is then free. Cost: 65K × 256 × 4 bytes = 64 MB
of speculative state. Fits in HBM with margin.

**Update**: `counts[c1, c2, ch] += 1`. Atomic-add on GPU. Single op.

### Sequitur grammar

**Shape**: top rule as `int32[max_top_len]`; rules as `int32[max_rules, max_body_len]`;
digram index as a hash table (open addressing) over `(sym1, sym2) → rule_id`.

**Speculative digram check**: for each possible next symbol `s`, check
whether `(top_rule[-1], s)` is in the digram index. 256-way parallel
hash lookup; one warp's worth. Result selected after the actual `s`
arrives.

**Rule promotion**: rare; happens serially when triggered. Buffer
candidate promotions across a chunk; apply at chunk boundary.

The grammar typically stabilises within the first few KB of input;
after that, the digram-index is mostly read-only. **Persistent-kernel
strategy**: launch one kernel that processes the whole stream, with
the stable digram-index in shared memory of a long-lived block.

### Chamber walk + cocycle + holonomy

**Shape**: pre-baked tables.

- `apply_table : Tensor[24, 3] int8` — `(chamber, gen) → next chamber`.
  72 bytes. Constant memory.
- `cocycle_table : Tensor[24, 3] int8` — `chamber → (orbit_idx, fiber_idx)`.
  72 bytes. Constant memory.
- `holonomy_table : Tensor[24] float32` — `chamber → κ`. 96 bytes.
  Constant memory.

These are TINY. They live in CUDA constant memory (broadcast-cached).
Each chamber walk is one table lookup; 24 SMs can each do their own
speculative walk for free.

**Speculative parallel**: for each of the 24 possible current chambers,
walk by each of 3 generators in parallel. 72 walks per step, all in
one warp. The actual current chamber selects one.

### Octonion rotation

**Shape**: `rot_lut : Tensor[16, 256] uint8` (4 KB). SM-resident.

**Per window (256 bytes)**: compute all 16 rotations of the window in
parallel. 16 × 256 = 4096 byte-rotations, done as a single
`rot_lut[r, window]` gather. One kernel call.

### Signature (recursive 2-bin)

**Shape**: `signature : Tensor[256] int16` (depth-8) or `Tensor[16]`
(depth-4). SM-resident.

**Per window**: histogram via `scatter_add` on `byte >> (8-depth)`.
For depth 4: 256-element scatter into 16 bins. One warp.

**Speculative parallel**: compute the signature for all 16 rotations
of the window in parallel. 16 × 16-bin histograms = 256 ints. Trivial.

### Chooser (16-rotation argmin)

**Per window**: for each of 16 rotations, compute the gt-cost of the
rotated window under the current predictor (uses the speculative
cumfreqs above). Reduce by argmin.

GPU primitives: 16 parallel cost accumulators in warp registers;
final argmin via warp shuffle. **All-SM-resident** for the 256-byte
window case.

### Range coder

**Truly serial within a chunk.** The acceleration discipline here:

- Split the input stream into independent chunks (e.g., 4 KB each).
- Each chunk has its own range-coder state (initial `low=0,
  high=0xFFFFFFFF`).
- Encode chunks in parallel — one per SM. Concatenate outputs with a
  small header (chunk offsets).
- Overhead per chunk: ~32 bits for finalization. At 4 KB chunks,
  that's <1% overhead.

For decoding, parallel chunks decode independently using the offset
header. Bits-per-byte is essentially the same as the single-stream
version.

**Per-symbol AC step**: ~10 ops on `(low, high)`. The hot loop fits
in registers. The cumfreq lookup (1 load) is the only memory access
per symbol. **SM-resident** for the whole chunk.

### Geo-SPPF and coalg

These are observation-only state mutations. They follow the Sequitur
pattern: buffer observations per chunk, apply at chunk boundary.
HBM-resident state, infrequent serial updates.

## Memory layout summary

| Tensor | Shape | Bytes | Tier |
| --- | --- | --- | --- |
| `apply_table` | `[24, 3]` int8 | 72 | constant |
| `cocycle_table` | `[24, 3]` int8 | 72 | constant |
| `holonomy_table` | `[24]` float32 | 96 | constant |
| `rot_lut` | `[16, 256]` uint8 | 4 K | shared/constant |
| `counts` | `[256, 256, 256]` int32 | 16 M | HBM |
| `cumfreqs_speculative` | `[256, 256, 257]` int32 | 64 M | HBM |
| Top-rule + rules | `[max_top, max_rules, max_body]` int32 | ~1 M typical | shared |
| Range-coder state per chunk | `(low, high, pending)` | <32 B | registers |
| Window buffer | `[256]` uint8 | 256 | shared |
| 16 rotated windows | `[16, 256]` uint8 | 4 K | shared |
| Per-rotation cost accumulator | `[16]` float32 | 64 | registers |

A typical kernel block processing a 256-byte window uses ~10 KB of
shared memory. Modern SMs have 48–192 KB, so multiple windows can be
in flight per SM.

## Speculative-parallel overall structure

```text
For each chunk of ~4 KB:

  GPU phase 1 — speculative prep:
    * Load `counts` slice for likely contexts into shared memory.
    * Compute `cumfreqs_speculative` for all (c1, c2) in the chunk's
      reachable context set.
    * Pre-rotate the chunk under all 16 octonion rotations.
    * Compute signatures for all 16 rotated versions.

  GPU phase 2 — chooser (per window):
    * For each of 16 rotations, compute the gt-cost via the
      speculative cumfreqs.
    * argmin over the 16 — pick rotation r.
    * Throw away the other 15 cost accumulators.

  GPU phase 3 — encode (per chunk):
    * Range-coder state in registers.
    * For each byte in the chosen rotation, lookup cumfreqs (from
      speculative), do AC step, accumulate output bits.
    * Buffered output bits written to HBM at chunk end.

  GPU phase 4 — state mutation:
    * Update `counts` via atomic adds (cheap; sparse).
    * Apply any deferred Sequitur promotions.
    * Move to next chunk.
```

Phases 1–3 are entirely SM-resident; only phase 4 touches HBM for
writes. Per-chunk wall-clock dominated by HBM bandwidth for the
`counts` slice load + bit-stream output; everything else is in
shared memory.

## numpy + cupy mapping

| Brick | numpy ops | cupy equivalent |
| --- | --- | --- |
| `apply_table` lookup | `table[chamber, gen]` | identical |
| `rot_lut` rotation | `rot_lut[r][window]` (advanced index) | identical |
| `signature` | `np.bincount(window >> shift)` | `cp.bincount` |
| `cumfreqs` | `np.cumsum(counts_row)` | `cp.cumsum` |
| 16-rotation cost | `np.sum(np.log2(p), axis=-1)` | `cp.sum`, `cp.log2` |
| argmin | `np.argmin(costs)` | `cp.argmin` |
| atomic-add `counts` | (CPU: just `+=`) | `cupyx.scatter_add` |
| AC step (serial) | Python loop in numba | custom kernel (RawKernel) or numba.cuda |

For non-AC work, the code is mostly numpy-style with `np.` swapped to
`cp.`. The AC step needs a custom kernel because it's branch-heavy
and bit-twiddling — but it's only ~30 lines of CUDA per the standard
range-coder algorithm.

## Order of implementation

1. **`apply_table`, `cocycle_table`, `holonomy_table` in constant
   memory.** No code change to algorithms; just `cp.array`-ify the
   tables and use them via cupy indexing. ~30 lines. Verifies the
   numpy → cupy substitution works for tiny tables.

2. **`rot_lut` 16-way speculative byte rotation.** Per window,
   `rotated = rot_lut[None, :, :].take(window[None, None, :])` →
   `[16, 256]` tensor. Trivial.

3. **`signature` batch on rotated windows.** `cp.apply_along_axis` or
   manual scatter. ~50 lines.

4. **Speculative `cumfreqs` table over the chunk's reachable
   contexts.** This is the biggest memory mover; profile and tune.

5. **Per-window chooser via 16-parallel costs.** Drops the chooser
   from O(16 × window_size) serial CPU work to one kernel launch.

6. **Range-coder custom kernel for chunk encoding.** Last because
   it's the trickiest; the gains from 1–5 likely already give a
   substantial speedup before this lands.

## Speculative-execution rule of thumb

For each operation in the codec, ask:

> *"If I had to pre-compute this for every possible value of the
> input it depends on, would it fit in shared memory and run in
> parallel?"*

If yes: precompute, select, throw away.
If no: chunk, persistent-kernel, or keep on CPU.

For our codec, the answer is YES for everything except range-coder
state evolution. And the range coder is the smallest part of the
per-symbol cost — the predictor lookup and the chooser scoring
dominate. Speculatively pre-computing those is the entire win.

## What we don't try

- Full grammar-rule promotion on GPU. The Sequitur algorithm has
  unbounded rewriting per observation. Buffer observations; flush
  at chunk boundaries; do promotions serially on CPU between chunks.
- Cross-chunk dependencies that aren't expressible as a single
  state-handoff. The chunked AC has a 32-bit state passed between
  chunks; cross-chunk grammar rewriting would need a much larger
  handoff that defeats the parallelism.
- Float-heavy work. Our predictor is integer counts; gt-cost is
  `int → -log₂(int/int) → float`. The float work is the log² and
  argmin; both fit in the chooser's 16-parallel accumulator and
  don't escape the SM.

## Expected speedup

Best case (chunk size = 4 KB, vocab = 256, per-chunk SM occupancy
saturated): the per-symbol latency on CPU is ~1 μs (Python loop with
numpy dict lookup); on GPU the same work fits in a warp's worth of
~32 cycles ≈ 30 ns. **~30× per-symbol** is the rough target.

Real bottleneck likely the HBM bandwidth for the `counts` slice
loads and the bit-stream output. With chunk-level pipelining
(prefetch next chunk's contexts while encoding current), this can be
hidden behind compute.

For 100KB input: CPU codec takes ~10 seconds (per pass-2 benchmarks).
GPU target: <300 ms. The chunked-AC overhead is the limiting factor.

## GF(2) substrate: the bitwise layer

The whole system was designed around GF(2) matrices — bits packed into
machine words, operations as XOR/AND/popcount, no floating point in
the hot path. The earlier sections drifted toward float-heavy
framing (cumsum, log₂); the substrate-honest GPU plan is GF(2)-native.

Concretely, every primitive in the codec has a bit-level
representation:

| Primitive | Float / int view | GF(2) view |
| --- | --- | --- |
| `Chamber` | int32 in [0,24) | 24-bit mask (one-hot) or a 4-tuple packed as 16 bits |
| `V₄ element` | int in [0,4) | 2-bit value (F₂² vector) |
| `S₃ element` | int in [0,6) | 3-bit value or a 6-bit mask |
| `Generator (s₁,s₂,s₃)` | enum | 3-bit transposition matrix in GF(2)^4×4 |
| `chamber_apply(g, x)` | tuple swap | GF(2)^4×4 matrix × permutation vector mod 2 |
| `V₄ rotation on byte` | XOR mask | direct XOR (already GF(2)) |
| `Octonion rotation` | bit-position perm + XOR | bit-shuffle as F₂³ permutation matrix + XOR mask |
| `Cocycle decomp` | (orbit, fiber) lookup | a 4×24 GF(2) projection matrix |
| `Signature (recursive 2-bin)` | histogram counts | bit-population over indexed shifts; popcount |
| `Trigram update` | `counts[c1, c2, ch] += 1` | bitfield set-or-increment over a packed counter array |
| `Beck-Chevalley κ` | float scalar | XOR-residue of two GF(2) path products |

The hot inner loop is **F₂ matrix-vector multiplication** with sparse
matrices that have ≤3 non-zeros per row (for Coxeter generators) or
specific bit-pattern structure (for octonion rotations).

### CUDA primitives for the GF(2) workload

CUDA has specific instructions that map directly onto our hot ops:

| Op | CUDA primitive | Use |
| --- | --- | --- |
| Bit XOR | `^` | V₄ rotation, octonion rotation, GF(2) matmul |
| Bit AND | `&` | mask selection, intersection |
| Population count | `__popc(x)` (32-bit) / `__popcll(x)` (64-bit) | signature bin counts, Hamming distance |
| Find-first-set | `__ffs(x)` | argmin over 32-element masks |
| Warp ballot | `__ballot_sync(mask, pred)` | gather a 32-thread predicate result into one 32-bit word |
| Warp shuffle | `__shfl_sync` | reduce 32-rotation costs into one register |
| Byte permute | `__byte_perm(a, b, idx)` | octonion-style bit-position permutation, 4 bytes at a time |
| Bit reversal | `__brev(x)` | one of the V₄ × S₃ involutions (γ residue, full bit-complement) |
| Conditional copy | `__byte_perm` + `select` | branch-free speculative selection |

For 256-byte windows, **one warp can process the entire window** for
many ops because 32 threads × 8 bytes/thread = 256 bytes per warp. The
"speculative-rotate-then-select" pattern becomes:

```cuda
// 32 threads cooperate on a 256-byte window
uint32_t my_4bytes = window_global[tid * 4 + ...];
uint32_t rotated_for_r = __byte_perm(my_4bytes, ...) ^ mask[r];
// 16 rotations × 32 threads × 4 bytes = 2048 byte-rotations per warp
```

### The packed representation of state

- **Chamber state**: a 24-element permutation of {1,2,3,4} fits in
  a uint8 by indexing the BFS-enumerated chamber list (24 < 256).
  Or a packed 16-bit representation: 4 elements × 2 bits each (since
  S₄ elements are functions [4] → [4]). The lookup table
  `apply_table[chamber, gen]` is then 24 × 3 × 1 byte = 72 bytes.
- **V₄ element**: 2 bits. A 4-element V₄ array fits in one byte.
- **S₃ element**: 3 bits. Six elements fit in a uint32 with room.
- **Cocycle decomposition**: lookup table `chamber → (orbit, fiber)`
  fits in 24 × 1 byte (4 bits orbit + 4 bits fiber) = 24 bytes.

All of this is well below shared-memory budgets. The 16 MB
`counts` tensor is the only large structure; everything else is
register-sized.

### The Laplacian over GF(2)

The Cayley graph's adjacency matrix `A` is a 24×24 matrix with
entries in GF(2): `A[x, y] = 1` iff `y = x · s_i` for some generator
`s_i`. The Laplacian `L = D - A` over GF(2) reduces to `L = D ⊕ A`
where ⊕ is XOR. Over GF(2), eigenvalues are roots of the
characteristic polynomial modulo 2, and eigenvectors live in
F₂^24.

The substrate's `Substrate.Groups.F2Cubed`, `Substrate.Category.F2Graded`,
and related modules already work in F₂. The spectral substrate
described earlier — Fiedler / turbulence vectors — has a GF(2)
counterpart: the eigenvectors of `L` over F₂ are sign-patterns that
partition the 24 chambers into 2-classes. These are LITERALLY V₄ ⋊ S₃
character functions over GF(2).

The polarity bands of the prototype arc are the F₂-eigenvector sign
patterns. Over the reals they look like Fiedler/turbulence; over
F₂ they ARE the V₄ characters.

### Updated implementation order with the GF(2) lens

The order from above is mostly correct, but the data types should
be re-spec'd as GF(2) packed bitfields:

1. Constant-memory tables as `uint8` (chamber lookup), `uint8` (cocycle
   table). Constant memory is broadcast-cached; 256-byte tables are free.
2. `rot_lut` as a 16 × 256 `uint8` table; rotation = `__byte_perm` +
   XOR.
3. Signature histogram via `__popc` over indexed shifts. Depth-4
   signature is 16 bins; one warp can compute the histogram of a
   256-byte window in <100 cycles.
4. `cumfreqs` over the predictor's counts: this is the one place we
   need int32 (not GF(2)) because we're carrying actual integer counts.
   Cumsum on int32 is well-supported in cupy.
5. Per-window chooser: 16 parallel cost accumulators in warp
   registers; argmin via `__shfl_sync`. Cost calculation involves
   log₂ — that's the only float work, ~16 ops per window.
6. Range coder: serial within a chunk, but bit-twiddling-heavy.
   CUDA's bit-ops (`__brev`, `__clz`, `__popc`) cover the standard
   range-coder normalization.

### Why this works

Our codec was built on V₄ ⋊ S₃ = S₄, an F₂-graded structure with
explicit GF(2) arithmetic in the substrate's algebraic backbone. The
CPU implementation in Python uses Python ints + dicts, which obscures
the GF(2) structure behind language-level abstractions. On GPU, the
GF(2) structure is the natural representation: bits are the
hardware-level unit, XOR is faster than multiplication, popcount is a
single instruction.

The float work (entropy calculations, surprise bits) is **non-hot** —
it happens once per window in the chooser, not once per byte. The
hot path is all integer / bit operations, which is exactly what
GPUs accelerate best.

The discipline: **make the GF(2) representation the runtime
representation, not just the conceptual one.** The substrate's Agda
formalism uses F₂ types directly (`Substrate.Groups.F2Cubed`,
`F2Graded`); the Python codec should be ported to use bitfields and
GPU bit-ops, not Python ints. Then the GPU acceleration is mostly a
re-targeting of the same code, not a rewrite.

## Coda

The codec's architecture from `DATAFLOW_REMODEL.md` is already in
the right shape for this. Every brick from sections G–K is either
SM-resident-cheap or chunk-buffered. The Pipeline combinator is the
unit of GPU kernel launch — one launch per Pipeline per chunk. The
brick-level types are the kernel-signature types. The Agda model in
`Substrate.Pipeline.Brick` is the spec; the cupy code is one of many
valid runtime witnesses — and the GF(2) substrate is the
representation that makes it match the hardware.
