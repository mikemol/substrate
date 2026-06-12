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

open import Substrate.Foundation.Bool using (Bool; true; false; _∧_; _∨_)
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
-- The connectives — the "joiners" (el-atlas §1, §5, §6). The carrier is
-- two INDEPENDENT accumulators (Law 1.3): each connective acts rail-wise,
-- never reading one rail while writing the other. Two orders, each a
-- meet/join pair:
--
--   * truth order — ∧E (meet) / ∨E (join): the §5/§6 connectives that
--     De Morgan (= notE = swapE) EXCHANGES (Theorem 5.2). Bounds ⊤t/⊥t.
--   * info  order — ⊗E (consensus) / ⊕E (accumulate): the §1 independent
--     accumulators; De Morgan PRESERVES them (the twist-structure). ⊤k/⊥k.
--
-- Discrete (Bool²) shadow of §6's log-linked semiring; the continuous
-- AND ~ log-product / OR ~ log-sum-exp lift is out of scope for the proof
-- tier. Hosted here, with the carrier they act on (carrier-locality
-- policy; cf. Foundation.Bool = Bool with its ∧/∨/not). The laws —
-- De Morgan, twist, the semilattice laws, and the Remark 6.2 non-collapse
-- — live in .Properties.
------------------------------------------------------------------------

infixr 7 _∧E_ _⊗E_
infixr 6 _∨E_ _⊕E_

-- truth meet: support needs BOTH, opposition needs EITHER
_∧E_ : Evidence → Evidence → Evidence
⟨ pa , na ⟩ ∧E ⟨ pb , nb ⟩ = ⟨ pa ∧ pb , na ∨ nb ⟩

-- truth join: support needs EITHER, opposition needs BOTH
_∨E_ : Evidence → Evidence → Evidence
⟨ pa , na ⟩ ∨E ⟨ pb , nb ⟩ = ⟨ pa ∨ pb , na ∧ nb ⟩

-- info join (accumulate): independently OR each rail (§1 accumulators)
_⊕E_ : Evidence → Evidence → Evidence
⟨ pa , na ⟩ ⊕E ⟨ pb , nb ⟩ = ⟨ pa ∨ pb , na ∨ nb ⟩

-- info meet (consensus): independently AND each rail
_⊗E_ : Evidence → Evidence → Evidence
⟨ pa , na ⟩ ⊗E ⟨ pb , nb ⟩ = ⟨ pa ∧ pb , na ∧ nb ⟩

-- NOT is the pin-swap (Theorem 5.2 / §6.1): reverses the truth order
-- (exchanging ∧E / ∨E), preserves the information order.
notE : Evidence → Evidence
notE = swapE

-- The two orders' bounds (the four corners). ⊤t/⊥t are the ∧E/∨E units;
-- ⊤k/⊥k the ⊗E/⊕E units. As values these coincide with the probe points
-- below (⊤t = eP, ⊥t = eF, ⊤k = eU) — the lattice-bound names for the
-- same corners.
⊤t ⊥t ⊤k ⊥k : Evidence
⊤t = ⟨ true  , false ⟩   -- truth top    (P-corner: pass)
⊥t = ⟨ false , true  ⟩   -- truth bottom (F-corner: fail)
⊤k = ⟨ true  , true  ⟩   -- info  top    (U-corner: both)
⊥k = ⟨ false , false ⟩   -- info  bottom (V-corner: neither)

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
