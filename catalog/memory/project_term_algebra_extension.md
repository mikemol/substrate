---
name: term-algebra-extension
description: "T1-T30: term-algebra layer for the 80+14-slice MK/PF/IG/PD extension. Every morphism category now has a typed-cons-list Term datatype + Category-as-term wrapper with category laws holding STRUCTURALLY via mechanical list-append induction, mirroring Substrate.Category.UniversalProperty's pattern. Substrate's UP-topos discipline now uniformly engaged across the extension surface"
metadata: 
  node_type: memory
  type: project
  originSessionId: bb094a39-05c5-494d-8b01-cc34809ccae9
---

Term-algebra extension closure summary. Triggered by user 2026-05-21
audit question: "There's been a lot of work around building UP-topos.
Check it out; is everything we've built compatible with it?"

**The structural finding (from audit):**
The 80+14 prior modules used RECORDS with abstract function-typed
fields as morphism types. The substrate's UP-topos discipline (per
Substrate.Category.UniversalProperty.Term + Category + Morphism)
requires:
  * Record-as-SEMANTIC-target (what a term evaluates to)
  * Term-as-SYNTACTIC-presentation (typed cons-list of named generators)
  * Category-as-terms with structural list-append laws

The 80+14 work produced only the SEMANTIC layer. The 30-slice
extension adds the SYNTACTIC + CATEGORY layers.

**Slices landed (all 30):**

  T1-T3   MarkovCategory      (Term, Category, Eval)
  T4-T6   StochasticLens      (Term, Category, Eval)
  T7-T9   Poly                (Term, Category, Eval)
  T10-T11 PolyLens            (Term, Eval — reuses Poly.Term)
  T12-T13 Comonoid            (Term, Category)
  T14     CommutativeComonoid (Term — reuses Comonoid.Term)
  T15-T16 CascadedCoalgebra   (Term, Category)
  T17-T18 ConjugateMonad      (Term, Category)
  T19-T20 DFT                 (Term, Category)
  T21-T22 PontryaginDual      (Term, Category — char as Coxeter word)
  T23-T28 TermAlgebraBridges  (6 cross-arc bridges)
  T29     TermAlgebraCapstone (structural index)
  T30     this memory entry

**Pattern uniformly applied:**

For each morphism category Xxx:

```agda
-- Term.agda — syntactic presentation
data XxxGen   : ObjType → ObjType → Set₁ where
  lift-xxx : ... → XxxGen A B
  (plus other named generators per category)

data XxxTerm  : ObjType → ObjType → Set₁ where
  []  : XxxTerm A A
  _∷_ : XxxGen A B → XxxTerm B C → XxxTerm A C

_++ₓ_ : XxxTerm A B → XxxTerm B C → XxxTerm A C
[]       ++ₓ ys = ys
(x ∷ xs) ++ₓ ys = x ∷ (xs ++ₓ ys)

-- Category.agda — laws hold structurally
++ₓ-identityˡ : [] ++ₓ t ≡ t              (refl)
++ₓ-identityʳ : t ++ₓ [] ≡ t              (induction)
++ₓ-assoc     : (t ++ₓ u) ++ₓ v ≡ t ++ₓ (u ++ₓ v)  (induction)
```

**Substrate alignment claims now structurally enforced:**

1. **UP-topos compatibility**: every morphism category's morphism IS
   a term (cons-list). Category laws hold by mechanical induction
   per the UP-topos's Term + Category pattern.

2. **Term-algebra alignment** (per [[roll-our-own-via-word-algebra]]):
   word-algebra over named generators is the substrate-native
   morphism encoding. Now applied across all 10 morphism categories
   in the extension (MK/SL/Poly/PolyLens/Comonoid/CCM/CascCoa/ConjM/
   DFT/PD).

3. **Constructive completeness** (user's 2026-05-21 sharpening):
   each Term datatype's []-and-cons constructors are precisely the
   data needed to construct any morphism mechanically. The Eval
   module's signature shows how a term denotes a record.

4. **Categorical-name-first** (per [[categorical-name-first]]): each
   Term encoding uses the established "term algebra over generators"
   pattern from category theory; no PLL- or application-layer names
   at the syntactic level.

5. **Coalgebraic-at-lowest-levels** (per [[coalgebraic-not-consumer-
   driven]]): the cons-list data structure IS coalgebraic (W-types /
   inductive lists); the term-algebra category sits monadically on
   top, satisfying the substrate's layer discipline.

**Total substrate-extension footprint:**

  Layer                   Modules    Status
  ---------------------------------------------------------
  Abstract primitives     80         All --safe --without-K
  Substrate sites         14         All --safe --without-K
  Term-algebra layer      30         All --safe --without-K
  ---------------------------------------------------------
  Total                   124        All --safe --without-K

**Structural anchoring complete:**

The substrate's UP-topos (`Substrate.Category.UniversalProperty.
SubstrateTopos`) now sees every primitive of the MK/PF/IG/PD
extension as a term-presented morphism category. Sheaves over any
of these categories are tractable via the same UP-topos
infrastructure that handles the substrate's own UPCategory.

The horizon items (sheaf-theoretic signal processing, traced
monoidal categories, synthetic measure theory, categorical
cybernetics / open games) all build on TERM-PRESENTED morphism
categories — which the substrate now has uniformly.

**Per [[expose-generator-not-orbit]]:** the term datatype EXPOSES
the named generators (lift, copy, delete, swap, forward-DFT, etc.)
as the morphism-category's gauge generators. Each concrete morphism
is one ORBIT — a specific cons-list reaching from source to target.

**Per [[multi-route-equivariance-recovery]]:** the cross-arc bridges
(T23-T28) realize equivalence between term-algebras of related
morphism categories — the atlas-of-charts at the term-algebra level.

**Per [[homology-cohomology-recursion]]:** the term cons-list is the
homology cycle (data); the Eval function is the cohomology contraction
(semantic denotation). Each Xxx pair (Term + Eval) closes one layer
of the recursion at the syntactic-semantic level.

Related:
  [[freelinearization-substrate-sites]] — sites pattern this extension
                                          follows
  [[roll-our-own-via-word-algebra]] — discipline that prompted the
                                       extension
  [[categorical-name-first]] — applied throughout
  [[v4-typeclass-architecture]] — V₄ sites' anchor
  [[q-over-r-constructive]] — ℚ probability sites' choice
