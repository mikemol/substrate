# RUNG 3b ⟡jac-poly-semiring — TURN-KEY EXECUTION SPEC

New module `Substrate.Algebra.Z.MPolySemiring` building
`NormPoly-Semiring : Semiring NormPoly`. Compaction-safe: every anchor below verified
against source (file:line) on 2026-07-21. Root plan: `scratch/JAC-DET-NATIVE-PLAN.md`.
Probe (RUNG 3a source): `scratch/polynorm-probe.agda`.

---

## 0. PRECONDITION — RUNG 3a IS NOT YET BUILT

Verified: `grep -rln 'isSortedB|NormPoly|normalize-sorted' Substrate/` returns **nothing**.
`agda/Substrate/Algebra/Z/MPolyNormalize.agda` **does not exist**. The probe
(`scratch/polynorm-probe.agda`) is sound but unpromoted. **RUNG 3b depends on RUNG 3a's
exports.** Before 3b, RUNG 3a must publish (in `Algebra.Z.MPolyNormalize`, promoting the probe):

| export | what | probe status |
|---|---|---|
| `consNZ`, `insertT`, `normalize` | sorted-insert canonicalizer | proven (probe:101-115) |
| `coeff-cons-tt` / `coeff-cons-ff` | directed cons read-off | proven (probe:129-139) |
| `coeff-++` | `coeff m (p++q) ≡ coeff m p +ℤ coeff m q` | proven (probe:141-145) |
| `coeff-normalize` | `coeff j (normalize p) ≡ coeff j p` | proven (probe:184-192) |
| `triM`, `TriM`, `<→≢`, `eqM-refl`, `eqM-sound` | lex trichotomy on Mono | proven (probe:53-95) |
| **`isSortedB : MPoly → 𝔹`** | strict-ascending keys **∧ all-coeff-nonzero** | **3a MUST ADD** (see §4.1) |
| **`ltM𝔹 : Mono → Mono → 𝔹`** | boolean lex-strict Mono order | **3a MUST ADD** (see §4.1) |
| **`normalize-sorted : isSortedB (normalize p) ≡ tt`** | | **3a MUST ADD** |

If RUNG 3a instead exposes `isSortedB` via a **relational** `Sorted` datatype rather than a
boolean, §1 (h-prop) breaks (needs a `𝔹`-valued invariant for UIP). **Keep the invariant
`𝔹`-valued** — that is the whole reason `NormPoly` uses `≡ tt` rather than a `data Sorted`.

⚠ **`isSortedB` must forbid zero coefficients** (not just enforce ordering). Without it,
`[term m 0]` and `[]` have identical `coeff` yet differ — `coeff-canonicity` (§4) is FALSE.
Design in §4.1.

---

## 1. `NormPoly` Σ-subtype h-prop

### Carrier
```agda
NormPoly : Set
NormPoly = Σ MPoly (λ p → isSortedB p ≡ tt)
```
`Σ` and `proj₁/proj₂` from `Foundation.Product` (`:24-30`); `_≡_` from `Foundation.Eq`.

### The reduction lemma
```agda
NormPoly-≡ : {a b : NormPoly} → proj₁ a ≡ proj₁ b → a ≡ b
```

### Ingredients (all verified present)
- **`Σ-≡,≡→≡`** — `Foundation/Product.agda:81-87` — builds a Σ-equality from component
  equalities:
  ```agda
  Σ-≡,≡→≡ : {p q : Σ A B} → Σ (proj₁ p ≡ proj₁ q) (λ eq → subst B eq (proj₂ p) ≡ proj₂ q) → p ≡ q
  ```
- **`Decidable⇒UIP`** — `Foundation/Hedberg.agda:80-83` — `DecidableEquality A → (p q : x ≡ y) → p ≡ q`.
  `DecidableEquality A = (x y : A) → Dec (x ≡ y)` (`Hedberg.agda:24-25`).
  *(Consumer pattern to copy: `Foundation/Product.agda` itself already imports Hedberg; also
  `WitnessTower/CodewordCountTies.agda`, `WitnessTower/InsertionParity.agda`.)*
- **DecEq on `𝔹`** — **DOES NOT EXIST** (verified: `grep '≟𝔹|DecidableEquality 𝔹'` empty; the
  substrate's `Foundation.Bool` is a *different* Bool, and `𝔹` is `JacobianResidue`'s local
  `data 𝔹 = tt | ff`, `JacobianResidue.agda:75-76`). **Build it — trivial, 4 lines:**
  ```agda
  _≟𝔹_ : DecidableEquality 𝔹        -- = (x y : 𝔹) → Dec (x ≡ y)
  tt ≟𝔹 tt = yes refl
  ff ≟𝔹 ff = yes refl
  tt ≟𝔹 ff = no (λ ())
  ff ≟𝔹 tt = no (λ ())
  ```
  (`Dec/yes/no` from `Foundation.Negation`, per probe:10.)

### Proof
```agda
𝔹-UIP : {x y : 𝔹} (p q : x ≡ y) → p ≡ q
𝔹-UIP = Decidable⇒UIP _≟𝔹_

NormPoly-≡ : {a b : NormPoly} → proj₁ a ≡ proj₁ b → a ≡ b
NormPoly-≡ {p , sp} {q , sq} e =
  Σ-≡,≡→≡ (e , 𝔹-UIP (subst (λ r → isSortedB r ≡ tt) e sp) sq)
```
The second component obligation is `subst (λ r → isSortedB r ≡ tt) e sp ≡ sq`, an equation
between two proofs of `isSortedB q ≡ tt` — discharged by `𝔹-UIP` (both are paths in `𝔹`).
`subst` from `Foundation.Eq` (probe:12). **This is the ENTIRE h-prop story; it is mechanical.**

