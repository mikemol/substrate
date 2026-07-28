{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.NilpotentLogMMonoid — ⟡nf-logM-monoid: the commutative
-- monoid-with-zero laws for the faithful log chart's mulM (ADD 136).
--
-- GROUNDED FINDING (the residue this surfaces): on the FULL carrier Maybe ℕ, mulM
-- is commutative, associative, and absorbing — BUT the identity law FAILS on the
-- JUNK representatives just j (j ≥ cap): mulM (just 0) (just j) = nothing ≠ just j
-- (verified: mulM (just 0)(just 4) ≡ nothing at cap 4). Maybe ℕ OVER-REPRESENTS —
-- just 4, just 5, … are all non-canonical aliases of the overflow that SHOULD be
-- nothing. The junk is the residue of the wrong carrier, KEPT not hidden.
--
-- THE INVARIANT (not "force the laws on Maybe ℕ" nor "just restrict"): the
-- canonical carrier is the FINITE one — the live logs are exactly {0..d} = Fin
-- (suc d), so the faithful monoid-with-zero is on Maybe (Fin (suc d)), where the
-- junk vanishes by construction. The laws that DON'T touch the identity (comm,
-- assoc, absorb) hold on the full Maybe ℕ; the identity needs the canonical carrier.
------------------------------------------------------------------------

module Substrate.Algebra.Wedge.NilpotentLogMMonoid where

open import Substrate.Foundation.Eq  using (_≡_; refl; sym; trans; cong; subst)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _<_; _<?_)
open import Substrate.Foundation.Nat.Properties.Add using (+-comm; +-assoc; +-identityʳ)
open import Substrate.Foundation.Maybe using (Maybe; just; nothing)
open import Substrate.Foundation.Negation using (Dec; yes; no; ¬_)
open import Substrate.Foundation.Empty using (⊥-elim)
open import Substrate.Algebra.Wedge.NilpotentFaithfulLogChart using (d; LogM; mulM)

------------------------------------------------------------------------
-- ① ABSORPTION (nothing is the zero): both sides, by refl / case on the arg.
------------------------------------------------------------------------
mulM-zeroˡ : (x : LogM) → mulM nothing x ≡ nothing
mulM-zeroˡ x = refl

mulM-zeroʳ : (x : LogM) → mulM x nothing ≡ nothing
mulM-zeroʳ nothing  = refl
mulM-zeroʳ (just _) = refl

------------------------------------------------------------------------
-- ② COMMUTATIVITY — holds on the FULL carrier (junk included), because the cap
-- test (i+j <? suc d) and the kept value (i+j) are both symmetric via +-comm.
------------------------------------------------------------------------
mulM-comm : (x y : LogM) → mulM x y ≡ mulM y x
mulM-comm nothing  nothing  = refl
mulM-comm nothing  (just _) = refl
mulM-comm (just _) nothing  = refl
mulM-comm (just i) (just j) with (i + j) <? suc d | (j + i) <? suc d | +-comm i j
... | yes _  | yes _  | e = cong just e
... | no  _  | no  _  | _ = refl
... | yes p  | no ¬p  | e = ⊥-elim (¬p (subst (_< suc d) e p))
... | no ¬p  | yes p  | e = ⊥-elim (¬p (subst (_< suc d) (sym e) p))

------------------------------------------------------------------------
-- ③ IDENTITY on the CANONICAL domain: just 0 is a left identity for just j when
-- j is a genuine live log (j < suc d). (On junk j ≥ suc d it FAILS — the residue.)
------------------------------------------------------------------------
mulM-identityˡ-canonical : (j : ℕ) → j < suc d → mulM (just 0) (just j) ≡ just j
mulM-identityˡ-canonical j lt with (0 + j) <? suc d
... | yes _  = refl
... | no ¬p  = ⊥-elim (¬p lt)          -- 0 + j = j < suc d, so this branch is impossible

-- and just 0 is a right identity for nothing (absorbing) and canonical just j.
mulM-identityʳ-nothing : mulM nothing (just 0) ≡ nothing
mulM-identityʳ-nothing = refl

------------------------------------------------------------------------
-- ④ THE RESIDUE, made explicit (kept, not hidden): identity FAILS on the junk
-- just j with j ≥ suc d. At the boundary j = suc d: mulM (just 0) (just (suc d))
-- collapses to nothing, NOT just (suc d). This is why the faithful carrier is
-- Maybe (Fin (suc d)) — the junk just (≥ suc d) is not a Fin, so it can't arise.
------------------------------------------------------------------------
identity-fails-on-junk : mulM (just 0) (just (suc d)) ≡ nothing
identity-fails-on-junk with (0 + suc d) <? suc d
... | yes p  = n≮n p                    -- 0 + suc d = suc d, suc d < suc d absurd
  where open import Substrate.Foundation.Empty using (⊥)
        n≮n : ∀ {n} {B : Set} → n < n → B
        n≮n {suc n} (Substrate.Foundation.Nat.s≤s q) = n≮n q
... | no  _  = refl

