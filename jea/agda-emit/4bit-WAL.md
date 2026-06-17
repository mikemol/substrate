# 4-bit limb carrier — WRITE-AHEAD LOG + premortem + shadows (STUDY, pre-build)

Status: **STUDY / write-ahead.** No 4-bit code yet. This log is the spec; it survives context
loss. Trajectory: `u64` → **8-bit byte-limb** (committed `376ede8`: dp4a-convolution multiply,
parallel carry, add, escalation-delivers) → **now studying 8→4**. Disciplines applied: the
retrospective ritual run *forward* (premortem), decomposable-by-entailment (shadows), WAL.

---

## 0. The grounded fact this all turns on (measured, not assumed)

The regular GPU ALU's smallest SIMD-MAC is the **byte**: `__dp4a` (4×int8), `__dp2a` (2×int16);
every `__v*4`/`__v*2` is byte/halfword. **There is NO nibble (4-bit) MAC on the ALU.** Therefore
a 4-bit multiply has only three realizations:

- **(A) nibbles-as-bytes + dp4a** — store each nibble in a byte (0–15), reuse the 8-bit kernel
  with base-16 carry. Correct, trivial to build. But it carries **2× the limbs** for the same
  value and uses a **full byte per nibble** → *more* MACs and the *same* storage as 8-bit.
  **Strictly worse than 8-bit on the ALU.**
- **(B) int4 TENSOR CORES** (`mma.sync` with `.u4`) — Ada sm_89 has them. Packs 8 nibbles/register;
  the bignum convolution = a structured (Toeplitz) matmul that int4 tensor cores do at high
  throughput. **The only path on which 4-bit can BEAT 8-bit.** Significant lift (fragment layouts,
  the convolution→matmul mapping, int32 accumulate, cupy/RawKernel access to `mma`/WMMA-int4).
- **(C) 2-nibbles/byte for STORAGE only** — finer pay-for-size + finer unfold grain, but unpack
  for compute (no nibble MAC) → compute overhead. A bandwidth/grain win, a compute loss.

---

## 1. PREMORTEM (the retrospective ritual, run BEFORE the work)

