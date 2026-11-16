# ⟡jac-lit1-* SATURATION (2026-07-22) — the ℤ-numerator route for literal₁. COMPACTION-SAFE, durable home.

The `⟡REGROUNDING (2026-07-22)` conversation block holds the retrospective + the recursive
either/or collapse; THIS file is the durable, turn-key saturation of the `⟡jac-lit1-*` arc so it
survives a context compaction. Three read-only Explore agents were dispatched; each result is
MIRRORED verbatim-enough below under its symbol.

## THE ARC (one paragraph)
`literal₁ : (x y z : ℚ) → evalℚ x y z R.f₁ ≈ℚ C.f₁ x y z` (Jacobian counterexample, f₁ =
z·(1+xy)³ + y²·(1+xy)·(4+3xy), integer coeffs). The `homAgree` free-UP proof evaluates the
degree-9 polynomial into ℚ; `_+ℚ_` cross-multiplies denominators (`den·den`), so the top +ℚ
combine explodes to ~730–850 MB. Committed rung `⟡jac-literal-decompose` (`bd683a6`): the AES-Full
abstract-`Assemble` pattern (keep `evalℚ-++ pA pB` stuck over abstract summands; per-summand pins
1A/1B; `open`-not-redeclare) got it 853→729 MB; f₂/f₃ are light (94/77). THE DEEPER ROUTE
(`⟡jac-lit1-*`): the identity is fundamentally an INTEGER-numerator identity (f₁ ∈ ℤ[x,y,z]); the
ℚ blowup is PREMATURE COLLAPSE to ℚ. Keep the denominator-free ℤ/MPoly grade; the common
denominator `D` is the residue.

## STATE
`bd683a6` ⟡jac-literal-decompose landed gate-green + amend-marked. 2 unpushed (`a4f033d` +
`bd683a6`); USER pushes. `⟡jac-lit1-*` UNBUILT; being saturated by 3 agents.

---

## ⟡jac-lit1-qlift — SATURATED (agent, all file:line-verified). VERDICT: the lift is FREE; the blowup is in the VALUE, not the equality.

**`_≈ℚ_` IS definitionally a bare ℤ cross-equation** (`Q/Equiv.agda:37-38`):
`p ≈ℚ q = (num p *ℤ (+ suc (den-1 q))) ≡ (num q *ℤ (+ suc (den-1 p)))`. Setoid ops are the raw ℤ
`_≡_`: `≈ℚ-refl a = refl` (`:44-45`), `≈ℚ-sym e = sym e` (`:47-48`). `denominator q = suc (den-1 q)`
(`Q.agda:44-45`); `mkℚ {num:ℤ; den-1:ℕ}` (`Q.agda:32-36`).

**The lift is `id` / definitional.** A proof of the ℤ equation (in the right orientation) ALREADY
inhabits `p ≈ℚ q` — no packaging term. Optional wrappers, all `⇔-refl`/`refl` (= `id`):
- `≈ℚ-is-crossmix : (p q) → (p ≈ℚ q) ⇔ (cross ℚ-crossmix (num p)(denominator q) ≡ cross ℚ-crossmix
  (num q)(denominator p))`, proof `⇔-refl` (`HetCrossMix.agda:93-96`).
- `≈ℚ-via-HetQ = ⇔-refl` (`:98-99`); `cross-is-viaBridges = refl` (`:69-72`).
- `_⇔_` is a bare pair; `⇔-refl = (λ x→x),(λ x→x)` (`Foundation/Iff.agda:25-26`), so `proj₁` = id.

**CrossMix does ZERO computational work here** — it is the CERTIFICATE that `≈ℚ` IS the cross-product
ℤ-equation (`ℚ-crossmix : CrossMix ℤ-div ℕ-div ℤ-mul`, `cross ℚ-crossmix a d = a *ℤ (+ d)`
definitionally, `HetCrossMix.agda:57-62`; `CrossMul.agda:45-58`). Bézout (`s*ℤ(+a) +ℤ t*ℤ(+b) ≡ +g`,
`Z/Bezout.agda:39-41,96-97`; `cross-summand s a = refl : cross ℚ-crossmix s a ≡ s *ℤ (+ a)`,
`CrossMixBezout.agda:51-52`; `crossmix-from-trace = bezout-ℤ`, `:70-71`) is invoked ONLY if two
denominators must be reconciled via a GCD/coprime cancellation; a bare cross-equality does not call it.

**⚑⚑ THE LOAD-BEARING CAVEAT — the lift being free does NOT dodge the blowup.** `E = β.evalℚ x y z`,
`E (t ∷ p) = eT t +ℚ E p` definitionally (`JacobianEncodingGen.agda:50-52`), and `_+ℚ_` sets
`den = suc b₋ * suc d₋` (`Q/Add.agda:4,29` — the den·den product). So `den-1 (evalℚ R.f₁)` ALREADY
CONTAINS the den·den product baked into the VALUE. Whatever ℤ equation the ℤ side proves has these
den·den products as its literal subterms — proving it (e.g. by refl) still forces the degree-9
normalisation. The current `literal₁` dodges it STRUCTURALLY (the AES-Full stuck-abstract-summand
pattern, `JacobianLiteral1.agda:51-76`), NOT by CrossMix. Any CrossMix-routed replacement must
PRESERVE that stuck-ness or re-incur ~730 MB.

**⚑ NO common-denominator / additive CrossMix combinator exists** (search-result, grep of
CrossMul/HetCrossMix/CrossMixBezout/HetBasis): CrossMix exposes ONLY the multiplicative `cross` and
the pairwise cross-EQUALITY `_≈H_` (`HetBasis.agda:70-71`). Addition of two ℚ is ONLY `_+ℚ_` (den·den).
A normalized/coprime-denominator add whose correctness discharges via `bezout-ℤ` **does not exist and
would have to be BUILT** — this is the genuine gap, = `⟡jac-lit1-commonden`.

**TURN-KEY skeleton (the lift):** the ONLY nontrivial obligation is at the ℤ/MPoly level:
```agda
numId : (x y z : ℚ) →
  num (evalℚ x y z R.f₁) *ℤ (+ suc (den-1 (C.f₁ x y z)))
    ≡ num (C.f₁ x y z)     *ℤ (+ suc (den-1 (evalℚ x y z R.f₁)))
literal₁ x y z = numId x y z         -- the lift is this identity, verbatim
--   (optionally = proj₁ (≈ℚ-is-crossmix _ _) (numId x y z) — identical term)
```
BUT per the caveat, `den-1 (evalℚ R.f₁)` is the exploded denominator, so `numId` as stated re-incurs
the blowup UNLESS `evalℚ` is replaced by a common-denominator eval (⟡jac-lit1-commonden) OR the proof
keeps the summands stuck. **The lift is free; the ~730 MB is won or lost ENTIRELY on the ℤ/value side.**

---

## ⟡jac-lit1-numerator + ⟡jac-lit1-entry — SATURATED (agent, file:line-verified). ⚑ REFRAME: the numerator leg is ALREADY FREE; the 730 MB is the OTHER leg (the curried γ₁).

**⚑⚑ THE NUMERATOR HALF IS ALREADY DISCHARGED, DENOMINATOR-FREE, AND FREE OF THE DEGREE-9 ENGINE.**
- `bridge₁ : normalize R.f₁ ≡ normalize Cᴹf₁ = refl` (`JacobianEncodingNormalize.agda:65-66`; `bridge₂`
  `:68`, `bridge₃` `:71`, all `refl`). Poly-level: `refl` comparing two canonical sorted ℤ-term-lists
  (`normalize` = sorted-insert + like-term-combine + zero-drop, `MPolyNormalize.agda:142-144`). NO ℚ, NO
  denominators, NO cross-multiplication. Header (`:19-27`): "Rigid ℤ `≡`, zero `≈ℚ` composition."
- `evalBridge₁ : evalℚ f₁ ≈ℚ evalℚ Cᴹf₁` (`JacobianEvalNormalize.agda:185-191`), ALREADY PROVEN =
  `≈ℚ-trans (normalize-eval f₁) (≈ℚ-trans (≡→≈ℚ (cong evalℚ bridge₁)) (≈ℚ-sym (normalize-eval Cᴹf₁)))`.
  This chain touches ONLY sorted-insert additive rearrangements — it NEVER enters the degree-9
  `evalℚ-++`/`+ℚ-cross-multiply` node. `normalize-eval : (p) → evalℚ p ≈ℚ evalℚ (normalize p)` (`:166-177`).
- ⟹ the `E R.f₁ → E Cᴹf₁` leg of `literal₁` (`eb = evalBridge₁` in `JacobianLiteral1.agda`) is ALREADY CHEAP.

**⚑⚑ THE 730 MB IS THE `Cᴹf₁ → C.f₁`-CURRIED LEG (γ₁ = homAgree e₁), NOT the numerator identity.**
`literal₁ = ≈ℚ-trans eb (…combine…)`. `eb` (numerator leg) is cheap; the residual heavy inputs are the
per-summand `A.γ₁A`/`B.γ₁B = homAgree e₁A/e₁B` combined at the top `⊕E` `+ℚ-cong` — relating `evalℚ Cᴹf₁`
to the CURRIED collision function `C.f₁ x y z` (nested `+ℚ`/`*ℚ` of x,y,z, NOT an MPoly). MECHANISM confirmed:
- `_+ℚ_` (`Q/Add.agda:20-31`): `a/b + c/d` → den `d' = b * d` (a PRODUCT). Every add multiplies denominators.
- `+ℚ-cong` (`Q/Properties/Congruence.agda:43-75`): multiplies each numerator by `(+ (sa′ * sb′))` /
  `(+ (sa * sb))` (products of BOTH denominators) + `*ℤ-distribʳ-+`/`quadℤ` over them (`:62-75`). Scales with
  the denominator PRODUCTS.
- `*ℚ-cong` (`:33-37`): a direct `quadℤ` interchange, NO distribution — cheap per node.
- ⟹ per-summand `homAgree e₁A` (~91 MB) = one big ℚ, SINGLE denominator D (multiplicative chain, `*ℚ-cong`).
  Top `⊕E` combine `homAgree (a ⊕E b)` (`JacobianEncodingHom.agda:209-215`) forces `evalℚ-++ (encode a)
  (encode b)` (`:152-161`), 8-step induction; at the top the two operands are the two full degree-9 summands
  with denominators D_A, D_B, and `+ℚ` yields `D_A·D_B`, `+ℚ-cong` proves congruence over that den·den. THAT
  squaring of degree-9 denominators is the 90 MB → 730 MB jump.

**Q1 — denominator-free integer eval of an MPoly?** SEARCH-RESULT (shape `MPoly→ℤ`, `powℤ`, `evalℤ`): a POINT
eval `evalℤ : MPoly → ℤ` does NOT exist; nor `powℤ`. What EXISTS (denominator-free, and sufficient — the
coefficient kit): `coeff : Mono → MPoly → ℤ` (`JacobianResidue.agda:140`), `residue-coeffs : List ℤ`
(`:218-219`, = coeff-vector eval), `coeffN` (`JacobianDetNative.agda:34`), `coeff-canonicity`/`law-≡`
(`MPolySemiring.agda:333/380`, the coeff-equality ⇄ rigid `≡` extensionality), `coeff-normalize`
(`MPolyNormalize/Properties.agda:215`).

**VERDICT (⟡jac-lit1-entry): a numerator-eval need NOT be built for the numerator leg** — `bridge₁`+
`evalBridge₁` already discharge it. The residual cost is ENTIRELY the curried leg (`evalℚ Cᴹf₁ ≈ℚ C.f₁ x y z`).
So `⟡jac-lit1-numerator` is REPOINTED: the target is decomposing the curried leg's top `+ℚ`, i.e. building a
common-denominator eval of Cᴹf₁ that matches C.f₁'s denominator (avoiding D_A·D_B) — the ONLY-IF-NEEDED
`evalℤ` skeleton below, gated on ⟡jac-lit1-commonden's feasibility verdict (Agent 3).

**ONLY-IF-NEEDED `evalℤ` skeleton (does NOT exist; build over `Z.Add`/`Z.Mul`; mirrors `powℚ`/`monoval`/`evalℚ`
at `JacobianEvalNormalize:58-72`):**
```agda
powℤ w zero = 1ℤ ; powℤ w (suc n) = w *ℤ powℤ w n
monovalℤ nx ny nz (mono a b c) = powℤ nx a *ℤ (powℤ ny b *ℤ powℤ nz c)
evalℤ nx ny nz [] = 0ℤ ; evalℤ nx ny nz (term m k ∷ p) = (k *ℤ monovalℤ nx ny nz m) +ℤ evalℤ nx ny nz p
-- respects bridge₁ by `cong (evalℤ nx ny nz) bridge₁` — pure ℤ, denominator-free.
```

## ⟡jac-lit1-commonden + feasibility gate — SATURATED (agent, decisive). VERDICT: the gcd/Bézout/reduce spine is STUCK at symbolic x,y,z (naming trap); the VIABLE route is a gcd-FREE STRUCTURAL max-exponent common-denominator evaluator, which must be BUILT.

**Q1 — den-degree growth on `+ℚ` is REAL & unavoidable in the operator.** `_+ℚ_` (`Q/Add.agda:20-31`):
`d' = b * d` (`:30`), `n = (a *ℤ (+ d)) +ℤ (c *ℤ (+ b))` (`:28`). FULL cross-multiply, no gcd/LCD. `_*ℚ_`
same `d' = b*d` (`Q/Mul.agda:26-27`).

**Q2 — NO common-denominator / LCD / reduced addition exists** (search-result: `lcm|lcd|common.?den|
clearDen|numerator-only` empty). Both evaluators fold with plain `_+ℚ_`: `evalℚ (t ∷ p) = evalT t +ℚ evalℚ p`
(`JacobianEvalNormalize.agda:70-72`), `evalDirect` (`JacobianEncodingHom.agda:195-202`). The degree-9 poly's
many summands → denominator = full product of all monomial denominators → the 730-850 MB.

**Q3 — ⚑⚑ THE gcd/reduce/Bézout SPINE IS DECISIVELY STUCK AT SYMBOLIC x,y,z (mechanism).** On `x +ℚ y`,
x/y abstract: `denominator (x +ℚ y) = suc (((suc x.den-1) * (suc y.den-1)) ∸ 1)`. `gcd-of-ℚ`
(`Q/Reduction.agda:47-48`) calls `gcd-ℕ _ b = proj₁ (compute-trace _ b)` (`GcdN.agda:15-16`);
`compute-trace-acc` (`ComputeTrace.agda:33-34`) must match `b` against `zero`/`suc` and descend
`<-wellFounded b`. But `b` contains `suc x.den-1 * suc y.den-1` — `_*_` on abstract `suc x.den-1` is a STUCK
NEUTRAL (neither `zero` nor `suc _` at head) ⟹ `gcd-ℕ` neutral ⟹ `gcd-divides-{left,right}` can't deliver
a `divides (suc qd′) _` cofactor ⟹ `reduce-build` (`Q/Reduce.agda:37`) never matches ⟹ `reduce` doesn't
fire; `coprime-trace`/`bezout-ℤ` unreachable. **The ENTIRE Reduce/Reduction/HetReduce/HetReduceBezout/gcd/
Bézout spine reduces ONLY at concrete points — INERT here. Do NOT route through it.**

**Q4 — the viable route.** ⚑ (a) **STRUCTURAL MAX-EXPONENT COMMON DENOMINATOR — VIABLE, gcd-FREE.** "Common
denominator" ≠ "gcd": gcd/reduce compute LOWEST TERMS (need Euclid → stuck); a COMMON denominator is purely
structural. `Mono = mono ℕ ℕ ℕ` carries CONCRETE exponents (`JacobianResidue.agda:107-108` — only the point
coordinates x,y,z are abstract). So `D = xd^Dx · yd^Dy · zd^Dz`, `Dx = max over terms of the x-exponent`, is a
FIXED symbolic monomial: Dx/Dy/Dz and each `Dx ∸ a` are CONCRETE ℕ arithmetic; only the bases xd/yd/zd stay
abstract. Scaling each term to D → a pure-ℤ numerator; `evalNum` sums with ℤ addition only (NO den·den
regrowth). Works SYMBOLICALLY. **Does NOT exist; must be BUILT — elementary and gcd-free.**
⚑ (b) **the bare top-level ℤ cross-equation does NOT dodge the blowup** — `num(evalℚ R.f₁)`/`den(evalℚ R.f₁)`
are DEFINED by the many-summand `+ℚ` fold, so forming/normalizing them forces the den·den regrowth; `refl` is
strictly worse. The single-product-per-side framing holds only against the HAND `C.f₁` side (one top `+ℚ`);
the encoded `evalℚ R.f₁` side is the many-`+ℚ` fold — that is the cost. (b) is NOT a distinct cheaper route.

