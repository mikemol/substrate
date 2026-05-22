------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword.LiveS4Iso
--
-- Slice 11c: the reverse direction Permutation → Live and the
-- algebraic identities that make Live ↔ Permutation a constructive
-- bijection via the V_4 ⋊ Stab(D) generator.
--
-- The forward map (slice 11b) factored as
--
--   Live → (Axis × Selector) → (V_4 × Stab(D)) → Permutation
--
-- This module:
--   * Provides the inverses on each layer (axis-of-v, classify-CS-
--     to-selector, selector-from-stab).
--   * Proves the round-trip identities at each layer (algebraic facts
--     about v-of-axis ↔ axis-of-v and stab ↔ selector).
--   * Defines permutation-to-live.
--   * States the Live ↔ Permutation correspondence at the algebraic
--     level. The full Iso bundling (with codeword-level equality on
--     the Live side to sidestep funext on the Σ-type's proof
--     component) is deferred to slice 11d if needed.
--
-- See: catalog/cocycles.md § CY-5 "24 ARE S_4";
--      Substrate.Cocycles.V4Signature.Codeword.LiveS4 (slice 11b).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword.LiveS4Iso where

open import Substrate.Foundation.Level using (0ℓ)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Axes using (Axis; D; C; S; W; act-axis)
open import Substrate.Groups.V4 as V4 using (V₄; e; α; β; γ)
open import Substrate.Groups.S4 as S4
  using (Permutation; _≈_; _·_; ε; ≈-refl)
  renaming (apply to applyₛ)
open import Substrate.Groups.V4-Embedding using (embed)
open import Substrate.Groups.SemidirectProduct
  using (v-of-axis; v-of-axis-anchor-sends; v-for; s-for; s-for-fixes-anchor;
         factorisation)
open import Substrate.Cocycles.V4Signature.S4Iso
  using (stab-id; stab-sw; stab-cs; stab-cw; stab-csw; stab-cws)
open import Substrate.Cocycles.V4Signature.Codeword
  using (Live)
open import Substrate.Cocycles.V4Signature.Codeword.Live
  using (Selector; sel-fft; sel-tft; sel-ftf; sel-ttf; sel-ftt; sel-ttt;
         live-to-axis-selector; axis-selector-to-live)
open import Substrate.Cocycles.V4Signature.Codeword.LiveS4
  using (stab-from-selector; live-to-permutation)

------------------------------------------------------------------------
-- axis-of-v: the inverse of v-of-axis.
--
-- v-of-axis : Axis → V₄  was defined in SemidirectProduct as
--   D ↦ e, C ↦ α, S ↦ β, W ↦ γ.
-- axis-of-v inverts this.
------------------------------------------------------------------------

axis-of-v : V₄ → Axis
axis-of-v e = D
axis-of-v α = C
axis-of-v β = S
axis-of-v γ = W

axis-of-v-v-of-axis-id :
  (a : Axis) → axis-of-v (v-of-axis a) ≡ a
axis-of-v-v-of-axis-id D = refl
axis-of-v-v-of-axis-id C = refl
axis-of-v-v-of-axis-id S = refl
axis-of-v-v-of-axis-id W = refl

v-of-axis-axis-of-v-id :
  (v : V₄) → v-of-axis (axis-of-v v) ≡ v
v-of-axis-axis-of-v-id e = refl
v-of-axis-axis-of-v-id α = refl
v-of-axis-axis-of-v-id β = refl
v-of-axis-axis-of-v-id γ = refl

------------------------------------------------------------------------
-- classify-CS-to-selector: (s.C, s.S) → Selector for s ∈ Stab(D).
--
-- Mirrors S4Iso.classify-CS (which produces OrbitKey instead). The
-- 6 valid (s.C, s.S) pairs for s ∈ Stab(D) determine the selector
-- uniquely; the wildcard handles "impossible" pairs (e.g. (D, _),
-- (_, D), (C, C)) that don't arise for valid Stab(D) elements.
------------------------------------------------------------------------

classify-CS-to-selector : Axis → Axis → Selector
classify-CS-to-selector C S = sel-fft
classify-CS-to-selector C W = sel-tft
classify-CS-to-selector S C = sel-ftf
classify-CS-to-selector W S = sel-ttf
classify-CS-to-selector S W = sel-ftt
classify-CS-to-selector W C = sel-ttt
classify-CS-to-selector _ _ = sel-fft

