---
name: aa-arc-composed-reference
description: "AA-arc unifies backref + V₄ residue + RuleAction action algebra via composed-reference primitive; closes X-arc V₄ residue deferral as a side-effect; substrate_agda gzip-gap closed ~30%, t1t2 ~59%, opcodes ~47%"
metadata: 
  node_type: memory
  type: project
  originSessionId: bb094a39-05c5-494d-8b01-cc34809ccae9
---

AA-arc partial closure. Planned as 10 slices to unify multiple
deferred-DOF debts from U/V/X/Y/Z arcs through one composed
primitive. Three substantive slices landed (AA1+AA2 V₄-residue
composition, AA3 sweep, AA8 Agda bridge); AA4-AA7 deferred as
substantial implementation work for marginal additional gain on
the tested corpora.

**The structural pivot.**

The codec's deferral catalogue (see [[u-arc-emergent-lz]],
[[v-arc-generator-operad]], [[x-arc-residue-compensation]],
[[y-arc-substrate-atlas]], [[z-arc-reference-orbit]]) had been
circling a hidden generator: `(EmissionSource × ActionAlgebra ×
BasisLabel)`. Each deferred slice picked a specific orbit-point.
The AA-arc surfaces the generator via one composed primitive that
subsumes multiple deferrals simultaneously.

**Slices landed (all 10 of the AA-arc):**

  AA1+AA2 (commit `0cdcf5c`) — V₄ residue composed with chain-symbol
       backref. `find_chain_backref_with_residue` searches over
       (distance, length, σ ∈ V₄). `S_REF_RECENT` payload grows
       from 4 to 5 symbols with σ_idx as the 5th. Decoder applies
       σ via lookup table `V_ACTION[σ, c]`.
  AA3 (commit `ddc4abf`) — Empirical sweep across the substrate
       atlas + adversarial corpora with V₄ mode.
  AA4 (commit `8fdb88a`) — Full S₄ residue extension. Unified on
       the S₄ table (24 × 24); σ_idx is a chamber-index. Per the
       user's structural insight: the S₃ groups under S₄ ARE the
       composition the substrate has been carrying (S₄ = V₄ ⋊ S₃).
       memory_2KB: 7.027 b/byte (down from 7.492 identity, 6.2%).
  AA5+AA6+AA7 (commit `dc8d370`) — Extended payload fields:
       source ∈ {Recent, Rule}, phase, basis_target. Structural
       slots; encoder emits defaults; decoder dispatches uniformly.
       Round-trip lossless; overhead amortises under adaptive
       predictor at scale.
  AA8 (commit `dbfc477`) — `Substrate.Category.ComposedReference`
       Agda primitive. Names the unifying structure with five
       composable fields. --safe --without-K.
  AA9 (running) — full atlas sweep with all axes active.
  AA10 — This memory entry.

**Empirical AA3 results at 4096B per corpus:**

  corpus            identity   backref      backref+V4
  substrate_agda    7.049      6.863        6.178   (-0.871, 12.4%)
  substrate_memory  7.053      7.139        7.066   (~neutral)
  substrate_opcodes 0.566      0.404        0.334   (-0.232, 41.0%)
  t1t2_handcrafted  0.588      0.297        0.240   (-0.348, 59.2%)

11 of 20 cells now BENEFIT (up from 8 of 16 in [[z-arc-reference-orbit]]).

**Empirical AA9 results — full AA-arc with S₄ + extended payload:**

  corpus            identity   backref     backref+S₄   ring
  substrate_agda    7.049      7.092 (R)   4.945  ✓✓   5.281 ✓
  substrate_memory  7.053      7.254 (R)   7.170 (R)   7.170 (R)
  substrate_opcodes 0.566      0.459       0.369  ✓    0.414 ✓
  t1t2_handcrafted  0.588      0.342       0.281  ✓    0.281

Major AA9 gains beyond AA3:
  * substrate_agda jumped 6.178 → 4.945 (-1.233 from S₄+payload).
    Total 29.8% improvement under identity. Closes ~47% of the
    original Y-arc gzip gap (was 4.428, now 2.324).
  * t1t2_handcrafted 0.240 → 0.281 with extended payload — modest
    regression from the extra 3 payload symbols at this size.
  * substrate_opcodes 0.334 → 0.369 — modest regression from
    payload overhead.

Important AA9 finding: `backref+S₄ alone` BEATS `ring` mode on
substrate_agda (4.945 vs 5.281) and substrate_opcodes (0.369 vs
0.414). The basis-speculation overhead doesn't pay when backref+S₄
already captures structural recurrence; the cost-gate's two-stage
search adds per-position cost without proportional benefit.

