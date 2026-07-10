------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationSumLaws
--
-- ⟡rig-5 (additive side) — the STRICT-transport laws of the graded rig's `+`. These
-- are the laws whose orientation-residue r = id: the block arrangement is IDENTICAL on
-- both sides, only the ℕ-grade index transports. So each is an on-the-nose equality
-- AFTER a `subst` over the corresponding ℕ law (the wedge's q, with r = id) — NOT an
-- up-to-iso coherence (that is ⟡rig-6, where r = a transposition).
--
--   ⊕-assoc      : subst LehmerPath (+-assoc m n p) ((l₁ ⊕ l₂) ⊕ l₃) ≡ l₁ ⊕ (l₂ ⊕ l₃)
--   ⊕-unit-right : subst LehmerPath (+-identityʳ n) (l ⊕ 0#)        ≡ l
--
-- (the left unit 0# ⊕ l ≡ l is already refl — OrientationSum.⊕-unit-left.) Both go by
-- induction on the first path, pushing the grade-`subst` through the `◂` constructor
-- (◂-subst) and discharging the Fin index with the inject+ coherence (inject+-assoc /
-- inject+0-id) — which this file also builds, since Foundation had none.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationSumLaws where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Nat.Properties.Add using (+-assoc; +-identityʳ)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Fin.Inject using (inject+)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; cong; cong₂; subst)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; start; _◂_)
open import Substrate.WitnessTower.Wedge.OrientationSum using (_⊕_; 0#)

------------------------------------------------------------------------
-- 1. subst-push helpers: transporting a Fin along a `cong suc` grade-equality commutes
--    with its zero/suc structure. (eq-induction; both refl.)
------------------------------------------------------------------------

subst-Fin-suc-zero : ∀ {m m'} (eq : m ≡ m') →
                     subst Fin (cong suc eq) zero ≡ zero
subst-Fin-suc-zero refl = refl

subst-Fin-suc-suc : ∀ {m m'} (eq : m ≡ m') (y : Fin m) →
                    subst Fin (cong suc eq) (suc y) ≡ suc (subst Fin eq y)
subst-Fin-suc-suc refl y = refl

-- subst over `Fin ∘ suc` is subst over `Fin` along the `cong suc` (the subst-∘ instance).
subst-cong-suc : ∀ {m m'} (eq : m ≡ m') (w : Fin (suc m)) →
                 subst (λ z → Fin (suc z)) eq w ≡ subst Fin (cong suc eq) w
subst-cong-suc refl w = refl

-- pushing a grade-`subst` through the `◂` constructor (it splits onto path + choice).
◂-subst : ∀ {k k'} (eq : k ≡ k') (l : LehmerPath k) (q : Fin (suc k)) →
          subst LehmerPath (cong suc eq) (l ◂ q)
            ≡ subst LehmerPath eq l ◂ subst (λ z → Fin (suc z)) eq q
◂-subst refl l q = refl

------------------------------------------------------------------------
-- 2. inject+ coherence — the Fin-index half of the strict laws (r = id on the choice).
------------------------------------------------------------------------

-- associativity: nesting two inject+ is one inject+ over the summed amount, after the
-- grade transport. (Induction on x; base = suc-zero push, step = suc push + IH.)
inject+-assoc : ∀ {m} (n p : ℕ) (x : Fin m) →
                subst Fin (+-assoc m n p) (inject+ p (inject+ n x)) ≡ inject+ (n + p) x
inject+-assoc {suc m} n p zero    = subst-Fin-suc-zero (+-assoc m n p)
inject+-assoc {suc m} n p (suc x) =
  trans (subst-Fin-suc-suc (+-assoc m n p) (inject+ p (inject+ n x)))
        (cong suc (inject+-assoc n p x))

-- right-unit: inject+ 0 is the identity, after the +0 transport.
inject+0-id : ∀ {m} (x : Fin m) → subst Fin (+-identityʳ m) (inject+ 0 x) ≡ x
inject+0-id {suc m} zero    = subst-Fin-suc-zero (+-identityʳ m)
inject+0-id {suc m} (suc x) =
  trans (subst-Fin-suc-suc (+-identityʳ m) (inject+ 0 x))
        (cong suc (inject+0-id x))

------------------------------------------------------------------------
-- 3. THE STRICT ADDITIVE LAWS. Induction on the first path; ◂-subst splits the goal
--    into (path IH) and (Fin coherence), each discharged above.
------------------------------------------------------------------------

⊕-assoc : ∀ {m n p} (l₁ : LehmerPath m) (l₂ : LehmerPath n) (l₃ : LehmerPath p) →
          subst LehmerPath (+-assoc m n p) ((l₁ ⊕ l₂) ⊕ l₃) ≡ l₁ ⊕ (l₂ ⊕ l₃)
⊕-assoc start l₂ l₃ = refl
⊕-assoc {suc m} {n} {p} (l₁ ◂ x) l₂ l₃ =
  trans (◂-subst (+-assoc m n p) ((l₁ ⊕ l₂) ⊕ l₃) (inject+ p (inject+ n x)))
        (cong₂ _◂_ (⊕-assoc l₁ l₂ l₃)
                   (trans (subst-cong-suc (+-assoc m n p) (inject+ p (inject+ n x)))
                          (inject+-assoc n p x)))

⊕-unit-right : ∀ {n} (l : LehmerPath n) →
               subst LehmerPath (+-identityʳ n) (l ⊕ 0#) ≡ l
⊕-unit-right start = refl
⊕-unit-right {suc n} (l ◂ x) =
  trans (◂-subst (+-identityʳ n) (l ⊕ 0#) (inject+ 0 x))
        (cong₂ _◂_ (⊕-unit-right l)
                   (trans (subst-cong-suc (+-identityʳ n) (inject+ 0 x))
                          (inject+0-id x)))
