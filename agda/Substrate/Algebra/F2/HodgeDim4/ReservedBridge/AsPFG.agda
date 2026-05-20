------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.ReservedBridge.AsPFG
--
-- The HodgeDim4 GaugeTorsor + GL3F2 SylowDecomposition packaged as a
-- full PrimeFactoredGauge instance. Closes
-- [[reserved-selfdual-bijection-gauge]] within the generic
-- PrimeFactoredGauge framework: the 168-bridge gauge family at
-- HodgeDim4 is now a STRUCTURAL instance of the universal PFG
-- primitive (T1), not just an ad-hoc GaugeTorsor.
--
-- T7 of the prime-factored-gauge arc per
-- [[prime-factored-gauge-arc]]. Combines:
--   * T6's GL3F2-SylowDecomposition-from-joint (Sylow predicates +
--     constructor parametric on joint-gen)
--   * The existing HodgeDim4 GaugeTorsor (= GL3F2 acting on itself
--     by left-multiplication; the substrate's first GTorsor instance)
--
-- Together: a PrimeFactoredGauge GL3F2 GL3F2 _·G_ id-GL _≈G_ _≈G_ 3,
-- parametric on the joint-generation witness.
--
-- Per [[multi-route-equivariance-recovery]] + the generic theorem
-- (T5): once this PFG is supplied with a joint-generated witness,
-- the multi-route-equivariance theorem applies — gauge elements
-- between any two of the 168 bridges decompose into Sylow-product
-- chains via the substrate's "extended Euclid for groups" content.
--
-- Per [[choice-rigidification]]: the bridges remain orbit-points of
-- the torsor; no specific bridge is privileged. The Sylow witnesses
-- (swap01, cycle3, singer) anchor the prime-decomposition layer.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.ReservedBridge.AsPFG where

open import Data.Fin using (Fin)
open import Data.Product using (Σ; _,_)

open import Substrate.Algebra.GL3F2
  using (GL3F2; _·G_; id-GL)
open import Substrate.Algebra.GL3F2.SylowDecomposition
  using (Sylow-predicates; GL3F2-SylowDecomposition-from-joint)
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridge.GaugeTorsor
  using (GaugeTorsor; _≈G_)
open import Substrate.Category.PrimeFactoredGauge
  using (PrimeFactoredGauge; mkPFG)
open import Substrate.Category.SylowDecomposition
  using (SylowDecomposition; InGenerated)

------------------------------------------------------------------------
-- 1. The PFG construction, parametric on joint-generated.
--
-- Combines T6's SylowDecomposition (with hypothesis) with the
-- existing HodgeDim4 GaugeTorsor. The output is the substrate's
-- first concrete PrimeFactoredGauge instance.
--
-- The joint-generated parameter is the multi-route generation
-- witness from [[multi-route-equivariance-recovery]] — proven
-- meta-mathematically via PSL(2, 7) simplicity; supplied here as
-- input for the constructor.
------------------------------------------------------------------------

HodgeDim4-Bridge-as-PFG :
  (joint-gen :
    (g : GL3F2) →
    InGenerated (λ z → Σ (Fin 3) (λ i → Sylow-predicates i z))
                _·G_ id-GL g) →
  PrimeFactoredGauge GL3F2 GL3F2 _·G_ id-GL _≈G_ _≈G_ 3
HodgeDim4-Bridge-as-PFG joint-gen = mkPFG
  (GL3F2-SylowDecomposition-from-joint joint-gen)
  GaugeTorsor

------------------------------------------------------------------------
-- 2. Capstone — substrate's first concrete PFG instance.
--
-- T7 of the prime-factored-gauge arc per
-- [[prime-factored-gauge-arc]]. With T7 landed, the substrate
-- exposes its first concrete PrimeFactoredGauge instance —
-- the HodgeDim4 Reserved↔SelfDual bridge family as a structural
-- universal-property object.
--
-- Downstream consumers needing the multi-route theorem at HodgeDim4
-- now have a single import-point:
--   `HodgeDim4-Bridge-as-PFG joint-gen` + the generic theorem from
--   T5 = the gauge-decomposition for any two of the 168 bridges.
--
-- The joint-gen witness remains as the OPEN OBLIGATION. Two paths
-- to discharge it (per T6's analysis):
--   * External: cite [[multi-route-equivariance-recovery]]'s meta-
--     theorem (PSL(2, 7) simple ⇒ no proper subgroup contains
--     orders 2, 3, 7 jointly).
--   * Internal: enumerate all 168 GL3F2 elements + per-element
--     InGenerated chain. Heavy but mechanical.
--
-- Per [[shadow-architecture]]: T7 is a thin retrofit (combination
-- of T6 + existing GaugeTorsor); structural content already exists.
-- T7 names + packages.
--
-- Per [[reserved-selfdual-bijection-gauge]]: with T7, the original
-- gauge memo's "168 bridges" framing is now SUBSUMED by the generic
-- PrimeFactoredGauge primitive. The HodgeDim4 instance is one
-- example among many possible (CRT abelian case, Monster, etc.);
-- structural commonality is exposed.
------------------------------------------------------------------------
