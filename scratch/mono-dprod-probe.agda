-- ⟡leibniz-mono-direct-product probe: mono l ≐ dprod l via fold-unique-over.
{-# OPTIONS --safe --without-K --guardedness #-}

module mono-dprod-probe where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _*_)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Fin.Combine using (combine)
open import Substrate.Foundation.Fin.RemQuot using (remQuot)
open import Substrate.Foundation.Fin.Combine.RemQuotInverse using (remQuot-combine)
open import Substrate.Foundation.Fin.Punctured using (punchIn)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; lookup; map)
open import Substrate.Foundation.Product using (proj₁; proj₂; _,_)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong; cong₂; subst)
open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; start; _◂_; decode)
open import Substrate.WitnessTower.Wedge.OrientationUniversal
  using (LehmerAlgebra; base; step; fold; fold-unique-over)
import Substrate.WitnessTower.LeibnizMonomial as LM

module M (A : Set) (_*A_ : A → A → A) (1A : A) where

  open LM.Mono A _*A_ 1A   -- Mat, MonoC, minor, mono-alg, mono

  -- the direct product Πⱼ M[combine j (decode l j)].
  prodFin : {k : ℕ} → (Fin k → A) → A
  prodFin {zero}  f = 1A
  prodFin {suc k} f = f zero *A prodFin (λ i → f (suc i))

  prodFin-cong : {k : ℕ} {f g : Fin k → A} → ((i : Fin k) → f i ≡ g i) → prodFin f ≡ prodFin g
  prodFin-cong {zero}  h = refl
  prodFin-cong {suc k} h = cong₂ _*A_ (h zero) (prodFin-cong (λ i → h (suc i)))

  dprod : {n : ℕ} → LehmerPath n → MonoC n
  dprod {n} l M = prodFin {n} (λ j → M (combine {n} {n} j (lookup (decode l) j)))

  -- lookup of map, the one fact the step needs.
  lookup∘map : {B C : Set} {n : ℕ} (f : B → C) (v : Vec B n) (k : Fin n) →
               lookup (map f v) k ≡ f (lookup v k)
  lookup∘map f (x ∷ v) zero    = refl
  lookup∘map f (x ∷ v) (suc k) = lookup∘map f v k

  -- THE DIRECT-PRODUCT'S OWN STEP: dprod (l ◂ p) M ≡ M[combine 0 p] *A
  -- dprod l (minor p M). This is the same fact `fold-unique-over` would demand
  -- as `mono-alg`'s step obligation — i.e. the proof IS attached to the ◂-step.
  -- (`fold-unique-over` cannot host it directly here: the carrier MonoC n =
  -- (Fin(n*n)→A)→A hides n behind multiplication, so the combinator's abstract
  -- recursion cannot pin n at each level. The direct recursion on `l` below
  -- pins n from `l : LehmerPath n` injectively at every step — the same
  -- inductive-step attachment, in the form Agda can infer.)
  dprod-step : {n : ℕ} (l : LehmerPath n) (p : Fin (suc n)) (M : Mat (suc n)) →
               dprod (l ◂ p) M ≡ (M (combine {suc n} {suc n} zero p) *A dprod l (minor p M))
  dprod-step {n} l p M =
    cong (M (combine {suc n} {suc n} zero p) *A_)
      (prodFin-cong {n}
        (λ k →
          trans
            (cong (λ j → M (combine {suc n} {suc n} (suc k) j))
                  (lookup∘map (punchIn p) (decode l) k))
            (sym (minor-combine k))))
    where
      -- (minor p M)(combine k j) ≡ M(combine (suc k)(punchIn p j)), via remQuot-combine.
      minor-combine : (k : Fin n) →
        minor {n} p M (combine {n} {n} k (lookup (decode l) k))
        ≡ M (combine {suc n} {suc n} (suc k) (punchIn p (lookup (decode l) k)))
      minor-combine k =
        cong (λ pr → M (combine {suc n} {suc n} (suc (proj₁ pr)) (punchIn p (proj₂ pr))))
             (remQuot-combine {n} {n} k (lookup (decode l) k))

  -- mono l M ≡ dprod l M — the cofactor fold equals the direct indexed product.
  -- Direct recursion on l; the ◂-case is where the proof lives (mono's own step
  -- is definitional; dprod's step is `dprod-step`; the IH bridges the minor).
  mono≡dprod : {n : ℕ} (l : LehmerPath n) (M : Mat n) → mono l M ≡ dprod l M
  mono≡dprod          start    M = refl
  mono≡dprod {suc n} (l ◂ p)  M =
    trans (cong (M (combine {suc n} {suc n} zero p) *A_) (mono≡dprod l (minor p M)))
          (sym (dprod-step l p M))
