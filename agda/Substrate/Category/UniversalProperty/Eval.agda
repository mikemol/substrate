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

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)

open import Substrate.Category.UniversalProperty using (UPArrowP)
open import Substrate.Category.UniversalProperty.Morphism
  using (UPMorphism; source-map; target-map; coherent)
open import Substrate.Category.UniversalProperty.Term
  using (UPGen; lift; UPTerm; []; _∷_; _++ᵤ_; ObjRel)
open import Substrate.Algebra.Quotient
  using (Quotient; ker-Quotient; split-Canonical)
  renaming (Canonical to Canonical⟦de760d07⟧)
open import Substrate.Category.UniversalProperty.Compose
  using (id-UPMorphism; compose-UPMorphism)

-- ⟡UPArrow-dissolve C: telescope over UPArrowP. Object binders {U : …} are
-- explicit per-signature (eta-record ⇒ not `variable`-generalizable); the
-- carrier Sets S/T/W ARE variables (auto-generalized before each U).
private variable
  S₁ T₁ S₂ T₂ S₃ T₃ S₄ T₄ : Set
  W₁ : S₁ → T₁ → Set
  W₂ : S₂ → T₂ → Set
  W₃ : S₃ → T₃ → Set
  W₄ : S₄ → T₄ → Set

------------------------------------------------------------------------
-- Record-level identity and composition of UPMorphisms (UP3).
--
-- Ⓓ: id-UPMorphism / compose-UPMorphism are UniversalProperty.Compose's
-- (imported above); Eval had re-defined them with byte-identical record bodies.
-- The consumers (FixedPoint, Phase1) already used Compose's; eval below uses
-- them too.
------------------------------------------------------------------------

------------------------------------------------------------------------
-- eval — the term → record bridge. [] ↦ identity; (lift m ∷ t) ↦ compose.
------------------------------------------------------------------------

eval : {U₁ : UPArrowP S₁ T₁ W₁} {U₂ : UPArrowP S₂ T₂ W₂} → UPTerm U₁ U₂ → UPMorphism U₁ U₂
eval []           = id-UPMorphism _
eval (lift m ∷ t) = compose-UPMorphism (eval t) m

------------------------------------------------------------------------
-- reify — the record → term bridge: a single-generator word.
------------------------------------------------------------------------

reify : {U₁ : UPArrowP S₁ T₁ W₁} {U₂ : UPArrowP S₂ T₂ W₂} → UPMorphism U₁ U₂ → UPTerm U₁ U₂
reify m = lift m ∷ []

------------------------------------------------------------------------
-- The round-trip: realising a reified morphism returns it (compose-with-identity,
-- by η). So record → term → record = id — the Forgetful side of the bridge.
------------------------------------------------------------------------

eval-reify : {U₁ : UPArrowP S₁ T₁ W₁} {U₂ : UPArrowP S₂ T₂ W₂} (m : UPMorphism U₁ U₂) → eval (reify m) ≡ m
eval-reify m = refl

------------------------------------------------------------------------
-- UPMorphism IS a category (the category laws the capstone deferred): identity
-- and associativity, all by η (refl) — function-composition assoc on source/target
-- and identical `coherent` chaining either way.
------------------------------------------------------------------------

compose-idʳ : {U₁ : UPArrowP S₁ T₁ W₁} {U₂ : UPArrowP S₂ T₂ W₂} (m : UPMorphism U₁ U₂)
            → compose-UPMorphism m (id-UPMorphism U₁) ≡ m
compose-idʳ m = refl

compose-idˡ : {U₁ : UPArrowP S₁ T₁ W₁} {U₂ : UPArrowP S₂ T₂ W₂} (m : UPMorphism U₁ U₂)
            → compose-UPMorphism (id-UPMorphism U₂) m ≡ m
compose-idˡ m = refl

