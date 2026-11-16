---
name: 3plus1-parity-universal
description: "The recurring \"3+1 parity\" pattern (every 2-dim F₂-subspace's 3 nonzero elements sum to its identity) is the universal generator behind V4-Nonzero, Fano lines, OrbitKey, Live/Reserved, and extended Hamming's parity bit. Resist wrapper extraction; catalogue instances."
metadata: 
  node_type: memory
  type: project
  originSessionId: 28a7490c-cf4a-4933-8773-215362d96f13
---

**Pattern.** Every 2-dimensional F₂-subspace has 4 elements: 3 nonzero (which sum to 𝟎) + the identity (= the parity of the other 3). The defining relation `α + β + γ = 𝟎` makes the 4th element the sum of the other 3. This is the F₂² Klein-four parity relation.

**Lift.** When a 2-dim subspace W sits inside F₂^n with orthogonal complement U of dim (n−2):

- F₂^n = W ⊕ U; cosets of U correspond to elements of W
- 3 "non-identity W-component" cosets = 3 · 2^(n−2) elements (3/4 of ambient)
- 1 "identity W-component" coset = U itself = 2^(n−2) elements (1/4 of ambient)
- The identity coset = the parity (sum) of the other 3 cosets in W

The 3:1 ratio is constant in n because the generator (W = 2-dim F₂-subspace) is constant.

**Instances in the codebase:**

| n | W (2-dim) | "3" portion (3/4) | "1" portion = parity dual (1/4) |
|---|-----------|-------------------|----------------------------------|
| 2 | F₂² itself | V4-Nonzero (3) | `{𝟎}` (1) |
| 3 (Fano line) | the line's plane | 3 collinear points | `𝟎ⱽ` (off Fano) |
| 3 (F₂³ split) | V₄-plane `⟨e₁, e₂⟩` | OrbitKey (6) | chirality axis `⟨e₃⟩` (2) |
| 5 (Codeword) | V₄-coords plane `⟨e₃, e₄⟩` | Live (24) | Reserved (8) |
| 8 (ext-Hamming) | parity row | non-parity codewords | parity-zero codewords (the code) |

**Why this matters — discipline implication.**

Per shadow-architecture orbit-saturation discipline: this is a **generator-driven orbit** (W is the generator at every scale), NOT free duplication. Resist extracting a "V4-Codim2-Wrapper" record above the instances — the wrapper would just re-state `V4-Nonzero × U` for each n. Lattice classification is **S2G (catalogue orbit position), not RFS (extract universal record)**.

**Why this is the unification — Fano connection.**

M-9's `Collinear-Three p₁ p₂ p₃ = ((p₁ +ⱽ p₂) +ⱽ p₃) ≡ 𝟎ⱽ` closes by `refl` for all 7 lines precisely because each Fano line IS the n=2 instance of this pattern. The line's 3 collinear points are V4-Nonzero of the line's 2-dim subspace; the "4th point" is `𝟎ⱽ` (= the parity = the sum of the 3).

**Hodge dual reading.**

Under standard form in F₂^n, the codim-2 subspace U is Hodge-dual to the 2-dim W. So the "1/4 portion" is geometrically the Hodge dual of the V₄-plane. This is why M-11 (Hodge ★) should be planned as multi-scale (dim 3 for OrbitKey↔Fano, dim 5 for Live↔Reserved, dim 8 for ext-Hamming structure).

**Chirality = parity = Hodge dual (at every scale).**

The 1/4 codim-2 subspace U at every n carries the **chirality encoding**. The chirality bit is always one F₂ component of U:

| n | Hodge dual U | Where the chirality bit lives |
|---|--------------|-------------------------------|
| 2 | `{𝟎}` (0-dim, degenerate) | The 4th element IS the parity = chirality of V₄ |
| 3 | `⟨e₃⟩` (1-dim) | U *is* the chirality axis — this IS M-12 N-4 `Chirality ↔ F₂` |
| 5 | `⟨e₀, e₁, e₂⟩` (3-dim) | Bit 2 (the "sign" component) within Axes × Sign |
| 8 | parity-zero subspace | The overall parity bit IS the codeword's chirality |

So **M-12 N-4's `Chirality ↔ F₂` is the canonical chirality bridge at the smallest non-degenerate scale (n=3)**. Every larger Hodge-dual subspace U contains a chirality F₂ as one of its dimensions; the rest of U's dimensions encode positional axis data.

The F₂⁵ decomposition makes this explicit:

```
F₂⁵ = V₄ (⟨e₃, e₄⟩)  ⊕  Axes (⟨e₀, e₁⟩)  ⊕  Chirality (⟨e₂⟩)
      ↑ group-acted     ↑ positional       ↑ chirality bit
                        ─────────────────────────────────────
                              U (3-dim) = Reserved = Axis × Sign
```

This matches Codeword.agda's bit semantics (`b₀, b₁` axis, `b₂` sign, `b₃, b₄` V₄-coords).

**Implication for M-11:** Hodge ★ at every scale IS the chirality-encoding operator. Each scale's Hodge dual exposes the chirality axis perpendicular to V₄.

**Implication for M-8 ext-Hamming:** the overall parity bit IS the chirality of the codeword. Ext-Hamming = "Hamming with chirality balanced to zero." The 4th parity-check row IS the chirality projection.

**F₂³ is the canonical base — higher scales are Axes-subdivisions.**

The map `proj : F₂^n ↠ F₂³` (drop the Axes bits, keep V₄-coords and chirality) preserves the V₄/Hodge-dual structure. Each F₂³ point has a fiber of `2^(n−3)` higher-n points indexed by Axes-choice. So **F₂³ is the minimum-information space for the chirality-as-Hodge-dual structure; higher-n instances are F₂³ × Axes-subdivision**.

At n=5 (Codeword):

| Subspace at F₂⁵ | Projects to (F₂³) | Fiber size |
|------------------|--------------------|-----------|
| V₄-plane `⟨e₃, e₄⟩` (4) | V₄-plane (4) | bijection |
| `⟨e₂⟩` chirality-alone (2) | chirality-axis (2) | bijection |
| Reserved (8) | chirality-axis (2) | 4-fold cover |
| Live (24) | OrbitKey (6) | 4-fold cover |

So Reserved is a 4-fold cover of chirality-axis, and Live is a 4-fold cover of OrbitKey, under axis-projection. The "subdivision" reading: each lower-n cell splits into 2^k higher-n cells; the V₄/chirality split is invariant.

**Implication for M-11 lifts:** future M-11.dim5 / .dim8 / .fano slices can be built as "transport `HodgeComplement-Dim3` across the projection," rather than re-deriving from scratch. The orthogonality survives because the dot product factors through projection on the Axes-vs-not-Axes split.

**Why the parity-bit construction of M-8 simplifies.**

Extended Hamming [8, 4, 4] adds an "overall parity bit" to Hamming [7, 4, 3]. The parent plan's M-8 caveat ("needs dual-code construction") is over-stated under the 3+1 reading: the parity bit IS the F₂² parity relation lifted to length 8. The construction reduces to "append a row of all-𝟙 to the parity-check matrix."

**Cross-references:** [[feedback_expose_generator_not_orbit]], [[feedback_v4_typeclass_architecture]], [[project_homology_cohomology_recursion]], [[feedback_composable_primitives_over_flat_enumeration]].
