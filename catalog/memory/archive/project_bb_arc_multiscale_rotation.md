---
name: bb-arc-multiscale-rotation
description: "BB-arc surfaces the scale generator hidden in eliza/octonion.py; multiscale Cayley-Dickson rotation (scale × k × f) wired into V7 as a byte-level transform; substrate's 3+1 universal recurs at every scale of the Cayley-Dickson ladder"
metadata: 
  node_type: memory
  type: project
  originSessionId: bb094a39-05c5-494d-8b01-cc34809ccae9
---

BB-arc closure summary. The arc was planned as 10 slices around
multiscale Cayley-Dickson rotation. Six substantive slices landed;
four deferred where the global-rotation prototype already
demonstrates the mechanism without sticky-scope or auto-speculation.

**The structural pivot.**

The substrate's `eliza/octonion.py` had infrastructure for 16
byte-rotations at the F₂-octonion-loop level — but only at byte
scale. Per the user: hardcoding "byte" was a rigidification of
the scale gauge. The BB-arc surfaces the scale generator:

  scale n: bit-width 2^n, group F₂^n × F₂ (size 2^(n+1))

  n = 0:  1-bit, 2 elements (chirality only)
  n = 1:  2-bit crumbs, 4 elements
  n = 2:  4-bit nibbles, 8 elements
  n = 3:  8-bit bytes, 16 elements (= octonion.py)
  n = 4:  16-bit words, 32 elements
  n = 5:  32-bit dwords, 64 elements

All rotations are involutions; encoder and decoder apply the SAME
rotation; round-trip via involution.

**Slices landed:**

  BB1-BB4 (commit `dca0484`) — `eliza/multiscale_rotation.py`
       module with `apply_rotation_to_bytes(data, scale, k, f)`;
       V7 integration with rotation_scale / rotation_k /
       rotation_f encoder params; header carries (scale, k, f);
       decoder applies same rotation (involution) after chain walk.
  BB7 — Empirical rotation sweep on substrate_memory_2KB across
       scales 2/3/4 × all (k, f) pairs. Best:
       scale=4 (word), k=15, f=1 → 7.398 b/byte
       (identity: 7.492). Modest 1.3% improvement.
  BB8 (commit `1b71d1a`) — `Substrate.Category.MultiscaleOctonion-
       Loop` Agda primitive. record Rotation (n : ℕ) + RotationAction
       parameterised over BitVector carrier. Per [[3plus1-parity-
       universal]] the (n axes × 1 chirality) structure realises
       the universal at every scale. --safe --without-K.

**Slices deferred:**

  BB5 — Sticky-scope mid-stream rotation. The global-rotation
       prototype works structurally; mid-stream emission of
       S_SCALE_ROTATE requires more substantial encoder/decoder
       restructuring (rotation state must track byte position).
       Deferred until empirical wins justify the lift.
  BB6 — Encoder rotation-speculation (auto-pick best rotation
       per region). The manual rotation parameter already
       demonstrates the mechanism; auto-speculation would search
       over the per-region (scale, k, f) space.
  BB9 — Composition with backref+S₄ (rotation × backref jointly).
       Test running; if rotation + backref+S₄ compound, the
       composition closes a larger gap on substrate corpora.

**Empirical (BB7 + BB9) — rotation and backref+S₄ do NOT compound:**

  T1+T2 (3KB):
    identity                       bpb = 2.747
    rotation only (3, 1, 0)        bpb = 2.168   ✓ (-21%)
    backref+S₄ (no rotation)        bpb = 0.642   ✓ (best)
    rotation + backref+S₄           bpb = 0.653   ✗ slight regression

  memory_2KB:
    identity                       bpb = 7.504
    rotation only (4, 15, 1)       bpb = 7.398   ✓ (-1.4%, best)
    backref+S₄ (no rotation)        bpb = 7.516   ✗ regresses
    rotation + backref+S₄           bpb = 7.703   ✗ worse

Per [[negative-findings-corpus-bound]]: at 2-3KB on these two
corpora, rotation alone is best on natural text (memory);
backref+S₄ alone is best on structured-recurrence text (T1+T2);
the combination doesn't compound — slight regression on T1+T2,
substantial regression on memory.

**Structural diagnosis (why composition fails):**

Rotation operates at the BYTE layer (before chain walk); backref
operates at the CHAIN-SYMBOL layer (after chain walk). The chain
walk is stateful (NIBBLE_TO_PERM composition), so applying a
byte-level rotation changes the entire downstream chain-symbol
sequence in non-trivial ways. The backref's S₄ residue search,
which was tuned to find chamber-state-aligned matches in the
NATURAL chain walk, now has to discover matches in a different
chamber-state-walked sequence. The 8-symbol backref payload
overhead is paid per match; if rotation reduces the number of
matches (or shifts which matches are profitable), the net effect
is negative.

The two axes are STRUCTURALLY ORTHOGONAL but EMPIRICALLY
INTERFERING. The substrate's ladder (V₄/S₄ at chain layer,
multiscale rotation at byte layer) is a valid generator family
but doesn't compose multiplicatively for compression.

**BB-arc deliverable is STRUCTURAL, not empirical:**

The scale generator is now first-class:
  * In runtime: `eliza/multiscale_rotation.py` exposes scales 0-5.
  * In substrate Agda: `Substrate.Category.MultiscaleOctonionLoop`
    names the family at every scale.
  * The codec's emission ring now has this generator as a peer
    of V₄/S₄ residue, backref, RuleAction, etc.

The empirical question (which combinations of generators compose
profitably) is now an EMPIRICAL QUESTION over a defined search
space — not a structural one.

**Per [[3plus1-parity-universal]]:** the (n × 1) structure at
every scale realises the universal — n bit-permutation axes plus
1 chirality F₂. At every level of the Cayley-Dickson ladder, the
same 3+1 pattern.

**Per [[expose-generator-not-orbit]]:** byte-only was the
rigidification; scale is now first-class. The 16 byte-rotations
in octonion.py are one orbit-point (scale=3); the substrate's
generator is `(scale ∈ ℕ, k ∈ F₂^scale, f ∈ F₂)`.

**Per [[choice-rigidification-in-substrate]]:** removing the byte-
specific hardcoding closes a rigidification on the scale gauge.

**Per [[tetrative-metacircularity]]:** the Cayley-Dickson ladder
n → n+1 doubles dimensions; the substrate's universal recurses
through every doubling. The codec operates at multiple levels
simultaneously.

**CC-arc target candidates (next):**

  1. **BB5+BB6 wired** — sticky mid-stream rotation + auto-
     speculation. Would let the encoder find the best rotation
     PER REGION and update mid-stream.
  2. **Composition with bzip2 BWT-style preprocessing** — the
     bigger gap to gzip on natural text needs block-level sort,
     not just rotation.
  3. **Range-coder rewiring** (X1+X2 deferred from prior arcs)
     — practical-speed compression composition.
  4. **Matricised matcher** (W5/Z3 deferred) — encode time is
     load-bearing now (100s per 4KB at backref+S₄ levels).

Related: [[u-arc-emergent-lz]] (RuleAction); [[v-arc-generator-
operad]] (operad framework); [[aa-arc-composed-reference]]
(parent arc — backref + V₄/S₄ residue composition);
[[z-arc-reference-orbit]] (8-orbit reference family);
[[y-arc-substrate-atlas]] (the gzip gap BB-arc partially
addresses).
