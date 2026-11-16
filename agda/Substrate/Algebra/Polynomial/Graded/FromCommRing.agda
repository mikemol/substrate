------------------------------------------------------------------------
-- Substrate.Algebra.Polynomial.Graded.FromCommRing
--
-- The adapter from the `CommutativeRing` RECORD to `Graded.Over`'s flat
-- bundle: it extracts the coefficient operations + laws from the record and
-- opens `Graded.Over` over them, so `open Over CR` gives the whole graded
-- polynomial ring R[y] for any `CR : CommutativeRing A`.
--
-- Only `+-comm` needs work: it lives on the Ring's additive AbelianGroup,
-- whose monoid is `+-coherent`-equal (not definitionally) to the Semiring's
-- `+-monoid`; we transport it onto the `+-monoid` operation once. Everything
-- else is a direct projection (definitionally the operation `Over` expects).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Polynomial.Graded.FromCommRing where

open import Substrate.Algebra.Magma using (Magma)
open import Substrate.Algebra.Semigroup using (Semigroup; magma; ·-assoc)
open import Substrate.Algebra.Monoid using (Monoid; semigroup; ε; ε-left; ε-right)
open import Substrate.Algebra.Group using (Group; monoid; inv; inv-left)
open import Substrate.Algebra.AbelianGroup using (AbelianGroup; group; ·-comm)
open import Substrate.Algebra.Semiring using (Semiring; +-monoid; *-monoid;
  distrib-left; zero-absorb-left; zero-absorb-right)
open import Substrate.Algebra.Ring using (Ring; semiring; +-abelian; +-coherent)
open import Substrate.Algebra.CommutativeRing.Record
-- ⚑ WAS `import Substrate.Algebra.Polynomial.Graded as G`, whose `Over` is a PURE
-- BARREL — zero definitions of its own, sixteen `open Pₙ.Over … public`. Level 2 of
-- ⟡AMBIG35 retires it: this module was its ONLY importer (`--importers` → 1 edge
-- in), so the hop costs a re-export and buys nothing. The sixteen parts are opened
-- directly below, applied to the same arguments this module already computes.
--
-- ⚑ `Graded.agda:60-63` defended the barrel as *"the one legitimate re-export …
-- Graded.Over IS the public API"*, and that was true when it had far more consumers
-- than it does now. The ⟡helper-sweep rewired every consumer to the leaves and left
-- it at one — so the
-- justification retired before the barrel did.
import Substrate.Algebra.Polynomial.Graded.Defs as P0
import Substrate.Algebra.Polynomial.Graded.Laws.Distrib as P3
import Substrate.Algebra.Polynomial.Graded.Laws.Scalar as P4
import Substrate.Algebra.Polynomial.Graded.Laws.Basis as P5
import Substrate.Algebra.Polynomial.Graded.Laws.Linear as P6
import Substrate.Algebra.Polynomial.Graded.Laws.Monomial as P7
import Substrate.Algebra.Polynomial.Graded.Laws.MonomialDelta as P8
import Substrate.Algebra.Polynomial.Graded.Laws.Comm as P9
import Substrate.Algebra.Polynomial.Graded.Laws.Assoc as P10
import Substrate.Algebra.Polynomial.Graded.Laws.AssocMono as P11
import Substrate.Algebra.Polynomial.Graded.Laws.AssocLinearP as P12
import Substrate.Algebra.Polynomial.Graded.Laws.AssocLinearQ as P13
import Substrate.Algebra.Polynomial.Graded.Laws.AssocLinearR as P14
import Substrate.Algebra.Polynomial.Graded.Laws.AssocMain as P15
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst
open import Substrate.Foundation.Eq.Trans
import Substrate.Algebra.Polynomial.Graded.Laws.Nth as P1
import Substrate.Algebra.Polynomial.Graded.Laws.Conv as P2

