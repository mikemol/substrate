------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.MultilinearFromImages  (ⁿ̌ᵍ — existence half)
--
-- The GENERIC construction half of the n-linear universal property: from a
-- table of images on basis n-TUPLES, build an n-linear map realising them.
-- The fold of `linear-from-images` over a `Vec ℕ n` of arities — the
-- "generator of generators" proper (the GENERATOR, dual to ⁿ̌ᵘ's uniqueness
-- fold), with `linear-from-images` (n=1) and `apply₂`/`bilinear-from-images`
-- (n=2) as its first two unrollings.
--
-- Four deliverables, matching the n=2 completeness of BilinearFromImages:
--   apply-n                         the construction (nested linear-from-images)
--   multilinear-from-images-basis   THE universal property: hits the table
--   apply-n-multilinear             apply-n f IS multilinear (the certificate)
--   multilinear-from-images-unique  any multilinear map hitting the table = apply-n f
--
-- The certificate rests on `lin-comb-multilinear` — a linear combination of
-- multilinear maps is multilinear — which is the reusable fact that the
-- n-1-linear maps form an F₂-module closed under the `linear-from-images`
-- combination. Slot-0 linearity is inherited from the outer arity-1 map;
-- deeper slots are pushed through with images-cong / images-add /
-- images-scale, exactly as BilinearFromImages does the n=2 right leg.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.MultilinearFromImages where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans)

open import Substrate.Algebra.F2 using (F₂)
open import Substrate.Algebra.F2.Vector using (Vector; basis; _+ⱽ_; _*ₛ_)
open import Substrate.Algebra.F2.Linear using (Linear; apply; preserves-+; preserves-*ₛ)
open import Substrate.Algebra.F2.Linear.FromImages
  using (linear-from-images; apply-linear-from-images-basis)
open import Substrate.Algebra.F2.Linear.BilinearFromImages
  using (images-cong; images-add; images-scale; apply₂)
open import Substrate.Algebra.F2.Linear.MultilinearUniversal
  using ( Args; BasisIndices; basis-tuple; IsLinear; IsMultilinear
        ; multilinear-extensionality )

------------------------------------------------------------------------
-- The construction: nest `linear-from-images` over the arities. At each
-- slot the inner (n-1)-ary construction supplies the image family that the
-- outer arity-1 `linear-from-images` extends over the current slot.
------------------------------------------------------------------------

apply-n : ∀ {n} {ks : Vec ℕ n} {m} → (BasisIndices ks → Vector m) → Args ks → Vector m
apply-n {ks = []}     f tt         = f tt
apply-n {ks = k ∷ ks} f (u , rest) =
  apply (linear-from-images (λ i → apply-n (λ j → f (i , j)) rest)) u

------------------------------------------------------------------------
-- THE UNIVERSAL PROPERTY: apply-n f hits the table on basis tuples.
-- Outer arity-1 basis lemma peels slot 0; the IH discharges the rest.
------------------------------------------------------------------------

multilinear-from-images-basis :
  ∀ {n} {ks : Vec ℕ n} {m}
  (f : BasisIndices ks → Vector m) (idx : BasisIndices ks) →
  apply-n f (basis-tuple idx) ≡ f idx
multilinear-from-images-basis {ks = []}     f tt      = refl
multilinear-from-images-basis {ks = k ∷ ks} f (i , j) =
  trans (apply-linear-from-images-basis
           (λ i' → apply-n (λ j' → f (i' , j')) (basis-tuple j)) i)
        (multilinear-from-images-basis (λ j' → f (i , j')) j)

------------------------------------------------------------------------
-- A linear combination of multilinear maps is multilinear. (apply (lfi
-- (λ i → G i rest)) u is the F₂-combination of the G i with weights from u;
-- multilinearity in `rest` survives the combination.) The reusable engine
-- of the certificate; proved by induction on the remaining arities.
------------------------------------------------------------------------

lin-comb-multilinear :
  ∀ {k n} {ks : Vec ℕ n} {m}
  (G : Fin k → (Args ks → Vector m)) →
  ((i : Fin k) → IsMultilinear ks m (G i)) →
  (u : Vector k) →
  IsMultilinear ks m (λ rest → apply (linear-from-images (λ i → G i rest)) u)
