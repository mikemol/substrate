------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Eval
--
-- THE TERM ↔ RECORD BRIDGE (user, 2026-06-13: "you want BOTH, because otherwise
-- right now we can't translate between terms and records, and that's a barrier we
-- need to bridge"). The capstone flagged `eval : UPTerm → UPMorphism` as planned
-- (UP5) but it was never built — so the syntactic free-category term and the
-- semantic commuting-square record were unbridged. This builds both directions:
--
--   eval  : UPTerm U₁ U₂ → UPMorphism U₁ U₂   (term → record; realise the stack)
--   reify : UPMorphism U₁ U₂ → UPTerm U₁ U₂   (record → term; a one-generator word)
--
-- and the round-trip `eval ∘ reify ≡ id`. This is the Free⊣Forgetful realisation:
-- UPTerm is free, UPMorphism the structure, eval the unique structure-map, reify
-- the unit. Record-level identity + composition (needed by eval) are built here too
-- (the UP3 "identity + composition" the capstone deferred).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Eval where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)

open import Substrate.Category.UniversalProperty using (UPArrow; Source; Target; Witness)
open import Substrate.Category.UniversalProperty.Morphism
  using (UPMorphism; source-map; target-map; coherent)
open import Substrate.Category.UniversalProperty.Term
  using (UPGen; lift; UPTerm; []; _∷_; _++ᵤ_)

------------------------------------------------------------------------
-- Record-level identity and composition of UPMorphisms (UP3).
------------------------------------------------------------------------

id-UPMorphism : (U : UPArrow) → UPMorphism U U
id-UPMorphism U = record
  { source-map = λ s → s
  ; target-map = λ i → i
  ; coherent   = λ s i w → w
  }

-- compose: forward on sources, BACKWARD on targets (the span/arrow-category law);
-- coherent chains the two squares.
compose-UPMorphism : {U₁ U₂ U₃ : UPArrow}
                   → UPMorphism U₂ U₃ → UPMorphism U₁ U₂ → UPMorphism U₁ U₃
compose-UPMorphism g f = record
  { source-map = λ s → source-map g (source-map f s)
  ; target-map = λ i → target-map f (target-map g i)
  ; coherent   = λ s i w → coherent f s (target-map g i) (coherent g (source-map f s) i w)
  }

------------------------------------------------------------------------
-- eval — the term → record bridge. [] ↦ identity; (lift m ∷ t) ↦ compose.
------------------------------------------------------------------------

eval : {U₁ U₂ : UPArrow} → UPTerm U₁ U₂ → UPMorphism U₁ U₂
eval []           = id-UPMorphism _
eval (lift m ∷ t) = compose-UPMorphism (eval t) m

------------------------------------------------------------------------
-- reify — the record → term bridge: a single-generator word.
------------------------------------------------------------------------

reify : {U₁ U₂ : UPArrow} → UPMorphism U₁ U₂ → UPTerm U₁ U₂
reify m = lift m ∷ []

------------------------------------------------------------------------
-- The round-trip: realising a reified morphism returns it (compose-with-identity,
-- by η). So record → term → record = id — the Forgetful side of the bridge.
------------------------------------------------------------------------

eval-reify : {U₁ U₂ : UPArrow} (m : UPMorphism U₁ U₂) → eval (reify m) ≡ m
eval-reify m = refl

------------------------------------------------------------------------
-- UPMorphism IS a category (the category laws the capstone deferred): identity
-- and associativity, all by η (refl) — function-composition assoc on source/target
-- and identical `coherent` chaining either way.
------------------------------------------------------------------------

compose-idʳ : {U₁ U₂ : UPArrow} (m : UPMorphism U₁ U₂)
            → compose-UPMorphism m (id-UPMorphism U₁) ≡ m
compose-idʳ m = refl

compose-idˡ : {U₁ U₂ : UPArrow} (m : UPMorphism U₁ U₂)
            → compose-UPMorphism (id-UPMorphism U₂) m ≡ m
compose-idˡ m = refl

compose-assoc : {U₁ U₂ U₃ U₄ : UPArrow}
                (h : UPMorphism U₃ U₄) (g : UPMorphism U₂ U₃) (f : UPMorphism U₁ U₂)
              → compose-UPMorphism (compose-UPMorphism h g) f
              ≡ compose-UPMorphism h (compose-UPMorphism g f)
compose-assoc h g f = refl

