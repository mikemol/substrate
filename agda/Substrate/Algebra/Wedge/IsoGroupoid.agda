------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.IsoGroupoid
--
-- Ⓤ.reify-setoid — the constructive "how close to a groupoid" invariant for the
-- interconnect's iso-edges. A `CategoryOf`+`IsGroupoid` over `≡` is funext-
-- blocked (it needs `WedgeIso`/`Bridge` equality of the `translate` functions).
-- The constructive route is SETOID-ENRICHMENT: morphism-equality is the
-- POINTWISE `_≈ʷ_`, and the groupoid structure holds over it WITHOUT funext —
-- because `_⊚_` is literal function composition, `id-bridge`'s translate is
-- `id`, and `WedgeIso`'s round-trips (`bwd∘fwd`, `fwd∘bwd`) are already pointwise.
--
-- The result: the interconnect's WedgeIso layer is a (setoid-enriched) GROUPOID,
-- machine-checked — identity/composition (`iso-id`/`iso-∘`, Wedge.Iso) + the
-- category laws over `≈ʷ` (all `refl`) + EVERY morphism invertible (`iso-sym`,
-- with the round-trips). The groupoid-DISTANCE is then exactly the non-iso
-- `Bridge`s of `Wedge.Registry` (parity, inclusion, …) — universal arrows of
-- several kinds (free/initial, cofree/terminal, quotient), which live OUTSIDE
-- this groupoid. That split is the answer to "how close to a groupoid."
--
-- Zero postulates, --safe --without-K (no funext, no guardedness).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.IsoGroupoid where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans)
open import Substrate.Algebra.Wedge using (DivStr; C)
open import Substrate.Algebra.Wedge.Bridge using (translate)
open import Substrate.Algebra.Wedge.Iso
  using (WedgeIso; fwd; bwd; bwd∘fwd; fwd∘bwd; iso-id; iso-sym; iso-∘)

------------------------------------------------------------------------
-- 1. The setoid enrichment: pointwise equality of the forward maps. (Funext-
--    free — it IS the pointwise statement, never collapsed to a function ≡.)
------------------------------------------------------------------------

_≈ʷ_ : {A B : DivStr} → WedgeIso A B → WedgeIso A B → Set
_≈ʷ_ {A} c d = (x : C A) → translate (fwd c) x ≡ translate (fwd d) x

≈ʷ-refl : {A B : DivStr} (c : WedgeIso A B) → c ≈ʷ c
≈ʷ-refl c x = refl

≈ʷ-sym : {A B : DivStr} {c d : WedgeIso A B} → c ≈ʷ d → d ≈ʷ c
≈ʷ-sym e x = sym (e x)

≈ʷ-trans : {A B : DivStr} {c d e : WedgeIso A B} → c ≈ʷ d → d ≈ʷ e → c ≈ʷ e
≈ʷ-trans p q x = trans (p x) (q x)

------------------------------------------------------------------------
-- 2. The CATEGORY LAWS over ≈ʷ — all `refl` (⊚ = function composition,
--    id-bridge translate = id), so NO funext is needed.
------------------------------------------------------------------------

≈ʷ-idˡ : {A B : DivStr} (f : WedgeIso A B) → iso-∘ (iso-id B) f ≈ʷ f
≈ʷ-idˡ f x = refl

≈ʷ-idʳ : {A B : DivStr} (f : WedgeIso A B) → iso-∘ f (iso-id A) ≈ʷ f
≈ʷ-idʳ f x = refl

≈ʷ-assoc : {A B M N : DivStr}
           (h : WedgeIso M N) (g : WedgeIso B M) (f : WedgeIso A B) →
           iso-∘ (iso-∘ h g) f ≈ʷ iso-∘ h (iso-∘ g f)
≈ʷ-assoc h g f x = refl

------------------------------------------------------------------------
-- 3. THE GROUPOID PROPERTY (IsGroupoid, setoid form): every WedgeIso is
--    invertible up to ≈ʷ — inverse `iso-sym`, the round-trips ARE the witness.
------------------------------------------------------------------------

≈ʷ-invˡ : {A B : DivStr} (c : WedgeIso A B) → iso-∘ (iso-sym c) c ≈ʷ iso-id A
≈ʷ-invˡ c x = bwd∘fwd c x

≈ʷ-invʳ : {A B : DivStr} (c : WedgeIso A B) → iso-∘ c (iso-sym c) ≈ʷ iso-id B
≈ʷ-invʳ c y = fwd∘bwd c y
