------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.StarV4
--
-- THE TWISTED ARROW — placing a V₄ = ℤ/2 × ℤ/2 at the centre of the wedge iso-
-- groupoid (Wedge.IsoGroupoid). Answer to: "the groupoid has an arrow at the
-- centre; what places a twisted arrow there, and an arrow + a twisted arrow (a
-- V₂×V₂ = V₄)?"
--
--   • THE ARROW (V₂, unconditional): the groupoid's inverse `iso-sym` is the
--     dagger † — a self-inverse. Its fraction-level shadow is `recip` (swap).
--   • THE TWISTED ARROW (the second V₂): a CONJUGATION `bar` — but it needs a
--     *-INVOLUTION on the carrier (`StarDivStr.conj`). Over plain ℚ (conj = id)
--     the twist is TRIVIAL — `bar = id`, so V₄ collapses back to V₂; you only
--     have the inverse. The conjugation turns genuine exactly at ℂ = ℚ(i) — the
--     Cayley–Dickson ℝ→ℂ step ("lose self-conjugacy", CayleyDickson.agda).
--   • V₄ (both): ⟨†, bar⟩ ≅ ℤ/2 × ℤ/2 (Groups.V4-as-Z2xZ2). The V₄-not-dihedral
--     condition is that the two involutions COMMUTE — proven here (`recip-bar`).
--     The fourth element † ∘ bar is the transpose/adjoint.
--
-- CROSSMUL IS A KLEIN ROTATION (user): on the 2×2 arrangement ((a,b),(c,d)),
-- ⟨rowSwap, colSwap⟩ ≅ V₄, and the 180° rotation `klein-rot` PERMUTES the two
-- diagonals (a,d) and (b,c) that cross-multiplication compares (a·d vs b·c) —
-- so cross-multiplication's comparison is V₄-equivariant: it IS a Klein rotation.
-- No multiplication is needed; it is the symmetry of the ARRANGEMENT.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.StarV4 where

open import Substrate.Foundation.Eq using (_≡_; refl; cong; cong₂)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Algebra.Wedge using (DivStr; C; recon)

------------------------------------------------------------------------
-- 1. *-DivStr: a wedge carrier equipped with a conjugation (a *-involution
--    compatible with reconstruction). The structure the twist requires.
------------------------------------------------------------------------

record StarDivStr : Set₁ where
  field
    base       : DivStr
    conj       : C base → C base
    conj-conj  : (x : C base) → conj (conj x) ≡ x
    conj-recon : (q b r : C base) →
                 conj (recon base q b r) ≡ recon base (conj q) (conj b) (conj r)

open StarDivStr public

module _ (S : StarDivStr) where
  private
    X  = C (base S)
    cj = conj S

  ------------------------------------------------------------------------
  -- 2. THE V₄ AT THE CENTRE: two commuting involutions on a fraction (a,b).
  --    recip = the dagger † (= the iso-sym inverse, fraction-level); bar = the
  --    conjugation twist. ⟨recip, bar⟩ ≅ ℤ/2 × ℤ/2.
  ------------------------------------------------------------------------

  Frac : Set
  Frac = X × X

  recip : Frac → Frac                       -- the dagger / inverse (V₂ #1)
  recip (a , b) = (b , a)

  bar : Frac → Frac                         -- the conjugation twist (V₂ #2)
  bar (a , b) = (cj a , cj b)

  recip-recip : (f : Frac) → recip (recip f) ≡ f
  recip-recip (a , b) = refl

  bar-bar : (f : Frac) → bar (bar f) ≡ f
  bar-bar (a , b) = cong₂ _,_ (conj-conj S a) (conj-conj S b)

  -- THE V₄ CONDITION: the dagger and the twist COMMUTE (so ⟨†,bar⟩ is abelian
  -- V₂×V₂, not dihedral). The fourth element recip∘bar is the transpose/adjoint.
  recip-bar : (f : Frac) → recip (bar f) ≡ bar (recip f)
  recip-bar (a , b) = refl

  ------------------------------------------------------------------------
  -- 3. CROSSMUL = A KLEIN ROTATION. The 2×2 arrangement ((a,b),(c,d)); the V₄
  --    ⟨rowSwap, colSwap⟩; the 180° rotation permutes the diagonals (a,d),(b,c)
  --    that cross-multiplication compares.
  ------------------------------------------------------------------------

  Mat : Set
  Mat = Frac × Frac                          -- ((a,b),(c,d))

  rowSwap : Mat → Mat
  rowSwap (r₁ , r₂) = (r₂ , r₁)

  colSwap : Mat → Mat
  colSwap ((a , b) , (c , d)) = ((b , a) , (d , c))

  rowSwap-rowSwap : (m : Mat) → rowSwap (rowSwap m) ≡ m
  rowSwap-rowSwap (r₁ , r₂) = refl

  colSwap-colSwap : (m : Mat) → colSwap (colSwap m) ≡ m
  colSwap-colSwap ((a , b) , (c , d)) = refl

  -- the two generators commute ⟹ ⟨rowSwap, colSwap⟩ ≅ V₄.
  row-col : (m : Mat) → rowSwap (colSwap m) ≡ colSwap (rowSwap m)
  row-col ((a , b) , (c , d)) = refl

  -- the Klein rotation = the 180° turn (the nontrivial central V₄ element).
  klein-rot : Mat → Mat
  klein-rot m = rowSwap (colSwap m)

  -- the diagonals cross-multiplication compares.
  diag  : Mat → X × X
  diag  ((a , _) , (_ , d)) = (a , d)        -- main diagonal a·d
  adiag : Mat → X × X
  adiag ((_ , b) , (c , _)) = (b , c)        -- anti-diagonal b·c

  swapP : X × X → X × X
  swapP (x , y) = (y , x)

  -- CROSSMUL IS A KLEIN ROTATION: the 180° turn swaps each diagonal's entries
  -- (a↔d, b↔c) — it fixes the two diagonals AS the unordered pairs that
  -- cross-multiplication compares. So the cross-comparison is V₄-equivariant.
  klein-diag : (m : Mat) → diag (klein-rot m) ≡ swapP (diag m)
  klein-diag ((a , b) , (c , d)) = refl

  klein-adiag : (m : Mat) → adiag (klein-rot m) ≡ swapP (adiag m)
  klein-adiag ((a , b) , (c , d)) = refl
