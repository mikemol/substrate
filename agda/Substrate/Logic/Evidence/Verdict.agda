------------------------------------------------------------------------
-- Substrate.Logic.Evidence.Verdict
--
-- The four-valued evidence verdict (Belnap–Dunn FOUR), continued from
-- el-atlas's proof tier (proofs/VerdictCrossbar.agda, W13) and re-homed
-- onto the substrate's Foundation so the two proof tiers compose. The
-- el-atlas original was self-contained (its own private Bool/≡/⊥); here
-- the carrier is the substrate's Bool and the apartness is its _≢_.
--
-- An `Evidence` carries two independent rails: a positive rail E⁺ and a
-- negative rail E⁻ (each a Bool — "is there evidence FOR / AGAINST?").
-- The four combinations give the four verdicts:
--
--     E⁺  E⁻   verdict
--     ──  ──   ───────
--     t   f      P   pass          (evidence for, none against)
--     f   t      F   fail          (evidence against, none for)
--     t   t      U   undetermined  (both — the paraconsistent corner)
--     f   f      V   vacuous       (neither — the gap corner)
--
-- This is the dual-rail carrier in miniature; el-atlas's §3 prohibition
-- (the two rails do not collapse onto one) is proved, and generalized to
-- an arbitrary quotient carrier, in `.NoCollapse`.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.Verdict where

open import Substrate.Foundation.Bool using (Bool; true; false)
open import Substrate.Foundation.Eq   using (_≡_; _≢_)

------------------------------------------------------------------------
-- The dual-rail carrier and the four-corner verdict.
------------------------------------------------------------------------

record Evidence : Set where
  constructor ⟨_,_⟩
  field
    pos : Bool   -- the positive rail E⁺
    neg : Bool   -- the negative rail E⁻

open Evidence public

data Verdict : Set where
  P F U V : Verdict   -- pass / fail / undetermined(both) / vacuous(neither)

verdict : Evidence → Verdict
verdict ⟨ true  , false ⟩ = P
verdict ⟨ false , true  ⟩ = F
verdict ⟨ true  , true  ⟩ = U
verdict ⟨ false , false ⟩ = V

------------------------------------------------------------------------
-- The rail-swap involution (S5) on the carrier, and its image on
-- verdicts (the verdict-level dual): P and F exchange; U and V are
-- self-dual.  The laws (involutivity, intertwining) live in .Properties.
------------------------------------------------------------------------

swapE : Evidence → Evidence
swapE ⟨ p , n ⟩ = ⟨ n , p ⟩

swapV : Verdict → Verdict
swapV P = F
swapV F = P
swapV U = U
swapV V = V

------------------------------------------------------------------------
-- Constructor apartness of the four verdicts. Trivial absurdity proofs
-- (kept beside the type: a `λ ()` carries zero proof-transitive weight,
-- so it does not burden this def module's load — cf. the def/proof
-- separation policy, which is about not dragging heavy *.Properties
-- closures into definition modules, not about banning trivial proofs).
------------------------------------------------------------------------

P≢F : P ≢ F
P≢F ()

P≢U : P ≢ U
P≢U ()

P≢V : P ≢ V
P≢V ()

F≢U : F ≢ U
F≢U ()

F≢V : F ≢ V
F≢V ()

U≢V : U ≢ V
U≢V ()

------------------------------------------------------------------------
-- The three probe points used by the no-collapse argument: three
-- evidence states demanding three pairwise-distinct verdicts.
------------------------------------------------------------------------

eP eF eU : Evidence
eP = ⟨ true  , false ⟩
eF = ⟨ false , true  ⟩
eU = ⟨ true  , true  ⟩