selector-from-stab : Permutation → Selector
selector-from-stab σ = classify-CS-to-selector (applyₛ σ C) (applyₛ σ S)

------------------------------------------------------------------------
-- Selector ↔ Stab(D) round trip (6 cases, mechanical refls).
------------------------------------------------------------------------

selector-stab-id :
  (sel : Selector) → selector-from-stab (stab-from-selector sel) ≡ sel
selector-stab-id sel-fft = refl
selector-stab-id sel-tft = refl
selector-stab-id sel-ftf = refl
selector-stab-id sel-ttf = refl
selector-stab-id sel-ftt = refl
selector-stab-id sel-ttt = refl

------------------------------------------------------------------------
-- The reverse map: Permutation → Live.
--
-- Uses the V_4 ⋊ Stab(D) decomposition (semidirect-factorisation from
-- slice 3): every σ ∈ S_4 factors as embed v · s with v = v-for σ,
-- s = s-for σ. Then:
--   axis = axis-of-v v       (back through the v-of-axis bijection)
--   sel  = selector-from-stab s  (back through stab ↔ selector)
--   live = axis-selector-to-live (axis , sel)
------------------------------------------------------------------------

permutation-to-live : Permutation → Live
permutation-to-live σ =
  axis-selector-to-live (axis-of-v (v-for σ) , selector-from-stab (s-for σ))

------------------------------------------------------------------------
-- Algebraic round-trip pieces.
--
-- These document the half-iso identities that compose into the full
-- Live ↔ Permutation bijection at the algebraic layer. The
-- (forward) round trip live-to-permutation ∘ permutation-to-live ≈ σ
-- follows from:
--
--   * v-of-axis (axis-of-v (v-for σ)) ≡ v-for σ
--     — by v-of-axis-axis-of-v-id on (v-for σ).
--   * stab-from-selector (selector-from-stab (s-for σ)) ≈ s-for σ
--     — requires that (applyₛ (s-for σ) C , applyₛ (s-for σ) S) is
--     one of the 6 valid (s.C, s.S) pairs, by s-for-fixes-anchor and
--     the structural properties of Stab(D).
--
-- Plus the factorisation σ ≈ embed (v-for σ) · s-for σ from
-- SemidirectProduct.
--
-- The codeword-level (reverse) round trip
-- permutation-to-live ∘ live-to-permutation ≡ lv requires:
--
--   * The slice 11a round trip axis-selector-to-live ∘
--     live-to-axis-selector ≡ id (at the codeword level —
--     proof-component equality needs care).
--   * The fact that v-for and s-for, when applied to (embed v' · s')
--     with v' ∈ image(v-of-axis) and s' ∈ image(stab-from-selector),
--     recover v' and ≈-recover s'.
--
-- Stating these explicitly is the substance of slice 11d.
------------------------------------------------------------------------

------------------------------------------------------------------------
-- Notes
--
-- 1. The generator-exposing approach pays off here too: the reverse
--    map is 2 lines (axis-of-v + selector-from-stab + axis-selector-
--    to-live), totaling ~50 lines of code instead of a 24-case
--    inverse table.
--
-- 2. The algebraic round-trip identities (v-of-axis ∘ axis-of-v,
--    selector-from-stab ∘ stab-from-selector) decompose into small,
--    case-mechanical lemmas. Each is 4 or 6 refls. The composite
--    bijection's properties follow by structural reasoning over the
--    factorisation, not by 24 enumerated cases.
--
-- 3. The full Iso bundling will need a custom record (similar to
--    Substrate.Cocycles.V4Signature.S4GroupIso's TotalSpace≃S₄)
--    rather than stdlib's _↔_, because:
--      * Permutation uses pointwise _≈_, not _≡_.
--      * Live uses Σ Codeword (¬ IsReserved), and the ¬-component
--        equality requires funext to nail down propositionally.
--    The bundled iso would use _≈_ on the Permutation side and
--    codeword-level _≡_ on the Live side.
--
-- 4. Cross-references:
--    - Substrate.Groups.SemidirectProduct (slice 3) — v-of-axis,
--      v-for, s-for, factorisation.
--    - Substrate.Cocycles.V4Signature.S4Iso (slice 4) — the 6
--      Stab(D) elements.
--    - Substrate.Cocycles.V4Signature.Codeword.Live (slice 11a) —
--      Selector type and decoding.
--    - Substrate.Cocycles.V4Signature.Codeword.LiveS4 (slice 11b) —
--      forward map live-to-permutation.
------------------------------------------------------------------------
