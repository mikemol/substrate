{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeSKIEncodeInj — ⟡extrude-ski-encode-inj-codec: the section's
-- total-space encoding injectivity, REUSING the wedge/recon codec (the guided tour of ADD 259, not a
-- hand-rolled block-proof). The tour: Factoradic (the tower flatten IS Wedge/recon: (suc n)! = recon ℕ-div
-- (suc n) n! 0) → Algebra.Wedge (recon q b r = q·b+r, the keystone) → Algebra.Wedge.BoundedIso.
-- recon-bounded-unique (recon INJECTIVE ON BOUNDED RESIDUES, = divmod-unique at the recon interface).
--
-- THE CODEC: a Total point (n , i) with i : Fin (suc n) is a WEDGE against the fixed base (suc n): the
-- quotient is the RUNG n, the remainder is the offset toℕ i (bounded: toℕ i < suc n, toℕ-bound). So
-- encode (n , i) = recon ℕ-div n (suc n) (toℕ i) = n * suc n + toℕ i. SAME-rung injectivity is
-- recon-bounded-unique DIRECTLY (fixed base suc n, both residues bounded). This grounds the section (258)
-- as an UNCONDITIONAL TowerLabeling on same-rung points; the cross-rung total order is the factoradic
-- ladder (scoped — it needs the mixed-radix carry, a further codec composition).
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: encode (the recon wedge),
-- encode-inj-sameRung (same-rung injectivity via recon-bounded-unique + toℕ-injective), and the resulting
-- same-rung label distinctness. The framing ('the codec grounds encode-inj') is (prose: the tour's result;
-- the full cross-rung flatten is the factoradic composition, scoped).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudeSKIEncodeInj where

open import Substrate.Foundation.Eq using (_≡_; refl; cong; sym; trans)
open import Substrate.Foundation.Product using (Σ; _,_; _×_; proj₁; proj₂)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_; _<_)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Fin.Op2
open import Substrate.Foundation.Fin.Properties using (toℕ-bound; toℕ-injective)
open import Substrate.Algebra.Wedge using (ℕ-div; recon)
open import Substrate.Algebra.Wedge.BoundedIso using (recon-bounded-unique)
open import Substrate.Algebra.R.Trace.SKIShedDuality using () renaming (Tm to Tm⟦533ef80d⟧)
open import Substrate.Category.UniversalProperty.ExtrudeSKISection using (Kⁿ; Kⁿ-inj)

------------------------------------------------------------------------
-- ① THE CODEC ENCODE: a same-rung point is a WEDGE against base (suc n). encode-at n i = recon ℕ-div n
--    (suc n) (toℕ i) = n * suc n + toℕ i, with toℕ i BOUNDED (< suc n). This is the wedge/recon codec (the
--    tour's structure), not an ad-hoc pairing.
------------------------------------------------------------------------
encode-at : (n : ℕ) → Fin (suc n) → ℕ
encode-at n i = recon ℕ-div n (suc n) (toℕ i)

------------------------------------------------------------------------
-- ② SAME-RUNG INJECTIVITY, straight from recon-bounded-unique (the tour's endpoint = divmod-unique at the
--    recon interface). Two same-rung points with equal encodings have equal offsets (recon-bounded-unique),
--    hence equal vertices (toℕ-injective). NO hand-rolled block argument — the codec supplies it.
------------------------------------------------------------------------
encode-at-inj : (n : ℕ) (i j : Fin (suc n)) → encode-at n i ≡ encode-at n j → i ≡ j
encode-at-inj n i j eq =
  toℕ-injective (proj₂ (recon-bounded-unique n n n (toℕ i) (toℕ j) (toℕ-bound i) (toℕ-bound j) eq))

------------------------------------------------------------------------
-- ③ THE SECTION IS INJECTIVE ON EACH RUNG (label = Kⁿ ∘ encode-at): distinct same-rung vertices get
--    distinct K-spine normal forms. So the ω-vertex NF-section (258) is grounded per fibre — the fibre
--    Fin (suc n) embeds injectively into the NF combinators via the codec, unconditionally.
------------------------------------------------------------------------
label-at : (n : ℕ) → Fin (suc n) → Tm⟦533ef80d⟧
label-at n i = Kⁿ (encode-at n i)

label-at-inj : (n : ℕ) (i j : Fin (suc n)) → label-at n i ≡ label-at n j → i ≡ j
label-at-inj n i j eq = encode-at-inj n i j (Kⁿ-inj eq)

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — encode-inj is the wedge/recon CODEC's injectivity through DivStr, NOT a
-- hand-rolled block-proof; the guided tour (259) delivered the exact keystone): the either/or "hand-roll the
-- triangular block argument OR import leaf-lemmas and re-derive it" DISSOLVED (259) into the substrate's
-- codec architecture, and THIS turn instantiates it: a same-rung Total point (n , i) is a WEDGE against base
-- (suc n) — encode-at n i = recon ℕ-div n (suc n) (toℕ i), the offset BOUNDED (toℕ-bound). recon-bounded-
-- unique (= divmod-unique at the recon interface, BoundedIso) gives injectivity DIRECTLY: equal encodings ⟹
-- equal offsets ⟹ equal vertices (toℕ-injective). So label-at is injective per fibre — the fibre Fin (suc n)
-- ↪ NF combinators, via the codec, unconditionally, with ZERO hand-rolled arithmetic. The tour's endpoint
-- (recon-bounded-unique) was the encode-inj I kept trying to reprove. D-study-implementations discharged.
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = the per-fibre (same-rung) injectivity via the codec
-- (encode-at-inj / label-at-inj), reusing recon-bounded-unique + toℕ-bound + toℕ-injective — no hand-rolled
-- block-proof. SCOPED: the CROSS-RUNG total flatten (a single injective encode : Σ ℕ (Fin (suc n)) → ℕ over
-- ALL rungs) is the FULL factoradic/mixed-radix composition (carry across rung bases) — ⟡extrude-ski-total-
-- flatten, itself a codec composition through DivStr (Factoradic is the ladder); the per-fibre grounding here
-- already makes the section injective ON EACH RUNG (the fibres are disjoint by rung, so this is the
-- load-bearing half). What's grounded: encode-inj per fibre is the codec's recon-bounded-unique — reuse, not
-- reinvention.
------------------------------------------------------------------------
