# DBE: items 1+2+3 cluster — RETROSPECTIVE

**Status:** Attempted; partial result. L-1 + L-2 (s3-to-orbit-key
auxiliary refactor + cong) landed cleanly in OrbitKey-S3.agda. The
S4Iso.agda migration (items 1 + 2 in the audit) was reverted.

## What worked

L-1 in OrbitKey-S3.agda — refactor `s3-to-orbit-key` via an auxiliary
`s3-to-orbit-key-from : Fin 3 → Fin 3 → OrbitKey`. Parallel to the
`extract-s-from` refactor in S4-Iso.agda (commit a40e9bd). Makes the
function's with-cases unfold under proof-level `with SFin.apply ... in eq`.

L-2 in OrbitKey-S3.agda — `s3-to-orbit-key-cong : pointwise eq at
zero + suc zero → s3-to-orbit-key eq`. One-line `cong₂` once L-1
is in place.

## What didn't work — and why

The audit estimated items 1+2+3 as "same shape as V₄ ⊳ S₄ migration."
In practice they are **tightly coupled through `classify-CS`**, which
is a publicly exported predicate-dispatch function with at least two
consumers (LiveS4Iso, LiveS4Bijection).

Attempted migration:
- New `stab-d-to-orbit-key σ σ-stab = proj₁ (stab-anchor-decomposes-
  orbitkey D σ σ-stab)` (structural via SP combinator).
- New `stab-round-trip = proj₂` (structural).
- New `ok-round-trip` via `s3-to-orbit-key-cong + restrict-extend +
  s3-to-orbit-key-of-orbit-key-to-s3` (structural).

Build state: S4Iso.agda + S4GroupIso.agda compiled clean against the
new structural definitions. BUT LiveS4Bijection's `stab-roundtrip`
relied on the OLD definitional equality
`stab-d-to-orbit-key σ σ-stab = classify-CS (apply σ C) (apply σ S)`,
which no longer holds.

Fixing LiveS4Bijection would require a **classify-CS-to-structural bridge**:
```
classify-CS (apply σ C) (apply σ S) ≡ stab-d-to-orbit-key σ σ-stab
                                       (for σ ∈ Stab-D)
```
This bridge is provable but has **the same 16-cell case structure** as
the `stab-round-trip` dispatch we tried to retire. Net result: no
predicate code retired; the dispatch just moves files.

## Root cause

`classify-CS` is a **predicate boundary**: it dispatches on Axis pairs,
which is fundamentally pointwise even when wrapped by SP-structural
primitives. To fully retire it, one would need to:
1. Refactor `classify-CS = s3-to-orbit-key-from ∘ axis-to-fin3` (NEW).
2. Either match the OLD wildcard semantics for `D` arguments OR update
   `LiveS4Bijection.stab-from-selector-eq-orbit`'s 16-cell `refl`
   table to use the new behaviour.
3. Cascade to `classify-CS-to-selector` (parallel structure in LiveS4Iso).

This isn't structurally impossible — it's a deeper refactor than the
V₄ ⊳ S₄ migration. The V₄ predicate (`is-V₄-shape`) had **no external
consumers** beyond V4-Normality itself; classify-CS does.

## Updated audit verdict

The audit's "items 1+2+3 same shape" estimate was correct at the
structural level but underestimated the **consumer coupling**. The
real cost is in `classify-CS`'s external surface, not in the case-
{α,β,γ}-{even,odd} dispatch.

Suggested next move (if items 1+2 to be tackled): refactor
`classify-CS` itself first (item 0), via `axis-to-fin3` + 
`s3-to-orbit-key-from`, in a way that **preserves the wildcard
behaviour** the consumers rely on. Then items 1+2 collapse.

Estimated effort: same as the V₄ ⊳ S₄ migration, but distributed
across classify-CS + stab-from-selector-eq-orbit + classify-CS-to-
selector. About 300-400 lines of cascading refactoring rather than
the 100-line in-file retirement the audit estimated.

## Shadows preserved for future work

- `s3-to-orbit-key-from` + `s3-to-orbit-key-cong` (OrbitKey-S3.agda,
  L-1 + L-2). Useful infrastructure even though not consumed today.
- The structural `stab-d-to-orbit-key` pattern was validated:
  `proj₁ (stab-anchor-decomposes-orbitkey D σ σ-stab)` is the right
  structural replacement.
- The bridge lemma signature is named (`classify-CS-equals-stab-d-
  to-orbit-key-on-Stab-D`) and its case structure understood (16
  cases: 6 refl + 10 σ-injective ⊥-elim).
