------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.TmDBGodel.Properties
--
-- ⟡odecode-B-godel — the PROOFS about the object-syntax Gödel codec: the
-- round-trip retract and the split-Canonical apex. (Split from the def module
-- per the def/proof separation policy — this is the *.Properties sibling.)
--
-- THE ONE PROOF is `parse-godel` (induction on the TERM): parsing (godel t ++
-- rest) with fuel ≥ size t recovers (t, rest). The fuel-accounting closes
-- because `size (app f x) = suc (size f + size x)`, so `size` IS the structural
-- measure — no Acc plumbing (cf. enum-fuel/factorize). From it, `godel-retract :
-- ungodel (godel t) ≡ t` (decode ∘ encode = id).
--
-- THE APEX: `TmDB-Canonical = split-Canonical ungodel godel godel-retract` lands
-- on the SAME `Canonical (ker-Quotient _)` shape as the term-algebra's
-- `UPTerm-Canonical = split-Canonical eval reify eval-reify` (Eval.agda) AND the
-- number-theoretic `factor-Canonical = split-Canonical factor-value factor-section
-- factor-retract` (Nat/Prime/Properties.agda). So the OBJECT codec, the MORPHISM
-- codec, and the ℕ-Gödel codec are ALL one split-idempotent apex — object codec =
-- term codec = wedge = CRT, one shape (object-universe-is-split-canonical). NOTE
-- the direction: godel is INJECTIVE-not-surjective, so it is the SECTION (s) and
-- ungodel the retraction (F) — the reverse of a naive `split-Canonical godel ungodel`.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.TmDBGodel.Properties where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _≤_; z≤n; s≤s)
open import Substrate.Foundation.Nat.Properties.Order
  using (≤-refl; ≤-trans; m≤m+n; n≤m+n; +-mono-≤)
open import Substrate.Foundation.List using (List; []; _∷_; _++_)
open import Substrate.Foundation.List.Length using (length)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; sym; trans; subst)
open import Substrate.Algebra.Quotient
  using (Quotient; ker-Quotient; split-Canonical)
  renaming (Canonical to Canonical⟦de760d07⟧)
open import Substrate.Category.UniversalProperty.TmDBGodel

------------------------------------------------------------------------
-- 0. Supporting List lemmas (inline; the dedup advisory on these + `size` is
--    non-blocking — they are standard and keep this proof self-contained).
------------------------------------------------------------------------

++-assoc : (xs ys zs : List ℕ) → (xs ++ ys) ++ zs ≡ xs ++ (ys ++ zs)
++-assoc []       ys zs = refl
++-assoc (x ∷ xs) ys zs = cong (x ∷_) (++-assoc xs ys zs)

++-identityʳ : (xs : List ℕ) → xs ++ [] ≡ xs
++-identityʳ []       = refl
++-identityʳ (x ∷ xs) = cong (x ∷_) (++-identityʳ xs)

length-++ : (xs ys : List ℕ) → length (xs ++ ys) ≡ length xs + length ys
length-++ []       ys = refl
length-++ (x ∷ xs) ys = cong suc (length-++ xs ys)

------------------------------------------------------------------------
-- 1. THE KEY LEMMA: parsing (godel t ++ rest) with fuel ≥ size t returns (t, rest).
------------------------------------------------------------------------

parse-godel : (t : TmDB) (rest : List ℕ) (f : ℕ) → size t ≤ f
            → parse-fuel f (godel t ++ rest) ≡ (t , rest)
parse-godel (var k) rest (suc f') _ = refl
parse-godel S       rest (suc f') _ = refl
parse-godel K       rest (suc f') _ = refl
parse-godel I       rest (suc f') _ = refl
parse-godel (app fn xn) rest (suc f') (s≤s fnxn≤f')
  rewrite ++-assoc (godel fn) (godel xn) rest
        | parse-godel fn (godel xn ++ rest) f' (≤-trans (m≤m+n (size fn) (size xn)) fnxn≤f')
        | parse-godel xn rest f' (≤-trans (n≤m+n (size fn) (size xn)) fnxn≤f')
  = refl
parse-godel (var k)     rest zero ()
parse-godel S           rest zero ()
parse-godel K           rest zero ()
parse-godel I           rest zero ()
parse-godel (app fn xn) rest zero ()

------------------------------------------------------------------------
-- 2. size ≤ length ∘ godel (so fuel = length (godel t) is enough).
------------------------------------------------------------------------

size≤length-godel : (t : TmDB) → size t ≤ length (godel t)
size≤length-godel (var k) = s≤s z≤n
size≤length-godel S       = ≤-refl _
size≤length-godel K       = ≤-refl _
size≤length-godel I       = ≤-refl _
size≤length-godel (app fn xn) =
  s≤s (subst (λ z → size fn + size xn ≤ z)
             (sym (length-++ (godel fn) (godel xn)))
             (+-mono-≤ (size≤length-godel fn) (size≤length-godel xn)))

------------------------------------------------------------------------
-- 3. THE RETRACT: ungodel ∘ godel ≡ id.
------------------------------------------------------------------------

godel-retract : (t : TmDB) → ungodel (godel t) ≡ t
godel-retract t =
  cong proj₁
    (trans (cong (parse-fuel (length (godel t))) (sym (++-identityʳ (godel t))))
           (parse-godel t [] (length (godel t)) (size≤length-godel t)))

------------------------------------------------------------------------
-- 4. THE APEX: TmDB-Canonical, the SAME split-Canonical apex as UPTerm-Canonical
--    and factor-Canonical. A = codes (List ℕ), F = ungodel, s = godel, retract =
--    godel-retract. The object-syntax IS Gödel-codeable.
------------------------------------------------------------------------

TmDB-Canonical : Canonical⟦de760d07⟧ (ker-Quotient ungodel)
TmDB-Canonical = split-Canonical ungodel godel godel-retract