compose-assoc : {U₁ : UPArrowP S₁ T₁ W₁} {U₂ : UPArrowP S₂ T₂ W₂} {U₃ : UPArrowP S₃ T₃ W₃} {U₄ : UPArrowP S₄ T₄ W₄}
                (h : UPMorphism U₃ U₄) (g : UPMorphism U₂ U₃) (f : UPMorphism U₁ U₂)
              → compose-UPMorphism (compose-UPMorphism h g) f
              ≡ compose-UPMorphism h (compose-UPMorphism g f)
compose-assoc h g f = refl

------------------------------------------------------------------------
-- eval IS A FUNCTOR (the analysis's real keystone, VERIFIED): it carries term
-- concatenation to record composition. So semantic composition reduces to
-- syntactic append — the free/forgetful homomorphism.
------------------------------------------------------------------------

eval-++ : {U₁ : UPArrowP S₁ T₁ W₁} {U₂ : UPArrowP S₂ T₂ W₂} {U₃ : UPArrowP S₃ T₃ W₃} (s : UPTerm U₁ U₂) (t : UPTerm U₂ U₃)
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

eval-cong : {U₁ : UPArrowP S₁ T₁ W₁} {U₂ : UPArrowP S₂ T₂ W₂} {s t : UPTerm U₁ U₂} → s ≡ t → eval s ≡ eval t
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

foldUPTerm : {T : ObjRel}
           → ({A B : Set} {V : A → B → Set} {U : UPArrowP A B V} → T U U)
           → ({A₁ B₁ : Set} {V₁ : A₁ → B₁ → Set} {U₁ : UPArrowP A₁ B₁ V₁}
              {A₂ B₂ : Set} {V₂ : A₂ → B₂ → Set} {U₂ : UPArrowP A₂ B₂ V₂}
              {A₃ B₃ : Set} {V₃ : A₃ → B₃ → Set} {U₃ : UPArrowP A₃ B₃ V₃}
              → T U₂ U₃ → T U₁ U₂ → T U₁ U₃)
           → ({A₁ B₁ : Set} {V₁ : A₁ → B₁ → Set} {U₁ : UPArrowP A₁ B₁ V₁}
              {A₂ B₂ : Set} {V₂ : A₂ → B₂ → Set} {U₂ : UPArrowP A₂ B₂ V₂}
              → UPGen U₁ U₂ → T U₁ U₂)
           → {U₁ : UPArrowP S₁ T₁ W₁} {U₂ : UPArrowP S₂ T₂ W₂} → UPTerm U₁ U₂ → T U₁ U₂
foldUPTerm idT cmpT interp []      = idT
foldUPTerm idT cmpT interp (g ∷ t) = cmpT (foldUPTerm idT cmpT interp t) (interp g)

-- eval IS this fold, at the UPMorphism target with `unlift` the interpretation.
unlift : {U₁ : UPArrowP S₁ T₁ W₁} {U₂ : UPArrowP S₂ T₂ W₂} → UPGen U₁ U₂ → UPMorphism U₁ U₂
unlift (lift m) = m

eval-is-fold : {U₁ : UPArrowP S₁ T₁ W₁} {U₂ : UPArrowP S₂ T₂ W₂} (t : UPTerm U₁ U₂)
             → eval t ≡ foldUPTerm (λ {U = U} → id-UPMorphism U) compose-UPMorphism unlift t
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
  {T : ObjRel}
  (idT : {A B : Set} {V : A → B → Set} {U : UPArrowP A B V} → T U U)
  (cmpT : {A₁ B₁ : Set} {V₁ : A₁ → B₁ → Set} {U₁ : UPArrowP A₁ B₁ V₁}
          {A₂ B₂ : Set} {V₂ : A₂ → B₂ → Set} {U₂ : UPArrowP A₂ B₂ V₂}
          {A₃ B₃ : Set} {V₃ : A₃ → B₃ → Set} {U₃ : UPArrowP A₃ B₃ V₃}
          → T U₂ U₃ → T U₁ U₂ → T U₁ U₃)
  (interp : {A₁ B₁ : Set} {V₁ : A₁ → B₁ → Set} {U₁ : UPArrowP A₁ B₁ V₁}
            {A₂ B₂ : Set} {V₂ : A₂ → B₂ → Set} {U₂ : UPArrowP A₂ B₂ V₂}
            → UPGen U₁ U₂ → T U₁ U₂)
  (G : {A₁ B₁ : Set} {V₁ : A₁ → B₁ → Set} {U₁ : UPArrowP A₁ B₁ V₁}
       {A₂ B₂ : Set} {V₂ : A₂ → B₂ → Set} {U₂ : UPArrowP A₂ B₂ V₂}
       → UPTerm U₁ U₂ → T U₁ U₂)
  → ({A B : Set} {V : A → B → Set} {U : UPArrowP A B V} → G {U₁ = U} {U₂ = U} [] ≡ idT {U = U})
  → ({A₁ B₁ : Set} {V₁ : A₁ → B₁ → Set} {U₁ : UPArrowP A₁ B₁ V₁}
     {A₂ B₂ : Set} {V₂ : A₂ → B₂ → Set} {U₂ : UPArrowP A₂ B₂ V₂}
     {A₃ B₃ : Set} {V₃ : A₃ → B₃ → Set} {U₃ : UPArrowP A₃ B₃ V₃}
     (g : UPGen U₁ U₂) (t : UPTerm U₂ U₃) → G (g ∷ t) ≡ cmpT (G t) (interp g))
  → {U₁ : UPArrowP S₁ T₁ W₁} {U₂ : UPArrowP S₂ T₂ W₂} (t : UPTerm U₁ U₂) → G t ≡ foldUPTerm idT cmpT interp t
foldUPTerm-unique idT cmpT interp G Gnil Gcons []      = Gnil
foldUPTerm-unique idT cmpT interp G Gnil Gcons (g ∷ t) =
  trans (Gcons g t)
        (cong (λ X → cmpT X (interp g))
              (foldUPTerm-unique idT cmpT interp G Gnil Gcons t))

------------------------------------------------------------------------
-- UP4, MADE PRECISE. Not "kernel" loosely — the CONGRUENCE induced by eval's
-- kernel pair: `s ≈ᵤ t  iff  eval s ≡ eval t`. It RESPECTS composition (`≈ᵤ-cong-++`),
-- and that is exactly what makes the quotient `UPTerm / ≈ᵤ` a CATEGORY — the
-- presented category the threads were heading toward. The respect-law follows from
-- `eval-++` (eval is a functor): the kernel of a functor is automatically a
-- congruence. So UP4 is no longer "word-equality work" — it is this proven
-- congruence; the quotient itself is the section-based PresentedUP/normalise step
-- (no quotient types under --without-K).
------------------------------------------------------------------------

_≈ᵤ_ : {U₁ : UPArrowP S₁ T₁ W₁} {U₂ : UPArrowP S₂ T₂ W₂} → UPTerm U₁ U₂ → UPTerm U₁ U₂ → Set
s ≈ᵤ t = eval s ≡ eval t

≈ᵤ-cong-++ : {U₁ : UPArrowP S₁ T₁ W₁} {U₂ : UPArrowP S₂ T₂ W₂} {U₃ : UPArrowP S₃ T₃ W₃} {s s' : UPTerm U₁ U₂} {t t' : UPTerm U₂ U₃}
           → s ≈ᵤ s' → t ≈ᵤ t' → (s ++ᵤ t) ≈ᵤ (s' ++ᵤ t')
≈ᵤ-cong-++ {s = s} {s'} {t} {t'} ss tt =
  trans (eval-++ s t)
        (trans (cong₂ compose-UPMorphism tt ss)
               (sym (eval-++ s' t')))

------------------------------------------------------------------------
-- THE QUOTIENT — the substrate way (user: "you're talking lack of quotient types
-- when we already have Q, wedge, and lossless Q↔R"). No HITs needed: the substrate
-- realizes a quotient by a CANONICAL FORM (a section) — ℚ = (ℤ×ℕ)/≈ via
-- reduce/Canonical, the wedge via rem<b, CRT via QuotientProduct. UPTerm/≈ᵤ is the
-- SAME: `normalize = reify ∘ eval` is the canonical form (the one-generator word),
-- idempotent, and ≈ᵤ is DECIDED by normal-form equality. So UPTerm/≈ᵤ is a
-- section-based Quotient (the ℚ pattern), realized losslessly through eval/reify —
-- not a barrier.
------------------------------------------------------------------------

normalize : {U₁ : UPArrowP S₁ T₁ W₁} {U₂ : UPArrowP S₂ T₂ W₂} → UPTerm U₁ U₂ → UPTerm U₁ U₂
normalize t = reify (eval t)

normalize-eval : {U₁ : UPArrowP S₁ T₁ W₁} {U₂ : UPArrowP S₂ T₂ W₂} (t : UPTerm U₁ U₂) → eval (normalize t) ≡ eval t
normalize-eval t = eval-reify (eval t)

normalize-idem : {U₁ : UPArrowP S₁ T₁ W₁} {U₂ : UPArrowP S₂ T₂ W₂} (t : UPTerm U₁ U₂)
               → normalize (normalize t) ≡ normalize t
normalize-idem t = cong reify (normalize-eval t)

-- ≈ᵤ ⟺ equal canonical form: the section decides the congruence (exactly ℚ's
-- `a ≈ℚ b ⟺ reduce a ≡ reduce b`).
≈ᵤ→normal : {U₁ : UPArrowP S₁ T₁ W₁} {U₂ : UPArrowP S₂ T₂ W₂} {s t : UPTerm U₁ U₂} → s ≈ᵤ t → normalize s ≡ normalize t
≈ᵤ→normal e = cong reify e

normal→≈ᵤ : {U₁ : UPArrowP S₁ T₁ W₁} {U₂ : UPArrowP S₂ T₂ W₂} {s t : UPTerm U₁ U₂} → normalize s ≡ normalize t → s ≈ᵤ t
normal→≈ᵤ {s = s} {t} p =
  trans (sym (normalize-eval s)) (trans (cong eval p) (normalize-eval t))

------------------------------------------------------------------------
-- UPTerm/≈ᵤ IS a substrate Quotient — and now visibly an INSTANCE of the
-- split-idempotent apex (Algebra.Quotient.split-Canonical): eval is the fold,
-- reify the section, eval-reify the retraction (eval ∘ reify ≡ id), and the
-- split idempotent reify ∘ eval = `normalize` is the canonical form. So the
-- whole quotient is `split-Canonical eval reify eval-reify` — the same lemma
-- that realizes ℚ `reduce`, the wedge `recon`, EEA CF-shape, CRT `combine`.
-- (≈ᵤ = KerRel eval definitionally; normalize etc. above are the unfolded
-- names this instance produces.)
------------------------------------------------------------------------

UPTerm-Quotient : (U₁ : UPArrowP S₁ T₁ W₁) (U₂ : UPArrowP S₂ T₂ W₂) → Quotient (UPTerm U₁ U₂) _≈ᵤ_
UPTerm-Quotient U₁ U₂ = ker-Quotient (eval {U₁ = U₁} {U₂ = U₂})

UPTerm-Canonical : (U₁ : UPArrowP S₁ T₁ W₁) (U₂ : UPArrowP S₂ T₂ W₂) → Canonical⟦de760d07⟧ (UPTerm-Quotient U₁ U₂)
UPTerm-Canonical U₁ U₂ = split-Canonical (eval {U₁ = U₁} {U₂ = U₂}) reify eval-reify