lin-comb-multilinear {ks = []}     G Gml u = tt
lin-comb-multilinear {ks = l ∷ ls} G Gml u =
    (λ rest →
        ( (λ w w' → trans (images-cong (λ i → proj₁ (proj₁ (Gml i) rest) w w') u)
                          (images-add (λ i → G i (w , rest)) (λ i → G i (w' , rest)) u))
        , (λ c w → trans (images-cong (λ i → proj₂ (proj₁ (Gml i) rest) c w) u)
                         (images-scale c (λ i → G i (w , rest)) u)) ))
  , (λ w → lin-comb-multilinear (λ i rest → G i (w , rest))
                                (λ i → proj₂ (Gml i) w) u)

------------------------------------------------------------------------
-- The certificate: apply-n f is multilinear. Slot 0 = the outer arity-1
-- map's laws; deeper slots = lin-comb-multilinear over the IH.
------------------------------------------------------------------------

apply-n-multilinear :
  ∀ {n} {ks : Vec ℕ n} {m}
  (f : BasisIndices ks → Vector m) → IsMultilinear ks m (apply-n f)
apply-n-multilinear {ks = []}     f = tt
apply-n-multilinear {ks = k ∷ ks} f =
    (λ rest →
        ( preserves-+  (linear-from-images (λ i → apply-n (λ j → f (i , j)) rest))
        , preserves-*ₛ (linear-from-images (λ i → apply-n (λ j → f (i , j)) rest)) ))
  , (λ u → lin-comb-multilinear (λ i rest → apply-n (λ j → f (i , j)) rest)
                                (λ i → apply-n-multilinear (λ j → f (i , j)))
                                u)

------------------------------------------------------------------------
-- Uniqueness: any multilinear map agreeing with the table on basis tuples
-- equals apply-n f. (Existence-meets-uniqueness — closes the UP against
-- ⁿ̌ᵘ's multilinear-extensionality.)
------------------------------------------------------------------------

multilinear-from-images-unique :
  ∀ {n} {ks : Vec ℕ n} {m}
  (f : BasisIndices ks → Vector m)
  (g : Args ks → Vector m) → IsMultilinear ks m g →
  ((idx : BasisIndices ks) → g (basis-tuple idx) ≡ f idx) →
  (xs : Args ks) → g xs ≡ apply-n f xs
multilinear-from-images-unique f g gml matches =
  multilinear-extensionality g (apply-n f) gml (apply-n-multilinear f)
    (λ idx → trans (matches idx) (sym (multilinear-from-images-basis f idx)))

------------------------------------------------------------------------
-- Ⓑ: BilinearFromImages IS the n=2 instance of this generic construction.
-- `apply₂` (the bilinear existence map) reduces, DEFINITIONALLY, to `apply-n`
-- at arity (k ∷ l ∷ []) on the uncurried basis-pair table — so the existence
-- side, like the uniqueness side (BilinearUniversal: bilinear-extensionality =
-- multilinear-extensionality at n=2), is ONE INSTANCE of the generic, not a
-- parallel build. The either/or "apply₂ vs apply-n" dissolves: apply₂ is
-- apply-n, read at n=2.
--
-- (Ⓑ′ deferred — the module-level dependency inversion: relocating images-cong
-- /add/scale to a base module so BilinearFromImages imports this one rather
-- than vice-versa. Those are base-level linear-from-images properties with 3+
-- consumers (Bilinear, Multilinear, SymBilinForm); moving them is a separate
-- mechanical multi-file refactor, not bundled here.)
------------------------------------------------------------------------

apply₂-is-apply-n :
  ∀ {k l n} (f : Fin k → Fin l → Vector n) (u : Vector k) (v : Vector l) →
  apply₂ f u v
    ≡ apply-n {ks = k ∷ l ∷ []} (λ idx → f (proj₁ idx) (proj₁ (proj₂ idx))) (u , v , tt)
apply₂-is-apply-n f u v = refl
