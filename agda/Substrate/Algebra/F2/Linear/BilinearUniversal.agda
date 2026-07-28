------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.BilinearUniversal
--
-- The UNIQUENESS half of the bilinear universal property, obtained as the
-- arity-2 INSTANCE of the generic `multilinear-extensionality` (ⁿ̌ᵘ) — NOT a
-- parallel hand-proof. A `Bilinear` is exhibited as an `IsMultilinear` over
-- the two-arity vector `k ∷ l ∷ []` (its four leg-laws ARE the slot-indexed
-- `IsMultilinear` fields), and bilinear-extensionality is then the generic
-- theorem read back through that adapter.
--
-- This discharges what an earlier note asserted but did not prove — that the
-- bilinear/trilinear/n-linear extensionalities "run the same recipe": the
-- recipe is the generic fold, and the lower arities are its instances. The
-- arity-1 leg machinery this file used to carry (left-leg/right-leg +
-- linear-extensionality ×2) is exactly what the generic fold performs
-- internally, so it is gone from here.
--
-- Together with `BilinearFromImages` (the EXISTENCE half), this is the full
-- universal property of the tensor — what `Category.TensorProduct` N-3 /
-- `Category.TensorProduct.Bilinearity` named as the deferred piece.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.BilinearUniversal where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec using (_∷_; [])
open import Substrate.Foundation.Unit using (tt)
open import Substrate.Foundation.Product using (_,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; sym; trans)

open import Substrate.Algebra.F2.Vector using (Vector; basis)
open import Substrate.Algebra.F2.Linear.BilinearFromImages
  using ( Bilinear; apply₂′
        ; preserves-+ₗ; preserves-*ₛₗ; preserves-+ᵣ; preserves-*ₛᵣ
        ; bilinear-from-images; bilinear-from-images-basis )
open import Substrate.Algebra.F2.Linear.MultilinearUniversal
  using ( Args; IsMultilinear; basis-tuple; multilinear-extensionality )

------------------------------------------------------------------------
-- A Bilinear IS a 2-ary multilinear map: uncurry it onto Args (k ∷ l ∷ [])
-- and read the four leg-laws as the IsMultilinear fields.
------------------------------------------------------------------------

b→f : ∀ {k l n} → Bilinear k l n → Args (k ∷ l ∷ []) → Vector n
b→f B args = apply₂′ B (proj₁ args) (proj₁ (proj₂ args))

b→ml : ∀ {k l n} (B : Bilinear k l n) → IsMultilinear (k ∷ l ∷ []) n (b→f B)
b→ml B =
    (λ rest → ( (λ u u' → preserves-+ₗ B u u' (proj₁ rest))
              , (λ c u → preserves-*ₛₗ B c u (proj₁ rest)) ))
  , (λ u → ( (λ rest' → ( (λ v v' → preserves-+ᵣ B u v v')
                        , (λ c v → preserves-*ₛᵣ B c u v) ))
           , (λ v → tt) ))

------------------------------------------------------------------------
-- Bilinear extensionality: agreement on all basis PAIRS ⟹ agreement
-- everywhere — the generic multilinear-extensionality at arity 2.
------------------------------------------------------------------------

bilinear-extensionality :
  ∀ {k l n} (B B' : Bilinear k l n) →
  ((i : Fin k) (j : Fin l) → apply₂′ B (basis i) (basis j) ≡ apply₂′ B' (basis i) (basis j)) →
  (u : Vector k) (v : Vector l) → apply₂′ B u v ≡ apply₂′ B' u v
bilinear-extensionality {k} {l} {n} B B' agree u v =
  multilinear-extensionality {ks = k ∷ l ∷ []} {m = n}
    (b→f B) (b→f B') (b→ml B) (b→ml B')
    (λ { (i , j , _) → agree i j })
    (u , v , tt)

------------------------------------------------------------------------
-- Capstone — the UNIVERSAL PROPERTY of the tensor, in full: any bilinear
-- map that matches a basis-pair table IS the free bilinear map of that
-- table (existence = BilinearFromImages, uniqueness = here).
------------------------------------------------------------------------

bilinear-from-images-unique :
  ∀ {k l n} (f : Fin k → Fin l → Vector n) (B : Bilinear k l n) →
  ((i : Fin k) (j : Fin l) → apply₂′ B (basis i) (basis j) ≡ f i j) →
  (u : Vector k) (v : Vector l) → apply₂′ B u v ≡ apply₂′ (bilinear-from-images f) u v
bilinear-from-images-unique f B matches u v =
  bilinear-extensionality B (bilinear-from-images f)
    (λ i j → trans (matches i j) (sym (bilinear-from-images-basis f i j)))
    u v