module Over {A : Set} (CR : CommutativeRing A) where

  open import Substrate.Algebra.Polynomial.Graded.FromCommRing.R CR public
  open import Substrate.Algebra.Polynomial.Graded.FromCommRing.SR CR public
  open import Substrate.Algebra.Polynomial.Graded.FromCommRing.PlusM CR public
  open import Substrate.Algebra.Polynomial.Graded.FromCommRing.TimesM CR public
  open import Substrate.Algebra.Polynomial.Graded.FromCommRing.OpOf public
  open import Substrate.Algebra.Polynomial.Graded.FromCommRing.Zero CR public
  open import Substrate.Algebra.Polynomial.Graded.FromCommRing.One CR public
  open import Substrate.Algebra.Polynomial.Graded.FromCommRing.Plus CR public
  open import Substrate.Algebra.Polynomial.Graded.FromCommRing.Times CR public
  open import Substrate.Algebra.Polynomial.Graded.FromCommRing.PlusAssoc CR public
  open import Substrate.Algebra.Polynomial.Graded.FromCommRing.PlusIdentityL CR public
  open import Substrate.Algebra.Polynomial.Graded.FromCommRing.PlusIdentityR CR public
  open import Substrate.Algebra.Polynomial.Graded.FromCommRing.TimesAssoc CR public
  open import Substrate.Algebra.Polynomial.Graded.FromCommRing.TimesComm CR public
  open import Substrate.Algebra.Polynomial.Graded.FromCommRing.TimesIdentityL CR public
  open import Substrate.Algebra.Polynomial.Graded.FromCommRing.TimesDistribL CR public
  open import Substrate.Algebra.Polynomial.Graded.FromCommRing.TimesAbsorbL CR public
  open import Substrate.Algebra.Polynomial.Graded.FromCommRing.TimesAbsorbR CR public
  open import Substrate.Algebra.Polynomial.Graded.FromCommRing.PlusComm CR public
  open import Substrate.Algebra.Polynomial.Graded.FromCommRing.Neg CR public
  open import Substrate.Algebra.Polynomial.Graded.FromCommRing.PlusInverseL CR public
  open import Substrate.Algebra.Polynomial.Graded.FromCommRing.PlusInverseR CR public

    -- ⚑ QUALIFIED: `CommutativeRing`'s re-export is retired (⟡AMBIG35), so the
    -- projection names the record. Two modules provide `ring` — this one and
    -- `Algebra.Field` — so the bare spelling was never unambiguous; it only
    -- looked settled while one `open … public` happened to win.
  -- The coefficient ops + laws, exposed BY NAME (so consumers — B2 reduce-mod-f,
  -- B3, EEA — get 𝟘/_+_/… and the ring laws, not just the polynomial machinery).
  -- ⚑ ONE SIGNATURE PER NAME (⟡AMBIG35 Ⓐ1⁷ᶜ). These were `𝟘 𝟙 : A` and
  -- `_+_ _*_ : A → A → A` — one line declaring TWO names, which is fine here and
  -- has NO faithful placement once each name becomes its own leaf: the line cannot
  -- go to both without being duplicated, and cannot be derived per-name without
  -- the splitter INVENTING source. Separating them at the source makes the split a
  -- pure move, so the conservation guard stays absolute rather than needing an
  -- exemption for generated signatures.
  -- +-comm lives on the abelian group; transport it onto the +-monoid op
  -- via +-coherent (refl for coherently-built rings, e.g. GF256-Ring).
  -- coefficient negation + its inverse laws (the additive abelian group of R[y]/(f)
  -- needs genuine negation — GF256's char-2 `inv = id` is not available generically).
  -- Transport inv-left from the group's monoid onto the +-monoid op/zero via +-coherent.
  -- ⚑ SIXTEEN DIRECT APPLICATIONS, replacing one hop through `Graded.Over`. The
  -- argument list is identical — `Graded.Over` did nothing but forward these same
  -- fourteen names to these same sixteen parts, so opening them here is the barrel
  -- inlined, not a new dependency. `Graded.agda` now has ZERO importers.
  --
  -- ⚑ THESE ARE STILL `public`, and that is level 1's job, not level 2's. This
  -- module re-exports the polynomial machinery to MEASURED 2026-09-26, 35
  -- consumers; retiring THAT requires splitting `Over` into leaves and
  -- rewiring them, which is the next step. Level 2 removes one barrel; it
  -- does not pretend to remove both.
  open P0.Over  _+_ _*_ 𝟘 𝟙 +-assoc +-comm +-identityˡ +-identityʳ *-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ public
  open P1.Over  _+_ _*_ 𝟘 𝟙 +-assoc +-comm +-identityˡ +-identityʳ *-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ public
  open P2.Over  _+_ _*_ 𝟘 𝟙 +-assoc +-comm +-identityˡ +-identityʳ *-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ public
  open P3.Over  _+_ _*_ 𝟘 𝟙 +-assoc +-comm +-identityˡ +-identityʳ *-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ public
  open P4.Over  _+_ _*_ 𝟘 𝟙 +-assoc +-comm +-identityˡ +-identityʳ *-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ public
  open P5.Over  _+_ _*_ 𝟘 𝟙 +-assoc +-comm +-identityˡ +-identityʳ *-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ public
  open P6.Over  _+_ _*_ 𝟘 𝟙 +-assoc +-comm +-identityˡ +-identityʳ *-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ public
  open P7.Over  _+_ _*_ 𝟘 𝟙 +-assoc +-comm +-identityˡ +-identityʳ *-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ public
  open P8.Over  _+_ _*_ 𝟘 𝟙 +-assoc +-comm +-identityˡ +-identityʳ *-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ public
  open P9.Over  _+_ _*_ 𝟘 𝟙 +-assoc +-comm +-identityˡ +-identityʳ *-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ public
  open P10.Over _+_ _*_ 𝟘 𝟙 +-assoc +-comm +-identityˡ +-identityʳ *-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ public
  open P11.Over _+_ _*_ 𝟘 𝟙 +-assoc +-comm +-identityˡ +-identityʳ *-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ public
  open P12.Over _+_ _*_ 𝟘 𝟙 +-assoc +-comm +-identityˡ +-identityʳ *-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ public
  open P13.Over _+_ _*_ 𝟘 𝟙 +-assoc +-comm +-identityˡ +-identityʳ *-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ public
  open P14.Over _+_ _*_ 𝟘 𝟙 +-assoc +-comm +-identityˡ +-identityʳ *-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ public
  open P15.Over _+_ _*_ 𝟘 𝟙 +-assoc +-comm +-identityˡ +-identityʳ *-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ public
