------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationFlatGradedBridge
--
-- ⟡rig-UP-flat-graded-bridge — the HONEST relation between the FLAT
-- division `divᴸ : DivStr (Σ ℕ LehmerPath)` (OrientationRigResidue) and the
-- GRADED `towerDiv : GradedDivStr LehmerPath (λ n → Fin (suc n))`
-- (OrientationTowerDiv). Theme: "flatten = the grade-collapse; expose the
-- last collapse."
--
-- THE LAST COLLAPSE. In the graded form the grade lives as a TYPE INDEX
-- (compile-time): `recon towerDiv n : C n → R n → C (suc n)` type-ENFORCES
-- the grade discipline (a step at grade n produces grade suc n, checked). The
-- flat form DEMOTES that index to a RUNTIME `proj₁` of `Σ ℕ LehmerPath`. The
-- grade-forgetting inclusion `ι {n} l = (n , l)` IS that demotion — the single
-- "last collapse" from a type-level index to a runtime tag.
--
--   ι {n} l = (n , l)                              -- index → runtime proj₁
--   proj₁ (ι l) ≡ n     (ι-grade)                  -- grade recoverable as proj₁
--   proj₂ (ι l) ≡ l     (ι-value)                  -- value recoverable
--   ι l ≡ ι l' → l ≡ l' (ι-injective)              -- so the collapse loses NO
--                                                  --   value DATA — only the
--                                                  --   type-level grade DISCIPLINE.
--   ι (recon towerDiv n l d) ≡ (suc n , l ◂ d)     -- (collapse-step) the graded
--                                                  --   tower step's flat image.
--
-- HONEST SCOPE — this is NOT "plain DivStr ⊂ GradedWedge" (a FORMER OVERCLAIM,
-- see the headers of Algebra.Wedge / Algebra.Wedge.Graded — there is NO such
-- degenerate embedding: the flat recon `C → C → C → C` [the rig product
-- (q⊗ˢb)⊕r] and the graded recon `C n → R n → C (suc n)` [the tower step l ◂ d]
-- are genuinely different SHAPES and ARITIES). We build NO `flatten : GradedDivStr
-- → DivStr` and we embed NEITHER DivStr into the other. The bridge is exactly the
-- grade-collapse ι — a section-with-forgotten-discipline, not a morphism of
-- DivStrs. The principled home of the flat/graded relation is the FORMAL ALLEGORY
-- Φ-chain refinement of `Substrate.Category.Allegory.Refinement` (ALG-7): the flat
-- form is the SHADOW / grade-collapse of the graded, and — as that file's NOTE
-- records — `GradedDivStr.R` is NOT itself a Φ-iterate. This module is consistent
-- with that framing and does not re-commit the plain⊂graded overclaim.
--
-- The bonus square `stepWedge-flat-image` sends the graded step wedge through
-- its FORGETFUL read `gforget` and then ι to the flat carrier — WITHOUT casting
-- it as a `divᴸ` corner (it is not one: divᴸ's corner is the grade-FIXED
-- reflexive rig wedge b↔b at (1,X),(0,start); the tower step RAISES the grade
-- n → suc n). `ι-z` ties ι to divᴸ's terminal element: the flat carrier
-- `Σ ℕ LehmerPath` IS ι's codomain and `ι start = z divᴸ`.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationFlatGradedBridge where

open import Substrate.Foundation.Nat using (ℕ; suc; _≟_)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; subst)
open import Substrate.Foundation.Hedberg using (Decidable⇒UIP)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; start; _◂_)
open import Substrate.Algebra.Wedge using (z)
open import Substrate.Algebra.Wedge.Graded using (recon; gforget)
open import Substrate.WitnessTower.Wedge.OrientationRigResidue using (divᴸ)
open import Substrate.WitnessTower.Wedge.OrientationTowerDiv using (towerDiv; stepWedge)

