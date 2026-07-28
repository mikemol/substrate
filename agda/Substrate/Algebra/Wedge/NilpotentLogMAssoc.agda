{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.NilpotentLogMAssoc — ⟡nf-logM-assoc: mulM is
-- ASSOCIATIVE (completing the monoid-with-zero laws, ADD 137).
--
-- The proof factors through capJust n = "just n if n < cap, else nothing": both
-- mulM (just a)(just b) IS capJust (a+b), and mulM (capJust m)(just k) IS
-- capJust (m+k) — the second by monotonicity (m ≤ m+k, so m+k < cap ⟹ m < cap,
-- and the collapse aligns). Then both associations of (just i)(just j)(just k)
-- reduce to capJust (i+j+k) via +-assoc, and the nothing cases are absorption.
------------------------------------------------------------------------

module Substrate.Algebra.Wedge.NilpotentLogMAssoc where

open import Substrate.Foundation.Eq  using (_≡_; refl; sym; trans; cong)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _<_; _<?_)
open import Substrate.Foundation.Nat.Properties.Add using (+-assoc; +-comm)
open import Substrate.Foundation.Nat.Properties.Order using (m≤m+n; ≤-<-trans)
open import Substrate.Foundation.Maybe using (Maybe; just; nothing)
open import Substrate.Foundation.Negation using (Dec; yes; no; ¬_)
open import Substrate.Foundation.Empty using (⊥-elim)
open import Substrate.Algebra.Wedge.NilpotentFaithfulLogChart using (d; LogM; mulM)
open import Substrate.Algebra.Wedge.NilpotentLogMMonoid using (mulM-comm)

------------------------------------------------------------------------
-- capJust: the canonical "cap this log" — just n below the bound, else nothing.
------------------------------------------------------------------------
capJust : ℕ → LogM
capJust n with n <? suc d
... | yes _ = just n
... | no  _ = nothing

-- mulM (just a)(just b) IS capJust (a+b) — definitional (same `with`).
mulM-jj : (a b : ℕ) → mulM (just a) (just b) ≡ capJust (a + b)
mulM-jj a b with (a + b) <? suc d
... | yes _ = refl
... | no  _ = refl

------------------------------------------------------------------------
-- THE KEY LEMMA: mulM (capJust m) (just k) ≡ capJust (m + k). Below the cap,
-- capJust m = just m and mulM (just m)(just k) = capJust (m+k). At/over the cap,
-- capJust m = nothing, mulM nothing (just k) = nothing, and capJust (m+k) is also
-- nothing because m ≤ m+k so m+k ≥ cap too (monotonicity ⟹ the collapse aligns).
------------------------------------------------------------------------
capJust-mulM : (m k : ℕ) → mulM (capJust m) (just k) ≡ capJust (m + k)
capJust-mulM m k with m <? suc d
... | yes _  = mulM-jj m k                       -- capJust m = just m
... | no ¬p  with (m + k) <? suc d
...            | yes m+k<cap = ⊥-elim (¬p (≤-<-trans (m≤m+n m k) m+k<cap))
...            | no  _       = refl               -- both nothing

------------------------------------------------------------------------
-- ASSOCIATIVITY. All-just: LHS ≡ capJust ((i+j)+k), RHS ≡ capJust (i+(j+k)),
-- and the two capJusts agree by +-assoc. Any-nothing: both sides nothing.
------------------------------------------------------------------------
mulM-assoc : (x y z : LogM) → mulM (mulM x y) z ≡ mulM x (mulM y z)
mulM-assoc nothing  y        z        = refl                       -- LHS,RHS both nothing
mulM-assoc (just _) nothing  z        = refl                       -- mulM · nothing = nothing
mulM-assoc (just i) (just j) nothing  = mulM-nothing-r i j         -- see below
  where
    -- mulM (mulM (just i)(just j)) nothing ≡ nothing ≡ mulM (just i)(mulM (just j) nothing)
    mulM-nothing-r : (i j : ℕ) → mulM (mulM (just i) (just j)) nothing
                              ≡ mulM (just i) (mulM (just j) nothing)
    mulM-nothing-r i j with (i + j) <? suc d
    ... | yes _ = refl
    ... | no  _ = refl
mulM-assoc (just i) (just j) (just k) =
  trans lhs≡ (trans (cong capJust (+-assoc i j k)) (sym rhs≡))
  where
    -- LHS = mulM (mulM (just i)(just j)) (just k) ≡ capJust ((i+j)+k)
    lhs≡ : mulM (mulM (just i) (just j)) (just k) ≡ capJust ((i + j) + k)
    lhs≡ = trans (cong (λ w → mulM w (just k)) (mulM-jj i j))
                 (capJust-mulM (i + j) k)
    -- RHS = mulM (just i)(mulM (just j)(just k)) ≡ capJust (i+(j+k)) — via comm.
    rhs≡ : mulM (just i) (mulM (just j) (just k)) ≡ capJust (i + (j + k))
    rhs≡ = trans (cong (mulM (just i)) (mulM-jj j k))
           (trans (mulM-comm (just i) (capJust (j + k)))
           (trans (capJust-mulM (j + k) i)
                  (cong capJust (+-comm (j + k) i))))