------------------------------------------------------------------------
-- eval IS A FUNCTOR (the analysis's real keystone, VERIFIED): it carries term
-- concatenation to record composition. So semantic composition reduces to
-- syntactic append — the free/forgetful homomorphism.
------------------------------------------------------------------------

eval-++ : {U₁ U₂ U₃ : UPArrow} (s : UPTerm U₁ U₂) (t : UPTerm U₂ U₃)
        → eval (s ++ᵤ t) ≡ compose-UPMorphism (eval t) (eval s)
eval-++ []           t = sym (compose-idʳ (eval t))
eval-++ (lift m ∷ s) t =
  trans (cong (λ X → compose-UPMorphism X m) (eval-++ s t))
        (compose-assoc (eval t) (eval s) m)

------------------------------------------------------------------------
-- The EASY half of "make everything commute": equal terms have equal records
-- (cong eval). The HARD half — getting parallel paths to NORMALISE to the same
-- term — is the UP4 equational theory, NOT done here. So commutativity reduces to
-- word equality, but the word equality itself is the remaining work.
------------------------------------------------------------------------

eval-cong : {U₁ U₂ : UPArrow} {s t : UPTerm U₁ U₂} → s ≡ t → eval s ≡ eval t
eval-cong = cong eval

------------------------------------------------------------------------
-- THE COMMON STRUCTURE (user: "when faced with an either/or, look for the common
-- structure, recursively"). The three open threads — det=(−1)ⁿ, UP4 (reify∘eval),
-- routing a .Term through eval — are NOT separate: they are all the FREE-CATEGORY
-- FOLD. `foldUPTerm` is the unique functor out of the free category UPTerm,
-- determined by a target (id + compose) and a generator interpretation. This IS the
-- centre (Free⊣Forgetful / FreeUP.extend): a word folds uniquely into any target.
--   • eval            = foldUPTerm into UPMorphism (interp = unlift)   [proved below]
--   • upterm-parity   = foldUPTerm into ℤ/2 = (Bool, false, xor, const-flip)
--   • cf-det / list-parity = the same fold on the CF/EEA-trace word
--   • UP4             = the KERNEL of this fold (terms with equal fold-image)
-- So the threads collapse to ONE object; each is `foldUPTerm` at a chosen target.
------------------------------------------------------------------------

foldUPTerm : {T : UPArrow → UPArrow → Set}
           → ({U : UPArrow} → T U U)
           → ({U₁ U₂ U₃ : UPArrow} → T U₂ U₃ → T U₁ U₂ → T U₁ U₃)
           → ({U₁ U₂ : UPArrow} → UPGen U₁ U₂ → T U₁ U₂)
           → {U₁ U₂ : UPArrow} → UPTerm U₁ U₂ → T U₁ U₂
foldUPTerm idT cmpT interp []      = idT
foldUPTerm idT cmpT interp (g ∷ t) = cmpT (foldUPTerm idT cmpT interp t) (interp g)

-- eval IS this fold, at the UPMorphism target with `unlift` the interpretation.
unlift : {U₁ U₂ : UPArrow} → UPGen U₁ U₂ → UPMorphism U₁ U₂
unlift (lift m) = m

eval-is-fold : {U₁ U₂ : UPArrow} (t : UPTerm U₁ U₂)
             → eval t ≡ foldUPTerm (λ {U} → id-UPMorphism U) compose-UPMorphism unlift t
eval-is-fold []           = refl
eval-is-fold (lift m ∷ t) = cong (λ X → compose-UPMorphism X m) (eval-is-fold t)

------------------------------------------------------------------------
-- RECURSE AGAIN (user: "again, the common structure recursively — point back at
-- EEA, Bézout, CRT, the wedge operator, the bidi Lawvere work"). `foldUPTerm` is
-- itself an instance: it is the UNIVERSAL fold of a free trace into a target
-- algebra. `foldUPTerm-unique` proves the universal property — ANY G that is a
-- functor (sends [] to id, g∷t to cmp) IS foldUPTerm. This is `FreeUP.extend`'s
-- `extend-unique` at UPTerm; the SAME property `Algebra.Nat.GCD.Fold.eea-fold` has
-- (EEATrace → gcd/Bézout/CRT, one trace folded into many targets), and the wedge
-- `Trace` reads (forget/cell/keep). So all of them — foldUPTerm, eea-fold, the
-- wedge reads, CRT-combine — are ONE object: the catamorphism of a free trace =
-- the centre, Free⊣Forgetful. The recursion bottoms at the centre.
------------------------------------------------------------------------

foldUPTerm-unique :
  {T : UPArrow → UPArrow → Set}
  (idT : {U : UPArrow} → T U U)
  (cmpT : {U₁ U₂ U₃ : UPArrow} → T U₂ U₃ → T U₁ U₂ → T U₁ U₃)
  (interp : {U₁ U₂ : UPArrow} → UPGen U₁ U₂ → T U₁ U₂)
  (G : {U₁ U₂ : UPArrow} → UPTerm U₁ U₂ → T U₁ U₂)
  → ({U : UPArrow} → G {U} {U} [] ≡ idT {U})
  → ({U₁ U₂ U₃ : UPArrow} (g : UPGen U₁ U₂) (t : UPTerm U₂ U₃)
       → G (g ∷ t) ≡ cmpT (G t) (interp g))
  → {U₁ U₂ : UPArrow} (t : UPTerm U₁ U₂) → G t ≡ foldUPTerm idT cmpT interp t
foldUPTerm-unique idT cmpT interp G Gnil Gcons []      = Gnil
foldUPTerm-unique idT cmpT interp G Gnil Gcons (g ∷ t) =
  trans (Gcons g t)
        (cong (λ X → cmpT X (interp g))
              (foldUPTerm-unique idT cmpT interp G Gnil Gcons t))