> **Note — `_≟ℤ_` is NOT needed for §1.** Plan line 46 mentions `_≟ℤ_` (`Algebra/Z.agda:81`,
> verified) as the DecEq feeding UIP; but the fiber whose proofs must be equated is
> `isSortedB p ≡ tt`, a `𝔹`-path, so **`_≟𝔹_` is the DecEq to feed Hedberg**, not `_≟ℤ_`.
> `_≟ℤ_` is instead consumed inside `consNZ`/`isSortedB` (the zero-coeff test) at RUNG 3a.

---

## 2. `scaleT-++` and `coeff-*P` left/right linearity

### Source reductions (verified `JacobianResidue.agda`)
```agda
scaleT t []       = []                              -- :128-130
scaleT t (u ∷ us) = mulT t u ∷ scaleT t us
[]      *P q = []                                   -- :132-134  (RECURSES ON FIRST ARG)
(t ∷ p) *P q = scaleT t q ++ (p *P q)
coeff m [] = 0ℤ                                      -- :140-144
coeff m (term n k ∷ p) with eqM m n | tt → k +ℤ coeff m p | ff → coeff m p
```
`_+P_ = _++_` (`:125-126`); `mulT (term m c)(term n d) = term (addM m n)(c *ℤ d)` (`:122-123`).

### 2.1 `scaleT-++` (raw ≡, structural refl-induction — EASY)
```agda
scaleT-++ : (t : Term) (b c : MPoly) → scaleT t (b ++ c) ≡ scaleT t b ++ scaleT t c
scaleT-++ t []            c = refl
scaleT-++ t (u ∷ b′)      c = cong (mulT t u ∷_) (scaleT-++ t b′ c)
```
Base: `scaleT t ([] ++ c) = scaleT t c` and `scaleT t [] ++ scaleT t c = [] ++ scaleT t c
= scaleT t c` — `refl`. Step: both sides head `mulT t u`, tail by IH.

### 2.2 The two coeff-linearities — ⚠ NAMING CROSS vs the `Semiring` record

**Verify against `Semiring.agda:37-46`:**
`distrib-left  a b c : a * (b + c) ≡ (a*b)+(a*c)`  — sum on the **RIGHT** `*`-operand.
`distrib-right a b c : (a + b) * c ≡ (a*c)+(b*c)`  — sum on the **LEFT** `*`-operand.

Since `_*P_` **recurses on its first argument**, the sum-in-first-arg case splits structurally
(EASY) and the sum-in-second-arg case cannot (needs coeff reorder, HARD). Therefore:

| `Semiring` field | poly shape | coeff lemma | difficulty |
|---|---|---|---|
| **`distrib-right`** | `(a ++ b) *P c` | `coeff-*P-distˡ` (sum in **1st** arg) | STRUCTURAL / easy |
| **`distrib-left`**  | `a *P (b ++ c)` | `coeff-*P-distʳ` (sum in **2nd** arg) | asymmetric / moderate |

> ⚠ **The prompt's §5 note is mislabeled.** It says "`distrib-left (a++b)*Pc` is structural …
> `distrib-right a*P(b++c)`". Per `Semiring.agda:37-46` this is **swapped**: `distrib-left` is
> `a*(b+c) = a *P (b++c)` (the HARD one that motivated normalization); `distrib-right` is
> `(a+b)*c = (a++b)*Pc` (structural). The plan's OBSTRUCTION note (line 42) calling
> `p *P (q+r)` "distrib-right" is the same mislabel. **Use the table above — it matches the
> record.** (`ℕ-semiring`/`ℤ-semiring` wire `distrib-left = *ℤ-distribˡ-+` = `a*(b+c)`,
> confirming the record convention, `Semiring/Instances.agda:77`, `Instances/Z.agda:88`.)

#### `coeff-*P-distˡ` (sum in first arg — STRUCTURAL, feeds `distrib-right`)
```agda
coeff-*P-distˡ : (m : Mono) (a b c : MPoly) →
                 coeff m ((a ++ b) *P c) ≡ coeff m (a *P c) +ℤ coeff m (b *P c)
coeff-*P-distˡ m []        b c = sym (+ℤ-identityˡ (coeff m (b *P c)))
coeff-*P-distˡ m (t ∷ a′)  b c =
  -- ((t∷a′)++b)*Pc = (t∷(a′++b))*Pc = scaleT t c ++ ((a′++b)*Pc)
  trans (coeff-++ m (scaleT t c) ((a′ ++ b) *P c))
  (trans (cong (coeff m (scaleT t c) +ℤ_) (coeff-*P-distˡ m a′ b c))
         (sym (+ℤ-assoc (coeff m (scaleT t c)) (coeff m (a′ *P c)) (coeff m (b *P c)))))
```
RHS `coeff m ((t∷a′)*Pc) +ℤ coeff m (b*Pc) = (coeff (scaleT t c) +ℤ coeff (a′*Pc)) +ℤ coeff (b*Pc)`
via `coeff-++`; the trans-chain reassociates. Anchors: `coeff-++` (probe:141), `+ℤ-assoc`
(`Add.agda:71`), `+ℤ-identityˡ` (`Add.agda:85`).

