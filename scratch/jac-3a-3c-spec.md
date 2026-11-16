# RUNG 3a + 3c — turn-key execution spec (⟡jac-poly-normalize, ⟡jac-det-native)

COMPACTION-SAFE. Root context: `scratch/JAC-DET-NATIVE-PLAN.md`. This spec makes 3a and 3c
directly executable. **The whole coeff-homomorphism core of 3a and the `isSortedB` decision
have been TEST-COMPILED GREEN** (Agda 2.8.0, `--safe --without-K --guardedness`) —
see `scratch/jac-3a-bcase-probe.VERIFIED.agda` (compiles, exit 0). Lift from there, not from
the older `scratch/polynorm-probe.agda` (which does NOT compile — it dies at the `coeff-cons-ff`
wrinkle, line 152; confirmed empirically).

Gating: **3a is standalone.** 3c is GATED on 3b (`NormPoly-Semiring`, `ε₂`, `ε₂-sq`, `coeff-*P`);
build 3b (see `scratch/jac-3b-spec.md`) before 3c.

Anchors verified against source at the file:line cited (all confirmed 2026-07-21).

--------------------------------------------------------------------------------
# RUNG 3a — `Substrate.Algebra.Z.MPolyNormalize`

New module. `{-# OPTIONS --safe --without-K --guardedness #-}`
(guardedness is inherited via the import graph of `Algebra.Z`; the probe uses it, keep it).

## 3a.0 Imports (verbatim from the verified probe header)

```agda
module Substrate.Algebra.Z.MPolyNormalize where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _<_; _≤_; z≤n; s≤s)
open import Substrate.Foundation.Nat.Properties.Order using (<-irrefl)
open import Substrate.Foundation.List using (List; []; _∷_; _++_)
open import Substrate.Foundation.Negation using (¬_; Dec; yes; no)
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong; cong₂; subst)
open import Substrate.Algebra.Z using (ℤ; +_; -suc_; 0ℤ; 1ℤ; _≟ℤ_)
open import Substrate.Algebra.Z.Add using (_+ℤ_)
open import Substrate.Algebra.Z.Properties.Add using (+ℤ-assoc; +ℤ-identityˡ)
open import Substrate.Algebra.Z.JacobianResidue
  using (Mono; mono; Term; term; MPoly; coeff; eqM; eqℕ; 𝔹; tt; ff; and)
```

Note: `Mono`/`term`/`MPoly`/`coeff`/`eqM`/`eqℕ`/`𝔹`/`tt`/`ff`/`and` are all re-used from
`Algebra.Z.JacobianResidue` (`JacobianResidue.agda`: `Mono`:107-108, `term`:110-111,
`MPoly`:113-114, `eqM`:119-120, `coeff`:140-144, `𝔹/tt/ff`:75-76, `and`:78-80, `eqℕ`:82-85).
Do NOT redefine them — 3c must compare against the SAME `coeff`/`Mono` that `detJac` uses.

## 3a.1 LIFT VERBATIM from `scratch/jac-3a-bcase-probe.VERIFIED.agda`

These blocks compiled green; copy them exactly. Section headers in the probe map 1:1:

| block | probe lines | notes |
|---|---|---|
| `fst₃/snd₃/thd₃`, `<→≢`, `and-l`, `and-r`, `cong₃` | helpers | verbatim |
| `eqℕ-refl`, `eqℕ-sound` (private) | verbatim | |
| `eqM-refl` | verbatim | |
| **`eqM-sound`** | **USE THE PINNED VERSION (below), not the probe:56-60 form** | see 3a.2 |
| `TriN`, `triℕ`, `TriM`, `triM` | verbatim | lex trichotomy, lt/gt carry `¬(m≡n)` |
| `consNZ`, `insertT`, `normalize` | verbatim | sorted-insert / combine-on-eq / drop-zero |
| **`Bcase`**, **`coeff-cons`** | new primitives (3a.2) | the wrinkle fix |
| `coeff-++` | verbatim | |
| **`coeff-consNZ`**, **`coeff-insertT`**, **`coeff-normalize`** | REWRITTEN via Bcase (3a.3) | settled, compiled |

