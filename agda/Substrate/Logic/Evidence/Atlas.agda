------------------------------------------------------------------------
-- Substrate.Logic.Evidence.Atlas
--
-- el-atlas Layer-0 claim ADJ — "the chart adjunction (exp ⊣ log)" — as a
-- substrate record. The el-atlas thesis: one value space presented by two
-- charts, 𝔸 (signed/additive) and 𝕄 (semiring/multiplicative), related by an
-- exp ⊣ log ADJOINT EQUIVALENCE that is LOSSLESS on (mass,bias) (Lemma 2.5b).
--
-- At the set level an adjoint equivalence is exactly a bi-invertible pair, so
-- the structural content is: two charts + a round-tripping (exp, log). The
-- continuous exp/log maps themselves are OUT OF SCOPE (the substrate formalises
-- discrete constructors, not ℝ-valued analysis — [[feedback_continuous_via_discrete_inference_rules]]);
-- what is in scope is the STRUCTURE and its discrete instances.
--
-- `nedge-atlas` is the in-scope witness: the evidence carrier's two charts —
-- the dual rail (E⁺,E⁻) and the (visible parity, hidden residue) pair — related
-- by the GL(2,F₂) `recode` (.NedgeShadow), the discrete shadow of the continuous
-- two-real-rails → one-complex-carrier lift. Its round-trips ARE the lossless
-- adjoint equivalence ([[feedback_wedge_not_projection]]: "we never discard
-- anything", proved). The additive↔multiplicative gcd/Bézout instance (the
-- literal exp/log pair) is the next Atlas — see the el-atlas Frontier.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.Atlas where

open import Substrate.Foundation.Bool    using (Bool)
open import Substrate.Foundation.Product using (_×_)
open import Substrate.Foundation.Eq      using (_≡_)

open import Substrate.Logic.Evidence.Verdict using (Evidence)
open import Substrate.Logic.Evidence.Verdict.NedgeShadow
  using (recode; unrecode; recode-unrecode; unrecode-recode)

------------------------------------------------------------------------
-- An Atlas: one value space under two charts, with a lossless exp ⊣ log
-- adjoint equivalence between them.
------------------------------------------------------------------------

-- ⟡set1-paydown: parameterize Chart₊, Chart× (the two chart carriers) out
-- of the record so it lands in Set (was Set₁ because both were `field : Set`).
module _ (Chart₊ Chart× : Set) where   -- Chart₊: additive/signed 𝔸; Chart×: multiplicative/semiring 𝕄
  record Atlas : Set where
    field
      exp     : Chart₊ → Chart×
      log     : Chart× → Chart₊
      exp-log : (m : Chart×) → exp (log m) ≡ m   -- counit: lossless on 𝕄
      log-exp : (a : Chart₊) → log (exp a) ≡ a   -- unit:   lossless on 𝔸

open Atlas public

------------------------------------------------------------------------
-- The evidence atlas: the dual-rail chart ⇄ the (parity, residue) chart, the
-- recode. A real, machine-checked instance — the discrete shadow of exp ⊣ log.
------------------------------------------------------------------------

nedge-atlas : Atlas Evidence (Bool × Bool)
nedge-atlas = record
  { exp     = recode
  ; log     = unrecode
  ; exp-log = unrecode-recode
  ; log-exp = recode-unrecode
  }
