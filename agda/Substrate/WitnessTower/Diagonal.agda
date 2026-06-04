------------------------------------------------------------------------
-- Substrate.WitnessTower.Diagonal
--
-- ONE ATOM, THREE FACES (user, 2026-06-04): "this is diagonalization, too;
-- the same disagreement that happens at a diagonal is the disagreement that
-- happens at grades is the disagreement that happens between the cone's apex
-- and its base."
--
-- The atom is the F₂ fact `𝟙 + b ≢ b`: the residue at a coordinate ALWAYS
-- disagrees with its source there. (Constructive negation — a derivation of
-- ⊥ from the equation via constructor disjointness, reusing Algebra.F2's
-- 𝟙≢𝟘 / 𝟘≢𝟙 — not absence-of-proof.) It is `flip-disagrees`. Its three
-- instantiations, all the SAME atom:
--
--   * APEX vs BASE (the cone). The Hodge residue ★ (FaceSet) flips the apex
--     bit: head (★ (b ∷ f)) = 𝟙 + b, which disagrees with the original head
--     b. The newest (apex) coordinate at each dimension is the cone's own
--     diagonal entry — ★ flips it. `apex-disagrees`.
--   * GRADES (no fixed point). Hence the cell-level ★ has NO fixed face:
--     ★ S ≡ S is impossible, because they already disagree at the apex.
--     `★-no-fixpoint`. (The grade-LABEL shadow is Hodge.witness-distinct.)
--   * THE DIAGONAL (Cantor). Given rows M i, the witness D whose i-th bit is
--     the flip 𝟙 + (M i)ᵢ differs from EVERY row at coordinate i — so D is
--     not among the rows. `cantor-diagonal`. Same flip, run along i.
--
-- So Cantor's diagonal, the grade ★'s fixed-point-freeness, and the cone's
-- apex/base distinction are one phenomenon: the residue disagreeing with the
-- quotient at the distinguished coordinate. The disagreement is exactly the
-- wedge residue (FaceSet.★) refusing to vanish.
--
-- Zero postulates, --safe --without-K. All algebra imported.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Diagonal where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Vec using (Vec; _∷_; head; lookup)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙; _+_; 𝟙≢𝟘; 𝟘≢𝟙)
open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.WitnessTower.FaceSet using (Face; ★)

------------------------------------------------------------------------
-- 1. THE ATOM. The residue 𝟙 + b never equals its source b. Constructive:
--    case on b routes to F₂'s existing constructor-disjointness refutations.
------------------------------------------------------------------------

flip-disagrees : (b : F₂) → 𝟙 + b ≡ b → ⊥
flip-disagrees 𝟘 eq = 𝟙≢𝟘 eq    -- 𝟙 + 𝟘 = 𝟙, so the equation is 𝟙 ≡ 𝟘
flip-disagrees 𝟙 eq = 𝟘≢𝟙 eq    -- 𝟙 + 𝟙 = 𝟘, so the equation is 𝟘 ≡ 𝟙

------------------------------------------------------------------------
-- 2. APEX vs BASE. ★ flips the apex bit (head (★ (b ∷ f)) = 𝟙 + b), so the
--    residue disagrees with the face at the apex — the cone's diagonal entry.
------------------------------------------------------------------------

apex-disagrees : {n : ℕ} (b : F₂) (f : Vector n) → ★ (b ∷ f) ≡ (b ∷ f) → ⊥
apex-disagrees b f eq = flip-disagrees b (cong head eq)

------------------------------------------------------------------------
-- 3. GRADES (no fixed point). The cell-level ★ has no fixed face: a face is
--    always a cons (apex ∷ base), and they disagree at the apex.
------------------------------------------------------------------------

★-no-fixpoint : {n : ℕ} (S : Face n) → ★ S ≡ S → ⊥
★-no-fixpoint (b ∷ f) eq = apex-disagrees b f eq

------------------------------------------------------------------------
-- 4. THE DIAGONAL (Cantor). Any D whose i-th bit is the flip of row i's
--    i-th bit differs from row i — at coordinate i. The same atom, indexed
--    by i along the diagonal. No row equals D ⟹ D is not in the list.
------------------------------------------------------------------------

cantor-diagonal :
  {n : ℕ} (M : Fin n → Vector n) (D : Vector n)
  (is-flip : (i : Fin n) → lookup D i ≡ 𝟙 + lookup (M i) i)
  (i : Fin n) → D ≡ M i → ⊥
cantor-diagonal M D is-flip i eq =
  flip-disagrees (lookup (M i) i)
    (trans (sym (is-flip i)) (cong (λ v → lookup v i) eq))