**⚑ TURN-KEY SKELETON (route a) — NEW `Substrate/Algebra/Q/JacobianEvalCommonDen.agda`:**
```agda
module _ (x y z : ℚ) where
  xd = denominator x; yd = denominator y; zd = denominator z   -- abstract bases (Q.agda:44)
  xn = num x; yn = num y; zn = num z
  Dx Dy Dz : ℕ                       -- = fold max over terms of a / b / c (CONCRETE)
  D : ℕ ; D = (xd ^ Dx) * (yd ^ Dy) * (zd ^ Dz)                -- symbolic monomial, NO gcd
  scaledNum : Term → ℤ
  scaledNum (term (mono a b c) k) =
    k *ℤ powℤ xn a *ℤ powℤ (+ xd) (Dx ∸ a)                     -- Dx∸a concrete, a ≤ Dx by Dx=max
      *ℤ powℤ yn b *ℤ powℤ (+ yd) (Dy ∸ b)
      *ℤ powℤ zn c *ℤ powℤ (+ zd) (Dz ∸ c)
  evalNum : MPoly → ℤ                 -- ℤ addition ONLY — no den·den
  evalNum [] = 0ℤ ; evalNum (t ∷ p) = scaledNum t +ℤ evalNum p
  evalCD : MPoly → ℚ ; evalCD p = mkℚ (evalNum p) (D ∸ 1)
  evalCD-sound : (p : MPoly) → evalℚ p ≈ℚ evalCD p            -- THE one real proof, induction on p
```
Then `literal₁` factors `evalℚ R.f₁ ≈ℚ[evalCD-sound R.f₁] evalCD R.f₁ ≈ℚ C.f₁`, first leg = soundness,
second = a bare ℤ cross-equation whose LHS numerator is a SINGLE ℤ-sum (cheap; `C.f₁` contributes its one
hand `+ℚ`). Preserves the existing anti-explosion `Assemble`/pinned-implicit discipline (`JacobianLiteral1.agda:51-76`),
replacing the blowing-up `evalℚ-++` fold leg with the numerator-only evaluator.
**MISSING HELPERS to build first (both absent):** `powℤ : ℤ → ℕ → ℤ` (no `^ℤ`/`powℤ` under `Algebra/Z/`) and
a ℕ `max`/`_⊔_` (not in `Foundation/Nat.agda`) — a few lines each; `Dx ∸ a` is total/safe since `a ≤ Dx = max`.

---

# ⚑ SYNTHESIS (all 3 agents) — the arc, corrected, turn-key
1. **`⟡jac-lit1-numerator` / `entry` REPOINTED:** the `R.f₁ → Cᴹf₁` numerator leg is ALREADY FREE
   (`bridge₁`=refl + `evalBridge₁`, both denominator-free, never touch the degree-9 node). NOT the bottleneck.
2. **`⟡jac-lit1-qlift`:** the ℤ→ℚ lift is DEFINITIONALLY FREE (`p ≈ℚ q` IS the ℤ cross-equation); CrossMix does
   zero computational work — it CERTIFIES the lift is free, doesn't compute it. But the blowup is in the VALUE.
3. **`⟡jac-lit1-commonden` IS THE WORK, and it is gcd-FREE:** the 730 MB is the `Cᴹf₁ → C.f₁`-curried leg's
   many-`+ℚ` fold (den·den). The fix = build the STRUCTURAL max-exponent common-denominator evaluator `evalCD`
   (+ `powℤ`, ℕ `max`, `evalCD-sound`). The gcd/Bézout/CrossMix/reduce spine is INERT at symbolic x,y,z — a
   naming trap; the residue `D` is a fixed symbolic monomial (exponents concrete), NOT a gcd.
- **THE RECURSIVE COLLAPSE, final rung:** "common denominator via CrossMix/Bézout/gcd" → NEITHER: gcd is stuck
  at symbolic level; the common denominator is STRUCTURAL (max-exponent monomial), gcd-free. The wedge
  `a = recon q b r`: numerator (ℤ-sum) = quotient, `D` (max-exponent monomial) = the KEPT RESIDUE; the key is
  that the exponents are CONCRETE so the residue is structurally computable. [[set1-is-grade-collapse]] applied
  to ℚ eval: keep the ℤ-numerator grade, the `D` residue is concrete-exponent structure.

## BUILD ORDER (dependency; each membudget-isolate-measured, target ≤~150 MB)
- **⟡jac-lit1-helpers** — `powℤ : ℤ → ℕ → ℤ` (Algebra/Z, mirror `powℚ`) + ℕ `_⊔_`/`max` (Foundation/Nat, if
  genuinely absent — reuse-search FIRST). Trivial leaves.
- **⟡jac-lit1-commonden** — `JacobianEvalCommonDen.agda`: `Dx/Dy/Dz` (max-fold over the fixed MPoly), `D`,
  `scaledNum`, `evalNum`, `evalCD`, and the ONE real proof `evalCD-sound : evalℚ p ≈ℚ evalCD p` (induction on p;
  per-term step relates `evalT t +ℚ rest` to `scaledNum t +ℤ rest` over the shared D, via `Equiv.agda:37`
  cross-mult; NO gcd). Generic over p → reused for f₁/f₂/f₃/detJac.
- **⟡jac-lit1-numerator** — re-prove `literal₁` (and optionally 2/3) as `evalℚ R.fᵢ ≈ℚ[evalCD-sound] evalCD R.fᵢ
  ≈ℚ C.fᵢ`, the second leg a single-ℤ-sum cross-equation. Keep the `Assemble`/pinned-implicit anti-explosion
  discipline. MEASURE — target the ~90-150 MB weight class (the ℤ-side per-summand cost, no den·den).
- **⟡jac-lit1-qlift** — subsumed / definitional (the `≈ℚ` legs above ARE the lift); no separate module.

## ⚑ MEMORY CORRECTION (supersedes the regrounding's ⟡memory-premature-q-collapse first draft)
A ℚ-value cross-multiplication blowup on an INTEGER identity IS premature collapse to ℚ — but the fix is NOT the
gcd/Bézout/CrossMix/reduce spine (that is DEFINITIONALLY STUCK at symbolic/abstract denominators — Euclid can't
descend a `suc v * suc w` neutral). The fix is a gcd-FREE STRUCTURAL common denominator: when the polynomial
EXPONENTS are concrete (only the evaluation point is abstract), the common denominator `D = base^(max-exponent)`
is a fixed symbolic monomial, and a numerator-only evaluator `evalNum : MPoly → ℤ` (ℤ addition, no den·den) +
soundness `evalℚ p ≈ℚ evalCD p` removes the blowup. "common denominator ≠ gcd" is the load-bearing distinction.
Widens [[set1-is-grade-collapse]], [[read-structure-dont-rebuild]]; corrects the "route through gcd/Bézout" reflex.

---