------------------------------------------------------------------------
-- 1. ι — the grade-forgetting inclusion: DEMOTE the type-level grade INDEX
--    to a runtime proj₁ of the flat carrier `Σ ℕ LehmerPath` (divᴸ's carrier).
--    This single arrow IS "the last collapse."
------------------------------------------------------------------------

ι : ∀ {n} → LehmerPath n → Σ ℕ LehmerPath
ι {n} l = n , l

------------------------------------------------------------------------
-- 2. The collapse loses NO value data — the grade AND the path are both
--    recoverable (proj₁ / proj₂), and ι is injective. What it loses is only
--    the compile-time grade DISCIPLINE (index → runtime tag).
------------------------------------------------------------------------

-- the grade is recoverable as proj₁ (the demoted index).
ι-grade : ∀ {n} (l : LehmerPath n) → proj₁ (ι l) ≡ n
ι-grade l = refl

-- the path value is recoverable as proj₂.
ι-value : ∀ {n} (l : LehmerPath n) → proj₂ (ι l) ≡ l
ι-value l = refl

-- and ι is injective: the demotion is faithful on data, so the collapse is
-- not lossy-on-data. Note WHY this is without-K safe (a plain `refl` pattern is
-- NOT — the dependent Σ-pair leaves a stuck reflexive index equation n = n): ℕ
-- is an h-set (Hedberg, from decidable `_≟_`), so the grade-path `cong proj₁ e`
-- IS trivial and the transported second component is the identity. The runtime
-- grade TAG being a set is exactly what makes the index→tag demotion faithful.
--
-- destruct a Σ-equality (the inverse of Product.Σ-≡,≡→≡): second components
-- agree after transporting along the first-component path.
Σ-proj₂-≡ : {p q : Σ ℕ LehmerPath} (e : p ≡ q) →
            subst LehmerPath (cong proj₁ e) (proj₂ p) ≡ proj₂ q
Σ-proj₂-≡ refl = refl

ι-injective : ∀ {n} {l l' : LehmerPath n} → ι l ≡ ι l' → l ≡ l'
ι-injective {n} {l} e =
  trans (cong (λ eq → subst LehmerPath eq l) (sym grade-triv)) (Σ-proj₂-≡ e)
  where
    grade-triv : cong proj₁ e ≡ refl
    grade-triv = Decidable⇒UIP _≟_ (cong proj₁ e) refl

------------------------------------------------------------------------
-- 3. collapse-step — the concrete "graded → flat" square on the tower STEP:
--    the graded (grade-raising) reconstruction `recon towerDiv n l d = l ◂ d`,
--    pushed through ι, is the flat pair `(suc n , l ◂ d)`. refl: recon towerDiv
--    reduces to ◂ definitionally, and ι tags the raised grade suc n at runtime.
------------------------------------------------------------------------

collapse-step : ∀ {n} (l : LehmerPath n) (d : Fin (suc n)) →
                ι (recon towerDiv n l d) ≡ (suc n , l ◂ d)
collapse-step l d = refl

------------------------------------------------------------------------
-- 4. (bonus) The honest tie to divᴸ WITHOUT an embedding.
--
--    ι-z: the flat carrier `Σ ℕ LehmerPath` IS ι's codomain, and ι carries
--    the grade-0 path `start` to divᴸ's terminal element z. So ι is a bridge
--    INTO divᴸ's carrier, not a DivStr morphism.
------------------------------------------------------------------------

ι-z : ι start ≡ z divᴸ
ι-z = refl

--    stepWedge-flat-image: the graded step wedge, read FORGETFULLY (gforget)
--    and then collapsed by ι, lands on the flat pair (suc n , l ◂ p). This is
--    the graded object's flat shadow — NOT a `divᴸ` corner (divᴸ's corner is
--    the grade-FIXED reflexive rig wedge; the tower step RAISES the grade). The
--    principled name for this relation is the allegory Φ-refinement (ALG-7), not
--    a plain⊂graded embedding.
stepWedge-flat-image : ∀ {n} (l : LehmerPath n) (p : Fin (suc n)) →
                       ι (gforget (stepWedge l p)) ≡ (suc n , l ◂ p)
stepWedge-flat-image l p = refl