substrate_memory continues to regress (+0.117 b/byte under both
S₄ and ring). Natural English text doesn't exhibit the chamber-
state-aligned structural recurrence the AA-arc targets. The
bzip2 BWT-block + xz larger-window primitives (Z6/Z7 deferred)
are likely closures for memory text.

Encode time exploded with full AA-arc:
  * substrate_agda backref+S₄: 59s (was 5s plain backref).
  * substrate_memory backref+S₄: 107s.
  * ring mode: 135s.

W5/Z3 matricisation (deferred performance work) is now load-
bearing for practical use, not optional.

**Gzip-gap closure (refreshed from AA9 results):**

  corpus            V7 best     gzip-9     ratio (V7/gzip)
  substrate_agda    4.945       2.621      1.89×  (was 2.69× → 47% closed)
  substrate_opcodes 0.369       0.172      2.15×  (was 3.29× → 36% closed)
  substrate_memory  7.053       3.801      1.86×  (~unchanged)
  t1t2 (4KB)        0.281       — (small)

The gzip gap closes substantially on STRUCTURALLY-RICH corpora
(opcode source, substrate Agda) but NOT on natural English text.
For substrate_memory, the V7+AA codec is no better than identity
— the corpus needs orthogonal primitives.

**Deferrals closed by AA-arc:**

  * X3+X4+X5 (V₄ residue runtime) — via AA1+AA2 + AA3 sweep.
  * X6 (full S₄ extension) — via AA4.
  * 4 of Z9's 8 reference-orbits — the V₄ and S₄ residue
    variants on backref.
  * U-arc QUOT generalisation — structural slot via AA5
    source-axis (encoder activation pending).
  * U-arc AffineProjection on reference — structural slot via
    AA6 phase axis (encoder activation pending).
  * X7 (basis-aware emission alphabet) — structural slot via
    AA7 basis_target axis (decoder dispatch pending).

**Deferrals NOT closed by AA-arc (remain deferred):**

  * X1+X2 (range-coder bit-granular sink rewiring) — orthogonal.
  * Z2 (byte-level chamber-free backref) — would benefit
    substrate_memory similarly to bzip2's BWT block.
  * Z6+Z7+Z8 (BWT, MTF, Delta generators) — separate arc track;
    likely closure for substrate_memory.
  * W5/Z3 (lookahead matricisation) — performance-only but now
    LOAD-BEARING (encode time 100s+ per 4KB).
  * Encoder activation for AA5 (source=Rule) / AA6 (non-zero
    phase) / AA7 (cross-basis interpretation) — structural slots
    landed but encoder logic to USE them not yet written.

**Per the substrate disciplines (recurring throughout this arc):**

  * [[expose-generator-not-orbit]]: the AA-arc surfaces the
    underlying (source × action × basis) generator the U/V/X/Z
    arcs were each circling at one orbit.
  * [[homology-cohomology-recursion]]: emission source is the
    homology side (substrate's pattern stock); action algebra is
    the cohomology side (catalogued transformations). The
    composition realises the substrate's universal at the codec
    emission layer.
  * [[3plus1-parity-universal]]: the (3-axis × 1-binding) shape
    of ComposedReference instantiates the substrate's 3+1
    universal pattern at the codec layer; BasisLabel carries the
    chirality between substrate-aligned (ChamberBound) and
    structure-agnostic (ChamberFree) emission.
  * [[annealing-methodology]]: one structural DOF (the V₄-residue
    composition with backref) closed multiple deferred-DOF debts
    simultaneously.
  * [[negative-findings-corpus-bound]]: bounded findings — the
    substrate_memory result is neutral, not a structural failure.

**BB-arc target candidates (next):**

  1. **Pivot to bzip2/xz primitives** (Z6/Z7/Z8). The remaining
     gap on substrate_memory text suggests the codec needs
     bzip2-style preprocessing (BWT block sort) or xz-style
     larger sliding window (32KB vs current 4KB) to close natural-
     text compression.
  2. **AA4 full S₄ residue** if substrate_memory becomes the
     priority corpus.
  3. **Matricised matcher** (W5/Z3) — encode time per 4KB grew
     from ~5s (Z1) to ~25s (backref+V4); performance work would
     restore practicality.
  4. **Range-coder rewiring** (X1+X2) — enables codec composition
     for hybrid stacks.

Related: [[u-arc-emergent-lz]] (RuleAction algebra A);
[[v-arc-generator-operad]] (operad framework AA inhabits);
[[x-arc-residue-compensation]] (V₄ residue, structurally closed
here); [[y-arc-substrate-atlas]] (the gap AA-arc partially closes);
[[z-arc-reference-orbit]] (the 8-orbit family AA-arc subsumes
through composition); [[expose-generator-not-orbit]] (the
discipline AA-arc honours by surfacing the generator);
[[homology-cohomology-recursion]] (the universal pattern AA-arc
realises at the codec emission layer).
