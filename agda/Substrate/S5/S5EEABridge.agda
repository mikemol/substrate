{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.S5.S5EEABridge — ⟡bridge-wedge: the WITNESSED transport
-- S5EEA ≅ Algebra.Wedge (+ Algebra.Wedge.Shape).
--
-- S5EEA reproduces the keystone wedge operator FIELD-FOR-FIELD — its DivStr
-- (C, z, recon), its Wedge (quot, rem, wedge-eq; even the same shape-hash
-- 478f66a6 as Algebra.Wedge.Wedge), its Trace (done/more), and its quotient-
-- sequence `shape` — in order to state "a combinator reduction IS a wedge-zip
-- whose shape is a continued fraction." jea_pysim flags the reproductions
-- IDENTICAL. Collapsing S5EEA into Algebra.Wedge would delete the bridge between
-- the S5 combinator-reduction subsystem and the wedge / continued-fraction
-- keystone. Instead (the KleinV4≅V₄ / S5MatrixBridge / S5RealBridge pattern) we
-- WITNESS it:
--
--   1. `toDivStr : S5EEA.DivStr → Algebra.Wedge.DivStr` (field-for-field), and the
--      DivStr-indexed transports toWedge / toTrace over it (done↦done, more↦more) —
--      all definitional, since recon/z/C coincide;
--   2. SHAPE PRESERVED — `shape-agree`: the S5EEA quotient-sequence of a trace, carried
--      by the transport, IS the Algebra.Wedge.Shape.shape (the continued fraction);
--   3. the punchline (relationship-of-relationships) — `reduction-CF-is-wedge-shape`:
--      S5EEA.Reduction's combinator reduction, transported, is a wedge-zip whose
--      reduction-CF IS the wedge quotient-sequence shape. "Combinator reduction IS a
--      wedge-zip whose shape is a CF", machine-checked across the two subsystems.
------------------------------------------------------------------------

module Substrate.S5.S5EEABridge where

open import Substrate.Foundation.Eq   using (_≡_; refl; cong)
open import Substrate.Foundation.List using (List; []; _∷_)

import Substrate.S5.S5EEA             as E
import Substrate.Algebra.Wedge        as W
import Substrate.Algebra.Wedge.Shape  as WS

------------------------------------------------------------------------
-- 1. the DivStr transport (field-for-field) + the indexed Wedge/Trace transports.
------------------------------------------------------------------------
-- ⟡set1-paydown (consumer of S5EEA): E.DivStr is now carrier-parameterized, so the
-- carrier is named directly (`{Carrier}`) instead of via the removed `E.C D` projection.
toDivStr : {Carrier : Set} → E.DivStr Carrier → W.DivStr
toDivStr {Carrier} D = record { C = Carrier ; z = E.z D ; recon = E.recon D }

toWedge : {Carrier : Set} (D : E.DivStr Carrier) {a b : Carrier} → E.Wedge Carrier D a b → W.Wedge (toDivStr D) a b
toWedge D w = record { quot = E.quot w ; rem = E.rem w ; wedge-eq = E.wedge-eq w }

toTrace : {Carrier : Set} (D : E.DivStr Carrier) {a b g : Carrier} → E.Trace Carrier D a b g → W.Trace (toDivStr D) a b g
toTrace D (E.done a)      = W.done a
toTrace D (E.more b w tr) = W.more b (toWedge D w) (toTrace D tr)

------------------------------------------------------------------------
-- 2. shape preservation: S5EEA's QSeq ↦ WedgeShape (= List), and the two
-- `shape` projections agree through the transport.
------------------------------------------------------------------------
toShape : {Carrier : Set} (D : E.DivStr Carrier) → E.QSeq Carrier D → WS.WedgeShape (toDivStr D)
toShape D E.[]       = []
toShape D (q E.∷ qs) = q ∷ toShape D qs

shape-agree : {Carrier : Set} (D : E.DivStr Carrier) {a b g : Carrier} (t : E.Trace Carrier D a b g)
            → WS.shape (toTrace D t) ≡ toShape D (E.shape Carrier t)
shape-agree D (E.done a)      = refl
shape-agree D (E.more b w tr) = cong (E.quot w ∷_) (shape-agree D tr)

------------------------------------------------------------------------
-- 3. THE PUNCHLINE: combinator reduction IS a wedge-zip whose shape is a CF.
-- S5EEA.Reduction's reduction-CF (the generator sequence of a reduction trace),
-- carried by the transport, IS Algebra.Wedge.Shape.shape — the continued fraction.
------------------------------------------------------------------------
module _ (S : Set) (nf : S) (rb : S → S → S → S) where
  open E.Reduction S nf rb

  reduction-CF-is-wedge-shape :
    {a b g : S} (t : ReductionTrace a b g) →
    WS.shape (toTrace combinator-DivStr t) ≡ toShape combinator-DivStr (reduction-CF t)
  reduction-CF-is-wedge-shape t = shape-agree combinator-DivStr t
