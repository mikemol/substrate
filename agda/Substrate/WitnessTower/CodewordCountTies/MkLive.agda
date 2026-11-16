------------------------------------------------------------------------
-- Substrate.WitnessTower.CodewordCountTies.MkLive
--
-- Defines: --, mkLive
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.CodewordCountTies; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.CodewordCountTies.MkLive where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Pow
open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Product
open import Substrate.Cocycles.V4Signature.Codeword.Type
open import Substrate.Cocycles.V4Signature.Codeword.Subtypes
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Hedberg.DecidableUIP
open import Substrate.Foundation.Nat.Plus



------------------------------------------------------------------------
-- ◆AI-1b'''' : |Live| = 24, filter-free (the Reserved=8 companion). A Live
-- codeword has (bit₃,bit₄) ≠ (false,false), i.e. one of the THREE patterns
-- (T,F),(F,T),(T,T), each with 3 free bits (bits 0,1,2) — so Live ≅ 3 × Vec
-- Bool 3, count 3·8 = 24. Same technique as Reserved (one pattern × Vec Bool 3
-- = 8); here three patterns. Closes the last SnVersusTwoPow co-apex count:
-- Live(24) ℕ+ Reserved(8) = 32 = 2⁵, all three now proved terms.
------------------------------------------------------------------------


mkLive : (Bool × Bool) → Vec Bool 3 → Codeword
mkLive (b3 , b4) (b0 ∷ b1 ∷ b2 ∷ []) = b0 , b1 , b2 , b3 , b4