## 3a.2 THE `coeff-cons` WRINKLE FIX — settled, compiled green

The probe's `coeff-cons-tt`/`coeff-cons-ff` (probe:129-139) do NOT compile: an external
`with eqM j m` reduces `coeff` but the `⊥-elim (ff≢tt e)` discharge fails
(`polynorm-probe.agda:152` → `[UnequalTerms] coeff j (term m k ∷ p) | eqM j m != coeff j p`).
REPLACE that whole pair with an **unconditional boolean eliminator** `Bcase` + one lemma
`coeff-cons`, both branches `refl`:

```agda
Bcase : 𝔹 → ℤ → ℤ → ℤ
Bcase tt a b = a
Bcase ff a b = b

coeff-cons : (j m : Mono) (k : ℤ) (p : MPoly) →
             coeff j (term m k ∷ p) ≡ Bcase (eqM j m) (k +ℤ coeff j p) (coeff j p)
coeff-cons j m k p with eqM j m
... | tt = refl
... | ff = refl
```

WHY THIS REDUCES (verified against source): `coeff` (`JacobianResidue.agda`:140-144) is defined
`coeff m (term n k ∷ p) with eqM m n | ... tt = k +ℤ coeff m p | ... ff = coeff m p`. When
`coeff-cons` does `with eqM j m`, the SAME `eqM j m` scrutinee drives BOTH `coeff j (term m k ∷ p)`
(coeff's own hidden with-auxiliary) AND `Bcase (eqM j m) …`, so in each branch both reduce to the
same numeral → `refl`. This is EXACTLY the `coeff-++` idiom (probe:143-145 / verified probe): a
`with eqM …` at the use site drives coeff and the RHS together. The KEY DISCIPLINE that follows:
never apply `coeff-cons`/`Bcase` inside a `with eqM j m` branch expecting the *result's* `eqM j m`
to be identified with the branch's — the with-abstraction only rewrites the goal, not a
separately-applied lemma's type (this bites; see the `rewrite`-first fix in 3a.3).

### `eqM-sound` — MUST use the pinned-implicit form (latent defect fixed)

The probe's `eqM-sound` (probe:56-60) has a latent defect that only fires when it is APPLIED at
abstract `Mono` variables (which the `gtM` corner of `coeff-insertT` does): `and-l h` cannot infer
its implicit `x` because `and` is non-injective on a stuck `eqℕ a d`
(`[UnsolvedMetaVariables]`, reproduced in isolation). FIX — pin the first implicit of every
`and-l`/`and-r` (compiled green):

```agda
eqM-sound : {m n : Mono} → eqM m n ≡ tt → m ≡ n
eqM-sound {mono a b c} {mono d e f} h =
  cong₃ mono (eqℕ-sound (and-l {eqℕ a d} h))
             (eqℕ-sound (and-l {eqℕ b e} (and-r {eqℕ a d} h)))
             (eqℕ-sound (and-r {eqℕ b e} (and-r {eqℕ a d} h)))
```

## 3a.3 THE THREE coeff-homomorphism lemmas, Bcase-style — ALL COMPILED GREEN

Copy verbatim from the verified probe. Reproduced here so the mechanics are settled, not
hand-waved. The recurring pattern: (1) collapse the RHS cons to `Bcase (eqM j m) …` via
`coeff-cons`; (2) when an *inner* `coeff j (term … ∷ …)` must also collapse under the same
scrutinee, use **`rewrite coeff-cons …` BEFORE `with eqM j m`** (a `with` alone won't identify the
two `eqM` occurrences); (3) discharge each boolean branch.

```agda
coeff-++ : (m : Mono) (p q : MPoly) → coeff m (p ++ q) ≡ coeff m p +ℤ coeff m q
coeff-++ m [] q = sym (+ℤ-identityˡ (coeff m q))
coeff-++ m (term n k ∷ p) q with eqM m n
... | tt = trans (cong (k +ℤ_) (coeff-++ m p q)) (sym (+ℤ-assoc k (coeff m p) (coeff m q)))
... | ff = coeff-++ m p q

coeff-consNZ : (j m : Mono) (k : ℤ) (p : MPoly) →
               coeff j (consNZ m k p) ≡ coeff j (term m k ∷ p)
coeff-consNZ j m k p with k ≟ℤ 0ℤ
... | no  _ = refl
... | yes k≡0 = trans eq (sym (coeff-cons j m k p))
  where
    eq : coeff j p ≡ Bcase (eqM j m) (k +ℤ coeff j p) (coeff j p)
    eq with eqM j m
    ... | tt = sym (trans (cong (_+ℤ coeff j p) k≡0) (+ℤ-identityˡ (coeff j p)))
    ... | ff = refl

coeff-insertT : (j m : Mono) (k : ℤ) (p : MPoly) →
                coeff j (insertT m k p) ≡ coeff j (term m k ∷ p)
coeff-insertT j m k [] = coeff-consNZ j m k []
coeff-insertT j m k (term n d ∷ p) with triM m n
... | ltM _ = coeff-consNZ j m k (term n d ∷ p)
... | eqM≡ refl =
      trans (coeff-consNZ j m (k +ℤ d) p)
      (trans (coeff-cons j m (k +ℤ d) p)
      (trans mid (sym (coeff-cons j m k (term m d ∷ p)))))
  where
    -- m ≡ n case; `rewrite coeff-cons j m d p` collapses the inner coeff onto the
    -- SAME eqM j m so the outer `with` drives all occurrences together.
    mid : Bcase (eqM j m) ((k +ℤ d) +ℤ coeff j p) (coeff j p)
        ≡ Bcase (eqM j m) (k +ℤ coeff j (term m d ∷ p)) (coeff j (term m d ∷ p))
    mid rewrite coeff-cons j m d p with eqM j m
    ... | tt = +ℤ-assoc k d (coeff j p)
    ... | ff = refl
coeff-insertT j m k (term n d ∷ p) | gtM m≢n =
      trans (coeff-cons j n d (insertT m k p))
      (trans mid
             (sym (coeff-cons j m k (term n d ∷ p))))
  where
    -- gt case: the two conses are on DIFFERENT monos (m ≢ n). Peel BOTH via
    -- coeff-cons + the IH, then split on BOTH eqM j m and eqM j n. The (tt,tt)
    -- corner (j≡m AND j≡n ⇒ m≡n) is impossible by m≢n; the other three are refl.
    mid : Bcase (eqM j n) (d +ℤ coeff j (insertT m k p)) (coeff j (insertT m k p))
        ≡ Bcase (eqM j m) (k +ℤ coeff j (term n d ∷ p))  (coeff j (term n d ∷ p))
    mid rewrite coeff-insertT j m k p | coeff-cons j m k p | coeff-cons j n d p
              with eqM j m in ejm | eqM j n in ejn
    ... | tt | tt = ⊥-elim (m≢n (trans (sym (eqM-sound {j} {m} ejm)) (eqM-sound {j} {n} ejn)))
    ... | tt | ff = refl
    ... | ff | tt = refl
    ... | ff | ff = refl

coeff-normalize : (j : Mono) (p : MPoly) → coeff j (normalize p) ≡ coeff j p
coeff-normalize j []             = refl
coeff-normalize j (term m k ∷ p) =
  trans (coeff-insertT j m k (normalize p))
  (trans (coeff-cons j m k (normalize p))
  (trans step (sym (coeff-cons j m k p))))
  where
    step : Bcase (eqM j m) (k +ℤ coeff j (normalize p)) (coeff j (normalize p))
         ≡ Bcase (eqM j m) (k +ℤ coeff j p)            (coeff j p)
    step with eqM j m
    ... | tt = cong (k +ℤ_) (coeff-normalize j p)
    ... | ff = coeff-normalize j p
```

The `with … in` idiom (gtM `mid`) is `--safe --without-K`-valid — live at
`Groups/S4-Iso/ExtractCorrect.agda:67`, `Groups/Stab-S3-Hom.agda:222`.

## 3a.4 `isSortedB` — COMPILED GREEN (accept / reject / zero poles all `refl`)

Decision taken: **encode BOTH strictly-ascending Mono AND coeff-nonzero in the ONE boolean**
(single invariant, because the `NormPoly` carrier and 3b's `coeff-canonicity` need both). Needs
`or`, a boolean `ltℕᵇ`/`ltMᵇ` (lex, mirrors `triℕ`/`triM`'s order), and `nonzeroᵇ`:

```agda
or : 𝔹 → 𝔹 → 𝔹
or tt _ = tt
or ff b = b

ltℕᵇ : ℕ → ℕ → 𝔹
ltℕᵇ zero    (suc _) = tt
ltℕᵇ (suc a) (suc b) = ltℕᵇ a b
ltℕᵇ _       _       = ff

ltMᵇ : Mono → Mono → 𝔹        -- strict lex on (x,y,z)
ltMᵇ (mono a b c) (mono d e f) =
  or (ltℕᵇ a d) (and (eqℕ a d) (or (ltℕᵇ b e) (and (eqℕ b e) (ltℕᵇ c f))))

nonzeroᵇ : ℤ → 𝔹
nonzeroᵇ k with k ≟ℤ 0ℤ
... | yes _ = ff
... | no  _ = tt

isSortedB : MPoly → 𝔹
isSortedB []                          = tt
isSortedB (term m k ∷ [])             = nonzeroᵇ k
isSortedB (term m k ∷ term n d ∷ p)   = and (nonzeroᵇ k) (and (ltMᵇ m n) (isSortedB (term n d ∷ p)))
```

## 3a.5 `normalize-sorted` / `normalize-idem` — SKELETON (the remaining 3a induction)

The coeff core (3a.1-3a.3) and `isSortedB` (3a.4) are compiled. The one induction left is the
sortedness/idempotence of `normalize`. Cleanest route: `normalize-idem` factors through a
"normalize is the identity on already-sorted" lemma applied to `normalize-sorted`.

```agda
-- (i) a bridge: the boolean order agrees with triM's decision.
--     Needed to connect isSortedB (which uses ltMᵇ) to insertT (which uses triM).
ltMᵇ→ltM : (m n : Mono) → ltMᵇ m n ≡ tt → ¬ (n ≡ m)          -- or land in TriM m n = ltM
--    (mirror of triM's lt case; prove by triℕ/lex, ~15 lines)

-- (ii) insertT preserves sortedness (induction on q, cases via triM m head):
insertT-sorted : (m : Mono) (k : ℤ) (q : MPoly) →
                 isSortedB q ≡ tt → isSortedB (insertT m k q) ≡ tt
--    q=[]:      consNZ m k [] ; split k ≟ℤ 0ℤ.
--    q=n∷:  triM m n → ltM: consNZ prepends (need m<n ⇒ ltMᵇ m n);
--                       eqM≡: consNZ combines at n (drop-or-keep, tail already sorted);
--                       gtM: term n d ∷ insertT m k p, IH + n<head(insertT m k p).

-- (iii) THE RESULT:
normalize-sorted : (p : MPoly) → isSortedB (normalize p) ≡ tt
normalize-sorted []             = refl
normalize-sorted (term m k ∷ p) = insertT-sorted m k (normalize p) (normalize-sorted p)

-- (iv) normalize fixes an already-sorted list:
normalize-fixed : (q : MPoly) → isSortedB q ≡ tt → normalize q ≡ q
--    []: refl. (term m k ∷ q'): normalize = insertT m k (normalize q');
--        IH normalize q' = q'; then insertT m k q' = term m k ∷ q'
--        because m < head q' (from isSortedB) and k ≠ 0 ⇒ insertT hits ltM then consNZ-no.
--        Sub-lemma insertT-prepend : ltMᵇ m (head) ≡ tt → nonzeroᵇ k ≡ tt →
--                 insertT m k q' ≡ term m k ∷ q'.

-- (v) IDEMPOTENCE, from (iii)+(iv):
normalize-idem : (p : MPoly) → normalize (normalize p) ≡ normalize p
normalize-idem p = normalize-fixed (normalize p) (normalize-sorted p)
```

Estimated ~70-90 lines for (i),(ii),(iv) + their sub-lemmas. Everything downstream (3b, 3c) needs
only the SIGNATURES of `normalize-sorted`/`normalize-idem` + `coeff-normalize`, so they are a clean
seam. If (ii)/(iv) prove sticky, an alternative for `normalize-idem` alone is direct double-induction
on `insertT (insertT …)` — but the `normalize-fixed` route is preferred (it also yields the
`NormPoly` retraction 3b wants).

## 3a.6 FILE THE REUSE WITNESS — `idem-Canonical` (verified anchor)

`normalize-idem` is exactly the idempotent law `e(e x) ≡ e x`, and the substrate already has its
apex. VERIFIED at `Algebra/Quotient.agda`:

- `ker-Quotient` (`Quotient.agda`:134-136): `(F : A → B) → Quotient A (KerRel F)`, `KerRel F x y = F x ≡ F y`.
- `idem-Canonical` (`Quotient.agda`:155-164):
  `(e : A → A) (idem : (x : A) → e (e x) ≡ e x) → Canonical (ker-Quotient e)`
  — "The apex of the idempotent law-motif f(f x)≡f x (normalize-idem, q-idempotent, …)"
  (the comment literally names `normalize-idem`). `canonical-respects-≈` is the identity.

Add:

```agda
open import Substrate.Algebra.Quotient using (Quotient; Canonical; ker-Quotient; idem-Canonical)

normalize-Canonical : Canonical (ker-Quotient normalize)
normalize-Canonical = idem-Canonical normalize normalize-idem
```

This is a ONE-LINER instantiation — do NOT hand-build a Canonical record; the trigger is on the
plan ("build a Canonical for normalize") → the generator is `idem-Canonical`.

## 3a.7 Non-vacuity poles (ship as terms)

```agda
-- (a) x + x normalizes so coeff x = 2 (combine-on-equal actually fires). COMPILED.
xP : MPoly
xP = term (mono 1 0 0) 1ℤ ∷ term (mono 1 0 0) 1ℤ ∷ []
pole-x+x : coeff (mono 1 0 0) (normalize xP) ≡ + 2
pole-x+x = refl

-- (b) isSortedB rejects a descending list [2x, 1]. COMPILED.
reject-pole : isSortedB (term (mono 1 0 0) (+ 2) ∷ term (mono 0 0 0) 1ℤ ∷ []) ≡ ff
reject-pole = refl

-- (c) isSortedB rejects a zero-coeff term. COMPILED.
zero-reject : isSortedB (term (mono 1 0 0) 0ℤ ∷ []) ≡ ff
zero-reject = refl

-- (optional, once normalize-sorted lands) accept pole:
accept-pole : isSortedB (term (mono 0 0 0) 1ℤ ∷ term (mono 1 0 0) (+ 2) ∷ []) ≡ tt
accept-pole = refl
```

## 3a.8 Build / gate

Heavy? No — this module is small integer/list algebra; the verified probe compiled in seconds.
Build via `make -C agda -j` (shim-routed, budgeted). Add the new module to
`agda/Substrate/Algebra/Z/Makefile` if the generator doesn't pick it up
(`scripts/gen_build_makefiles.py`, then `scripts/gen_reuse_index.py` to home `normalize`/`isSortedB`
in `catalog/reuse-index.md`). Commit on `main`; wait for the `post-commit advisory` marker before push.

--------------------------------------------------------------------------------
# RUNG 3c — `Substrate.Algebra.Z.JacobianDetNative`  (GATED on 3b)

New module. `{-# OPTIONS --safe --without-K #-}` (match `LeibnizDet`/`JacobianResidue`).
PRECONDITION — 3b must have delivered, in `Substrate.Algebra.Z.MPolySemiring`:
`NormPoly : Set` (= `Σ MPoly (λ p → isSortedB p ≡ tt)`), `NormPoly-Semiring : Semiring NormPoly`,
`ε₂ : NormPoly` (= `normalize (kP (-suc 0))` packaged with its sorted proof),
`ε₂-sq : (ε₂ *A ε₂) ≡ 1A`, and `coeff-*P` (coeff pushes through `_*P_`). Also a helper
`coeffN : Mono → NormPoly → ℤ` := `λ j q → coeff j (proj₁ q)`.

## 3c.1 The `Det`/`Mono` convention — VERIFIED row-major, row = component

VERIFIED against source:
- `LeibnizMonomial.agda`: `Mat n = Fin (n * n) → A` (`:73-74`), flat **row-major** via
  `combine`/`remQuot` (`:17-23`). `mono-alg.step` (`:109`) is
  `λ {n} c p → λ M → M (combine {suc n}{suc n} zero p) *A c (minor p M)`, and `mono = fold mono-alg`
  (`:113-114`) computes `Πᵢ M[i, (decode l) i]`. So the flat index of entry (row `i`, col `j`) is
  `combine i j = i*n + j`. **Row = the fold's row index `i` (domain of σ); col = σ i.**
- `LeibnizDet.agda`: `det {n} M = Σ_{σ∈Sₙ} signVal (signF σ) (mono (encode σ) M)` (`:116-119`) =
  `Σ_σ sign(σ) · Πᵢ M[i, σ i]`. Confirmed by `det-M3 : det{3} M3 ≡ -suc 2` `refl` (`:165-166`) over
  the row-major `M3 = [[1,2,3],[4,5,6],[7,8,10]]` indexed `0..8 = row*3 + col` (`:154-163`).

The classical Jacobian determinant is `Σ_σ sign(σ) Πₐ J[a, σ a]` with **row a = component fₐ,
col = variable**. So `JacMat`'s flat index = `component*3 + variable`. Cross-check against
`detJac` (`JacobianResidue.agda`:192-199): summand `(0,1,2)+` is `∂x f₁ *P ∂y f₂ *P ∂z f₃` =
row0→col0, row1→col1, row2→col2 = σ=id (even); `(1,2,0)+` is `∂y f₁ *P ∂z f₂ *P ∂x f₃` =
row0→col1, row1→col2, row2→col0 = 3-cycle (even). Matches `det`'s `Πᵢ M[i,σi]` exactly. ✓

## 3c.2 `JacMat` — the entries (normalized existing derivatives)

`∂x/∂y/∂z` and `f₁/f₂/f₃` are REUSED from `JacobianResidue.agda` (`∂`:151-160, `f`:182-185); each
entry is `mkN (normalize (∂v fᵢ))` where `mkN : (p : MPoly) → NormPoly` packages `normalize p` with
`normalize-sorted p` (3a). Map (col x/y/z × row f₁/f₂/f₃), flat = row*3 + col:

```agda
open import Substrate.Algebra.Z.JacobianResidue using (∂x; ∂y; ∂z; f₁; f₂; f₃; kP; detJac; coeff; Mono; mono)
open import Substrate.Algebra.Z.MPolyNormalize  using (normalize; normalize-sorted; coeff-normalize; coeff-++)
open import Substrate.Algebra.Z.MPolySemiring   using (NormPoly; NormPoly-Semiring; ε₂; ε₂-sq; mkN; coeffN; coeff-*P; _*P_)   -- names 3b exposes
open import Substrate.WitnessTower.LeibnizDet using (module Det)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Product using (proj₁)

open Det NormPoly NormPoly-Semiring using (Mat; mono)
open Det.WithSign NormPoly NormPoly-Semiring ε₂ ε₂-sq using (det; signVal)

JacMat : Mat 3                       -- Fin 9 → NormPoly, flat = component*3 + variable
JacMat zero                                     = mkN (∂x f₁)   -- 0 : row f₁, col x
JacMat (suc zero)                               = mkN (∂y f₁)   -- 1 : row f₁, col y
JacMat (suc (suc zero))                         = mkN (∂z f₁)   -- 2 : row f₁, col z
JacMat (suc (suc (suc zero)))                   = mkN (∂x f₂)   -- 3 : row f₂, col x
JacMat (suc (suc (suc (suc zero))))             = mkN (∂y f₂)   -- 4
JacMat (suc (suc (suc (suc (suc zero)))))       = mkN (∂z f₂)   -- 5
JacMat (suc (suc (suc (suc (suc (suc zero)))))) = mkN (∂x f₃)   -- 6 : row f₃, col x
JacMat (suc (suc (suc (suc (suc (suc (suc zero))))))) = mkN (∂y f₃) -- 7
JacMat (suc (suc (suc (suc (suc (suc (suc (suc zero)))))))) = mkN (∂z f₃) -- 8

detNative : NormPoly
detNative = det {3} JacMat
```

Instantiation mirrors `LeibnizDet.agda`:139-140 (`open Det ℤ ℤ-semiring using (Mat)` /
`open Det.WithSign ℤ ℤ-semiring (-suc 0) mul-sign-computes using (det)`) with `ℤ↦NormPoly`,
`ℤ-semiring↦NormPoly-Semiring`, `(-suc 0)↦ε₂`, `mul-sign-computes↦ε₂-sq`.

## 3c.3 The final theorem — coeff-level agreement of the two determinant trees

```agda
det-native-correct : (j : Mono) → coeffN j detNative ≡ coeff j detJac
```

PROOF STRATEGY (coeff-homomorphism, expression-tree matching). Both `detNative` and `detJac` are
the SAME six signed 3-fold products of the SAME entries — `detNative` normalizes at every
`+A`/`*A`/`signVal`, `detJac` uses raw `_+P_`(=`++`)/`_*P_` (`JacobianResidue.agda`:125,132-134,
192-199). `coeff` is invariant under `normalize` (`coeff-normalize`, 3a) and is a homomorphism for
`++` (`coeff-++`, 3a) and `*P` (`coeff-*P`, 3b). So push `coeff j` through both trees to the same
leaf expression:

1. Unfold `detNative = det {3} JacMat` = `sumF` over `Fin 6` of `signVal (signF σᵢ) (mono (encode σᵢ) JacMat)`
   (`LeibnizDet.agda`:116-119). `sumF` is `+A`-fold (`:98-100`); `+A` on `NormPoly` = `mkN ∘ (++)`,
   so `coeffN j (a +A b) ≡ coeffN j a +ℤ coeffN j b` via `coeff-normalize` then `coeff-++`
   (prove once as `coeffN-+A`).
2. Each `mono (encode σᵢ) JacMat` is a 3-fold `*A` product of `JacMat` entries (`mono-alg.step`,
   `LeibnizMonomial.agda`:109); `*A` = `mkN ∘ (*P)`, so `coeffN j (a *A b) ≡ coeff j (proj₁ a *P proj₁ b)`
   via `coeff-normalize` then `coeff-*P` (prove once as `coeffN-*A`, **needs 3b's `coeff-*P`**).
   `signVal 𝟙 x = ε₂ *A x` (`:111-113`) — one more `*A`, with `proj₁ ε₂ = normalize (kP (-suc 0))`.
3. On the `detJac` side, the same six summands are raw `*P`/`++` of the raw derivatives; `coeff-*P`
   + `coeff-++` push `coeff j` to identical leaf products of `coeff … (∂v fᵢ)` (the entries agree
   because `coeff j (mkN (∂v fᵢ)) = coeff j (normalize (∂v fᵢ)) = coeff j (∂v fᵢ)` by `coeff-normalize`).
4. Both reduce to the SAME ℤ-expression at `j` ⇒ `refl`/`trans`-chain. The permutation bookkeeping
   (`encode`/`signF`/`enumerate`) is IDENTICAL on both sides (both range over the same six σ with the
   same signs — detJac's `:194-199` labels are S₃ with 3-cycles even / transpositions odd), so it
   cancels structurally; you match summand-by-summand.

Because the enumeration/sign are shared, the cleanest execution is: prove `coeffN-+A`, `coeffN-*A`,
and a `coeff-signVal` helper, then `det-native-correct j` unfolds `sumF` to six terms and matches
each against the corresponding `detJac` summand with a `coeff-*P`/`coeff-++`/`coeff-normalize`
chain. (Do NOT expect `det {3} JacMat` to `refl`-reduce to a closed NormPoly — see risk below.)

## 3c.4 Correctness checkpoints + native residue re-derivation

- **Convention checkpoint**: `det-M3 : det{3} M3 ≡ -suc 2` `refl` (`LeibnizDet.agda`:165-166) already
  proves the enumerate/encode/mono/sign/sum pipeline over a CONCRETE ℤ matrix. Optionally replicate a
  small NormPoly matrix pole to confirm the NormPoly instantiation reduces at all before tackling `JacMat`.
- **Native constant −2**: compose `det-native-correct` at `j = mono 0 0 0` with
  `JacobianResidue.constant-part : coeff (mono 0 0 0) detJac ≡ -suc 1` (`:229-230`):
  ```agda
  det-native-constant : coeffN (mono 0 0 0) detNative ≡ -suc 1     -- = −2
  det-native-constant = trans (det-native-correct (mono 0 0 0)) constant-part
  ```
- **Native residue vanishing (the box)**: `residue = detJac +P kP (+ 2)` and
  `residue-vanishes : residue-coeffs ≡ mapL (λ _ → 0ℤ) box` (`:207-208`, `:226-227`). Natively, for
  every `j` in `box` (`:210-215`), `coeffN j (detNative +A mkN (kP (+ 2))) ≡ 0ℤ` via
  `coeffN-+A` + `det-native-correct` + `coeff-++` reducing to `coeff j residue`, which is `0ℤ` on the
  box by `residue-vanishes`. Deliver as the graded object (the WEDGE discipline: read the observable,
  don't assume-and-refute), mirroring `residue-coeffs`.

## 3c.5 RISKS (flagged)

- **`det {3} JacMat` reduction is heavy.** Over ℤ it was `refl`; over `NormPoly` every `+A`/`*A`
  carries `normalize` + a `Σ`-proof, so the closed form is large and may not `refl`-close. MITIGATION:
  do NOT compute `detNative` to a normal form — work at the `coeff` level (3c.3), where `coeff-normalize`
  discards the sorted-proof and each node becomes a bounded ℤ-arithmetic step. Use `membudget`
  (`scripts/membudget run <MB> …`) for this module; expect it to be the heaviest of the three rungs.
- **The comparison DOES need `coeff-*P`** (3b). `coeffN-*A` cannot be proven without it — this is the
  hard 3b dependency; do not attempt 3c before 3b's `coeff-*P` (left/right linearity) lands.
- **`mkN`/`coeffN` glue**: ensure 3b exposes `mkN : MPoly → NormPoly` and `coeffN`/`coeff-*P` with the
  `_*P_` used matching `JacobianResidue._*P_` — 3c compares against `detJac` built from THAT `*P`, so
  the semiring's `*A` must be `mkN ∘ _*P_` over the identical `_*P_` (Cauchy list product, `:132-134`),
  else the leaf products won't match. Verify the `open` names against the actual 3b module before wiring.

--------------------------------------------------------------------------------
# Verification ledger (what was compiled vs. skeletoned)

- COMPILED GREEN (`scratch/jac-3a-bcase-probe.VERIFIED.agda`, exit 0): all of 3a.1-3a.4 —
  `Bcase`, `coeff-cons`, pinned `eqM-sound`, `coeff-++/consNZ/insertT/normalize`, `isSortedB`,
  and poles `pole-x+x`, `reject-pole`, `zero-reject`.
- CONFIRMED BROKEN (`scratch/polynorm-probe.agda`, exit 42 at `:152`): the probe's `coeff-cons-ff`
  route — this is why 3a.2 replaces it.
- SKELETON (real induction still to write, ~70-90 lines): 3a.5 `insertT-sorted` /
  `normalize-sorted` / `normalize-fixed` / `normalize-idem`. Signatures are the stable seam.
- SOURCE-VERIFIED ANCHORS (read 2026-07-21): `JacobianResidue.agda` (coeff:140-144, detJac:192-199,
  ∂:151-160, constant-part:229-230, residue-vanishes:226-227), `LeibnizDet.agda` (det:116-119,
  det-M3:165-166, instantiation:139-140), `LeibnizMonomial.agda` (Mat/step/mono:73-114, row-major:17-23),
  `Quotient.agda` (ker-Quotient:134-136, idem-Canonical:155-164), `Semiring.agda` (record:29-56).