**G0 — Precommit (what we'd expect 4-bit to buy).** Denser packing (8 nibbles/u32 vs 4 bytes),
finer unfold grain, and — the seductive one — "even faster, continuing the 64→8 win."

**G1 — Freeze (the trajectory facts).** 64→8 was a *real* win because it landed on `dp4a`, a
native byte-SIMD MAC (the int8 fast path, verified). The win was **datapath-specific**, not a
property of "smaller is faster."

**G2 — Anticipated delta (where reality will diverge from G0).** 8→4 will **not** repeat 64→8 on
the ALU: there is no nibble `dp4a`, so realization (A) is *slower* than 8-bit and (C) trades
compute for grain. 4-bit beats 8-bit *only* via (B) int4 tensor cores — a different, harder
datapath. The expected "even faster" is **false on the path we actually have built.**

**G3 — Anticipated cause (the root, if we shipped the naive version).** Extrapolating the 64→8
*trend* to 8→4 without checking the instruction support — **the exact value-size-trend
extrapolation that mispredicted ℚ-tiling ("32B ⇒ bandwidth-bound ⇒ tiling wins" → it lost) and the
gcd-step "134× headroom" (→ 1.2×) earlier this session.** The reflex: a property that held at one
scale is assumed to hold at the next. It does not; the datapath changes under us at the nibble.

**G6 — Sustain (what 8-bit got right; preserve it).** Value-as-byte-stream (pay-for-size,
unfold-on-demand); multiply = convolution (base-agnostic); parallel carry; escalation-as-append.
None of these are width-specific — they are the *shadow* (§2). Verify-exact-vs-Python-before-claim:
keep it; it's what would catch a 4-bit carry/packing bug.

**G7 — Commits (verify FIRST, in this order; do not build the carrier until these resolve).**
1. **Probe int4-tensor feasibility from cupy/RawKernel on sm_89** — can we emit `mma.sync.*.u4` (or
   WMMA int4) and get an exact u4×u4→s32 result? If not accessible from our toolchain, (B) is
   blocked and 4-bit has **no win** → defer 4-bit.
2. **Measure (A) vs 8-bit** on a fixed value — confirm nibbles-as-bytes is *slower* (it must be, by
   §0). This is the cheap empirical refutation of the G0 expectation; do it to *kill the trend
   assumption with a number*, per session discipline.
3. Only if (1) succeeds: estimate the int4-tensor convolution throughput vs the dp4a 8-bit baseline
   on a representative big multiply. Build 4-bit **only if it measurably wins.**

**G8 — Handoff / blind spot.** The assumption shared across these passes I can't self-check: that
the *bignum convolution → int4 matmul* mapping is efficient (Toeplitz structure may waste tensor-core
tiles; the operands are 1-D, tensor cores want 2-D dense). An external check on the matmul-mapping
efficiency is the thing to get before committing to (B).

**G9 — Escalate (make it correct-by-construction).** Class-level finding: **limb width is a GAUGE,
not a constant** — we froze it at 64, then 8; freezing it at 4 repeats the mistake. The
correct-by-construction fix: the carrier is **parametric in w**, and the **nedge controller picks w
per workload×hardware** (the same controller that picks the gcd window K). Then 4-bit is not a
rebuild — it is the controller selecting `w=4` *iff* the int4-tensor datapath wins. Don't hardcode 4;
parametrize and let the scheduler choose. (Escalation ledger entry: width-selection joins K-selection
as a controller knob.)

---

## 2. SHADOWS (decomposable-by-entailment)

**Costructure (the reusable form):** a **width-parametric limb carrier** `Limb(w)` — value = little-
endian stream of base-`B=2^w` limbs. The 8-bit carrier (`jea_limb_gpu.py`) is the instance `w=8`.

**Composition:** `multiply = convolution(col[k]=Σ a[i]·b[k-i]) ∘ carry(base B)`. Both pieces are
**base-agnostic**; only two things vary with w: the **SIMD MAC** (w=8→dp4a; w=4→int4-tensor or
unpack) and the **accumulator bound** (`col[k] < (B-1)²·min(La,Lb)` must fit s32 ⇒ for w=8, La,Lb up
to ~33k; for w=4, up to ~9.5M — finer limbs *relax* the accumulator bound).

**Entailment (the non-trivial step, stated as the obligation):** *correctness for every w follows
from one proof* — the convolution identity and base-B carry are width-independent; a single
`verify-vs-Python` over `w∈{4,8}` discharges it. So **build the carrier once, parametric in w**;
4-bit correctness is *free*, and only its *performance* is datapath-gated (§1 G7).

This is why the honest plan is **not** "write a 4-bit carrier" but "**parametrize the 8-bit carrier
by w, then let the controller pick w**" — the 4-bit question collapses to the int4-tensor datapath
probe (G7.1), with correctness already entailed.

---

## 3. THE PLAN (replayable; each step PLANNED until done)

- [PLANNED] **P1.** Probe: can cupy/RawKernel emit an exact int4 tensor MAC on sm_89? (G7.1) →
  decides whether 4-bit has any win. If BLOCKED → log "4-bit deferred: no int4 datapath" and stop.
- [PLANNED] **P2.** Refute the trend: build the trivial (A) nibbles-as-bytes multiply, measure it
  *slower* than 8-bit for the same value (G7.2). One number, kills the G0 expectation.
- [PLANNED] **P3.** If P1 ok: map bignum convolution → int4 Toeplitz matmul; measure vs dp4a 8-bit
  baseline (G7.3 + G8). Build 4-bit only if it wins.
- [PLANNED] **P4.** Regardless of P1/P3: refactor the carrier to be **w-parametric** (§2) and add
  **width-selection to the nedge controller** (G9). This is the durable deliverable; 4-bit is then
  an instance the controller may or may not select.

**Bottom line of the study:** 4-bit is a **tensor-core question, not an ALU question**. The right
move is to parametrize width as a controller-tuned gauge and gate the int4 path on a measured win —
*not* to assume 8→4 repeats the dp4a win of 64→8. Verify the datapath before writing the kernel.

---

## REVISION 2 (2026-06-14) — widths are MANDATORY; the question is least-cost DESCENT 8→4→2→1

**Framing correction (user):** we *will* do 4-bit, then 2-bit (and the trajectory points at 1-bit) —
**regardless of performance**. So Rev-1's "is it worth it / verify-or-defer" gate is the wrong axis.
The axis is: **what architecture costs the least to descend the ladder?** This separates two things
Rev-1 conflated:

- **operate AT width w** (correctness/representation) — *cheap*, and what we actually need now;
- **exploit width w's packing/tensor datapath** (int4/int1 performance) — *expensive, per-width
  rework*, and explicitly NOT the goal yet.

The grounded "no nibble ALU MAC" fact (§0) is then a *reason to NOT chase the datapath*, not a reason
to defer the width: keep **byte storage + dp4a** and change only the **base**.

### Least-cost architecture: parametrize the BASE `B = 2^w`

The 8-bit carrier (`jea_limb_gpu.py`) is *already* base-256. The only base-specific code is the
carry's `& 0xff` and `>> 8`. Generalize to `& (B-1)` and `>> w`:

- **Multiply (dp4a convolution): UNCHANGED.** Limbs are byte values in `0..B-1` (always ≤255), so
  `__dp4a` works identically at every w. The accumulator bound `col[k] < (B-1)²·minL` only *relaxes*
  as B shrinks (B=256→65025·minL; B=2→1·minL). Zero datapath change across the whole ladder.
- **Carry / scatter: base-B** (`& (B-1)`, `>> w`) — the existing parallel scatter+ripple, one
  parameter. (col[k] in base B spans ⌈log_B(col_max)⌉ positions; the scatter loop bound follows w.)
- **Descent 8→4→2→1 = changing one constant B.** Not new carriers. The cheapest possible descent.

**Endpoint design (honoring the trajectory to 1-bit).** At w=1, B=2: WITH carry it's binary integer;
**CARRYLESS (XOR, no propagate) it is GF(2)** — polynomial/F₂ arithmetic = the substrate's home field
(commuting-sphere, 3+1 parity, GL(3,F₂)) AND the int1 binary-tensor path (XOR-popcount = GF(2)
matmul). So add a **carry / carryless MODE** flag; then the GF(2) endpoint is *also* one parameter,
and **the big-value carrier and the F₂ substrate UNIFY at w=1**. (I won't claim your exact reason,
but the architecture should be ready for that unification — it's the obvious place the ladder bottoms.)

### Premortem (re-run for the descent)

- **G0 precommit:** be able to operate at any sub-byte width 8→4→2→1 at minimal incremental cost.
- **G2 delta to avoid:** the expensive failure = building per-width carriers, or optimizing each
  width's packing/tensor datapath as we descend. Either re-does work per step.
- **G3 cause:** conflating *operate-at-width* (cheap: base param) with *exploit-width-datapath*
  (expensive: int4/int1 tensor). Same trend-chasing reflex, one level up.
- **G6 sustain:** base-agnostic convolution + carry + verify-vs-Python — they already make the descent
  free; that's the whole point.
- **G7 commits:** (1) parametrize base B in the carry (`0xff/8 → B-1/w`); (2) verify exact for
  w∈{8,4,2,1}; (3) add carry/carryless mode, verify w=1 carryless == GF(2) poly-mul; (4) DEFER all
  int4/int1-tensor datapath work to a separate, perf-gated effort.
- **G9 escalate:** base B and the carry/carryless mode are **controller gauges** (join K, w). ONE
  parametric carrier, never per-width forks — correct-by-construction descent.

### Shadow (sharpened costructure)

`Limb(B, carryless)` — base-`B=2^w` little-endian limb stream, optional carryless (GF(2)) mode.
Composition = `convolution ∘ carry(base B | carryless)`. **Entailment:** correct for every
w∈{8,4,2,1} and both modes by *one* proof (convolution + base-B carry are base-agnostic; carryless is
the carry map replaced by XOR). A single verify over the widths+modes discharges the ladder.

**Bottom line (Rev-2):** least-cost descent = **base-parametrize the existing carrier** (`0xff/8 →
B-1/w`) + a **carry/carryless mode**; 8→4→2→1 is then *changing B*, dp4a unchanged, all widths correct
by one entailment, and the GF(2)/F₂ endpoint falls out free. Datapath/packing optimization (int4/int1
tensor) is a separate deferred axis, not on the descent's critical path.
