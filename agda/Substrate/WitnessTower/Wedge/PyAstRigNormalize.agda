------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.PyAstRigNormalize
--
-- ⟡pyrig-normalizer — the FORGET direction of the orbit wedge: the interning
-- KEY. `normalize` sends a pyast rig-term to a canonical representative of its
-- Sₙ-ORBIT (positions relabelled to first-appearance rank), so that orbit-
-- equivalent terms — those related by a permutation of the generator positions
-- — get the SAME key. This is what makes orbit-interning (nodes = orbits, not
-- points) RUN: `intern (normalize t)`.
--
--   positions t   — the generator positions in pre-order (a fold over SPPF)
--   rank xs y     — the first-appearance rank of y in xs (its ℕ index)
--   normalize t   — mapSPPF (rank (positions t)) t : SPPF ℕ (relabel to ranks)
--
-- THE THEOREM (`normalize-orbit-inv`): for any GROUP element σ (IsPerm σ),
-- normalize (act σ t) ≡ normalize t. The whole content: first-appearance rank
-- is invariant under an INJECTIVE relabelling of positions (`rank-inj`), and a
-- permutation's action IS injective (IsPerm = apply injective). So the orbit's
-- canonical key does not depend on which point of the orbit you start from.
--
-- HONEST SCOPE: this is orbit-INVARIANCE (the property orbit-interning needs:
-- same orbit ⇒ same key). It targets `SPPF ℕ` (ranks), so idempotence is a
-- fixed-point statement over ℕ (a follow-on, not needed for correctness of the
-- key). Positions that repeat / are absent are handled (rank is a plain ℕ, not
-- forced to be a Perm) — so this is the GENERAL normalizer, not spine-only.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.PyAstRigNormalize where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin using (Fin; _≟_)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; cong₂; trans; sym)
open import Substrate.Foundation.Empty using (⊥-elim)
open import Substrate.Foundation.Negation using (Dec; yes; no)
open import Substrate.Foundation.List using (List; []; _∷_; _++_)
open import Substrate.Algebra.Semiring.SPPF using (SPPF; gen; one; _⊗_; _⊕_)
open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.SnGroup using (apply)
open import Substrate.WitnessTower.IsPermutation using (IsPerm)
open import Substrate.WitnessTower.Wedge.PyAstRig using (Objpy; mapSPPF; mapSPPF-∘; act)

------------------------------------------------------------------------
-- list map (local; keeps this module's imports minimal) + its ++-law.
------------------------------------------------------------------------

mapL : {A B : Set} → (A → B) → List A → List B
mapL f []       = []
mapL f (x ∷ xs) = f x ∷ mapL f xs

mapL-++ : {A B : Set} (f : A → B) (xs ys : List A) →
          mapL f (xs ++ ys) ≡ mapL f xs ++ mapL f ys
mapL-++ f []       ys = refl
mapL-++ f (x ∷ xs) ys = cong (f x ∷_) (mapL-++ f xs ys)

------------------------------------------------------------------------
-- positions : the generator positions of a term, in pre-order.
------------------------------------------------------------------------

positions : {G : Set} → SPPF G → List G
positions (gen g) = g ∷ []
positions one     = []
positions (a ⊗ b) = positions a ++ positions b
positions (a ⊕ b) = positions a ++ positions b

-- positions commutes with the free functor: positions (map f t) = map f (positions t).
positions-map : {G H : Set} (f : G → H) (t : SPPF G) →
                positions (mapSPPF f t) ≡ mapL f (positions t)
positions-map f (gen g) = refl
positions-map f one     = refl
positions-map f (a ⊗ b) =
  trans (cong₂ _++_ (positions-map f a) (positions-map f b))
        (sym (mapL-++ f (positions a) (positions b)))
positions-map f (a ⊕ b) =
  trans (cong₂ _++_ (positions-map f a) (positions-map f b))
        (sym (mapL-++ f (positions a) (positions b)))

------------------------------------------------------------------------
-- rank : the first-appearance rank of a position in a list (its ℕ index).
------------------------------------------------------------------------

rank : {n : ℕ} → List (Fin n) → Fin n → ℕ
rank []       y = zero
rank (x ∷ xs) y with x ≟ y
... | yes _ = zero
... | no  _ = suc (rank xs y)

-- THE CRUX: first-appearance rank is invariant under an INJECTIVE relabelling.
-- (f injective ⇒ the first occurrence of `f y` in `map f xs` is where `y` first
-- occurs in `xs`.) The two impossible branches are killed by injectivity / cong.
rank-inj : {n m : ℕ} (f : Fin n → Fin m) →
           ((i j : Fin n) → f i ≡ f j → i ≡ j) →
           (xs : List (Fin n)) (y : Fin n) →
           rank (mapL f xs) (f y) ≡ rank xs y
rank-inj f inj []       y = refl
rank-inj f inj (x ∷ xs) y with f x ≟ f y | x ≟ y
... | yes _ | yes _ = refl
... | yes p | no ¬q = ⊥-elim (¬q (inj x y p))
... | no ¬p | yes q = ⊥-elim (¬p (cong f q))
... | no _  | no _  = cong suc (rank-inj f inj xs y)

------------------------------------------------------------------------
-- mapSPPF respects pointwise-equal relabellings (a cong for the functor).
------------------------------------------------------------------------

mapSPPF-cong : {G H : Set} {f g : G → H} → ((x : G) → f x ≡ g x) →
               (t : SPPF G) → mapSPPF f t ≡ mapSPPF g t
mapSPPF-cong h (gen g) = cong gen (h g)
mapSPPF-cong h one     = refl
mapSPPF-cong h (a ⊗ b) = cong₂ _⊗_ (mapSPPF-cong h a) (mapSPPF-cong h b)
mapSPPF-cong h (a ⊕ b) = cong₂ _⊕_ (mapSPPF-cong h a) (mapSPPF-cong h b)

------------------------------------------------------------------------
-- normalize : the orbit canonical key (positions ↦ first-appearance rank).
------------------------------------------------------------------------

normalize : {n : ℕ} → Objpy n → SPPF ℕ
normalize t = mapSPPF (rank (positions t)) t

-- THE THEOREM: orbit-invariance. A group element σ (IsPerm σ) leaves the key
-- unchanged — orbit-equivalent terms get the SAME normalize. This is exactly
-- what orbit-interning needs (same orbit ⇒ same interned node).
normalize-orbit-inv : {n : ℕ} (σ : Perm n) → IsPerm σ → (t : Objpy n) →
                      normalize (act σ t) ≡ normalize t
normalize-orbit-inv σ perm t =
  trans (cong (λ ps → mapSPPF (rank ps) (mapSPPF (apply σ) t))
              (positions-map (apply σ) t))
  (trans (mapSPPF-∘ (rank (mapL (apply σ) (positions t))) (apply σ) t)
         (mapSPPF-cong (λ i → rank-inj (apply σ) perm (positions t) i) t))