#### `coeff-*P-distʳ` (sum in second arg — feeds `distrib-left`; the interchange)
```agda
coeff-*P-distʳ : (m : Mono) (a b c : MPoly) →
                 coeff m (a *P (b ++ c)) ≡ coeff m (a *P b) +ℤ coeff m (a *P c)
coeff-*P-distʳ m []       b c = refl              -- 0ℤ ≡ 0ℤ +ℤ 0ℤ  (both reduce; else sym(+ℤ-identityˡ 0ℤ))
coeff-*P-distʳ m (t ∷ a′) b c =
  -- LHS = coeff(scaleT t (b++c)) +ℤ coeff(a′*P(b++c))
  --     = (coeff(scaleT t b)+coeff(scaleT t c)) +ℤ (coeff(a′*Pb)+coeff(a′*Pc))   [scaleT-++, coeff-++, IH]
  -- RHS = (coeff(scaleT t b)+coeff(a′*Pb)) +ℤ (coeff(scaleT t c)+coeff(a′*Pc))
  -- ⇒ MIDDLE-TWO INTERCHANGE  (A+B)+(C+D) ≡ (A+C)+(B+D)   via +ℤ-assoc + +ℤ-comm
  …
```
**This is the only place `+ℤ-comm` (`Add.agda:57`) is consumed in §2** — the coeff-level reorder
that raw `++` cannot do. Structure of the proof term:
1. `coeff-++ m (scaleT t (b++c)) (a′*P(b++c))` to split the head.
2. `cong (_+ℤ_)` rewriting `coeff m (scaleT t (b++c))` by `cong (coeff m) (scaleT-++ t b c)`
   then `coeff-++ m (scaleT t b) (scaleT t c)` → `A +ℤ B`.
3. IH `coeff-*P-distʳ m a′ b c` → `C +ℤ D`.
4. A local `interchange : (A B C D : ℤ) → (A+ℤB)+ℤ(C+ℤD) ≡ (A+ℤC)+ℤ(B+ℤD)` (≈6-line
   assoc/comm chain), then fold RHS back with two `coeff-++`.
**`interchange` sub-lemma** (build once, reuse in §5):
```agda
interchange : (A B C D : ℤ) → (A +ℤ B) +ℤ (C +ℤ D) ≡ (A +ℤ C) +ℤ (B +ℤ D)
interchange A B C D =
  trans (+ℤ-assoc A B (C +ℤ D))
  (trans (cong (A +ℤ_) (trans (sym (+ℤ-assoc B C D))
                        (trans (cong (_+ℤ D) (+ℤ-comm B C)) (+ℤ-assoc C B D))))
         (sym (+ℤ-assoc A C (B +ℤ D))))
```

**Verdict on §2:** all mechanical. `scaleT-++` and `coeff-*P-distˡ` are trivial;
`coeff-*P-distʳ` is one interchange. ~40 lines total.

---

## 3. THE SLOG #1 — `*P`-associativity