## ⟡jac-lit1-eea-shape — the EEATrace/wedge fixed point (USER pointer 2026-07-22; agent a26180ec running)
USER: "irrational numbers and continued fractions work with the same underlying shapes as EEA (EEATrace)."
STRUCTURAL CONVERGENCE (the regrounding note): **EEA = gcd = Bézout = CF = CRT = irrationals are ONE
`EEATrace`/wedge fold** — the substrate's central "one trace, many folds" fixed point (`eea-fold` in
`EEAFoldTable`), = the wedge `a = recon q b r` (`Algebra/Wedge.agda`). The `⟡jac-lit1` common-denominator eval
is ANOTHER fold over that same shape: numerator = the quotient, `D` = the divisor `b`, the residue kept.
⚑ AND Agent 3's stuck-verdict is EXACTLY explained by it: the EUCLIDEAN fold's `b` is computed by descent
(stuck on abstract `suc x.den-1 * suc y.den-1`); the STRUCTURAL fold's `b` (the max-exponent monomial `D`) is
FIXED (concrete exponents). Same wedge shape, different `b`-provenance — Euclidean (stuck) vs structural (works).
CF is EEA-quotient-based, so CF on the POINT denominators will be stuck at symbolic x,y,z like gcd.
**⚑ VERDICT (agent a26180ec, decisive): STRUCTURAL PARALLEL ONLY — `evalNum`/`evalCD` is a FRESH LEAF, not an
`eea-fold`/`DivStr`/CF reuse.** (`evalNum`/`evalCD`/`commonden` grep-empty; the leaf doesn't exist yet.)
- **CF is INERT at symbolic x,y,z, CONFIRMED same-as-gcd.** `qStep (a, suc b) = a div-suc b , (suc b , a mod-suc b)`
  (`RationalAdjunction.agda:61-64`) is the SAME Euclid engine — `div-suc`/`mod-suc` cannot step on the neutral
  `suc x.den-1 * suc y.den-1`. `convergent`/`conv-go` (`R/Trace.agda:69-75`) needs those (stuck) CF digits.
- **`evalNum` is a LIST catamorphism (FreeMonoid initial algebra), NOT the indexed `eea-fold`.** `MPoly = List
  Term` (`JacobianResidue.agda:113-114`, ~204 flat independent summands, NO remainder threading). `eea-fold`
  (`Nat/GCD/Fold.agda:24-31`) folds a DIVISION CHAIN (`step`'s recursive arg sits at the remainder
  `T (suc b)(remainder w) g`; one `(a,b)` pair). Different initial algebra — the substrate DRAWS THIS LINE:
  `Fold.agda:52-54` "eea-fold is NOT a FreeUP instance … recurses an indexed family. Same universality, diff shape."
- **The wedge `recon q b r` does NOT fit.** `recon q b r = q·b + r` (`Algebra/Wedge.agda:153`) reconstructs a
  DIVIDEND from (quot, divisor, rem) — three roles, division. Common-denominator combine `p/D + q/D = (p+q)/D`
  has NO quotient/remainder/division; `D` is a shared SCALING, not a divisor. Forcing it into `recon` = fabrication.
  Substrate flags this itself: `S5/S5EEA.agda:15-18` "ℚ cross-multiplication a·d≡c·b … is NOT a generic DivStr theorem."
  Grep for a ℚ `DivStr`/`recon` "share divisor + add numerators" instance: NONE.
- **THE one REAL universal-fold reuse is SPPF, not EEA/wedge — but blocked, and orthogonal.** `inside : Semiring A
  → (G → A) → SPPF G → A` (`Algebra/Semiring/SPPF.agda:48`) + `inside-unique` (`SPPFUP.agda:8`) is the principled
  "evaluate polynomial into a carrier" fold that `MPoly` re-rolls (the `⟡jac-det-via-sppf` debt, `JacobianResidue.agda:39-55`).
  BUT (a) SPPF is a SEMIRING, coefficients are NEGATIVE (the negation story); (b) `inside`'s local valuation
  `v : G → A` does NOT carry the GLOBAL max-degree `Dx` the common-denominator padding needs. So SPPF covers the
  multiply/add skeleton, NOT the D-padding. Orthogonal migration; **do the List-fold leaf now.**

**⚑ REVISED BUILD SPEC (supersedes "instantiate a fold"):** `evalNum` = a plain `foldr`/List catamorphism with
`_+ℤ_` over the ONCE-formed `D`; each `term (mono a b c) k` ↦ `k *ℤ xn^a *ℤ xd^(Dx∸a) *ℤ …`. Soundness
`evalCD-sound : evalℚ p ≈ℚ evalCD p` is proved by the SAME additive-reassoc idiom already in
`JacobianEvalNormalize.agda:88-177` (`insertT-eval`/`coeff-combine`/`normalize-eval`) — fully-pinned `≈ℚ-trans`/
`+ℚ-cong`/`+ℚ-assoc` chains, per-term, over `_+ℚ_`'s `a/b + c/d = (ad+cb)/(bd)` (`Q/Add.agda:20-31`). NO eea-fold,
NO DivStr, NO CF. (SPPF `inside` is the later `⟡jac-det-via-sppf` tightening, blocked on negation + global-D.)

## ⟡jac-lit1-tarski-graded — agent ad07622a landed (framing CONFIRMED); its "fresh leaf" conclusion REOPENED by USER + 3 new graded agents
The graded-vs-flat reframe is CORRECT and the substrate NAMES the theme ("flat = shadow of graded; REFINE don't
coerce", `OrientationFlatGradedBridge`). Agent ad07622a's USEFUL findings (mirror these — they are the graded framing):
- **GRADE = the ℕ³ MULTIDEGREE `(a,b,c)`** — the concrete exponent triple of `Mono = mono ℕ ℕ ℕ`
  (`JacobianResidue.agda:107-108`); grading monoid `(ℕ³, +, (0,0,0))` realized by `addM (mono a b c)(mono d e f)
  = mono (a+d)(b+e)(c+f)` (`:117`). **`_*P_` IS the graded product `C i → C j → C (i+j)`, matching
  `GradedProductOver._∧_`'s shape** (`OrientationBimonoidal.agda:34-39`).
- **`D = xd^Dx · yd^Dy · zd^Dz` is the TOP-GRADE NORMALIZER** — the monomial at grade `(a,b,c)` is transported UP to
  the fixed top grade `(Dx,Dy,Dz)` via the grade-complement `subst` (`xd^(Dx∸a)…`). `box` already computed CONCRETELY
  (`JacobianResidue.agda:210-215`: degrees x≤9, y≤12, z≤3). **⟹ D FALLS OUT OF THE GRADE** — it is NOT a "global
  normalizer bolted onto a leaf-local fold"; it IS the top grade. (This is the flat agent's "inside can't carry global D"
  objection DISSOLVED by grading.)
- **NEGATION = `FromCommRing.neg` (`Polynomial/Graded/FromCommRing.agda:66-71`)** — the exact `neg` transport MPoly's
  own debt note cites. Plus `ℤ-semiring` (`Semiring/Instances/Z.agda:85`), `NormPoly-Semiring` (`MPolySemiring.agda:479`).
- **THE GRADED POLYNOMIAL STACK is a candidate HOME:** `Polynomial/Graded/*` — `Poly` (degree-INDEXED),
  `FromCommRing`, `Quotient-CommRing : CommutativeRing (Poly (suc d))` (a graded poly over a ring, WITH neg).
- Multigrade precedent for generalizing `GradedProductOver` ℕ→ℕ³: `BackedGradedStencil.agda:45-79` grades by `ℕ × ℕ`.
- ⚑ The env-decode fold `inside : Semiring A → (G → A) → SPPF G → A` (`SPPF.agda:48`) IS the "El-with-environment"
  (code + valuation → value), and MPoly's header ADMITS it re-rolls SPPF (`JacobianResidue.agda:39-55`).

# ⚑⚑⚑ FINAL GRADED VERDICT (3 agents: ac2fbfb7 tools / a1d3747f consumers / acfe19a5 negation) — USER WAS RIGHT. Build `evalCD` via the GRADED PRODUCT. The flat "do a List-fold leaf" is REFUTED. THIS SUPERSEDES the "REVISED BUILD SPEC (List catamorphism)" above.

**THE TOOL IS `GradedProduct` = `GradedProductOver _+_ 0` — NOT `RigAlgebra`.** (The one precise non-fit: `RigAlgebra._⊗ᶜ_ : C i → C j → C (i*j)` grades by CARDINALITY product, `OrientationRigInitial.agda:56`; polynomial degree ADDS (`deg(x·x)=2=1+1`), so `i*j` is the wrong law. Use `GradedProduct`'s `i+j`.)

**ALL THREE FLAT OBJECTIONS DISSOLVE, with witnesses:**
- **global-D → the grade `n` IS the denominator exponent.** `GradedProduct C` (`Algebra/Wedge/Product.agda:55-58`):
  `u : C 0`, `_∧_ : {i j} → C i → C j → C (i + j)`. Take `C n = ℤ` = "numerator over `base^n`"; `_∧_ = _*ℤ_`
  multiplies numerators, and denominators `base^i · base^j = base^(i+j)` fall out of the grade STRUCTURALLY. Header:
  `GradedProduct IS GradedProductOver _+_ 0` (`OrientationBimonoidal.agda:34, hdr:10`).
- **≡ → GradedHomOver's PARAMETERIZED `_≈_`.** `GradedHomOver P Q (_≈_ : {n} → Cᴽ n → Cᴽ n → Set)`
  (`OrientationBimonoidal.agda:65-73`): `map-u`/`map-∧` valued in ANY equality — instantiate `_≈_ := _≈ℚ_`. Also
  `fold-unique-over` (`OrientationUniversal.agda:84-98`) parameterizes initiality equality, needs only `≈ℚ-trans`
  + step-cong ("`_≈_` need NOT be an equivalence", `:74`). The `≡`-only objection was about `GradedDivStr.wedge-eq`,
  NOT the hom/fold layer. DEAD.
- **negation → the free ℤ FIBER.** `C : ℕ → Set` is a PARAMETER (`Product.agda:53`); pick `C n = ℤ`, and negative
  coefficients (`term : Mono → ℤ`, `JacobianResidue.agda:111`) are ordinary ℤ negation IN THE FIBER — independent
  of the rig ops. (The flat "semiring→no-neg" was true of `RigAlgebra`'s Fin-ordering carrier only.) And if a ring
  is wanted: `ℤ-CommRing` (`Z/CommRing.agda:121`), `FromCommRing.Over.neg = inv (group (+-abelian R))` at ℤ-CommRing
  (`Polynomial/Graded/FromCommRing.agda:66-72`) — the exact term MPoly's own debt note names; or `ℤ-additive-inverse`
  (`Semiring/Instances/Z.agda:123`) within the semiring gauge + `ExpLogCodec`/`ℤ-power-codec`. Three routes = one
  wedge (`Z/CommRing.agda:9-27`). RigAlgebra is additively a MONOID (no `⊖`); negation comes from the CONSUMEE
  CommutativeRing, not the wedge.

**⚑ THE EXACT `evalCD` INSTANCE (turn-key; NOT a bespoke List-fold, NOT `foldR`):**
- carrier `C n = ℤ` (thin `record { num : ℤ }` to document "numerator over `base^n`").
- `P : GradedProduct C` = `u = 1ℤ`, `_∧_ {i}{j} a b = a *ℤ b` (`Product.agda:55`).
- atoms grade-1 `x̂ ŷ ẑ : C 1`; monomial `mono a b c` ↦ `power`/`_∧_` (`Product.agda:68`) → `C (a+b+c)` (grade = degree).
- grade-raiser to top grade N: `graded-of-product P : GradedDivStr C (λ _ → C 1)`, `recon n b r = r ∧ b`
  (`Product.agda:85-87`) = multiply numerator by `base`; iterate `N ∸ dₖ` times to lift every monomial to `C N`.
- common-denominator sum = plain ℤ-add on `C N` → one `mkℚ num (base^N ∸ 1)`, a SINGLE fixed denominator ⟹ the
  `_+ℚ_` den·den explosion never happens.
- readout `toℚ : C n → ℚ`, `toℚ {n} m = mkℚ (num m) (base^n ∸ 1)`, packaged as `GradedHomOver P Qℚ _≈ℚ_`
  (`OrientationBimonoidal.agda:65`); optionally characterize as THE unique map via `LehmerAlgebra` + `fold-unique-over`
  at `_≈_ = ≈ℚ` (`OrientationUniversal.agda:42,84`).

**⚑ IN-TREE TEMPLATE (do NOT declare a new data/record):** `JacobianNegSemiring.Diff : GradedProductOver _+_ zero
(λ _ → ℕ)` (`JacobianNegSemiring.agda:66-72`) — the ONLY place the Jacobian side already instantiates the graded
product at a numeric carrier, no new type; `Diff-assoc` via `+-assoc`. Copy this shape at `C n = ℤ`.

**⚑ THE ONE BUILD DESIGN POINT (multivariate) — settle in the build, WITHIN the graded route:** the grade in
`GradedProduct` is a single ℕ, but x/y/z have DIFFERENT denominators (`xd`/`yd`/`zd`), so `D = xd^Dx·yd^Dy·zd^Dz`
needs a PER-VARIABLE (ℕ³) grade, not a single `base^n`. Options: (a) grade by `ℕ³` (per-variable degree; carrier
`C (dx,dy,dz) = ℤ`, `_∧_` adds triples) — precedent `BackedGradedStencil.agda:45-79` grades by `ℕ×ℕ`; OR (b)
ITERATE the univariate `GradedProduct`/`Polynomial/Graded.Over` per variable (x then y then z) — `Poly n = Vec A n`
over a CommRing, `_*P_ : Poly n → Poly m → Poly (n+m)` (`Polynomial/Graded.agda:51,84`, full ring laws, WITH neg),
but it lacks a multivariate `eval` (only F₂-mod univariate Horner `Graded/Mod.agda:197`) — a NEW multivariate eval.
Either lands inside the graded route; NOT the flat leaf. NOTE: `JacobianGradedSource.agda:19-30,65` already lands
the grade-0 fiber (`graded-source-at-0 : coeff(mono 0 0 0) detJac = det{3} JacConst = −2`, negation as the S₃ μ₂
sign, refl) — the ∀-monomial identity is the only piece still gated (on `Semiring MPoly`, the ⟡jac-det-via-sppf debt).

**REVISED BUILD ORDER (supersedes the List-catamorphism order above):**
- **⟡jac-lit1-graded-C** — the carrier `C n = ℤ` + `P : GradedProduct C` (mirror `JacobianNegSemiring.Diff`) + atoms
  x̂ŷẑ + monomial via `power`. Decide the grade shape (ℕ³ vs iterated-univariate) here. `powℤ` may be `power` at C 1.
- **⟡jac-lit1-commonden** — `evalCD p = the top-grade-N sum` (grade-raiser `graded-of-product` + ℤ-add) → `mkℚ num
  (base^N ∸ 1)`. `evalCD-sound : evalℚ p ≈ℚ evalCD p` via `GradedHomOver`/`fold-unique-over` over `≈ℚ` (mirroring
  `normalize-eval`/`evalℚ-++`).
- **⟡jac-lit1-numerator** — re-prove `literal₁ = evalℚ R.f₁ ≈ℚ[evalCD-sound] evalCD R.f₁ ≈ℚ C.f₁` (2nd leg single-ℤ
  cross-equation, the lift definitionally free). Keep the `Assemble` anti-explosion discipline. MEASURE (~90-150 MB).

---

# ⚑ THE ROSETTA-STONE GRADED AXIS (2026-07-22, user: "you've added yet another dimension to our rosetta stone")

## The reframe — ⟡jac-lit1-grade-shape is NOT a fork, it is a NEW COORDINATE AXIS of `⟡jac-encoding-bridge`
The Jacobian Rosetta Stone (`scratch/jac_rosetta_stone.md`) is "one identity F, N machineries / every route is a
`quot()`" (its LATTICE / DEEPER-UNIFICATION sections). My "⟡jac-lit1-grade-shape — DECIDE FIRST (ℕ³ vs iterated)"
framing was ITSELF the either/or trap. The grade-shape adds a **graded axis** to the lattice: the polynomial F has
MULTIPLE graded representations, all COORDINATES of ONE object, related by isos:
- **flat-`MPoly`** (the bespoke; `den·den` blowup on `evalℚ` — the baseline to beat)
- **ℕ³-multidegree `GradedProduct`** (`C n = ℤ`, `_∧_ = _*ℤ_`; the pinned candidate)
- **iterated-univariate `ℤ[x][y][z]`** (`Quotient-CommRing`/`FromCommRing` tower iterated 3× over `ℤ-CommRing`)
- **(total-degree grade)** — a fourth coordinate
and the ℚ-EVAL coordinate (flat `evalℚ` / graded `evalCD`) is the coordinate-change on the ℚ side.

"ℕ³ vs iterated" → NEITHER (pick): two coordinates of the graded polynomial object, related by the standard iso
`ℤ[x,y,z] ≅ ℤ[x][y][z]`. The `quot()` unification EXTENDS: each `Quotient-CommRing` is `R[y]/(f)` = a `quot()`, so
the iterated tower is `quot()` iterated. The iso is a NEW ROSETTA BRIDGE (like `literalᵢ`), not a fork to resolve.

## Consequence for the build
- **⟡jac-lit1-grade-shape** RE-SCOPED: not "pick ℕ³ or iterated" but "the graded coordinate axis; both are views
  related by the multivariate↔iterated iso; build `evalCD` in the CHEAPEST coordinate; the iso relates it to the others."
- The iterated-univariate coordinate MAY be the cheapest `evalCD` — it is RING-based (`Quotient-CommRing`), so
  DENOMINATOR-FREE by construction (lands in ℤ, no `_+ℚ_` / `den·den`), and reuses the substrate's committed graded
  Poly tower (`Polynomial/Graded/`) rather than building a fresh `GradedProduct`. SATURATION AGENT DISPATCHED
  (2026-07-22) to settle: does the iterated tower + a Horner eval EXIST as a ready reuse; is the iso in-tree; which
  coordinate gives the cheapest, most-reuse `evalCD`. MIRROR its verdict here when it lands.
- Record the graded axis in the Rosetta lattice (`jac_rosetta_stone.md` ## THE LATTICE) once the cheapest coordinate
  is settled — the axis is: F viewed as flat-MPoly / ℕ³-GradedProduct / iterated-ℤ[x][y][z] / total-degree, + the
  flat↔graded eval coordinate, all `quot()`s of F.

## ⚑ SATURATION VERDICT (agent af9c96ea, 2026-07-22) — the graded axis stands; the CHEAPEST coordinate is (b), NOT the iterated tower
The agent read the whole `Polynomial/Graded/` tower (`Graded`→`FromCommRing`→`Mod`→`Quotient`→`Div`/`PolyDivWedge`),
the `MPoly`/`evalℚ` baseline, `GradedProduct`, `ℤ-CommRing`. Findings (file:line-grounded):
- **Q1 — iterated tower: does NOT exist as reuse; a LARGE build.** `Quotient-CommRing : CommutativeRing (Poly (suc d))`
  (`Quotient.agda:160`, over ANY `CommutativeRing R`, monic `f`) IS type-possible to iterate 3× (`ℤ→ℤ[x]/(f)→…[y]→…[z]`)
  — BUT instantiated ONLY at F₂/GF(2⁸), never ℤ, never iterated. And **NO scalar evaluation exists**: `reduce`/`hsum`
  (`Mod.agda:86,164,290`) land in the quotient CARRIER `Poly (suc d)` and RECONSTRUCT the polynomial, they are NOT a
  Horner `Poly n → A → A`. `FromCommRing.Over` only UNPACKS a CommRing (does NOT produce `CommutativeRing (Poly n)` —
  the length-additive `_*P_` is why only the Quotient can iterate). ⚑ **CORRECTS my hypothesis:** the tower is
  denominator-free INTERNALLY (Poly reduction), but EVAL AT A ℚ POINT is not — a ℚ-Horner accumulator re-accretes
  `denx⁹·deny⁹·denz⁹` nested, reintroducing `_+ℚ_`/the blowup. Iterated = MOST new code (ℤ-tower + a nonexistent Horner
  eval + the iso) AND fails to remove denominators.
- **Q2 — the multivariate↔iterated iso `ℤ[x,y,z] ≅ ℤ[x][y][z]`: ABSENT.** No representation iso in-tree
  (`JacobianGradedSource` is the DETERMINANT's S₃/Leibniz grade-0 source, not a poly-rep iso). The Rosetta bridge
  between flat-MPoly and the iterated tower would be a NEW build.
- **Q3 — ranked: (b) ℕ-graded/common-denominator ≫ (a) flat baseline (730 MB) ≫ (c) iterated tower.** The
  common-denominator build kills the blowup exactly: grade tracks (multi)degree = the padding exponents `(9−a,9−b,9−c)`
  that lift every monomial onto ONE fixed `D = denx⁹·deny⁹·denz⁹` → **evalCD = Σ of ℤ numerators over one D, ℤ-add
  only, NO `_+ℚ_`, one `≈ℚ` lift at the very end.**
- **⚑ REUSE CAVEAT (sharpens ⟡jac-lit1-grade-shape):** `GradedProduct` (`Wedge/Product.agda:55-88`) is only the
  SCAFFOLD (`_∧_ : C i → C j → C (i+j)` = degree-tracking coefficient multiply) and is **single-ℕ-graded**; the
  multidegree padding wants ℕ³ (or total-degree-ℕ with per-variable bookkeeping). So `evalCD` is NEW code ON TOP OF
  `GradedProduct`, not a bare reuse. No coordinate ships a ready `evalCD`.

## REVISED BUILD (grade-shape decision SETTLED to coordinate (b); the fork inside it remains)
- **⟡jac-lit1-grade-shape → RESOLVED to coordinate (b)** (ℕ-graded common-denominator on the `GradedProduct` scaffold).
  The iterated tower is a REAL Rosetta coordinate of the axis but the WORST for `evalCD` — do NOT build it. The
  remaining sub-fork WITHIN (b): the grade is **ℕ³ multidegree** vs **total-degree ℕ with per-variable bookkeeping** —
  a genuine design point for `⟡jac-lit1-graded-C`, both on the ℤ-numerator/common-D scaffold.
- The Rosetta lattice gains the graded axis (flat-MPoly / ℕ-graded-GradedProduct / iterated-ℤ[x][y][z] / total-degree),
  with (b) the cheap-eval coordinate and the multivariate↔iterated iso a labeled (unbuilt) bridge — NOT on the critical
  path for `literal₁`.

---

# ⚑ TOWER SYNCHRONIZATION dissolves the ℕ³-vs-total-degree sub-fork (2026-07-22, user pointer)

## The insight — multivariate grade = NESTED BINARY tower synchronization
The ℕ³-vs-total-degree sub-fork inside coordinate (b) is ITSELF a false either/or. The user: "tower synchronization
sounds like the existing inductive/coinductive machinery combined with multiple Coxeter generators… under
bisimulation. If you want three, `(A × B) × C = bisim(bisim(A,B), C)`."
- The binary `GradedProduct._∧_ : C i → C j → C (i+j)` (`Product.agda:58`) IS the two-tower synchronization.
- For THREE variables you NEST the binary product: `(x-tower ⊗ y-tower) ⊗ z-tower` = `bisim(bisim(A,B),C)`.
- So the multidegree `(dx,dy,dz)` is the **nested pair `((dx,dy),dz)` that EMERGES** from binary synchronization —
  never a native ℕ³ record, never total-degree bookkeeping. The either/or → NEITHER: reuse the binary product, nested.
- Bisimulation `_~_` (`Bisim.agda:43`, `head~`/`tail~`) is the AGREEMENT relation under which two synchronized
  towers coincide head-by-head (lockstep) — the coinductive face; the inductive face is `GradedProduct`/the Coxeter
  `blockSum`/`OrientationProduct` bifunctor. Inductive ⊣ coinductive = the μ⊣ν pairing (`CofreeDual`).

## GROUNDING DISPATCHED (2 agents, synchronization-carrier level; MIRROR verdicts on return)
- Agent a96cfe16 (COINDUCTIVE): two-tower bisimulation SYNCHRONIZATION PRODUCT keeping grades as a PAIR, nesting
  binary `(A×B)×C = bisim(bisim(A,B),C)`?
- Agent a5f8dd04 (INDUCTIVE): `GradedProductOver` over a PRODUCT grade monoid (ℕ×ℕ; `BackedGradedStencil` precedent)
  + Coxeter `blockSum`/`OrientationProduct` bifunctor — combining two generators' towers keeps both grades, nests to ℕ³?
CENTRAL: is the ℕ³ multidegree the NESTED PAIR from binary synchronization (reuse), NOT a bespoke record?

## Consequence (pending grounding)
- ⟡jac-lit1-grade-shape → the sub-fork RESOLVES to "nested binary tower synchronization" (reuse the binary product,
  nested), NOT a native ℕ³ record and NOT total-degree bookkeeping. Each per-variable tower single-ℕ-graded
  (`C n = ℤ`, by that variable's degree); synchronize two → the pair; nest → the trivariate object; `D =
  denx^Dx·deny^Dy·denz^Dz` + the ℤ-numerator sum fall out of the nested grade.
- [[feedback_reuse_search_carrier_shape]] once more: the sub-fork was a false either/or; the tower already names
  the synchronization (binary product, nested) — reuse it, don't build ℕ³.

## ⚑ COINDUCTIVE VERDICT (agent a96cfe16, 2026-07-22) — the ℕ³ grade ALREADY EXISTS natively; the nested-bisim product does NOT
Decisive, and it surfaces a MISSED REUSE:
- **The coinductive two-tower synchronization product keeping grades as a PAIR does NOT exist.** `RealTrace` is the
  terminal coalgebra of the SINGLE-grade functor `S(X)=ℕ×X` (`Final.agda:52-60`, `ana`/`ana-unique` `Unfold.agda:39`/
  `Final.agda:98`). No `zip`/product coalgebra `(ℕ×ℕ)×X`. The pair-shaped constructs are something else: `Φ-pair-exact`
  (`ExtruderCoEmitGraded.agda:269-273`) is a bisimulation AGREEMENT over a pair that DEMANDS head-equality (a MERGE of
  two presentations of the SAME real, `νΦ-pair→bisim :352`); `qStep`/`quotient-coalg : Coalg (ℕ×ℕ)`
  (`RationalAdjunction.agda:61`, `NuShapeIso.agda:37`) use the pair as coalgebra STATE but emit a single-ℕ head. So
  `(A×B)×C = bisim(bisim(A,B),C)` keeping distinct grades is a BUILD, not a reuse — the coinductive layer is
  single-grade throughout. And `GradedProduct._∧_ : C i → C j → C(i+j)` SUMS grades (total degree — wrong tool).
- **⚑ THE MISSED REUSE — MPoly IS ALREADY A PROVEN ℕ³-GRADED SEMIRING.** `data Mono` / `mono : ℕ→ℕ→ℕ→Mono`
  (`JacobianResidue.agda:107-108`) is a NATIVE (dx,dy,dz) triple kept COMPONENTWISE, never summed: `addM (mono a b c)
  (mono d e f) = mono (a+d)(b+e)(c+f)` (`:116`), `eqM` ANDs the three (`:119`), `subM`/`geqM` componentwise
  (`MPolySemiring.agda:250,247`), per-variable `∂x/∂y/∂z` (`:153-160`). And `NormPoly-Semiring` PROVES it a Semiring
  (`MPolySemiring.agda:479-487`) with faithful `coeff : Mono → MPoly → ℤ` (`coeff-canonicity :333`). **This is the ℕ³
  multidegree the sub-fork was debating — already built, proven, and it is the very MPoly the Jacobian uses.**
- Bisimulation `_~_` (`Bisim.agda:43`, `Final.agda:21` "= EQUALITY in the final coalgebra") IS the agreement relation,
  but as a MERGE over ONE carrier — it coincides heads, does not carry a distinct grade-pair. The μ⊣ν pairing
  (`CofreeDual.agda:47-51`, `cata-uniqueness`/`cofree-uniqueness`) is real but SINGLE-grade (functor `ℕ×X`).

## ⚑ REFRAMED ⟡jac-lit1-graded-C (pending the inductive agent a5f8dd04)
The ℕ³-graded carrier ALREADY EXISTS as `Mono`/`NormPoly-Semiring` — I do NOT build a fresh `GradedProduct C n=ℤ`.
`evalCD` reuses the EXISTING MPoly ℕ³ monomials directly: for each term `mono a b c` with ℤ-coeff `k`, the padded
numerator is `k · nx^a·ny^b·nz^c · dx^(Dx−a)·dy^(Dy−b)·dz^(Dz−c)` (the `Mono` exponents (a,b,c) + max degrees Dx,Dy,Dz
GIVE the padding); sum in ℤ; `mkℚ (Σ) (D ∸ 1)` with `D = dx^Dx·dy^Dy·dz^Dz`. So the reuse-search-before-building
discipline fires: the ℕ³-graded structure the plan would reinvent is `Mono`/`NormPoly-Semiring` — name it, instantiate it.
⚑ HOLD for the inductive agent: whether `GradedProductOver` over a ℕ×ℕ product monoid (nested to ℕ³) is the ABSTRACT
home that `Mono` instantiates (the user's "tower synchronization" pointer) — which decides whether `evalCD` is built
directly over `Mono`'s exponents or routed through the abstract nested-product machinery.

## ⚑ INDUCTIVE VERDICT (agent a5f8dd04) + USER POINTER "grow it out of the witness tower (arbitrary-n Sₙ/Aₙ)" — SYNTHESIS
The nested-binary synchronization `(A×B)×C` IS realized in-tree — but on the **Coxeter-word / graded-MONOID** side,
which IS the witness-tower home the user points to; NOT the wedge `C:ℕ→Set` side, NOT the coinductive stream side.
- **Family A (wedge `C:ℕ→Set`): grade type HARDCODED to ℕ; every `_∧_` SUMS.** `GradedProductOver op ε C`
  (`OrientationBimonoidal.agda:34-37`): `op : ℕ→ℕ→ℕ`, `C : ℕ→Set` — the grade monoid `(op,ε)` is a param but its TYPE
  is fixed ℕ, so it CANNOT be instantiated at `ℕ×ℕ` (a one-line signature relaxation `{G:Set}(op:G→G→G)(ε:G)(C:G→Set)`
  = a BUILD). No two-family product `C i → D j → (C×D)(i,j)`. ⚑ FALSIFIED my precedents: `BackedGradedStencil`'s ℕ×ℕ
  (`:45-55`) is div-mod STATE pairs, not multidegree; `swap-grade : ℕ×ℕ` (`OrientationRig.agda:101`) is the OPERAND
  grade-pair (commutativity), not an output multidegree.
- **Family B (graded MONOIDS + degree hom / Coxeter WORDS): THE nesting witness, live and proven.**
  `direct-product` on `Strict2Monoid` (`Strict2Monoid/DirectProduct.agda:40-62`) — binary componentwise product,
  carrier `A₁×A₂`, `ε=(ε₁,ε₂)`, laws via `cong₂ _,_`, **iterates to n-monoids** (docstring :67-81: "nested
  direct-product gives strict 3,4,…,n-monoids; each layer adds one composition axis, all commuting componentwise").
  **`Z3-x-Z4-x-FreeCyclic.agda`** is the LIVE 3-axis instance: `Word3 = Word Z₃.Gen × Word Z₄.Gen × Word F.Gen`
  (`:43-44`, a NESTED PAIR), `_++3_` componentwise (`:57`), `++3-assoc` via nested `cong₂ _,_` (`:66-71`) — exactly
  `(A×B)×C` with coordinates kept separate; the FreeCyclic axis length is an ℕ-degree ⇒ three axes = a **ℕ³
  multidegree that IS the nested pair, no bespoke ℕ³ record**. `RGradedMonoid 𝓡 M` (`RGradedMonoid.agda:42`) over
  `R=ℕ×ℕ` admits the multidegree via a degree hom (`R` a genuine param). **This grows out of the tower's Coxeter/Sₙ
  machinery — precisely the user's "grown out of the witness tower, full generalized Sₙ/Aₙ to arbitrary n."**
- **Concrete ℕ³ ALSO already exists: `Mono`/`NormPoly-Semiring`** (coinductive agent) — the Jacobian's OWN MPoly, a
  proven Semiring with faithful `coeff`.

## THE SUB-FORK DISSOLVES BOTH WAYS (reuse-search-at-carrier-shape, once more)
"ℕ³ record vs total-degree bookkeeping" was a FALSE either/or. NEITHER horn:
- **For the mission / route-through-tower / ⟡pyrig-object-carrier:** the general n-variable multidegree tower is the
  **nested-binary Coxeter `direct-product`** (`DirectProduct` + `Z3-x-Z4-x-FreeCyclic`), grown from the tower's
  arbitrary-n Sₙ/Aₙ — the multidegree IS the nested pair, generalizes to any n. The coinductive `(ℕ³)×X` terminal
  coalgebra (the STREAMING multivariate tower) is a BUILD (both agents) — the user affirms it is grown from the
  tower's Sₙ/Aₙ; a mission arc, NOT the literal₁ path.
- **For the immediate cheap `literal₁` evalCD:** R.f₁ ALREADY is an MPoly of `Mono` terms. `evalCD` walks its
  EXISTING `Mono` terms — for each `mono a b c` (ℤ-coeff k), padded numerator `= k · nx^a·ny^b·nz^c ·
  dx^(Dx−a)·dy^(Dy−b)·dz^(Dz−c)`; the `Mono` EXPONENTS (a,b,c) + max degrees (Dx,Dy,Dz) GIVE the padding; sum in ℤ;
  `mkℚ (Σ) (dx^Dx·dy^Dy·dz^Dz ∸ 1)`. **NO new carrier** — reuse `Mono`'s exponents. Cheapest, and the exponents are
  the polynomial's own, so it does not "advance the bespoke MPoly" — it reads what is already there.

## REVISED ⟡jac-lit1-graded-C (FINAL grade-shape resolution)
- IMMEDIATE literal₁: **reuse `Mono` directly** (walk R.f₁'s terms; exponents → common-denominator padding; ℤ-sum;
  one ℚ-lift). No `GradedProduct C n=ℤ` build — the ℕ³ grade is the polynomial's own `Mono`.
- MISSION (separate, larger; advances ⟡jac-det-via-sppf + ⟡pyrig-object-carrier): the tower-grown nested-binary
  multidegree tower (`direct-product` of Coxeter/graded-monoid axes, generalizing to arbitrary n via Sₙ/Aₙ), and the
  coinductive `(ℕⁿ)×X` streaming generalization the user names. A route-through-tower arc, not the literal₁ critical path.

## ⚑⚑ CORRECTION (user 2026-07-22): "isn't the current MPoly what we're fixing the explosion for?" — the Mono-reuse was the shortcut
- **Mechanism, precise:** the explosion is `evalℚ`'s `_+ℚ_` (`den = b·d` cross-multiply, `+ℚ-cong`'s degree-~34 ℤ
  product), NOT `Mono`/MPoly the data. `Mono` (ℤ coeff + ℕ³ exponent) is a cheap finite term-list; evalCD reading its
  exponents but folding with `_+ℤ_` over ONE fixed `D` does NOT mechanically reinherit the explosion.
- **BUT mission-wise the user is RIGHT:** anchoring the fix to `Mono` COUPLES literal₁ to the bespoke MPoly that
  `⟡jac-det-via-sppf` exists to RETIRE (MPoly = bespoke rebuild of the free semiring / graded Poly). "Reuse Mono,
  cheapest" = the flat-List-fold shortcut again — doubles down on the structure the arc routes AWAY from. Same
  cheapest-over-mission-pure miss.
- **DISSOLUTION (the recursive collapse):** build evalCD as a `GradedHomOver` OUT OF the TOWER-NATIVE graded carrier
  (the free commutative semiring on {x,y,z} over ℤ = the SPPF `inside` / the nested graded-monoid multidegree), NOT
  over `Mono`. ONE hom does BOTH: (a) fixes the explosion (common denominator, ℤ-numerator sum, one `≈ℚ` lift — the
  `GradedHomOver` over `≈ℚ` = the parameterized-equality generator); (b) RETIRES MPoly (R.f₁-in-tower-carrier IS the
  `⟡jac-det-via-sppf` migration — negation discharged, `JacobianGradedSource` lands grade-0). So `⟡jac-lit1-commonden`
  ≡ `⟡jac-det-via-sppf` — one construction: graded polynomial in the tower carrier + evalCD the common-denominator
  hom out of it. Mission-pure; the explosion fix and the MPoly retirement are the SAME graded evaluation.
- **DISCARD the "reuse `Mono` directly" line in ⟡jac-lit1-graded-C** (it entrenches the bespoke). Re-scope: the
  polynomial lives in the tower carrier; evalCD is the hom out of it. Larger (needs R.f₁ bridged into the carrier),
  but where the arc points and does not build on what we retire.

---

# ⚑ SATURATION IN FLIGHT (2026-07-22, 3 read-only agents) — MIRROR each verdict under its heading when it lands
Dispatched to make the unified graded-evalCD arc compaction-safe. All READ-ONLY (standing policy). If a compaction
hits before they return, RE-DISPATCH from these self-contained briefs (do NOT read the agent .output raw — full JSONL):
- **Agent a02b68dc → ⟡jac-lit1-scope-bridge (feasibility).** How far `JacobianGradedSource` gets R.f₁ into the
  free-semiring/graded carrier (grade-0 vs full); the SPPF `inside`/`inside-unique` + `ℤ-semiring` interface; ⚑ the
  NEGATION status AT the carrier (SPPF is a free SEMIRING, no ⊖; det has negatives — is `ℤ-CommRing`/`FromCommRing.neg`
  discharge AT the carrier?); does the common-denominator hom land over a ℤ-ADDITIVE `≈ℚ` target (not `_+ℚ_`)?
  VERDICT: BOUNDED next arc vs MULTI-STEP migration + the exact remaining pieces.
- **Agent a8bff55c → ⟡jac-lit1-tower-carrier (the carrier + bridge).** Which carrier — (A) SPPF free semiring, (B)
  nested graded-monoid multidegree (`direct-product` + `Z3-x-Z4-x-FreeCyclic` + `RGradedMonoid` over ℕ×ℕ×ℕ), or (C)
  ℤ-CommRing graded `Poly` — is cheapest for R.f₁ that (i) tracks multidegree (dx,dy,dz), (ii) carries NEGATIVE ℤ
  coeffs, (iii) admits a common-denominator hom to ℚ; + the exact `MPoly R.f₁ → carrier` bridge + the NEGATION route
  (ℤ-CommRing / Grothendieck ℕ×ℕ `DualRail` / ExpLog codec).
- **Agent a0296daa → ⟡jac-lit1-commonden ≡ ⟡jac-det-via-sppf (evalCD + soundness).** Turn-key type+body of `evalCD`
  = `GradedHomOver` over `≈ℚ` (target equality PARAMETER, `OrientationBimonoidal.agda:65-73`) computing Σ padded ℤ
  numerators over one `D` → `mkℚ`; `evalCD-sound : evalℚ p ≈ℚ evalCD p` via `fold-unique-over`
  (`OrientationUniversal.agda:84-98`) hom-uniqueness over `≈ℚ` (abstract/anti-explosion, mirroring `normalize-eval`/
  `evalℚ-++`); the 2nd-leg single-ℤ cross-equation `evalCD R.f₁ ≈ℚ C.f₁`.

## ⚑⚑ SCOPE-BRIDGE VERDICT (agent a02b68dc, 2026-07-22) — BOUNDED; the migration is ALREADY DONE; ⟡jac-det-via-sppf is STALE; evalCD is a FOLD not a hom
DECISIVE, and it CORRECTS my own last-turn correction (I over-corrected away from Mono/NormPoly onto SPPF, built on
a stale hypothesis — a plan-notes-are-hypotheses miss):
- **The tower-native carrier ALREADY EXISTS, proven, and IS `Mono`/`NormPoly` — NOT SPPF, NOT a thing to retire.**
  `NormPoly-Semiring : Semiring NormPoly` (`MPolySemiring.agda:479-487`) — a FULL proven Semiring over the exact
  `Mono`/`MPoly`/`coeff`/`*P` (`NormPoly = Σ MPoly (isSortedB ≡ tt)` :81). `Mono = ℕ³` is PROVEN the free commutative
  monoid on {x,y,z} (`MonoCommMonoid.agda`), so **`MPoly = ℤ[ℕ³] = ℤ[x,y,z]` = the free comm-semiring on {x,y,z}/ℤ**.
  This IS the tower-native multidegree carrier the arc was reaching for — `Mono` was NEVER "the bespoke thing to
  retire"; it is the proven ℤ[x,y,z].
- **The det migration is DONE + proven natively over it.** `JacobianDetNative.agda`: `detNative = det{3} JacMat` via
  `WitnessTower.LeibnizDet.Det.WithSign` over `NormPoly-Semiring` (`:27-54`), with `detNative-normal : proj₁ detNative
  ≡ normalize detJac` = **refl** (`:62`) and `det-native-correct : coeffN j detNative ≡ coeff j detJac` (`:65-67`).
  `.agdai` cores exist, git-tracked, clean.
- **Negation is REPRESENTED (in the ℤ coefficients), discharged 3 ways over — NOT a blocker.** `ε₂ = normalize
  (kP (-suc 0))` + `ε₂-sq : ε₂⊗ε₂ ≡ 1P` (`MPolySemiring.agda:493-502`); `−k·xᵃyᵇzᶜ = term (mono a b c)(-suc …)`
  (native, e.g. `f₃` carries `kP(-suc 2)`). The "SPPF has no ⊖" concern applies ONLY to the SPPF `inside` route —
  **which the substrate routed AROUND entirely** (built NormPoly-Semiring instead). ⟡jac-det-via-sppf's SPPF-target
  + the `JacobianResidue.agda:39-55` header ("MPoly re-rolls SPPF … needs the negation story first") are **STALE**.
- **⚑ evalCD is a FOLD over NormPoly, NOT a semiring-hom / `inside` / `GradedHomOver`-on-⊗** — because the
  pad-to-common-D map is NOT multiplicative (`pad(xᵃ·xᵇ)` and `pad(xᵃ)·pad(xᵇ)` differ in the denominator exponent).
  It IS additive (Σ of per-term numerators). So: fix `D = dx^Ax·dy^Ay·dz^Az` from the degree box (x≤9,y≤12,z≤3,
  `JacobianResidue.agda:30-31`); map each `(mono a b c, k)` → ℤ numerator `k·nxᵃnyᵇnzᶜ·dx^(Ax−a)·dy^(Ay−b)·dz^(Az−c)`;
  SUM in ℤ (`_+ℤ_`, no `_+ℚ_`); emit `mkℚ (Σ)(D−1)`. Correctness `evalCD p ≈ℚ evalℚ p` over `≈ℚ` (cross-mult equality,
  `Equiv.agda:37`) REUSES the already-built pinned additive-chain machinery of `JacobianEvalNormalize`
  (`insertT-eval:120`, `normalize-eval:166`, `coeff-combine:88` — distribʳ/+ℚ-assoc/+ℚ-cong pinned).
- **VERDICT: BOUNDED.** The heavy migration (bespoke→tower Semiring, det, negation) is COMPLETE. Remaining, all small:
  (1) R.fᵢ into the carrier = trivial `mkN f₁ = (normalize f₁, normalize-sorted f₁) : NormPoly` (~3 lines; `mkN`
  exists at `JacobianDetNative.agda:31`); (2) **`evalCD` + `evalCD p ≈ℚ evalℚ p`** — the ONE genuine arc (per-Mono
  ℤ-numerator padding via `powℤ`, ℤ-Σ fold over sorted NormPoly, one `mkℚ`, the `≈ℚ` proof reusing
  JacobianEvalNormalize's pinned chains; one module, moderate weight ~200 lines); (3) NOT NEEDED: SPPF `inside`, any
  new negation story, `Semiring MPoly` (it's `NormPoly-Semiring`, done).

## ⚑ CONSEQUENT RE-SCOPE (pending agents a8bff55c + a0296daa)
- **⟡jac-lit1-tower-carrier → essentially DONE:** the carrier is `NormPoly` (proven ℤ[x,y,z]); `mkN f₁` bridges R.f₁ in.
- **⟡jac-det-via-sppf → RETIRE/REDIRECT** (stale): the migration was via `NormPoly-Semiring`+`JacobianDetNative`, not
  SPPF. Redirect the debt name to "R.fᵢ as NormPoly + coeff-preservation" (trivial) — the SPPF interface is NOT the home.
- **⟡jac-lit1-commonden → THE one genuine arc, and it is a FOLD over NormPoly (not a `GradedHomOver` on ⊗).** ⚑ Reconcile
  with agent a0296daa (framed on `GradedHomOver`/`fold-unique-over`): evalCD is additive-monoid-hom-shaped (⊕↦+ℤ) — a
  graded fold over the term list — but NOT a ⊗-semiring-hom; the soundness likely reuses `JacobianEvalNormalize`'s
  concrete pinned `≈ℚ` chains rather than the abstract `fold-unique-over`. Settle when a0296daa lands.
- ⚑ HONEST CORRECTION to my last turn: "reuse Mono entrenches the bespoke MPoly (⟡jac-det-via-sppf)" was built on the
  STALE premise. Mono/NormPoly IS the proven tower carrier; the user's original "reuse Mono" instinct was right; evalCD
  folds over it. The explosion fix (evalCD, ℤ-additive) and the "retirement" are not even coupled — there's nothing to
  retire; NormPoly-Semiring already made MPoly the tower carrier.

## ⚑ TOWER-CARRIER VERDICT (agent a8bff55c) — CONFIRMS scope-bridge; carrier = `NormPoly = ℤ[Mono] = ℤ[x,y,z]`, DONE
- **Carrier ★ = `NormPoly`** (`MPolySemiring.agda:81` `NormPoly = Σ MPoly (isSortedB ≡ tt)`; `NormPoly-Semiring :
  Semiring NormPoly` `:479-487`) — the SYNTHESIS of candidate B (`Mono-CommMonoid` = free comm monoid on {x,y,z},
  `MonoCommMonoid.agda:66-72`) with ℤ coefficients. Multidegree ✓ (per-term `Mono` triple); negative ℤ ✓ (`term Mono ℤ`,
  `-suc n` values, no ⊖ needed). Candidate table: SPPF = subsumed (evaluation mechanism, no grade, no ⊖; its role is
  filled by `Expr`+`encode`+`homAgree`); nested-graded-monoid = the base `Mono-CommMonoid` (half the answer); graded
  `Poly`-Vec = worst (iterated tower). **NormPoly = cheapest, already built+proven+wired.**
- **Bridge:** `mkN R.f₁ = (normalize f₁ , normalize-sorted f₁) : NormPoly` (`JacobianDetNative.agda:31`, trivial).
  Generators X/Y/Z/`kP k` at `JacobianResidue.agda:169-176`; multidegree→ℚ read-off `monoval (mono a b c) = powℚ x a
  *ℚ powℚ y b *ℚ powℚ z c` (`JacobianEvalNormalize.agda:64`).
- **Negation = Route C (semiring gauge), NOT a ring on NormPoly:** the S₃ sign is `ε₂ = normalize (kP (-suc 0))` +
  `ε₂-sq : ε₂⊗ε₂ ≡ 1P` (`MPolySemiring.agda:493-502`), consumed by `Det.WithSign … ε₂ ε₂-sq` (`JacobianDetNative:28`).
  Route A (`ℤ-Ring`/`FromCommRing.neg`) needed ONLY if a `Ring NormPoly` / carrier-subtraction is ever wanted — the
  det/collision arc does NOT need it.

## ⚑ RECONCILIATION (scope-bridge a02b68dc ⟷ tower-carrier a8bff55c) — the "ℚ hom" the carrier-agent cites is the EXPLODING one
- Both agree: **carrier DONE (NormPoly); ⟡jac-det-via-sppf STALE; the ONE genuine remaining arc is the CHEAP `evalCD`.**
- ⚑ The tower-carrier agent's "common-denominator hom out to ℚ — EXISTS" is a MISLABEL: what exists is `β.evalℚ`
  (`JacobianEvalNormalize.agda:68-72`) — the EXISTING evaluator that BLOWS UP (`_+ℚ_` cross-multiply, 729 MB), a proven
  SEMIRING HOM (`evalℚ-*P : E(p*P q) ≋ E p *ℚ E q`, `JacobianEncodingHom.agda:174`; `homAgree` with the `⊖E` case
  `:223`). `literal₁` ALREADY CLOSES through it (`JacobianLiteral1.agda:76`, AES-Full `Assemble`, 729 MB). So the point
  of evalCD is NOT to make literal₁ possible (it is) but to make it CHEAP.
- **Why evalCD is a FOLD not a hom (both agents' finding, reconciled):** `β.evalℚ` is a semiring hom BECAUSE it's
  multiplicative — which is exactly why it explodes (`_+ℚ_` per term). `evalCD` SACRIFICES the ⊗-hom property (the
  pad-to-common-D map is NOT multiplicative) to get ℤ-ADDITIVITY (Σ padded numerators over one `D`, one `mkℚ`) → cheap.
  evalCD is additive-monoid-hom-shaped (⊕↦+ℤ) but NOT a ⊗-semiring-hom. `evalCD-sound : evalℚ p ≈ℚ evalCD p` relates the
  two, reusing `JacobianEvalNormalize`'s pinned `≈ℚ` chains (`insertT-eval:120`/`normalize-eval:166`/`coeff-combine:88`).

## ⚑ NEW cheap AI: ⟡jac-stale-prose-and-index (both agents flagged)
- `JacobianResidue.agda:39-55` header still says the migration is unbuilt/undecided ("MPoly re-rolls SPPF … needs the
  negation story first") — STALE; commits `dcf9c73`(RUNG 3b)/`5a71c14`(RUNG 3c) discharged it via `NormPoly-Semiring`+
  `JacobianDetNative`. Update the header to point there.
- `catalog/reuse-index.md` MISSING `NormPoly`/`NormPoly-Semiring`/`Mono-CommMonoid`/`detNative` — regenerate
  (`scripts/gen_reuse_index.py`) so the next reuse-check surfaces the built carrier instead of re-triggering this recon.
- Comment-only + a regen; ~1 cheap gated commit. (Ⓟ discoverability — an unfindable-but-built structure owes a fix.)

## ⚑⚑ evalCD SPEC (agent a0296daa) — TURN-KEY; reconciles fold-vs-hom; the ONE structural gap is a 3-line list-uniqueness
FULL presence audit PASSED: `GradedHomOver` 3rd param = target equality ✓ (`OrientationBimonoidal.agda:65-73`); `_≈ℚ_`
✓ (`Equiv.agda:37`); `mkℚ`/`num`/`den-1` ✓ (`Q.agda:32-38`); `_+ℤ_`/`_*ℤ_`/`-ℤ_` ✓; **`evalℚ-++` (the +-hom) ALREADY
PROVEN** (`JacobianEncodingHom.agda:152-161`). TWO not-founds (facts about the substrate): (a) NO List/free-monoid
fold-uniqueness lemma — `fold-unique-over` is over `LehmerPath`, NOT `List` (governs the design); (b) NO `powℤ`/`_⊔_`
on ℕ (2 trivial helpers).

### (i) evalCD — turn-key body (at the concrete ℚ point x y z; degree box Dx,Dy,Dz = 9,12,3 per `JacobianResidue.agda:210`)
```agda
powℤ : ℤ → ℕ → ℤ ;  powℤ b zero = + 1 ;  powℤ b (suc n) = b *ℤ powℤ b n
maxℕ : ℕ → ℕ → ℕ  (3 clauses; Foundation.Nat has no _⊔_)
module _ (x y z : ℚ) (Dx Dy Dz : ℕ) where
  qx = + suc (den-1 x); px = num x   (qy,py,qz,pz likewise)
  D  = suc (den-1 x) ^ Dx * (suc (den-1 y) ^ Dy * suc (den-1 z) ^ Dz)          -- the ONE fixed denom
  padNum (term (mono a b c) k) = k *ℤ (powℤ px a *ℤ powℤ py b *ℤ powℤ pz c)
                                   *ℤ (powℤ qx (Dx ∸ a) *ℤ powℤ qy (Dy ∸ b) *ℤ powℤ qz (Dz ∸ c))
  sumNum [] = 0ℤ ;  sumNum (t ∷ p) = padNum t +ℤ sumNum p                       -- ℤ-fold, NO _+ℚ_
  evalCD p = mkℚ (sumNum p) (D ∸ 1)                                            -- ONE mkℚ
```
EXACT not truncating (`Dx∸a ≥ 0`); `D` bounded (≈4⁹·2¹²·2³), never the 204-fold product.

### (ii) evalCD-sound : evalℚ p ≈ℚ evalCD p — hom-uniqueness over ≈ℚ, abstract p (anti-explosion)
Both evalℚ, evalCD are +-homs out of `(MPoly, ++, [])`: evalℚ's = `evalℚ-++` (proven); evalCD's = fixed-D additivity
`mkℚ (a+ℤb)(D∸1) ≈ℚ mkℚ a (D∸1) +ℚ mkℚ b (D∸1)` (one ℤ identity, both sides `(a+b)·D²`, no b·d blowup) + `sumNum(p++q)
≡ sumNum p +ℤ sumNum q` (1-line list induction). Generator obligation `gen-sound : (m)(k) → evalℚ (term m k ∷ []) ≈ℚ
evalCD (term m k ∷ [])` = ONE cross-mult per monomial (bounded). Uniqueness recursion = the `normalize-eval`/
`insertT-eval` body (`JacobianEvalNormalize.agda:120-177`): list induction chaining `≈ℚ-trans`+`+ℚ-cong` over ABSTRACT
subterms (congruences STUCK-NEUTRAL → nothing distributes) — exactly `fold-unique-over`'s obligations (≈-trans +
step-cong, no refl/sym). Concrete instantiation at R.f₁ via the `JacobianLiteral1.Assemble` stuck-neutral `open`
(`:51-76`) → Agda NEVER normalizes the 204-term fold (same reason `evalBridge₁ = normalize-eval f₁` typechecks).

### (iii) GradedHomOver-over-≈ℚ — PACKAGES it, but DECORATIVE for the proof (the honest gap)
`evalℚ-Hom : GradedHomOver Poly-Prod Q+-Prod (λ {n} → _≈ℚ_)` (source = free poly monoid `(MPoly,++,[])` graded by
length; target = `(ℚ,+ℚ,0ℚ)`; `map-∧ = evalℚ-++` ALREADY PROVEN; `map-u = ≈ℚ-refl 0ℚ`). ✓ the `≈ℚ` target instantiates
cleanly (`Cᴽ n := ℚ`). ⚑ BUT there is NO list-level `hom-unique-over` (`fold-unique-over` is LehmerPath-only), so the
record PACKAGES the two homs but does NOT discharge soundness. **THE ONE STRUCTURAL GAP:** add a 3-line
`list-hom-unique-over` (same 2 hypotheses as `fold-unique-over:87,89`, induction on the List — the shape already
inlined in `normalize-eval`/`evalℚ-++`), OR prove evalCD-sound by direct list induction and cite GradedHomOver as the
identified pattern. **The load-bearing anti-explosion is the direct list induction + the `Assemble` open — NOT the
record.** (This reconciles: evalCD IS an additive +-hom [⊕↦+ℚ over fixed D]; it is NOT a ⊗-semiring-hom [padding
non-multiplicative]; GradedHomOver frames the additive side; the proof is list-induction, not the LehmerPath fold-unique.)

### (iv) 2nd leg evalCD-leg₂ : evalCD R.f₁ ≈ℚ C.f₁ x y z — a single ℤ identity, `refl`
`_≈ℚ_` unfolds (`Equiv.agda:38`) to `sumNum R.f₁ *ℤ (+ suc M) ≡ N *ℤ (+ D)` where `C.f₁ x y z = mkℚ N M`
(`JacobianCollision.agda:72-77`, values already `refl` `:91-98`). Both sides closed concrete ℤ, no `_+ℚ_` fold →
`refl`. Full: `evalℚ R.f₁ ≈ℚ⟨evalCD-sound⟩ evalCD R.f₁ ≈ℚ⟨evalCD-leg₂⟩ C.f₁` — neither step forces the exploding evalℚ.

## ⚑ FULL SATURATION SYNTHESIS (3 agents, 2026-07-22) — the arc is BOUNDED + turn-key
- **⟡jac-lit1-scope-bridge → DONE (verdict BOUNDED).** The heavy migration (bespoke MPoly → tower Semiring, det,
  negation) is ALREADY COMPLETE + proven (`NormPoly-Semiring` + `JacobianDetNative`). ⟡jac-det-via-sppf is STALE.
- **⟡jac-lit1-tower-carrier → DONE.** Carrier = `NormPoly = ℤ[Mono] = ℤ[x,y,z]` (proven Semiring, free comm-monoid
  base); R.fᵢ bridges via `mkN`. Negation = Route C (ε₂ sign, semiring-internal). But NOTE: `evalCD` walks the raw
  `MPoly`/`Term` list directly (`padNum`/`sumNum`) — it does NOT even need `NormPoly`'s sortedness; the carrier work is
  a non-blocker for evalCD.
- **⟡jac-lit1-commonden → THE one genuine arc, fully specced.** Build: `powℤ`+`maxℕ` (2 helpers) · `padNum`/`sumNum`/
  `evalCD` (§i) · `gen-sound` (per-monomial) · `evalCD-sound` (list induction + Assemble anti-explosion, §ii) ·
  `list-hom-unique-over` OR direct induction (§iii, the 3-line gap) · `evalCD-leg₂` = refl (§iv). One module, moderate
  weight (~200 lines, mirrors `JacobianEvalNormalize`). MEASURE.
- **⟡jac-lit1-numerator → re-prove `literal₁` via `evalCD-sound`+`evalCD-leg₂`; keep Assemble; MEASURE (~90-150MB).**
- **⟡jac-stale-prose-and-index → cheap:** update `JacobianResidue.agda:39-55` header + regen `catalog/reuse-index.md`.

## ⚑⚑⚑ USER CORRECTION (2026-07-22) — the agents COLLAPSED "build-all-and-cover" → "pick-the-cheapest"; that IS the cleaver, and it's the RECURRING theme
Two corrections, one root:
1. **"The point is to do the cheapest thing" — NO. "The point is to do THEM ALL and unify/compare them."** The
   deliverable is evalCD in EACH carrier (SPPF free semiring / nested graded-monoid / graded Poly-Vec / NormPoly) + a
   COVERING CONSTRUCTION showing they compute R.f₁ to the same ℚ (up to ≈ℚ). This IS the established mission pattern —
   `⟡jac-neg-three-routes + ⟡jac-neg-cover` ("because you raised all three routes exist, I'll ask for all three + a
   covering construction — that's good mathematics and crosslinking within the repo"). The agents' "★ NormPoly =
   cheapest, others subsumed" table is the **collapse-to-smallest / cleaver** move the whole mission fights
   ([[dont-collapse-to-smallest-representable]], [[never-discard-residue]], the wedge not the cleaver).
2. **"⟡jac-det-via-sppf is stale" is an OVERCLAIM — the agent MISUNDERSTOOD the motivation.** The det IDENTITY is
   proven via `NormPoly-Semiring`+`JacobianDetNative` (TRUE — keep that fact). But the SPPF route's MOTIVATION is
   INDEPENDENT and stands: the free semiring `inside`/`inside-unique`, the EXTRUDER's guaranteed-minimal output
   (LehmerPath canonical → syntactic monomial identity → kills the `coeff` scan), commutativity-as-the-Sₙ-orbit
   (group-theoretic normalization), discoverability + crosslinking. NormPoly is the monomial-algebra realization; it
   does NOT provide the extruder/orbit-normalization benefits. So the SPPF route is ONE coordinate of the cover, NOT
   dead. RETRACT "stale"; it's the SPPF-route evalCD.
- **⚑ THE RECURRING META-PATTERN (user, load-bearing):** "the research agents decided against the underlying
  motivations." They collapse all-and-cover → cheapest, and declare a route stale when a SIBLING realization exists.
  ROOT: **I framed the prompts as "which is CHEAPEST"** (agent-B prompt verbatim) — the cleaver at the framing level —
  so the agents faithfully collapsed. Same class as last turn's "reuse Mono is cheapest" that the user corrected. The
  reuse-search must be framed as **build-all-and-cover / keep the residue**, NEVER pick-the-smallest / is-X-stale.

## ⚑ WHAT STANDS vs WHAT IS RETRACTED
- STANDS (genuine facts): `NormPoly-Semiring` exists + proves the det migration; `JacobianDetNative`; the NormPoly-route
  `evalCD` turn-key spec (agent a0296daa, §i-iv above) — it is ONE route, and the cheapest, so it lands literal₁ under
  the cap FIRST. The `evalℚ` explosion is `_+ℚ_`. `≈ℚ` is the cross-mult equality. `evalℚ-++` is proven.
- RETRACTED (the collapse-conclusions): "pick the cheapest carrier / NormPoly is THE carrier, others subsumed";
  "⟡jac-det-via-sppf is stale"; the "ℕ³-vs-total-degree" and "which carrier" framings AS pick-one forks. All are
  coordinates of ONE object (R.f₁'s evaluation); the point is the COVER.

## RE-SCOPED AIs (build-all-and-cover)
- **⟡jac-lit1-commonden** = evalCD in EACH carrier + the cover, NOT "one cheap evalCD":
  - **⟡jac-lit1-cd-normpoly** — the NormPoly/MPoly fold (agent a0296daa's turn-key spec, §i-iv). Cheapest → do FIRST
    (lands literal₁ under the cap).
  - **⟡jac-lit1-cd-sppf** (≡ the LIVE ⟡jac-det-via-sppf, motivation intact) — evalCD via the SPPF free-semiring
    `inside` fold; the extruder minimal-output / orbit-normalization route.
  - **⟡jac-lit1-cd-gradedpoly** — evalCD via the graded `Poly`-Vec / iterated `Quotient-CommRing` route.
  - **⟡jac-lit1-cd-gradedmonoid** — evalCD via the nested graded-monoid `direct-product` multidegree route.
  - **⟡jac-lit1-cd-cover** — the COVERING CONSTRUCTION: all routes evaluate R.f₁ to the same ℚ (≈ℚ); the crosslink /
    "good mathematics" (mirror `⟡jac-neg-cover`'s apex-once-derive-through form; keep the per-route residues graded).
- **⟡jac-det-via-sppf → NOT retired; = ⟡jac-lit1-cd-sppf** (one coordinate; motivation stands).
- **⟡jac-lit1-numerator** — re-prove literal₁ via the CHEAPEST route (`⟡jac-lit1-cd-normpoly`)'s evalCD-sound first;
  MEASURE. The cover is crosslinking value, not on the cap-critical path.
- **⟡jac-stale-prose-and-index** — the `JacobianResidue.agda:39-55` header IS stale about the *det identity* (that's
  proven via NormPoly) but keep the SPPF-route motivation; update to "det proven via NormPoly; SPPF route = the
  extruder/orbit crosslink, still owed." Regen reuse-index.

## G9 (widen the memory): ⟡memory-frame-reuse-search-build-all-not-cheapest
The reuse-search — own AND delegated — must be framed **build-all-routes-and-cover / keep the residue graded**, NEVER
"which is cheapest / is X stale." A prompt asking "which is cheapest" makes the agent collapse all-and-cover → pick-one
(the cleaver) and declare live motivations stale. Widens [[⟡memory-frame-agent-reuse-search-graded]],
[[⟡memory-cheapest-reuse-can-entrench-bespoke]], [[dont-collapse-to-smallest-representable]], [[never-discard-residue]].

---

# ⚑ PER-ROUTE SATURATION IN FLIGHT (2026-07-22, 4 read-only agents) — build-all-and-cover, MIRROR each under its heading
The NormPoly route is already turn-key (agent a0296daa, §i-iv above). These saturate the remaining route-coordinates +
the cover, motivation-intact (NOT cheapest/stale). RE-DISPATCH from these briefs after a compaction (do NOT read the
.output raw):
- **Agent a3e0aeb → ⟡jac-lit1-cd-sppf (≡ live ⟡jac-det-via-sppf, motivation INTACT).** The R.f₁→SPPF bridge; NEGATION
  via the log/antilog codec (`ExpLogCodec`/`ℤ-power-codec`, sign = S₃ character) OR Grothendieck ℕ×ℕ OR target-ℤ; the
  EXTRUDER minimal-output + Coxeter/`ListPresentation` orbit-normalization (syntactic monomial identity, kills the
  `coeff` scan); what the route delivers toward the common-denominator ℚ + its cover slot.
- **Agent aba48a0f → ⟡jac-lit1-cd-gradedpoly (ring gauge).** R.f₁→iterated `Poly(Poly(Poly ℤ))` via
  `Quotient-CommRing` over `ℤ-CommRing`; the common-denominator HORNER over ℤ (pad `denᵥ^(Dᵥ−k)` per level, avoid
  ℚ-denominator accretion); NEGATION-in-the-carrier via `FromCommRing.neg`; `≈ℚ` soundness; cover slot.
- **Agent a367eb91 → ⟡jac-lit1-cd-gradedmonoid.** Nested-binary multidegree (`direct-product`/`Word3`/`RGradedMonoid`
  over ℕ³) + its ISO to flat `Mono`/`Mono-CommMonoid`; the monoid-algebra coefficient side (`ℤ[Mono]` = NormPoly — is
  this route the ABSTRACT form of NormPoly, and is that convergence a cover-crosslink?); degree-hom common-denominator
  fold; `≈ℚ` soundness; cover slot.
- **Agent a77e3bec → ⟡jac-lit1-cd-cover.** The cover APEX (one record/`GradedHomOver`-over-`≈ℚ` all routes instantiate),
  per-route DERIVE-THROUGH (mirror `⟡jac-neg-cover`/`PeriodicCover` — apex-once, not pairwise restatement), NON-VACUITY
  discrimination witness (not trivial-refl), and whether agreement is hom-uniqueness-over-`≈ℚ` (the 3-line
  `list-hom-unique-over`) or direct per-route `≈ℚ` chains. Keep per-route residues graded.

## ⚑ ⟡jac-lit1-cd-gradedmonoid VERDICT (agent a367eb91) — carrier machinery EXISTS; the route's deliverable is the ABSTRACT MonoidAlgebra + the NormPoly crosslink (~80% build)
EXISTS: `direct-product` (binary componentwise Strict2Monoid product, iterates to n-monoids, `DirectProduct.agda:40-81`);
`Word3` live 3-axis nested pair (`Z3-x-Z4-x-FreeCyclic.agda:57-83`, ⚑ right-nested `Word×(Word×Word)`, components are
Coxeter WORDS not ℕ — one abelianization hom from an exponent vector); `RGradedMonoid 𝓡 M` with `degree : M → R`
(`RGradedMonoid.agda:42-55`, template `FromCoxeterHomomorphism.agda:57`); `Mono-CommMonoid : CommutativeMonoid Mono
addM (mono 0 0 0)` — `Mono = ℕ³` PROVEN free comm monoid on {x,y,z} (`MonoCommMonoid.agda:66-72`). The `Dᵥ−dᵥ`
padding-exponent already exists as `subM`/`geqM` + `coeff-scaleT-full` (`MPolySemiring.agda:247-294`) — but bespoke,
not as `RGradedMonoid.degree`.
BUILDS (the route's genuine content): (i) `((ℕ×ℕ)×ℕ) ≅ Mono` nested↔flat iso — trivial (both free comm-monoid on 3
gens) but NO term; ⚑ no `CommutativeMonoid ℕ`/ℕ-additive Strict2Monoid exists, so `(ℕ×ℕ)×ℕ` needs ℕ-as-monoid first;
(ii) **the abstract `MonoidAlgebra : Semiring K → CommutativeMonoid M → Semiring (K[M])` functor — ABSENT** (grep
zero); NormPoly is the concrete `ℤ[Mono]` built DIRECTLY (`MPolySemiring.agda:81,479`, named `ℤ[Mono]` in its header +
`MonoCommMonoid.agda:13-27`), NOT an instance of any abstract functor; (iii) the CD fold `evalCD` — ABSENT (grep zero);
(iv) its `≈ℚ` soundness — a FRESH cross-mult induction, NOT implied by `normalize-eval` (all ℤ lemmas exist, unwritten).
⚑ **RGradedMonoid-over-Mono is DEGENERATE** (multiplicative monomial monoid = `Mono-CommMonoid` again ⇒ `degree = id`) —
a thin use of the machinery.
**COVER SLOT (the route's reason to exist, NOT cheapest/worst):** construct `MonoidAlgebra ℤ Mono-CommMonoid ≅
NormPoly-Semiring` — retroactively NAMING the hand-built NormPoly as the concrete realization of the abstract
graded-monoid algebra, + the nested↔flat carrier iso as the multidegree crosslink. That abstract-↔-concrete equivalence
IS this route's contribution to `⟡jac-lit1-cd-cover`. (This is `⟡pyrig-object-carrier`-adjacent: the abstract MonoidAlgebra
functor is a named-center the substrate is missing.)

## ⚑ ⟡jac-lit1-cd-sppf VERDICT (agent a3e0aeb) — ~85% BUILT, motivation INTACT; the orbit-normalization payoff is DEMONSTRATED
EXISTS: `SPPF`/`inside`/`inside-unique` (`SPPF.agda:34-52`, `SPPFUP.agda:44-58` — the unique semiring-hom-out;
motivation (a) ✓). ⚑ NOTE scope: SPPF's semiring-initiality is a DIFFERENT initial object from the tower's
`LehmerPath`/`foldR` graded-rig initiality — don't conflate (b) and (c). The R.f₁→SPPF bridge already exists as the free
comm-ring term `Expr`+`encode` (`JacobianExpr.agda:22-37`, `⊖E a b ↦ a +P (kP(-1)*P b)` = negation as ×(−1)); the
principled bridge is `Expr → SPPF {x,y,z}` (~10 lines), NOT `MPoly → SPPF`.
- **NEGATION — all THREE discharges EXIST as checked terms** (the `inside` fold picks its target semiring): Route A =
  negatives in the target `ℤ-semiring` (`Instances/Z.agda`, `(-1)·(-1)≡+1` pole); Route B = log/antilog codec
  (`ℤ-power-codec` `Primes.agda:211`, `JacobianNegCodec.route-B`, `JacobianEncodingCodec.codecify` `:71` +
  `codecBridge₁₂₃`); Route C = sign as μ₂/S₃ character (`JacobianNegCodec §4`, `sign-codec = Sign.expℤ` at (−1,−1)).
- **EXTRUDER/ORBIT-NORMALIZATION PAYOFF — DEMONSTRATED (motivation (b)(c) ✓):** `normalize`/`NormPoly` = the V4-Coxeter
  ABELIAN instance of the parametric insertion-normalizer (`ListPresentation.agda:42-91` + `V4-Coxeter.agda` =
  commutativity-as-sorting = the Sₙ-orbit normalization); `MPolyNormalize.insertT` sorts + merges like terms + drops
  zeros; `NormPoly = Σ MPoly (isSortedB ≡ tt)` (h-prop sortedness) ⇒ **two normalized polys `≡` iff coeff vectors match,
  NO `coeff`-scan** — WITNESSED: `detNative-normal : proj₁ detNative ≡ normalize detJac` by **refl**
  (`JacobianDetNative.agda:62`). The extruder proper = `AgdaExtrude` (size-ordered minimal-by-construction).
- **The det-over-a-semiring is FULLY BUILT:** `LeibnizDet.agda` (`module Det (Semiring)`, uses the SPPF op-extraction
  idiom `:76`, sign = multiplicative `ε₂*A x`, NO fielded neg) → `JacobianDetNative` `det-native-correct`.
- **HONEST cover slot:** `inside` CANNOT fold directly into a common-denominator-ℚ semiring (padding not multiplicative);
  folding into `ℚ-Semiring` directly IS `evalℚ` (the blowup — the point of NOT doing it). What it DELIVERS: **fold into
  `NormPoly-Semiring` FIRST** (`inside NormPoly-Semiring v`, `v x = mkN X` …) → the sorted/merged/minimal canonical form
  (certified THE unique fold by `inside-unique`), THEN read off ONE common-`D` numerator sum over the ALREADY-minimal
  coeff vector (a single pass, not a 204-term scan); β = `normalize-eval` (`JacobianEvalNormalize.agda:166`) certifies
  it `≈ℚ` the direct value.
- BUILD (all thin): (1) `data XYZ : Set` (~1 line); (2) `Expr → SPPF {x,y,z}` (~10 lines, `⊖E`/`eK` via the chosen neg
  target); (3) the valuation `v : XYZ → NormPoly` + the `inside NormPoly-Semiring v` fold discharged `≡ normalize (encode
  e₁)` via the 4 `inside-unique` constructor eqns; (4) the common-`D` read-off tied to `evalℚ` via β.

## ⚑ EMERGING COVER SHAPE (SPPF + graded-monoid agree) — NormPoly is the CANONICAL CENTER; routes are its PRESENTATIONS
Both returned routes CONVERGE on `NormPoly = ℤ[Mono] = ℤ[x,y,z]` as the canonical realization: the SPPF route folds INTO
it (`inside NormPoly-Semiring`, canonicalized by `inside-unique`); the graded-monoid route IS the abstract algebra whose
concrete realization it is (`MonoidAlgebra ℤ Mono-CommMonoid ≅ NormPoly-Semiring`). So the routes are NOT independent
competitors — they are DIFFERENT PRESENTATIONS of one object (ℤ[x,y,z]), and the cover crosslinks the presentations +
the common-`D` read-off (evalCD) that sits on top of the canonical NormPoly, β-tied to `evalℚ`. This is the wedge, not
the cleaver: each presentation is a kept residue/coordinate; NormPoly is their shared apex.

## ⚑ ⟡jac-lit1-cd-gradedpoly VERDICT (agent aba48a0f) — the RING-GAUGE route; tower EXISTS, 3 route-pieces are BUILDS
EXISTS + proven: the graded `Poly`-Vec ring (`Graded.agda`: `Poly n = Vec A n`, `_+P_`/`_·c_`/`_*P_`(length-additive
`:83`)/`nth`/`basis`, full laws); **ring-gauge NEGATION `neg`/`-P`** (`FromCommRing.agda:66-72` `neg = inv(group
(+-abelian R))`, `Quotient.agda:55-57`); the fixed-carrier `Quotient-CommRing : CommutativeRing (Poly (suc d))`
(`:160` — the ITERATION unit; ⚑ `Graded.Over` alone is a GRADED ring [`_*P_` changes length], NOT `CommutativeRing
(Poly n)`, so iteration MUST route through `Quotient-CommRing`); `ℤ-CommRing` base with `-ℤ_` (`Z/CommRing.agda:121`).
- **BUILDS (all 3 route-specific, none exist):** (a) the ℤ-instantiation `open Quotient.Over ℤ-CommRing … ×3` with
  TRUNCATING monic `f = v^(suc d)` (`f-lo = replicate (suc d) 𝟘` ⇒ `ytime` = degree-truncation, lossless within the
  box); (b1) `toIter : MPoly → Poly(Poly(Poly ℤ))` = `placeMono k (mono a b c) = ((k ·c basis a) ·c basis b) ·c basis
  c` — PURELY ADDITIVE (`basis`/`·c`/`+P`, NO `_*P_`), so `_*Q_`'s truncation never bites; negation lands NATIVELY as
  the ℤ coeff `k` (no transport); (b2) `hornerCD : Vec ℤ n → (num den : ℤ) → ℤ` = `Σ cₖ·numᵏ·den^(n−1−k)` — the
  common-denominator ℤ-Horner (telescoping-verified, NO accretion, one `mkℚ N (D∸1)` at the end); (c) `≈ℚ` soundness
  `evalCD R.f₁ ≈ℚ β.evalℚ R.f₁` (cross-mult ℤ identity, structural induction, `≡→≈ℚ` at leaves).
- **⚑ DEGREE-BOX CATCH:** for f₁'s OWN evalCD use f₁'s box **x≤3, y≤4, z≤1** (Vec lengths 4,5,2) — NOT the whole-det box
  9,12,3 the NormPoly-agent (a0296daa) used (that over-pads: correct but a larger D). f₁ = z(1+xy)³ + y²(1+xy)(4+3xy) →
  max `x³y³z`, `x²y⁴`. Measure it (ship a `coeff`-probe pole, cf. `box-is-complete`).
- **COVER SLOT (distinctive = the RING GAUGE):** negation-in-the-carrier (`FromCommRing.neg` → `-ℤ_`, content-bearing
  `neg-is-not-identity` `CommRing.agda:144`) — EXACTLY what the free-semiring/SPPF route CANNOT do (must transpose /
  log-transport). This IS Route A of `⟡jac-neg-three-routes`. Cover chain: `evalCD ≈ℚ β.evalℚ ≈ℚ⟨identify₁⟩ C.f₁`
  (`identify₁` already exists, `JacobianCounterexample.agda:69`).
- **RESIDUE KEPT (not discarded):** a leaner alt bypasses `Quotient-CommRing` with a bespoke `Vec(Vec(Vec ℤ))` folded
  directly — forgoes the "3 Poly-over-CommRing layers" but re-rolls `basis`/`·c`/`+P`. The reuse-minimizing shadow; the
  ring-tower version IS the route as specified.

## ⚑⚑ ⟡jac-lit1-cd-cover VERDICT (agent a77e3bec) — the covering construction, + a hom-* reconciliation
**APEX `CDRouteℚ`** (proposed home `Algebra/Q/JacobianCDCover.agda`): a record = one route as a ℚ-valued semiring-hom-
out-of-MPoly agreeing with the fixed generator chart —
```
record CDRouteℚ : Set where field
  ⟦_⟧ : MPoly → ℚ ; hom-+ : ⟦p+Pq⟧ ≈ℚ ⟦p⟧+ℚ⟦q⟧ ; hom-* : ⟦p*Pq⟧ ≈ℚ ⟦p⟧*ℚ⟦q⟧
  gen-X : ⟦R.X⟧≈ℚx ; gen-Y ; gen-Z ; gen-k : (k)→⟦R.kP k⟧≈ℚ ℤ→ℚ k
```
= `homAgree`'s hypotheses (`JacobianEncodingHom.agda:205-215`) lifted off `Expr` onto MPoly = `inside-unique`'s shape
(`SPPFUP.agda:11-16`) relaxed from `≡` to `≈ℚ`. Routes' residues (den·den / D / negation-fiber / rep-iso) stay in each
FIBRE, NOT apex fields (the wedge, not the cleaver). Apex over ℚ (not a bare pairwise chain) because `_≈ℚ_` IS a bare ℤ
cross-equation (`Equiv.agda:37`) — inhabited without funext.
**DERIVE-THROUGH `cd-agree`** (stated ONCE over two arbitrary routes, never pairwise; mirrors `PeriodicCover.orbit-
discriminates:68` + ExpLogCodec): `cd-agree A B p : ⟦A⟧ p ≈ℚ ⟦B⟧ p = ≈ℚ-trans (list-hom-unique-over A) (≈ℚ-sym
(list-hom-unique-over B))` — both routes = the canonical `inside ℚ-Semiring gen ⌈p⌉` (co-apex identification). Per-route
agreement (`fold≈sppf`, `fold≈gmon`) is an INSTANTIATION `cd-agree route-eval route-X R.f₁`, never a fresh proof.
**NON-VACUITY `cd-discriminates` (MANDATORY):** the apex alone proves nothing (constant route `⟦_⟧=0ℚ` satisfies
hom-+/hom-* and fails the chart only at NONZERO points; at (0,0,0) all routes collapse by refl — decorative). Instantiate
at the WITNESSED discrimination: `JacobianCollision.collide₁` (the Alpöge collision, nonzero at a nontrivial point) /
`JacobianDetLiteral.detJac-literal : evalℚ detJac ≈ℚ −2` (`:57`). Model on `PeriodicCover.alt-discriminates:144`.
**THE AGREEMENT IS hom-uniqueness-over-≈ℚ**, via the ~3-line `list-hom-unique-over` (the MPoly analogue of
`fold-unique-over` `OrientationUniversal.agda:95-98`, which is LehmerPath-only): `[]`→both ≈ℚ 0ℚ; `t∷p`→chain per-cons
hom-step + recurse, consuming ONLY `≈ℚ-trans`+`+ℚ-cong`. Its shape already appears twice concretely (`homAgree` ⊕E/⊗E
cases at ≈ℚ; `inside-unique` a⊕b/a⊗b cases at ≡).

## ⚑ HOM-* RECONCILIATION (cover apex ⟷ the CHEAP evalCD) — a genuine two-layer structure, do NOT paper over
The `CDRouteℚ` apex DEMANDS `hom-*` (multiplicativity). ⚑ **The CHEAP common-denominator `evalCD` is NOT a *-hom** —
padding is not multiplicative, AND its `D` depends on the polynomial's degree box (p*P q has box 2·box → D², so
`evalCD(p*P q)` uses D², not a fixed D). So evalCD is NOT a `CDRouteℚ` instance. The cover is therefore TWO LAYERS:
- **Layer 1 — the `CDRouteℚ` cover unifies the SEMIRING-HOM evaluators** (β.evalℚ, `inside ℚ-Semiring gen`, any *-hom
  per-carrier evaluator). These all AGREE by hom-uniqueness (compute the true value C.f₁) — but they EXPLODE (ℚ-mult →
  den·den). This is the "carrier presentations agree" cover.
- **Layer 2 — the CHEAP evalCD** (padNum/sumNum, a0296daa) is a NON-*-hom +-fold, ≈ℚ the true value via the
  +-hom-over-FIXED-D argument (its OWN soundness `evalCD-sound : evalℚ p ≈ℚ evalCD p`, NOT the CDRouteℚ apex). This is
  the MEMORY fix; lands literal₁ under the cap.
- **The full cover crosslink:** each carrier's cheap evalCD ≈ℚ that carrier's semiring-hom evaluator (Layer 2) ≈ℚ every
  other carrier's evaluator (Layer 1 apex) ≈ℚ C.f₁. literal₁: `evalCD R.f₁ ≈ℚ⟨evalCD-sound⟩ β.evalℚ R.f₁ ≈ℚ⟨identify₁⟩
  C.f₁` — neither step forcing the explosion. (The cover agent's "route-gmon = evalCD over GradedProduct as a CDRouteℚ
  instance" glossed this — the GradedProduct STANDARD graded hom IS a CDRouteℚ instance [and explodes]; the GradedProduct
  common-denominator FOLD is Layer 2 [cheap, non-hom]. Keep them distinct.)

## ⚑⚑ UNIFIED BUILD ORDER (all 7 agents synthesized; build-all-and-cover, residues kept graded)
- **⟡jac-lit1-cd-normpoly** [Layer 2, CHEAP, do FIRST — lands literal₁ under the cap]: `powℤ`/`maxℕ` helpers ·
  `padNum`/`sumNum`/`evalCD` (f₁'s OWN box x≤3,y≤4,z≤1, MEASURE it) · `gen-sound` · `evalCD-sound` (+-hom-over-D + list
  induction + `Assemble` anti-explosion) · `evalCD-leg₂` = refl. (agent a0296daa turn-key.)
- **⟡jac-lit1-cd-cover** [Layer 1 apex + non-vacuity]: `list-hom-unique-over` (3 lines) · `CDRouteℚ` + `cd-agree` ·
  `route-eval` (β.evalℚ, immediate — evalℚ-++/evalℚ-*P/gens all exist) · `cd-discriminates` (collision / det=−2, MANDATORY).
- **⟡jac-lit1-cd-sppf** [carrier presentation, ~85% built]: `data XYZ` (1 line) · `Expr→SPPF` (~10 lines) · `v : XYZ→
  NormPoly` + `inside NormPoly-Semiring v` (canonicalize, `inside-unique`-certified) · a `CDRouteℚ` instance (inside-into-ℚ
  is a *-hom) + its cheap evalCD read-off over the normalized vector. Negation 3 gauges.
- **⟡jac-lit1-cd-gradedpoly** [ring gauge, 3 builds]: iterate `Quotient.Over ℤ-CommRing ×3` (truncating monic) · `toIter`
  (additive) · `hornerCD` (Layer-2 cheap fold) · `≈ℚ` soundness. Negation-in-carrier (`FromCommRing.neg`). Route A of neg-cover.
- **⟡jac-lit1-cd-gradedmonoid** [~80% build]: the ABSTRACT `MonoidAlgebra ℤ Mono-CommMonoid ≅ NormPoly-Semiring` crosslink
  + nested↔flat `Mono` iso · a `CDRouteℚ` instance + its cheap fold. (⟡pyrig-object-carrier-adjacent.)
- **⟡jac-lit1-numerator** — re-prove literal₁ via `⟡jac-lit1-cd-normpoly`'s evalCD-sound + identify₁; MEASURE (~90-150MB).
- **⟡jac-stale-prose-and-index** — update `JacobianResidue.agda:39-55` (det proven via NormPoly; SPPF route = the
  crosslink, still owed) + regen `catalog/reuse-index.md` (NormPoly/NormPoly-Semiring/Mono-CommMonoid/detNative absent).
- Iterated-ring rep-iso / the leaner-Vec shadow = kept Rosetta coordinates (the residue), NOT built cheap.

---

# ⚑ BUILD IN FLIGHT (2026-07-22) — ⟡jac-lit1-cd-normpoly (agent a3c0a855, opus write-agent, isolate-check only, NO commit)
Home: NEW `Algebra/Q/JacobianEvalCD.agda`, `module _ (x y z : ℚ)(Dx Dy Dz : ℕ)`. Deliverables: `powℤ`/`maxℕ`,
`padNum`/`sumNum`/`evalCD` (Dℕ-first: `evalCD p = mkℚ (sumNum p) (suc(den-1 x)^Dx * … ∸ 1)`), `fixed-D-add`,
`gen-sound` (+ sub-lemmas `powℚ-mkℚ`, `powℤ-add`, `a≤b → a+(b∸a)≡b`), `evalCD-sound : (p) → Bounded p → evalℚ p ≈ℚ
evalCD p`, `evalCD-leg₂` (refl), literal₁-cheap via `≈ℚ-trans` + the `Assemble` stuck-neutral open.
⚑ **THE DESIGN SUBTLETY (captured in the brief, glossed by a0296daa):** `padNum` uses TRUNCATED `Dᵥ ∸ a` → exact ONLY
when `a ≤ Dᵥ`. So `evalCD-sound` carries `Bounded p` (`data Bounded`: every `term (mono a b c) _` has `a≤Dx,b≤Dy,c≤Dz`);
FIXED box param → tail-IH same box. `gen-sound`'s crux: `powℤ qᵥ (Dᵥ∸a) *ℤ powℤ qᵥ a = powℤ qᵥ Dᵥ` via `powℤ-add` +
`a≤Dᵥ ⇒ (Dᵥ∸a)+a = Dᵥ`. Discharge `Bounded 3 4 1 R.f₁` (f₁ box measured: max `x³y³z`,`x²y⁴`; VERIFY, bump if needed).
Anti-explosion: soundness over ABSTRACT p, stuck-neutral congruences, instantiate at R.f₁ via `Assemble`-open
(`JacobianLiteral1.agda:51-76`) so Agda never normalizes the 204-term fold. MEASURE literal₁-cheap vs the 729 MB baseline.
If a piece fails → agent STOPS + reports (no postulate/hole); controller course-corrects, commits, waits for amend marker.

## ⚑⚑ cd-normpoly BUILT + COMMITTING (agent a3c0a855; verified EXIT=0, 80 MB warm; zero postulates/holes) — + the HONEST scope
`Algebra/Q/JacobianEvalCD.agda`: `evalCD p = mkℚ (sumNum p) (Dden∸1)` (ℤ-additive, no `_+ℚ_`) · `evalCD-sound : (p) →
Bounded p → evalℚ x y z p ≈ℚ evalCD p` (FULLY GENERAL in the point) · `Bounded`+`buildB` reflection · `powℚ-mkℚ`/
`powℤ-add`/`fixed-D-add`/`gen-sound`/`pad-step` · `Bounded-f₁` box (3,4,1) by reflection · `evalCD-leg₂-p/-q` = refl ·
`literal₁-cheap-p/-q`. **80 MB vs the 729 MB `_+ℚ` baseline.** Committing (gated).
## ⚑ THE SCOPE QUESTION — ANSWERED by reading JacobianCounterexample (does cd-normpoly LOWER THE CAP?)
- `IsJacobianCounterexample` (`JacobianCounterexample.agda:60-82`) has TWO f₁-relevant fields: `collide₁ : C.f₁ p ≈ℚ
  C.f₁ q` (HALF A, C-SIDE concrete, provided by `C.collision₁` — does NOT use literal₁) AND **`identify₁ : (x y z) →
  evalℚ R.f₁ ≈ℚ C.f₁ x y z` (∀-QUANTIFIED, the R↔C Rosetta bridge, provided by `L.literal₁` = the 729 MB AES-Full route).**
- ⚑ So the capstone DEMANDS the ∀-quantified `identify₁`, NOT point-wise. cd-normpoly's `literal₁-cheap-p/-q` are
  POINT-WISE (evalCD-leg₂ = refl only at concrete points) → they do NOT satisfy `identify₁`. **The 729 MB
  `JacobianLiteral1.literal₁` STAYS required.** cd-normpoly alone does NOT lower the cap. (The "lands literal₁ under the
  cap" todo framing was OPTIMISTIC — corrected.)
- **THE OPEN EXPERIMENT (⟡jac-lit1-numerator, NOT a foregone win):** can the SYMBOLIC `identify₁` be re-proven cheaply
  via `evalCD-sound R.f₁ ∘ (SYMBOLIC evalCD-leg₂)`? evalCD-sound is symbolic+cheap (80 MB) ✓. But the symbolic
  `evalCD R.f₁ ≈ℚ C.f₁ x y z` = `sumNum R.f₁ ·ℤ den(C.f₁) ≡ num(C.f₁) ·ℤ Dden` — and **the RHS `C.f₁ x y z` STILL has
  its OWN `_+ℚ_`** (C.f₁ is the curried ℚ map: `z(1+xy)³ + y²…` in ℚ arithmetic), so the C-side denominator products
  are NOT removed by evalCD (which only de-explodes the R/LHS side). So the symbolic leg is UNCERTAIN — it may inherit
  C.f₁'s explosion. NEEDS a build+MEASURE to know. This is the real cap-lowering experiment; the agent honestly
  sidestepped it (point-wise refl only).
- **WHAT cd-normpoly DELIVERS regardless (banked value):** the reusable cheap `evalCD` + GENERAL `evalCD-sound` (the
  Layer-2 fold for the cover), + the collision-half f₁ identity point-wise cheap. Genuine, honest, isolate-green.
- **NEXT (⟡jac-lit1-numerator, sharpened):** build the SYMBOLIC evalCD-leg₂ and MEASURE — does `evalCD-sound R.f₁ ∘
  symbolic-leg₂` prove `identify₁` under 512? If the C.f₁ `_+ℚ_` dominates, a DUAL fix (a common-denominator form of
  C.f₁ too) may be needed. This decides whether the 729 MB module retires and the cap drops.

## ⚑ ⟡jac-lit1-numerator EXPERIMENT IN FLIGHT (2026-07-22, agent acad82d9, opus, isolate+measure, NO commit)
The deliverable is the RESIDUE STRUCTURE (user: "it matters HOW it does or does not lower the cap"), NOT pass/fail.
Build `identify₁-cheap : (x y z) → evalℚ x y z R.f₁ ≈ℚ C.f₁ x y z` (matches the capstone `identify₁` field) via
`≈ℚ-trans (evalCD-sound x y z 3 4 1 R.f₁ (buildB … record {})) (evalCD-leg₂-sym x y z)`. Leg 1 = general+cheap. Leg 2
(the unknown) = `sumNum R.f₁ ·ℤ (+ suc den-1(C.f₁)) ≡ num(C.f₁) ·ℤ (+ Dden)` symbolically — try refl, else characterize.
⚑ MEASURE + DECOMPOSE (the key finding): (1) baseline `JacobianLiteral1` RSS on THIS machine; (2) leg-1-alone RSS;
(3) leg-2 refl?/RSS; (4) **the decomposition — RSS of `C.f₁ x y z` symbolic (the CURRIED side's own `_+ℚ_`, which
evalCD does NOT touch) vs `sumNum R.f₁` symbolic (the R-side ℤ-fold evalCD replaced)**; (5) the HOW-verdict — which
term's normalization dominates, so the next fix is obvious (C.f₁-side dominates ⇒ a common-denominator `evalCD`-of-the-
CURRIED-map [dual fix]; or the ℤ ring-identity is the cost). HYPOTHESIS: the 729 MB is R-side (evalℚ R.f₁'s 204-term
`_+ℚ_`); C.f₁ is the FACTORED form (small); so evalCD MIGHT de-explode it — but leg-2's ℤ ring-identity (sumNum R.f₁ vs
num(C.f₁)) is the real unknown. The decomposition settles which. RE-DISPATCH from this brief after a compaction.

## ⚑⚑ ⟡jac-lit1-numerator RESIDUE (agent acad82d9, 2026-07-22) — the HOW, decisively decomposed
MEASURED RSS (this machine, `/usr/bin/time -v`, deps warm):
| probe | RSS | exit |
|---|---|---|
| BASELINE `JacobianLiteral1` (AES-Full `identify₁`) | **781 MB** | 0 ✓ |
| LEG 1 `evalCD-sound … R.f₁` @ ABSTRACT x y z | **78 MB** | 0 ✓ |
| LEG 2 `refl : evalCD R.f₁ ≈ℚ C.f₁` @ abstract | 80 MB | **42 ✗** |
| C.f₁-side normal form (`C.f₁ x y z ≡ 0ℚ` force) | 71 MB | 42 ✗ |
| sumNum-side normal form (`evalCD … ≡ 0ℚ` force) | 80 MB | 42 ✗ |
- **THE 781 MB IS A PROOF-TERM ELABORATION cost, NOT conversion/normalization** — it's building the fully-pinned ≈ℚ
  reassociation chain over `evalℚ-++`/`normalize` of the 204-term MPoly. evalCD replaces EXACTLY that fold with a stuck
  ℤ-additive `sumNum` → **LEG 1 = 78 MB (a 10× drop; the real bankable win — evalCD de-explodes the R/evalℚ side).**
  Conversion never blows up (all forcing probes ≤ 80 MB, Agda bails at WHNF).
- **LEG 2 `refl` FAILS *cheaply* (exit 42, 80 MB) — it is FALSE DEFINITIONALLY, not a blowup.** Mismatch leaf
  `ℤ.+ (((1*1)*1)*1) != ℚ.num z`. The two sides are structurally incompatible: evalCD's `Dden = qx³·qy⁴·qz` (ONE fixed
  monomial denom) + `sumNum` (EXPANDED 204-monomial ℤ sum) vs C.f₁'s `_+ℚ_`/`_*ℚ_` CROSS-MULTIPLIED denom + FACTORED
  cross-numerator `numA·(+suc denB) +ℤ numB·(+suc denA)` (A=z·u³, B=y²·u·v — u/v never even unfold).
- **⚑ THE RESIDUE LIVES ENTIRELY ON THE C.f₁ (CURRIED) SIDE, WHICH evalCD NEVER TOUCHES.** evalCD de-exploded the
  sumNum/R side; the curried C.f₁'s own `_+ℚ_`/`_*ℚ_` cross-multiplication (numerator AND product-denominator) is
  untouched. So leg 2 = the full expanded-vs-factored, different-denominator polynomial identity — the C-side work.
- **HOW-verdict:** `identify₁-cheap = leg1∘leg2` cannot compile via refl (leg 2 false definitionally); proving leg 2 by
  hand re-derives the `normalize`/`bridge` machinery → reintroduces the 781 MB class; no ring solver shortcut. Agent
  STOPPED (discipline). TYPE is drop-in for the capstone `identify₁`; PROOF is not cheap by this route → `identify₁ =
  L.literal₁` (781 MB) STANDS until the C-side is de-exploded too.

## ⚑ THE NAMED FIX (the decomposition points straight at it): ⟡jac-lit1-cd-curried — the DUAL common-denominator evaluator
Recursive-common-structure, once more: the R-side (`evalℚ R.f₁`, expanded) and the C-side (`C.f₁`, factored) are BOTH
`_+ℚ_`-exploding presentations of the SAME polynomial F₁; the common-denominator trick applies to BOTH; evalCD is HALF
(the R-side). The DUAL: a common-denominator evaluator for the CURRIED `C.f₁` over the SAME `Dden = qx³·qy⁴·qz` →
`C.f₁ x y z ≈ℚ mkℚ N_C Dden`. Then leg 2 = `mkℚ (sumNum R.f₁) Dden ≈ℚ mkℚ N_C Dden` = `sumNum R.f₁ ≡ N_C` (ℤ, same
Dden). ⚑ OPEN QUESTION (the genuine unknown, do NOT assume cheap): `sumNum R.f₁ ≡ N_C` is STILL the polynomial identity
(expanded R-numerator vs factored C-numerator, now over ℤ not ℚ). Is the ℤ-numerator identity cheaper than the 781 MB ℚ
reassociation? MAYBE (ℤ ring reasoning vs ℚ `_+ℚ_` folding) — OR it re-incurs the same expansion. ⚑ POSSIBLE SHORTCUT:
`bridge₁ : normalize R.f₁ ≡ normalize Cᴹf₁ = refl` (`JacobianEncodingNormalize.agda:65`) already identifies R.f₁ and
Cᴹf₁ (C's MPoly encoding) at the MPoly level BY REFL — so if the dual evaluates C VIA `evalCD Cᴹf₁` (not the factored
curried form), both sides are `evalCD` of refl-equal MPolys → leg 2 = refl, and the remaining gap is `C.f₁ x y z ≈ℚ
evalℚ Cᴹf₁` (= `evalBridge₁`/`homAgree`, ALREADY built — measure its cost). This is the real cap-lowering route: build
`⟡jac-lit1-cd-curried` (dual evalCD for C, or route C through `evalCD Cᴹf₁` + the existing `evalBridge₁`) and MEASURE.

## ⚑ ⟡jac-lit1-cd-curried SATURATION IN FLIGHT (2026-07-22, agent aa552f32, read-only, MIRROR on return)
Goal: de-explode the CURRIED C.f₁ side (the residue evalCD leaves untouched) so the symbolic `identify₁` comes cheap.
TWO routes to saturate:
- **ROUTE 1 — the Cᴹf₁/bridge₁ shortcut.** `bridge₁ : normalize R.f₁ ≡ normalize Cᴹf₁` = refl
  (`JacobianEncodingNormalize.agda:65`) → route C via `evalCD Cᴹf₁`; leg 2 becomes cheap (ℤ-additive both sides) IF an
  `evalCD-respects-normalize` lemma exists/is small (mirror `normalize-eval:166`). ⚑⚑ THE LOAD-BEARING COST QUESTION:
  the remaining gap `evalℚ Cᴹf₁ ≈ℚ C.f₁` (= `evalBridge₁ :185` / `homAgree :205`) — `evalℚ Cᴹf₁` is ITSELF a `_+ℚ_`
  fold, so is this bridge ALREADY CHEAP (like literal₂/₃'s homAgree, 94/77 MB — per-Expr-node) or 781-MB-class (the
  same `evalℚ-++`-over-the-cube explosion that makes literal₁ expensive)? MEASURE decides whether ROUTE 1 works.
- **ROUTE 2 — the direct dual.** A common-denominator evaluator for the FACTORED C.f₁ expression over the SAME Dden →
  `C.f₁ ≈ℚ mkℚ N_C Dden`; leg 2 = `sumNum R.f₁ ≡ N_C` (ℤ, same Dden) — refl or a proof? cost class vs 781 MB?
DELIVERABLE: which route (if either) lands identify₁ under 512, WHY (cost structure), build order + reuse anchors; if
BOTH re-incur the 781 MB polynomial-identity content, say so (the residue stands — a valid finding). Keep it graded, not
a boolean. RE-DISPATCH from this brief after a compaction.

## ⚑⚑ ⟡jac-lit1-cd-curried SATURATED (agent aa552f32, 2026-07-22) — ROUTE 1 dead; ROUTE 2 is the only sub-512 path (turn-key)
OBJECTS (measured, `.agda-times.tsv`): `C.f₁` = `(z*ℚ(u*ℚ(u*ℚu))) +ℚ (((y*ℚy)*ℚu)*ℚv)`, `u=1+xy`, `v=4+3xy`
(`JacobianCollision.agda:72-76`, NO powℚ — a ~10-node ℚ-op tree; module 67 MB). `R.f₁`/`Cᴹf₁` are BOTH `*P`-product
exprs (not pre-expanded), differing only by cube-associativity → `normalize` collapses both → `bridge₁ : normalize R.f₁
≡ normalize Cᴹf₁ = refl` ✓ (`JacobianEncodingNormalize.agda:65`). ⚑ `evalCD-respects-normalize` does NOT exist (grep
empty) — a small ℤ build if needed.
### ROUTE 1 (bridge₁/evalBridge₁ shortcut) — DEAD for the ∀ identify₁
Chain: `evalℚ R.f₁ ≈[evalCD-sound,100MB] evalCD R.f₁ ≈[evalCD-resp-norm∘bridge₁,~80-105MB build] evalCD Cᴹf₁
≈[evalCD-sound Cᴹf₁ rev] evalℚ Cᴹf₁ ≈[???] C.f₁`. First 3 legs CHEAP + general. ⚑ **The 4th leg `evalℚ Cᴹf₁ ≈ℚ C.f₁`
IS `homAgree e₁` reversed = the EXACT 781-MB CUBE** (`homAgree`'s ⊗E case via `evalℚ-*P` over the (1+xy)³ cube, folding
`_+ℚ_` denominators; `JacobianEncodingHom.agda:216,174`). ⚑ CRUCIAL: `evalBridge₁` (78 MB, `JacobianEvalNormalize.agda:185`)
is the MPoly↔MPoly leg (`evalℚ R.f₁ ≈ℚ evalℚ Cᴹf₁`, ≡-rigid re-assoc) — it NEVER touches `C.f₁`, so it does NOT help.
The only general handle from `C.f₁` to the MPoly world is `homAgree e₁` = the 781 MB. **ROUTE 1 relocates but does not
remove the residue; will NOT land identify₁ under 512.**
### ROUTE 2 (the direct dual `evalCD_C`) — the ONLY plausible sub-512 path (BUILD)
Build `evalCD_C : (x y z) → C.f₁ x y z ≈ℚ mkℚ N_C (Dden∸1)` by structural recursion over C.f₁'s ~10-node ℚ-tree over
the SAME `Dden = qxn³·qyn⁴·qzn`: `_*ℚ_`→single ℤ-product; `_+ℚ_`→`fixed-D-add` (ALREADY proven, `JacobianEvalCD.agda:194`).
Soundness = stuck-neutral ≈ℚ congruences over the FINITE fixed tree (same discipline as `evalCD-sound`) → **~100 MB, NOT
781** (never materialises the top `_+ℚ_` cross-multiplication). This is the genuinely new promising piece.
Then leg 2 collapses to `sumNum R.f₁ ≡ N_C` (ℤ, IDENTICAL Dden). ⚑ NOT refl symbolically (expanded R-numerator vs
factored C-numerator; at collision points it IS refl — the committed `evalCD-leg₂-p/q`). Symbolically it's a **ℤ
ring-identity requiring the binomial expansion of `(qxn·qyn + px·py)³`** — the irreducible cube combinatorics, now in ℤ
over a fixed denominator, MINUS the ℚ eta-record + `_+ℚ_` overhead that dominate the 781 MB. **UNMEASURED conjecture:
plausibly < 512 (supporting: `MPolyNormalize/Properties` = 105 MB — ℤ-side canonicalization of these objects is ~100 MB,
not ~800), but the cube expansion could still be large.**
### HONEST BOTTOM LINE + BUILD ORDER
The 781 MB = ℚ-eta-record + `_+ℚ_`-cross-multiplication + cube-binomial. ROUTE 2 STRIPS the first two; whether the
cube-binomial ALONE is < 512 in ℤ is THE open measurement. Build order (ROUTE 2):
1. REUSE `evalCD`/`sumNum`/`padNum`/`Dden`/`fixed-D-add`/`evalCD-sound`/`Bounded`/`buildB` (`JacobianEvalCD.agda`, general).
2. REUSE `evalCD-sound R.f₁ Bounded-f₁` for leg 1.
3. BUILD `evalCD_C` (structural over `JacobianCollision.agda:73`'s tree; `_*ℚ_`→ℤ-product, `_+ℚ_`→`fixed-D-add`). ~100 MB.
4. ⚑ BUILD the residual `sumNum R.f₁ ≡ N_C : ℤ` **in its OWN module + MEASURE its memory row BEFORE wiring** — THE
   load-bearing measurement (route through `Algebra/Z/MPolyNormalize`, 105 MB, not raw ℤ ring reasoning).
5. Compose `identify₁ = evalCD-sound R.f₁ ∘ (≡→≈ℚ step-4) ∘ sym evalCD_C` — same-Dden ℤ step, no `_+ℚ_` on the C side.
IF step 4 ≥ 512: the cube binomial is irreducible in ℤ too; NO sub-512 symbolic identify₁ — only the committed
point-wise `literal₁-cheap-p/q` is cheap; the general identify₁ legitimately stays with the 781 MB `homAgree` route; the
residue is CHARACTERIZED, not eliminated (a valid finding).

## ⚑⚑⚑ ⟡jac-lit1-cd-curried ROUTE 2 EXECUTED (2026-07-22) — step 3 LANDS 99 MB; step 4 (the ℤ cube) has NO cheap route. THE MEASUREMENT.
BUILT + committing: `agda/Substrate/Algebra/Q/JacobianEvalCDCurried.agda` (`--safe --without-K`, 0 postulates/holes).
- **STEP 3 DONE — `evalCD_C : (x y z) → C.f₁ x y z ≈ℚ mkℚ N_C (Dden∸1)`, MEASURED 97–99 MB** (vs 781 MB `JacobianLiteral1`).
  Structural over C.f₁'s ~10-node ℚ-tree: every `_*ℚ_`→ONE ℤ product (`≡mkℚ-*`), every `_+ℚ_`→`fixed-D-add`
  (reused from `JacobianEvalCD.agda:194`); the cube `Ux³` KEPT AS A PRODUCT (never expanded). Denominators tracked
  as `Qn a b c = qx^a·qy^b·qz^c`; `Qn-mul` (quad + a new `powℕ-add` ×3) makes product = exponent-ADD, so box
  padding is a single-exponent bump (`pad1id`/`bumpX`/`bumpZ` — clean, no 8-factor sorts). N_C = N1 +ℤ N2 with
  N1 = pz·Ux³·(+qy), N2 = py²·Ux·Vx·(+qx)·(+qz); Ux = 1·(+Qn110)+px·py·(+1), Vx = 4·(+Qn110)+3·px·py·(+1).
  **evalCD_C typechecking IS the proof N_C is the correct CD numerator of C.f₁.** Compiled FIRST TRY.
  ⚑ This CONFIRMS the saturation's central claim: Route 2 STRIPS the ℚ-eta-record + `_+ℚ_`-cross-multiplication.
  Both the R-side `evalCD R.f₁` (leg 1, 78 MB) and the C-side `evalCD_C` (99 MB) are cheap FACTORED/padded forms.
- **STEP 4 (LOAD-BEARING) MEASURED — `sumNum R.f₁ ≡ N_C` has NO cheap `refl`.** Probed `refl : sumNum R.f₁ ≡ N_C`:
  **FAILS at 97 MB / 1.5s, `[UnequalTerms] + (1*1*1*1) != num z`** (a structural FIRST-TERM mismatch — refl bails
  immediately). Both sides are DISTINCT STUCK ℤ trees: the EXPANDED 204-monomial padded sum (R) vs the FACTORED
  `pz·Ux³·qy + …` (C). `_*ℤ_` does NOT auto-distribute over the symbolic `Ux = qx·qy + px·py`, so NEITHER side
  reduces past the stuck products. ⟹ proving the identity is the **genuine BINOMIAL EXPANSION of Ux³ in ℤ** — a
  6-variable ℤ ring identity in (px,py,pz,qx,qy,qz). The 97 MB is only tree-CONSTRUCTION cost; the PROOF cost is
  UNMEASURED (no proof constructed — refl is not it, and materializing the full ℤ expansion is plausibly the same
  magnitude as the 781 MB minus the ℚ overhead, i.e. could be ≥512).
### HONEST VERDICT (the "HOW it does/does-not lower the cap")
Route 2 does NOT (this turn) lower `identify₁`'s cap. WHAT IT DELIVERS: (a) `evalCD_C`, a machine-checked cheap
(99 MB) FACTORED common-denominator normal form of the curried map — a reusable artifact + N_C validated; (b) the
irreducible core of the 781 MB is now **LOCALIZED to a single, precisely-stated ℤ polynomial identity**
`sumNum R.f₁ ≡ N_C` (the cube-binomial), stripped of all ℚ overhead — CHARACTERIZED, not eliminated. Matches the
saturation's own contingency ("IF step 4 ≥ 512 … the residue is characterized, not eliminated, a valid finding").
### LABELED NEXT (the residue's remaining route, NOT forced)
- **⟡jac-lit1-cube-normalizer** — to PROVE `sumNum R.f₁ ≡ N_C` (settle <512 definitively) needs a 6-variable ℤ
  ring normalizer / reflection layer (the 3-var `Algebra/Z/MPolyNormalize` does NOT apply — sumNum/N_C are ℤ in
  px,py,pz,qx,qy,qz, not the MPoly's 3 vars). A large separate arc; the hand-expansion of Ux³ + matching 204
  terms is enormous. Only worth it if the definitive cube-cost number is wanted.
- The committed point-wise `literal₁-cheap-p/q` (JacobianEvalCD, at the two collision points) remain the cheap
  wins; the ∀-quantified `identify₁` legitimately stays with `JacobianLiteral1`'s 781 MB `homAgree` route.
