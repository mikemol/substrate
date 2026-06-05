------------------------------------------------------------------------
-- Substrate.Algebra.Q.Properties.Congruence
--
-- `_≈ℚ_` is a CONGRUENCE for ℚ's operations: +ℚ and *ℚ respect
-- cross-multiplication equality. Together with Q.Equiv.ℚ-Quotient (the setoid)
-- and Q.Properties.Field (the 14 laws), this makes (ℚ, ≈ℚ, +ℚ, *ℚ) a usable
-- setoid field — operations may be rewritten under ≈ℚ.
--
-- *ℚ-cong is a direct ℤ-interchange (quadℤ); +ℚ-cong expands each numerator
-- term and matches via the hypotheses + ℕ reorders.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Properties.Congruence where

open import Substrate.Foundation.Nat using (suc; _*_)
open import Substrate.Foundation.Nat.Properties.Mul using (*-comm; *-assoc)
open import Substrate.Foundation.Eq using (_≡_; sym; trans; cong; cong₂)
open import Substrate.Algebra.Z using (ℤ; +_)
open import Substrate.Algebra.Z.Arithmetic using (_+ℤ_; _*ℤ_)
open import Substrate.Algebra.Z.Properties.MulFull using (*ℤ-assoc; *ℤ-distribʳ-+; quadℤ)
open import Substrate.Algebra.Q using (ℚ; mkℚ; num; den-1)
open import Substrate.Algebra.Q.Arithmetic using (_+ℚ_; _*ℚ_)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_)

------------------------------------------------------------------------
-- Multiplication respects ≈ℚ.
------------------------------------------------------------------------

*ℚ-cong : {a a′ b b′ : ℚ} → a ≈ℚ a′ → b ≈ℚ b′ → (a *ℚ b) ≈ℚ (a′ *ℚ b′)
*ℚ-cong {mkℚ na da₋} {mkℚ na′ da′₋} {mkℚ nb db₋} {mkℚ nb′ db′₋} H1 H2 =
  trans (quadℤ na nb (+ suc da′₋) (+ suc db′₋))
  (trans (cong₂ _*ℤ_ H1 H2)
         (quadℤ na′ (+ suc da₋) nb′ (+ suc db₋)))

------------------------------------------------------------------------
-- Addition respects ≈ℚ.
------------------------------------------------------------------------

+ℚ-cong : {a a′ b b′ : ℚ} → a ≈ℚ a′ → b ≈ℚ b′ → (a +ℚ b) ≈ℚ (a′ +ℚ b′)
+ℚ-cong {mkℚ na da₋} {mkℚ na′ da′₋} {mkℚ nb db₋} {mkℚ nb′ db′₋} H1 H2 =
  trans lhs-exp (trans (cong₂ _+ℤ_ term-a term-b) (sym rhs-exp))
  where
    sa  = suc da₋
    sa′ = suc da′₋
    sb  = suc db₋
    sb′ = suc db′₋
    Ka : sa * (sb * sb′) ≡ sb′ * (sa * sb)
    Ka = trans (cong (sa *_) (*-comm sb sb′))
         (trans (sym (*-assoc sa sb′ sb))
         (trans (cong (_* sb) (*-comm sa sb′))
                (*-assoc sb′ sa sb)))
    Kb : sb * (sa * sa′) ≡ sa′ * (sa * sb)
    Kb = trans (cong (sb *_) (*-comm sa sa′))
         (trans (sym (*-assoc sb sa′ sa))
         (trans (cong (_* sa) (*-comm sb sa′))
         (trans (*-assoc sa′ sb sa)
                (cong (sa′ *_) (*-comm sb sa)))))
    lhs-exp : ((na *ℤ (+ sb)) +ℤ (nb *ℤ (+ sa))) *ℤ (+ (sa′ * sb′))
            ≡ ((na *ℤ (+ sb)) *ℤ (+ (sa′ * sb′))) +ℤ ((nb *ℤ (+ sa)) *ℤ (+ (sa′ * sb′)))
    lhs-exp = *ℤ-distribʳ-+ (na *ℤ (+ sb)) (nb *ℤ (+ sa)) (+ (sa′ * sb′))
    rhs-exp : ((na′ *ℤ (+ sb′)) +ℤ (nb′ *ℤ (+ sa′))) *ℤ (+ (sa * sb))
            ≡ ((na′ *ℤ (+ sb′)) *ℤ (+ (sa * sb))) +ℤ ((nb′ *ℤ (+ sa′)) *ℤ (+ (sa * sb)))
    rhs-exp = *ℤ-distribʳ-+ (na′ *ℤ (+ sb′)) (nb′ *ℤ (+ sa′)) (+ (sa * sb))
    term-a : (na *ℤ (+ sb)) *ℤ (+ (sa′ * sb′)) ≡ (na′ *ℤ (+ sb′)) *ℤ (+ (sa * sb))
    term-a = trans (quadℤ na (+ sb) (+ sa′) (+ sb′))
             (trans (cong (_*ℤ (+ (sb * sb′))) H1)
             (trans (*ℤ-assoc na′ (+ sa) (+ (sb * sb′)))
             (trans (cong (na′ *ℤ_) (cong +_ Ka))
                    (sym (*ℤ-assoc na′ (+ sb′) (+ (sa * sb)))))))
    term-b : (nb *ℤ (+ sa)) *ℤ (+ (sa′ * sb′)) ≡ (nb′ *ℤ (+ sa′)) *ℤ (+ (sa * sb))
    term-b = trans (cong ((nb *ℤ (+ sa)) *ℤ_) (cong +_ (*-comm sa′ sb′)))
             (trans (quadℤ nb (+ sa) (+ sb′) (+ sa′))
             (trans (cong (_*ℤ (+ (sa * sa′))) H2)
             (trans (*ℤ-assoc nb′ (+ sb) (+ (sa * sa′)))
             (trans (cong (nb′ *ℤ_) (cong +_ Kb))
                    (sym (*ℤ-assoc nb′ (+ sa′) (+ (sa * sb))))))))