**KEY FINDING (simplifies the plan's "~150-line slog"): `_*P_` is associative ON THE NOSE
(raw `MPoly` ≡), so `coeff-*P-assoc` is a one-liner `cong (coeff m) *P-assoc`.** No coeff
reduction is needed for associativity — every sub-step is a raw list/term equality. Prove the
raw form; derive the coeff form.

```agda
coeff-*P-assoc : (m : Mono) (a b c : MPoly) → coeff m ((a *P b) *P c) ≡ coeff m (a *P (b *P c))
coeff-*P-assoc m a b c = cong (coeff m) (*P-assoc a b c)
```

### Sub-lemma dependency chain (all raw ≡, bottom-up)

**(1) `++-assoc` — list associativity. DOES NOT EXIST in `Foundation.List` (verified: only
`_++_` def at `List.agda:30`). Build locally, 3 lines:**
```agda
++-assoc : {A : Set} (xs ys zs : List A) → (xs ++ ys) ++ zs ≡ xs ++ (ys ++ zs)
++-assoc []       ys zs = refl
++-assoc (x ∷ xs) ys zs = cong (x ∷_) (++-assoc xs ys zs)
```

**(2) `mulT-assoc` — consumes BOTH heavy anchors.** This is the *only* sub-lemma touching
arithmetic:
```agda
mulT-assoc : (t u w : Term) → mulT t (mulT u w) ≡ mulT (mulT t u) w
mulT-assoc (term p x) (term q y) (term r z) =
  cong₂ term (sym (addM-assoc p q r)) (sym (*ℤ-assoc x y z))
```
`addM-assoc` — `MonoCommMonoid.agda:50-52` (verified). `*ℤ-assoc` — `MulFull.agda:61` (verified).
`cong₂` from `Foundation.Eq` (probe:12). *(Check direction:
`mulT t (mulT u w) = term (addM p (addM q r)) (x*ℤ(y*ℤz))`,
`mulT (mulT t u) w = term (addM (addM p q) r) ((x*ℤy)*ℤz)`; `addM-assoc p q r :
addM(addM p q)r ≡ addM p(addM q r)` and `*ℤ-assoc x y z : (x*ℤy)*ℤz ≡ x*ℤ(y*ℤz)`, hence
`sym` on both.)*

**(3) `scaleT-scaleT` — induction on the list, uses (2):**
```agda
scaleT-scaleT : (t u : Term) (c : MPoly) → scaleT t (scaleT u c) ≡ scaleT (mulT t u) c
scaleT-scaleT t u []       = refl
scaleT-scaleT t u (w ∷ c′) = cong₂ _∷_ (mulT-assoc t u w) (scaleT-scaleT t u c′)
```

**(4) `scaleT-*P` — induction on `b`, uses `scaleT-++` (§2.1) + (3):**
```agda
scaleT-*P : (t : Term) (b c : MPoly) → scaleT t (b *P c) ≡ (scaleT t b) *P c
scaleT-*P t []       c = refl
scaleT-*P t (u ∷ b′) c =
  -- scaleT t ((u∷b′)*Pc) = scaleT t (scaleT u c ++ (b′*Pc))
  --                      = scaleT t (scaleT u c) ++ scaleT t (b′*Pc)     [scaleT-++]
  --                      = scaleT (mulT t u) c   ++ (scaleT t b′ *P c)   [scaleT-scaleT, IH]
  -- (scaleT t (u∷b′))*Pc = (mulT t u ∷ scaleT t b′)*Pc = scaleT (mulT t u) c ++ (scaleT t b′ *P c)
  trans (scaleT-++ t (scaleT u c) (b′ *P c))
        (cong₂ _++_ (scaleT-scaleT t u c) (scaleT-*P t b′ c))
```

**(5) `*P-++-distˡ` — `(p++q)*Pc = (p*Pc)++(q*Pc)`, induction on `p`, uses (1):**
```agda
*P-++-distˡ : (p q c : MPoly) → (p ++ q) *P c ≡ (p *P c) ++ (q *P c)
*P-++-distˡ []       q c = refl
*P-++-distˡ (t ∷ p′) q c =
  -- ((t∷p′)++q)*Pc = (t∷(p′++q))*Pc = scaleT t c ++ ((p′++q)*Pc)
  --                = scaleT t c ++ ((p′*Pc)++(q*Pc))                     [IH]
  -- ((t∷p′)*Pc)++(q*Pc) = (scaleT t c ++ (p′*Pc)) ++ (q*Pc)
  trans (cong (scaleT t c ++_) (*P-++-distˡ p′ q c))
        (sym (++-assoc (scaleT t c) (p′ *P c) (q *P c)))
```

**(6) `*P-assoc` — induction on `a`, glue via (4)+(5):**
```agda
*P-assoc : (a b c : MPoly) → (a *P b) *P c ≡ a *P (b *P c)
*P-assoc []       b c = refl
*P-assoc (t ∷ a′) b c =
  -- ((t∷a′)*Pb)*Pc = (scaleT t b ++ (a′*Pb))*Pc
  --                = (scaleT t b *P c) ++ ((a′*Pb)*Pc)                   [*P-++-distˡ]
  --                = scaleT t (b*Pc)   ++ (a′*P(b*Pc))                   [sym scaleT-*P, IH]
  -- (t∷a′)*P(b*Pc) = scaleT t (b*Pc) ++ (a′*P(b*Pc))
  trans (*P-++-distˡ (scaleT t b) (a′ *P b) c)
        (cong₂ _++_ (sym (scaleT-*P t b c)) (*P-assoc a′ b c))
```

**Verdict on §3:** the "slog" is a chain of **6 short raw-≡ lemmas**, mechanical by count not
depth. The heavy anchors (`addM-assoc`, `*ℤ-assoc`) enter at exactly ONE leaf (`mulT-assoc`,
2 lines). Estimate ~35 lines. **Much lighter than the plan's ~150 estimate** because assoc is
on-the-nose — record this in the commit message as a finding.

---

## 4. THE SLOG #2 — `coeff-canonicity` (genuinely no reuse)

```agda
coeff-canonicity : (p q : MPoly) → isSortedB p ≡ tt → isSortedB q ≡ tt →
                   ((m : Mono) → coeff m p ≡ coeff m q) → p ≡ q
```
This is the real slog: peel-the-minimum induction over the Sorted invariant. **No in-tree
reuse** (verified: this is canonicity of a sparse assoc-list; the SPPF/witness-tower carry
no analogue — searched). Induction MEASURE: **structural on `p`** (q shrinks in lockstep in
the equal-head case; the unequal-head cases derive `⊥`, no recursion).

### 4.1 `isSortedB` design (RUNG 3a must ship this exact shape)
The invariant must encode BOTH strict-ascending keys AND all-nonzero coeffs. Recommended:
```agda
ltM𝔹 : Mono → Mono → 𝔹                       -- boolean lex-strict, from triℕ
ltM𝔹 (mono a b c) (mono d e f) =
  or (ltℕ a d) (and (eqℕ a d) (or (ltℕ b e) (and (eqℕ b e) (ltℕ c f))))
  -- (ltℕ, or : add to the 𝔹 helpers alongside JacobianResidue.and/eqℕ)

nzB : ℤ → 𝔹                                   -- nonzero test via _≟ℤ_
nzB k with k ≟ℤ 0ℤ
... | yes _ = ff
... | no  _ = tt

isSortedB : MPoly → 𝔹
isSortedB []                    = tt
isSortedB (term m k ∷ [])       = nzB k
isSortedB (term m k ∷ term n d ∷ p) = and (nzB k) (and (ltM𝔹 m n) (isSortedB (term n d ∷ p)))
```
(`normalize` from the probe already produces this shape: `consNZ` drops zeros, `insertT` keeps
strict order. `normalize-sorted` is RUNG 3a's obligation.)

### 4.2 Invariant-extraction sub-lemmas (all from `and-l`/`and-r`, probe:31-34)
```agda
sorted-nz     : (m : Mono)(k : ℤ)(p : MPoly) → isSortedB (term m k ∷ p) ≡ tt → nzB k ≡ tt
sorted-tail   : (m : Mono)(k : ℤ)(p : MPoly) → isSortedB (term m k ∷ p) ≡ tt → isSortedB p ≡ tt
sorted-head<  : (m n : Mono)(k d : ℤ)(p : MPoly) →
                isSortedB (term m k ∷ term n d ∷ p) ≡ tt → ltM𝔹 m n ≡ tt
```
`sorted-tail` for the singleton case: `isSortedB (term m k ∷ []) = nzB k`, and `isSortedB []
= tt`, so tail-of-singleton returns `refl`.

### 4.3 Order sub-lemmas (⚠ the fiddliest — the ordering machinery)
```agda
nz→≢0        : nzB k ≡ tt → ¬ (k ≡ 0ℤ)                     -- invert nzB via _≟ℤ_ with-branch
ltM𝔹→≢       : ltM𝔹 m n ≡ tt → eqM m n ≡ ff                -- strict ⇒ keys distinct ⇒ eqM = ff
ltM𝔹-trans   : ltM𝔹 m n ≡ tt → ltM𝔹 n o ≡ tt → ltM𝔹 m o ≡ tt   -- transitivity (lex, via triℕ/ltℕ)
ltM𝔹-asym    : ltM𝔹 m n ≡ tt → ltM𝔹 n m ≡ tt → ⊥
```
`ltM𝔹→≢` bridges to `coeff`'s `eqM` test: if `m` is strictly below key `n`, then `eqM m n =
ff`, so `coeff m` skips that term. `ltM𝔹-trans` is the fiddliest (lex-transitivity over the
three ℕ coordinates) — expect ~15 lines with nested `triℕ`/`ltℕ` case analysis. **This is the
genuine no-reuse cost.** *(`triℕ` from probe:71 gives the ℕ-level trichotomy to build these.)*

### 4.4 The key coeff lemmas
```agda
-- every key of a sorted p strictly exceeds m ⇒ m absent ⇒ coeff m p ≡ 0ℤ
coeff-below : (m : Mono)(p : MPoly) →
              isSortedB p ≡ tt → below m p →              -- below m p : ltM𝔹 m (head-key) ≡ tt
              coeff m p ≡ 0ℤ
-- proof: p = term n d ∷ p′.  ltM𝔹 m n ≡ tt ⇒ eqM m n ≡ ff ⇒ coeff m p = coeff m p′
--        (coeff-cons-ff); ltM𝔹-trans (m<n, n<head p′) gives below m p′; recurse.

-- the head of a sorted list carries its full coefficient
coeff-head : (m : Mono)(k : ℤ)(p : MPoly) →
             isSortedB (term m k ∷ p) ≡ tt → coeff m (term m k ∷ p) ≡ k
-- proof: coeff-cons-tt m m k p (eqM-refl m) : coeff m (term m k ∷ p) ≡ k +ℤ coeff m p;
--        coeff-below m p (sorted-tail …) (sorted-head< …) : coeff m p ≡ 0ℤ;
--        trans (cong (k +ℤ_) that) (+ℤ-identityʳ k).
```
`coeff-cons-tt`/`coeff-cons-ff` (probe:129-139), `eqM-refl` (probe:53), `+ℤ-identityʳ`
(`Add.agda:89`).

### 4.5 ℤ additive cancellation (DOES NOT EXIST — build it)
Verified: no `+ℤ-cancelˡ` in `Algebra/Z/Properties/Add.agda`. Derive from inverse+assoc:
```agda
+ℤ-cancelˡ : (a b c : ℤ) → a +ℤ b ≡ a +ℤ c → b ≡ c
+ℤ-cancelˡ a b c e =
  trans (sym (+ℤ-identityˡ b))
  (trans (cong (_+ℤ b) (sym (+ℤ-inverseˡ a)))          -- ((-a)+a)+b
  (trans (+ℤ-assoc (-ℤ a) a b)                          -- (-a)+(a+b)
  (trans (cong (-ℤ a +ℤ_) e)                            -- (-a)+(a+c)
  (trans (sym (+ℤ-assoc (-ℤ a) a c))
  (trans (cong (_+ℤ c) (+ℤ-inverseˡ a)) (+ℤ-identityˡ c))))))
```
`+ℤ-inverseˡ` (`Add.agda:102`), `-ℤ_` (`Algebra.Z`), `+ℤ-assoc`/`+ℤ-identityˡ` (`Add.agda:71,85`).

### 4.6 The main induction
```agda
coeff-canonicity []              []                sp sq h = refl
coeff-canonicity []              (term n d ∷ q′)   sp sq h =
  ⊥-elim (nz→≢0 (sorted-nz n d q′ sq)                  -- d ≠ 0
                (sym (trans (sym (coeff-head n d q′ sq)) (sym (h n)))))
  -- h n : coeff n [] ≡ coeff n (term n d ∷ q′);  coeff n [] = 0ℤ, coeff-head = d ⇒ d ≡ 0ℤ ⇒ ⊥
coeff-canonicity (term m k ∷ p′) []               sp sq h =
  ⊥-elim (nz→≢0 (sorted-nz m k p′ sp)
                (trans (sym (coeff-head m k p′ sp)) (h m)))   -- coeff m [] = 0ℤ ⇒ k ≡ 0ℤ ⇒ ⊥
coeff-canonicity (term m k ∷ p′) (term n d ∷ q′)  sp sq h with triM m n
... | ltM m≢n = ⊥-elim (nz→≢0 (sorted-nz m k p′ sp) k≡0)      -- m<n ⇒ coeff m q = 0, coeff m p = k
      where k≡0 = trans (sym (coeff-head m k p′ sp))
                        (trans (h m) (coeff-below m (term n d ∷ q′) sq  ltM𝔹[m,n]))
      -- need ltM𝔹 m n ≡ tt from the ltM case of triM; if triM only carries ¬(m≡n), rebuild
      -- the strict bit via ltM𝔹 directly (see NOTE below).
... | gtM m≢n = ⊥-elim …                                      -- symmetric: n<m
... | eqM≡ refl =                                              -- m ≡ n
      let k≡d : k ≡ d
          k≡d = trans (sym (coeff-head m k p′ sp))
                      (trans (h m) (coeff-head m d q′ sq))     -- (m=n so coeff-head both at m)
          h′ : (x : Mono) → coeff x p′ ≡ coeff x q′
          h′ x with eqM x m in e
          ... | tt = +ℤ-cancelˡ k (coeff x p′) (coeff x q′)
                     (trans (sym (coeff-cons-tt x m k p′ e))
                     (trans (h x)
                     (trans (coeff-cons-tt x m d q′ e) (cong (_+ℤ coeff x q′) (sym k≡d)))))
          ... | ff = trans (sym (coeff-cons-ff x m k p′ e))
                     (trans (h x) (coeff-cons-ff x m d q′ e))
      in cong₂ (λ kk pp → term m kk ∷ pp) k≡d
               (coeff-canonicity p′ q′ (sorted-tail m k p′ sp) (sorted-tail n d q′ sq) h′)
```
> **NOTE on `triM` vs `ltM𝔹`.** The probe's `triM` (probe:80-95) carries only `¬(m≡n)` on its
> `ltM`/`gtM` branches, NOT the boolean `ltM𝔹 m n ≡ tt` needed to invoke `coeff-below`. Two
> clean options: **(a)** replace the split with a purpose-built
> `triM𝔹 : (m n) → ltM𝔹 m n ≡ tt ⊎ (m ≡ n) ⊎ ltM𝔹 n m ≡ tt` (carrying the boolean witnesses);
> or **(b)** keep `triM` and, in the `ltM`/`gtM` branches, recompute `ltM𝔹 m n`/`ltM𝔹 n m` from
> the `triℕ` structure. **(a) is cleaner** — build `triM𝔹` once. This is part of §4.3's cost.

**Verdict on §4:** the genuine slog. ~10 sub-lemmas, `ltM𝔹-trans` + `triM𝔹` the fiddliest.
Estimate ~120-150 lines. No shortcut; no reuse.

---

## 5. Assemble `NormPoly-Semiring : Semiring NormPoly`

### Operations (all land back in `NormPoly` via `normalize` + `normalize-sorted`)
```agda
0P 1P : NormPoly
0P = ([] , refl)                                    -- isSortedB [] = tt, definitionally
1P = (normalize 𝟙P , normalize-sorted 𝟙P)           -- 𝟙P from JacobianResidue.agda:173

_⊕_ _⊗_ : NormPoly → NormPoly → NormPoly
a ⊕ b = (normalize (proj₁ a ++ proj₁ b) , normalize-sorted _)
a ⊗ b = (normalize (proj₁ a *P proj₁ b) , normalize-sorted _)
```

### The universal reduction: every law via `NormPoly-≡` + `coeff-canonicity`
For any two `NormPoly` values whose underlying lists are BOTH sorted, `coeff`-agreement gives
list-equality (§4), which `NormPoly-≡` (§1) lifts to `NormPoly`-equality. Since every op result
is `normalize (…)` (sorted by `normalize-sorted`), **each Semiring law reduces to a `coeff`
equation** dischargeable by §2/§3 + `coeff-normalize` + `coeff-++`. General shape:
```agda
law-via-coeff : (u v : MPoly) → isSortedB u ≡ tt → isSortedB v ≡ tt →
                ((m : Mono) → coeff m u ≡ coeff m v) → (u , su) ≡ (v , sv)   -- = NormPoly-≡ ∘ coeff-canonicity
```
The recurring coeff identity: `coeff m (normalize x) ≡ coeff m x` (`coeff-normalize`, probe:184)
lets every `normalize` be peeled at the coeff level before applying §2/§3.

### Monoids (via `mk-monoid`, `Semiring/Instances.agda:41`)
`mk-monoid op e assoc idˡ idʳ : Monoid A`. Field obligations:

**`+-monoid` = `mk-monoid _⊕_ 0P ⊕-assoc ⊕-idˡ ⊕-idʳ`:**
- `⊕-assoc a b c`: reduce to `∀m. coeff m (normalize(normalize(pa++pb)++pc)) ≡ coeff m
  (normalize(pa++normalize(pb++pc)))`. Peel all `normalize` by `coeff-normalize`; both sides
  become `(coeff pa +ℤ coeff pb) +ℤ coeff pc` vs `coeff pa +ℤ (coeff pb +ℤ coeff pc)` via
  `coeff-++`; close by `+ℤ-assoc`.
- `⊕-idˡ a`: `0P ⊕ a = normalize ([] ++ pa) = normalize pa`; coeff-peel `coeff-normalize` →
  `coeff m pa`; but `a`'s list is ALREADY sorted, so `normalize pa ≡ pa`? **Not definitionally.**
  Discharge via `NormPoly-≡ (coeff-canonicity (normalize pa) pa (normalize-sorted pa) sa
  (λ m → coeff-normalize m pa))`. Same trick for `⊕-idʳ` (uses `coeff-++` + `+ℤ-identityʳ`).

**`*-monoid` = `mk-monoid _⊗_ 1P ⊗-assoc ⊗-idˡ ⊗-idʳ`:**
- `⊗-assoc`: the payoff of §3 — peel `normalize`, apply `coeff-*P-assoc` (§3), close.
- `⊗-idˡ`/`⊗-idʳ`: `coeff m (𝟙P *P pa) ≡ coeff m pa`. `𝟙P = [term (mono 0 0 0) 1ℤ]` so
  `𝟙P *P pa = scaleT (term (mono 0 0 0) 1ℤ) pa ++ []`; `mulT (term 0 1ℤ) (term n c) =
  term (addM (mono 0 0 0) n) (1ℤ *ℤ c) = term n c` (addM-idˡ is `refl`, `*ℤ-identityˡ`).
  Small helper `scaleT-1 : scaleT (term (mono 0 0 0) 1ℤ) p ≡ p` by induction + `*ℤ-identityˡ`
  (`MulFull.agda:42`) + `addM-idˡ`-refl. Then `NormPoly-≡ ∘ coeff-canonicity`.

### Distributivity (⚠ mapping per §2.2 table)
- **`distrib-left a b c : a ⊗ (b ⊕ c) ≡ (a ⊗ b) ⊕ (a ⊗ c)`** — the HARD one, uses
  **`coeff-*P-distʳ`** (§2.2). Reduce (peel all `normalize` via `coeff-normalize`, split via
  `coeff-++`): `coeff m (pa *P (pb ++ pc)) ≡ coeff m (pa*Ppb) +ℤ coeff m (pa*Ppc)` = exactly
  `coeff-*P-distʳ m pa pb pc`. **THIS is the law raw `++` cannot satisfy — normalization is
  load-bearing here** (the `coeff-*P-distʳ` interchange reorders what `++` freezes).
- **`distrib-right a b c : (a ⊕ b) ⊗ c ≡ (a ⊗ c) ⊕ (b ⊗ c)`** — the EASY one, uses
  **`coeff-*P-distˡ`** (§2.2, structural).

### Zero-absorption
- `zero-absorb-left a : 0P ⊗ a ≡ 0P`. `[] *P pa = []` definitionally (`_*P_` :133), so
  `normalize ([] *P pa) = normalize [] = []`; `NormPoly-≡` on `[] ≡ []` = `refl` (or coeff-peel).
- `zero-absorb-right a : a ⊗ 0P ≡ 0P`. `pa *P [] `: `coeff m (pa *P []) ≡ 0ℤ` needs a small
  `coeff-*P-nilʳ : coeff m (p *P []) ≡ 0ℤ` (induction on p: `(t∷p′)*P[] = scaleT t [] ++
  (p′*P[]) = [] ++ (p′*P[]) = p′*P[]`; base refl). Then `NormPoly-≡ ∘ coeff-canonicity`.

### The record
```agda
NormPoly-Semiring : Semiring NormPoly
NormPoly-Semiring = record
  { +-monoid          = mk-monoid _⊕_ 0P ⊕-assoc ⊕-idˡ ⊕-idʳ
  ; *-monoid          = mk-monoid _⊗_ 1P ⊗-assoc ⊗-idˡ ⊗-idʳ
  ; distrib-left      = distribL
  ; distrib-right     = distribR
  ; zero-absorb-left  = zabsL
  ; zero-absorb-right = zabsR
  }
```
Field types (verified `Semiring.agda:29-55`): `distrib-left/right : (a b c) → …`,
`zero-absorb-left/right : (a) → …`. `Monoid` fields (verified `Monoid.agda:28-39`): the
`_·_` used in each law is `Magma._·_ (magma (semigroup <monoid>))` — for `+-monoid` it is
`_⊕_`, for `*-monoid` it is `_⊗_`, exactly the ops fed to `mk-monoid`.

### `ε₂` and `ε₂-sq` (for RUNG 3c's `WithSign`)
```agda
ε₂ : NormPoly
ε₂ = (normalize (kP (-suc 0)) , normalize-sorted _)     -- kP from JacobianResidue.agda:176

ε₂-sq : ε₂ ⊗ ε₂ ≡ 1P
```
`kP (-suc 0) = [term (mono 0 0 0) (-suc 0)]`. `ε₂ ⊗ ε₂ = normalize (normalize(kP -1) *P
normalize(kP -1))`. Reduce via coeff: at `mono 0 0 0`, constant×constant, the coefficient is
`(-suc 0) *ℤ (-suc 0) = + 1` — **`mul-sign-computes`** (`Semiring/Instances/Z.agda:112`,
verified `refl`); at every other `m`, both sides `0ℤ`. So `∀m. coeff m (proj₁ (ε₂⊗ε₂)) ≡
coeff m (proj₁ 1P)`, closed by `NormPoly-≡ ∘ coeff-canonicity`. (`1P = normalize 𝟙P`,
constant `+1`.)

### POLE — normalization is load-bearing (ship as a non-vacuity witness)
Exhibit a concrete `⊗` that genuinely reorders — a product whose raw `*P` list order differs
from the normalized order, so `distrib-left` could NOT hold for raw `++`:
```agda
-- (x + y)·(x + y) via ⊗ has its cross terms MERGED/REORDERED; the raw *P list does not.
-- Concretely: coeff (mono 1 1 0) ((X⊕Y) ⊗ (X⊕Y)) ≡ + 2   (the 2xy term — combined),
-- whereas the raw (X+Y)*P(X+Y) keeps two separate xy entries in ++ order.
poly-⊗-reorders : coeff (mono 1 1 0) (proj₁ ((X∷ ⊕ Y∷) ⊗ (X∷ ⊕ Y∷))) ≡ + 2
poly-⊗-reorders = refl        -- pole: normalization actually combined like terms
```
where `X∷ = (normalize X , _)`, `Y∷ = (normalize Y , _)` from `X`,`Y`
(`JacobianResidue.agda:170-171`). This is the term witnessing that `⊕`/`⊗` do the reordering
`++`/`*P` cannot — the same asymmetry the plan's OBSTRUCTION names.

---

## 6. IMPORT HEADER (turn-key)
```agda
{-# OPTIONS --safe --without-K --guardedness #-}
module Substrate.Algebra.Z.MPolySemiring where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂; subst)
open import Substrate.Foundation.Negation using (¬_; Dec; yes; no)
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂; Σ-≡,≡→≡)
open import Substrate.Foundation.List using (List; []; _∷_; _++_)
open import Substrate.Foundation.Hedberg using (DecidableEquality; Decidable⇒UIP)
open import Substrate.Algebra.Z using (ℤ; +_; -suc_; 0ℤ; 1ℤ; -ℤ_; _≟ℤ_)
open import Substrate.Algebra.Z.Add using (_+ℤ_)
open import Substrate.Algebra.Z.Mul using (_*ℤ_)
open import Substrate.Algebra.Z.Properties.Add
  using (+ℤ-assoc; +ℤ-comm; +ℤ-identityˡ; +ℤ-identityʳ; +ℤ-inverseˡ)
open import Substrate.Algebra.Z.Properties.MulFull using (*ℤ-assoc; *ℤ-identityˡ)
open import Substrate.Algebra.Monoid using (Monoid)
open import Substrate.Algebra.Semiring using (Semiring)
open import Substrate.Algebra.Semiring.Instances using (mk-monoid)
open import Substrate.Algebra.Z.MonoCommMonoid using (addM-assoc; addM-idˡ; addM-idʳ)
open import Substrate.Algebra.Z.JacobianResidue
  using (Mono; mono; Term; term; MPoly; coeff; eqM; eqℕ; and; 𝔹; tt; ff;
         addM; mulT; scaleT; _*P_; _+P_; 𝟙P; kP; X; Y)
open import Substrate.Algebra.Z.MPolyNormalize          -- RUNG 3a (MUST EXIST FIRST)
  using (consNZ; insertT; normalize; isSortedB; ltM𝔹; nzB;
         normalize-sorted; coeff-normalize; coeff-++; coeff-cons-tt; coeff-cons-ff;
         triM; eqM-refl; eqM-sound; and-l; and-r)
```
> ⚠ Confirm the exact RUNG-3a export list once `MPolyNormalize.agda` lands — names above are
> the probe's names (`scratch/polynorm-probe.agda`) plus the §4.1 additions. `_+P_` is unused
> if you spell `++` directly; keep whichever RUNG 3a exports.

## 7. BUILD / GATE
Heavy-ish (canonicity + assoc). Compile via membudget per project CLAUDE.md:
```
cd agda && make -C . -j          # shim self-throttles; records proof-cost
# or one-off:  scripts/membudget run 1536 mpolysemiring -- agda --safe -i. Substrate/Algebra/Z/MPolySemiring.agda
```
Commit on `main`; wait for `post-commit advisory (auto-captured)` in HEAD before push.
Regenerate `catalog/reuse-index.md` after (adds `NormPoly`, `NormPoly-Semiring`).

## 8. HONEST SLOG-vs-MECHANICAL LEDGER
| item | status | est. lines |
|---|---|---|
| §1 NormPoly-≡ h-prop (`Σ-≡,≡→≡` + Hedberg + `_≟𝔹_`) | MECHANICAL | ~12 |
| §2.1 scaleT-++ | trivial | 3 |
| §2 coeff-*P-distˡ / distʳ (+ interchange) | MECHANICAL | ~40 |
| §3 *P-assoc chain (6 lemmas; assoc is ON-THE-NOSE) | MECHANICAL (surprise: lighter than planned) | ~35 |
| §4 coeff-canonicity (ltM𝔹-trans, triM𝔹, coeff-below/head, +ℤ-cancelˡ) | **REAL SLOG, no reuse** | ~130 |
| §5 assemble Semiring + ε₂-sq + reorder pole | MECHANICAL (glue over §1-§4) | ~70 |
| **TOTAL** | | **~290** |
The ONLY irreducible cost is §4 (canonicity's ordering machinery). §3, framed as a slog in the
plan, collapses to on-the-nose `*P`-associativity — record that finding.

## 9. ANCHOR TABLE (all verified 2026-07-21)
| symbol | home | line |
|---|---|---|
| `Mono/Term/MPoly/coeff/eqM/scaleT/_*P_/mulT/addM/𝟙P/kP/X/Y` | `Algebra/Z/JacobianResidue.agda` | 107,110,113,140,119,128,132,122,116,173,176,170 |
| `_*P_` recurses on 1st arg | ″ | 132-134 |
| `coeff` with-eqM read-off | ″ | 140-144 |
| `addM-assoc/idˡ/idʳ/comm`, `Mono-CommMonoid` | `Algebra/Z/MonoCommMonoid.agda` | 50,55,58,62,66 |
| `Decidable⇒UIP`, `DecidableEquality` | `Foundation/Hedberg.agda` | 80,24 |
| `Σ-≡,≡→≡`, `Σ/_,_/proj₁₂` | `Foundation/Product.agda` | 81,24 |
| `_≟ℤ_`, `ℕ-≟` | `Algebra/Z.agda` | 81,73 |
| `Semiring` record (6 fields) | `Algebra/Semiring.agda` | 29-55 |
| `Monoid` record (ε, ε-left, ε-right, Magma `_·_`) | `Algebra/Monoid.agda` | 28-39 |
| `mk-monoid` | `Algebra/Semiring/Instances.agda` | 41 |
| `mul-sign-computes` = `(-1)·(-1)=+1` | `Algebra/Semiring/Instances/Z.agda` | 112 |
| `*ℤ-assoc`, `*ℤ-identityˡ`, `+ℤ-injective` | `Algebra/Z/Properties/MulFull.agda` | 61,42,124 |
| `+ℤ-assoc/comm/identityˡ/identityʳ/inverseˡ/inverseʳ` | `Algebra/Z/Properties/Add.agda` | 71,57,85,89,102,97 |
| `det`, `WithSign`, `det{3}` convention | `WitnessTower/LeibnizDet.agda` | (module Det.WithSign) |
| probe lemmas (coeff-cons-tt/ff, coeff-++, normalize, triM, …) | `scratch/polynorm-probe.agda` | 129,135,141,113,85,184 |
| **NOT PRESENT — build locally**: `++-assoc` (List), `+ℤ-cancelˡ`, `_≟𝔹_`, `isSortedB/ltM𝔹` | — | §3(1),§4.5,§1,§4.1 |
