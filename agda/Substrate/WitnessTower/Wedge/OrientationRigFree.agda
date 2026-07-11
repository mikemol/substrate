------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigFree
--
-- ⟡rig-UP-free (Step 1 — THE HEART) — the concrete dissolution of the
-- insertion move ◂ into a RIG-TERM: a σ-INDEPENDENT rotation composed with
-- ⊕-ing the grade-1 generator.
--
--   insert-at p σ ≡ ρ p ∘ (insert-at 0 σ)          (insert-at 0 σ = X ⊕ σ)
--
-- where ρ p : Fin (suc m) → Fin (suc m) is the rotation cycle sending the
-- head to rank p:  ρ p 0 = p ,  ρ p (suc j) = punchIn p j.  It does NOT
-- depend on σ.  The composition ∘ is post-application to the image vector
-- (map ρ over the ordering).  numpy-verified (rig_free.py); here formalized.
--
-- CONSEQUENCE: ◂ = rotation ∘ ⊕-generator is a rig-term, so any map
-- respecting ⊕ and the rotation (braiding) already respects ◂ — the lever
-- that lifts the ◂-initiality (fold-unique) to the free-rig-algebra UP.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigFree where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; map; lookup; tabulate)
open import Substrate.Foundation.Vec.Properties using (lookup∘tabulate)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.Foundation.Empty using (⊥-elim)
open import Substrate.Foundation.Fin.Punctured using (punchIn; punchIn-≢)
open import Substrate.WitnessTower.Enumerate using (Perm; insert-at)
open import Substrate.WitnessTower.IsPermutation using (IsPerm; lookup-map; punchIn-injective)
open import Substrate.WitnessTower.Decompose using (lookup-ext)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; start; _◂_; decode)
open import Substrate.WitnessTower.Wedge.OrientationSum using (_⊕_)

------------------------------------------------------------------------
-- 1. THE ROTATION ρ p — σ-INDEPENDENT. Sends the new head (rank 0) to rank
--    p, and every witnessed rank (suc j) to punchIn p j (dodging p). This is
--    exactly the rotation cycle (0 p … 1) moving the head to position p.
------------------------------------------------------------------------

ρ : ∀ {m} → Fin (suc m) → Fin (suc m) → Fin (suc m)
ρ p zero    = p
ρ p (suc j) = punchIn p j

------------------------------------------------------------------------
-- 2. THE HEART: insert-at p σ = ρ p applied pointwise to insert-at 0 σ.
--    insert-at 0 σ = 0 ∷ map (punchIn 0) σ = X ⊕ σ (the generator block-sum),
--    and mapping ρ p over it rotates the head into rank p — recovering
--    insert-at p σ = p ∷ map (punchIn p) σ. Pointwise via lookup-ext.
--
--    Both sides reduce, at (suc j), to punchIn p (lookup σ j):
--      LHS: lookup (insert-at p σ) (suc j) = punchIn p (lookup σ j)
--      RHS: ρ p (lookup (insert-at 0 σ) (suc j))
--         = ρ p (punchIn 0 (lookup σ j)) = ρ p (suc (lookup σ j))
--         = punchIn p (lookup σ j)
------------------------------------------------------------------------

insert-at-rot : ∀ {m} (p : Fin (suc m)) (σ : Perm m) →
                insert-at p σ ≡ map (ρ p) (insert-at zero σ)
insert-at-rot {m} p σ =
  lookup-ext (insert-at p σ) (map (ρ p) w) pointwise
  where
    w : Perm (suc m)
    w = insert-at zero σ

    pointwise : (i : Fin (suc m)) →
                lookup (insert-at p σ) i ≡ lookup (map (ρ p) w) i
    -- head: lookup(insert-at p σ) 0 = p = ρ p (lookup w 0) = lookup(map (ρ p) w) 0
    pointwise zero    = sym (lookup-map (ρ p) w zero)
    -- witnessed rank: both sides are punchIn p (lookup σ j).
    pointwise (suc j) =
      trans (lookup-map (punchIn p) σ j)
            (sym rhs-eq)
      where
        rhs-eq : lookup (map (ρ p) w) (suc j) ≡ punchIn p (lookup σ j)
        rhs-eq = trans (lookup-map (ρ p) w (suc j))
                       (cong (ρ p) (lookup-map (punchIn zero) σ j))

------------------------------------------------------------------------
-- 3. THE ROTATION IS A PERMUTATION (Step 2, minimal form). ρ p is injective
--    as a function on Fin (suc m): 0 ↦ p is distinct from every suc j ↦
--    punchIn p j (punchIn dodges p — punchIn-≢), and punchIn p is injective
--    (punchIn-injective). So ρ p is a genuine bijection — the braiding
--    element realizing the head→rank-p rotation lives in Sₘ₊₁.
------------------------------------------------------------------------

ρ-injective : ∀ {m} (p : Fin (suc m)) {i j : Fin (suc m)} →
              ρ p i ≡ ρ p j → i ≡ j
ρ-injective p {zero}  {zero}  eq = refl
ρ-injective p {zero}  {suc j} eq = ⊥-elim (punchIn-≢ p j (sym eq))
ρ-injective p {suc i} {zero}  eq = ⊥-elim (punchIn-≢ p i eq)
ρ-injective p {suc i} {suc j} eq = cong suc (punchIn-injective p eq)

-- Packaged as the image-vector permutation `tabulate (ρ p) : Perm (suc m)`,
-- IsPerm (lookup injective) reduced to ρ-injective through lookup∘tabulate.
ρ-vec : ∀ {m} → Fin (suc m) → Perm (suc m)
ρ-vec p = tabulate (ρ p)

ρ-perm : ∀ {m} (p : Fin (suc m)) → IsPerm (ρ-vec p)
ρ-perm p i j eq =
  ρ-injective p
    (trans (sym (lookup∘tabulate (ρ p) i))
           (trans eq (lookup∘tabulate (ρ p) j)))

------------------------------------------------------------------------
-- 4. LIFT TO THE TOWER (Step 3, partial). The grade-1 generator X = start◂0
--    (a single element). ⊕-ing it on the LEFT of any path IS the canonical
--    ◂0 step — definitionally, since start⊕l = l and inject+ _ 0 = 0:
--
--      X ⊕ l ≡ l ◂ 0
--
--    so `insert-at 0 σ = X ⊕ σ` at the tower level. Combined with Step 1,
--    EVERY witnessing step decodes as the σ-independent rotation ρ p applied
--    to the generator block-sum:
--
--      decode (l ◂ p) ≡ ρ p ∘ decode (X ⊕ l)
--
--    i.e. the choice digit p enters ONLY through ρ p — ◂ is the rig-term
--    (rotation ∘ ⊕-generator), fully at the LehmerPath/decode level. This is
--    the lever the free-rig-algebra UP rests on: a hom respecting ⊕ and the
--    rotations is already determined on ◂.
------------------------------------------------------------------------

X : LehmerPath 1
X = start ◂ zero

-- ⊕-ing the generator on the left is the canonical ◂0 step (definitional).
gen-⊕-is-◂0 : ∀ {n} (l : LehmerPath n) → (X ⊕ l) ≡ (l ◂ zero)
gen-⊕-is-◂0 l = refl

-- THE TOWER-LEVEL DISSOLUTION: decode(l ◂ p) = ρ p ∘ decode(X ⊕ l).
decode-◂-rot : ∀ {n} (l : LehmerPath n) (p : Fin (suc n)) →
               decode (l ◂ p) ≡ map (ρ p) (decode (X ⊕ l))
decode-◂-rot l p = insert-at-rot p (decode l)
