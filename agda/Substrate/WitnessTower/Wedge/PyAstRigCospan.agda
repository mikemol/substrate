------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.PyAstRigCospan
--
-- ⟡pyrig-cospan — the OFF-DIAGONAL residue of the wedge (Gap B): the
-- CROSS-TERM of two pyast rig-terms. Where the orbit (⟡pyrig-normalizer) is one
-- term up to the group, the cospan is TWO terms meeting in the shared carrier —
-- the pipeline's ast×cst coherence (jea_pyalg.CrossMix = Algebra.Wedge.CrossMul
-- realized for python).
--
-- The structural cross-term (what the pipeline computes; CrossMul's ALGEBRAIC
-- graded case is deferred there — "needs a richer common carrier"):
--   shared a b   — the generators of a that also occur in b: the coherent
--                  OVERLAP, the cross-term's shared part. Its residue (what each
--                  keeps the other lacks) is the graded obstruction.
--   orthogonal   — shared a b ≡ [] : disjoint support = CrossMul's clean /
--                  degree-0 correspondence (the CRT e₁·e₂ ≡ 0 orthogonality).
--
-- THE THEOREM (`shared-equivariant`): the cross-term is EQUIVARIANT — a
-- simultaneous group action relabels it by σ, `shared (act σ a) (act σ b) ≡
-- map σ (shared a b)`. So the cross-term's CONTENT is a well-defined invariant
-- of the orbit-pair; the relabelling is the GAUGE, the overlap the FIBER —
-- exactly jea_sppf_torsor's Σ-TORSOR-VERIFY (fiber shift-invariant, span the
-- gauge), now for the SPPF cross-term. The whole content is `∈?-inj`:
-- membership is preserved under an INJECTIVE relabel, and a group element's
-- action IS injective (IsPerm).
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.PyAstRigCospan where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin using (Fin; _≟_)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; cong₂; trans)
open import Substrate.Foundation.Empty using (⊥-elim)
open import Substrate.Foundation.Bool using (Bool; true; false)
open import Substrate.Foundation.Negation using (Dec; yes; no)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.SnGroup using (apply)
open import Substrate.WitnessTower.IsPermutation using (IsPerm)
open import Substrate.WitnessTower.Wedge.PyAstRig using (Objpy; act)
open import Substrate.WitnessTower.Wedge.PyAstRigNormalize using (positions; mapL; positions-map)

------------------------------------------------------------------------
-- membership + membership-filter (the cross-term's coherent overlap).
------------------------------------------------------------------------

_∈?_ : {n : ℕ} → Fin n → List (Fin n) → Bool
x ∈? []       = false
x ∈? (y ∷ ys) with x ≟ y
... | yes _ = true
... | no  _ = x ∈? ys

filter∈ : {n : ℕ} → List (Fin n) → List (Fin n) → List (Fin n)
filter∈ ys []       = []
filter∈ ys (x ∷ xs) with x ∈? ys
... | true  = x ∷ filter∈ ys xs
... | false = filter∈ ys xs

-- the SHARED support: the coherent overlap of two terms' generators (the cross-term).
shared : {n : ℕ} → Objpy n → Objpy n → List (Fin n)
shared a b = filter∈ (positions b) (positions a)

-- orthogonal (CrossMul's clean/degree-0 correspondence): disjoint support.
orthogonal : {n : ℕ} → Objpy n → Objpy n → Set
orthogonal a b = shared a b ≡ []

------------------------------------------------------------------------
-- THE CRUX: membership is invariant under an INJECTIVE relabelling.
------------------------------------------------------------------------

∈?-inj : {n m : ℕ} (f : Fin n → Fin m) →
         ((i j : Fin n) → f i ≡ f j → i ≡ j) →
         (y : Fin n) (ys : List (Fin n)) →
         (f y ∈? mapL f ys) ≡ (y ∈? ys)
∈?-inj f inj y []       = refl
∈?-inj f inj y (x ∷ xs) with f y ≟ f x | y ≟ x
... | yes _ | yes _ = refl
... | yes p | no ¬q = ⊥-elim (¬q (inj y x p))
... | no ¬p | yes q = ⊥-elim (¬p (cong f q))
... | no _  | no _  = ∈?-inj f inj y xs

-- filter-by-membership commutes with an injective relabel.
filter∈-map : {n m : ℕ} (f : Fin n → Fin m) →
              ((i j : Fin n) → f i ≡ f j → i ≡ j) →
              (ys xs : List (Fin n)) →
              filter∈ (mapL f ys) (mapL f xs) ≡ mapL f (filter∈ ys xs)
filter∈-map f inj ys []       = refl
filter∈-map f inj ys (x ∷ xs) rewrite ∈?-inj f inj x ys with x ∈? ys
... | true  = cong (x' ∷_) (filter∈-map f inj ys xs)
  where x' = f x
... | false = filter∈-map f inj ys xs

------------------------------------------------------------------------
-- THE THEOREM: the cross-term is EQUIVARIANT (the Σ-TORSOR-VERIFY: the overlap
-- is invariant under a simultaneous group action, up to the relabel gauge).
------------------------------------------------------------------------

shared-equivariant : {n : ℕ} (σ : Perm n) → IsPerm σ → (a b : Objpy n) →
                     shared (act σ a) (act σ b) ≡ mapL (apply σ) (shared a b)
shared-equivariant σ perm a b =
  trans (cong₂ filter∈ (positions-map (apply σ) b) (positions-map (apply σ) a))
        (filter∈-map (apply σ) perm (positions b) (positions a))
