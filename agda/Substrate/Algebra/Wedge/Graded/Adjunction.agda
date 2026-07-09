------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Graded.Adjunction
--
-- Free ⊣ Forgetful at the GRADED carrier — the graded lift of
-- Algebra.Wedge.Adjunction (which was only over plain DivStr). Exactly the
-- same shape, definitional:
--
--   GradedWedge G n a b  ≅  gTerm G n a b      (uniform in G : GradedDivStr)
--
-- because `gTerm G n a b = Σ r. a ≡ recon G n b r` is the SAME data as a
-- graded wedge (rem + wedge-eq). Forgetful = `geval = recon` (the grade-raising
-- reconstruction); Free = package an element-with-decomposition; the
-- counit/triangle `geval (rem) ≡ a` IS the witness, read backward (and reading
-- it twice cancels: `sym-sym`).
--
-- So the Free⊣Forgetful core is uniform across all three wedge carriers:
-- DivStr (Wedge.Adjunction), GradedDivStr (here), and GradedProduct (via
-- `graded-of-product`, whose adjunction is this one at the +1-step slice).
-- HONEST SCOPE: the hom-iso + triangle core (as in the plain case); the full
-- FreeUP/naturality packaging is the uniting view (A3), not claimed here.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Graded.Adjunction where

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Eq using (_≡_; refl; sym)
open import Substrate.Foundation.Product using (Σ; _,_)
-- ⟡set1-paydown: GradedDivStr's carrier/remainder families are now its params, so
-- the old `C G` / `R G` projections become the (implicit) module params C / R here.
open import Substrate.Algebra.Wedge.Graded
  using (GradedDivStr; recon; GradedWedge; rem; wedge-eq;
         gforget; gforget-correct)
open import Substrate.Algebra.Wedge.Adjunction using (sym-sym)

module _ {C : ℕ → Set} {R : ℕ → Set} where

  ----------------------------------------------------------------------
  -- 1. Forgetful (geval) and the graded term it evaluates.
  ----------------------------------------------------------------------

  geval : (G : GradedDivStr C R) (n : ℕ) → C n → R n → C (suc n)
  geval = recon

  gTerm : (G : GradedDivStr C R) (n : ℕ) → C (suc n) → C n → Set
  gTerm G n a b = Σ (R n) (λ r → a ≡ recon G n b r)

  --------------------------------------------------------------------
  -- 2. The hom-set bijection GradedWedge ≅ gTerm, uniform in G — DEFINITIONAL.
  --------------------------------------------------------------------

  to : {G : GradedDivStr C R} {n : ℕ} {a : C (suc n)} {b : C n} →
       GradedWedge G n a b → gTerm G n a b
  to w = rem w , wedge-eq w

  from : {G : GradedDivStr C R} {n : ℕ} {a : C (suc n)} {b : C n} →
         gTerm G n a b → GradedWedge G n a b
  from (r , e) = record { rem = r ; wedge-eq = e }

  from∘to : {G : GradedDivStr C R} {n : ℕ} {a : C (suc n)} {b : C n}
            (w : GradedWedge G n a b) → from (to w) ≡ w
  from∘to _ = refl

  --------------------------------------------------------------------
  -- 3. The triangle law = the witness. geval after packaging returns the
  --    grade-(n+1) element: `geval n b (rem) ≡ a`, i.e. `gforget w ≡ a`.
  --------------------------------------------------------------------

  geval-eq : {G : GradedDivStr C R} {n : ℕ} {a : C (suc n)} {b : C n}
             (w : GradedWedge G n a b) → geval G n b (rem w) ≡ a
  geval-eq w = sym (wedge-eq w)

  gtriangle : {G : GradedDivStr C R} {n : ℕ} {a : C (suc n)} {b : C n}
              (w : GradedWedge G n a b) → gforget w ≡ a
  gtriangle = gforget-correct

  reorient : {G : GradedDivStr C R} {n : ℕ} {a : C (suc n)} {b : C n}
             (w : GradedWedge G n a b) → sym (geval-eq w) ≡ wedge-eq w
  reorient w = sym-sym (wedge-eq w)
