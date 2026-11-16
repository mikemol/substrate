---
name: set1-carrier-always-parameterize
description: "A record that fields a Set-valued carrier is never \"honest Set₁\" — always parameterize the carrier and make the consumer name it explicitly."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

A `record R : Set₁` that FIELDS a `Set`-valued carrier or relation (`field Carrier : Set`,
`field _~_ : X → X → Set`) is **never an honest Set₁** — not even a structure-bundle over an
"abstract carrier" (like a Monoid/Algebra/Action bundle). There is NO debt-vs-design judgment
to make here: the Set₁ is always paydownable debt, and the fix is uniform.

**Why:** fielding `Set` is exactly what forces the universe bump; the carrier does not belong
*inside* the record's fields, it belongs *outside* as a module parameter. Leaving it a field
hides which carrier the structure is over and pushes the level up for nothing.

**How to apply:** take the carrier as a module parameter and let the CONSUMER be explicit —
```
module _ (Carrier : Set) where
  record R : Set where          -- was : Set₁
    field op : Carrier → Carrier ; …
```
so consumers write `R MyCarrier` instead of the record carrying `Carrier` internally. This is
the house pattern (Substrate.Category.Lawvere's carrier-generic atoms; the interned
StarV4 / FoldUnfold / ConversionCongruence paydowns). It resolves what I had labelled ⟡D5
("is `Fam : Set → Set₁` the one honest home?") for the RECORD case: parameterize, always.
Genuinely level-1 things that are NOT carrier-bundles (a FUNCTION `Fam : Set → Set₁`,
`⊤₁ : Set₁` the polymorphic unit) are a separate question; the rule here is about records that
field a carrier. See [[def-proof-separation-lever]], [[free-universal-property]].

**Confirmed at scale (DivStr paydown, HEAD a5286a0, 2026-07-09, 753→710).** `record DivStr : Set₁
where field C : Set` → `record DivStr (C : Set) : Set`; ditto `MulDivStr (Cr : Set)`. Cascade = 65
files. Three operational lessons:
1. **The blast radius EXCEEDS a bare-`Record`-in-signature grep.** The break surface also includes
   files that `import … C …` the removed carrier projection (esp. via `renaming`) and use `C D` only
   in bodies, and files with a bare `MulDivStr`/`DivStr` type. Before declaring the cascade done, run
   the residual sweeps: `grep -rn 'Substrate.Algebra.Wedge using' | grep '\bC\b'` (empty) and
   `grep -rnE ':\s*MulDivStr\b|→\s*MulDivStr\b' | grep -vE 'MulDivStr\s+[carrier]'` (empty). These ARE
   the coverage gate.
2. **Adding a leading `{C : Set}` shifts positional implicits** — every `f {D}`/`f {ℕ-div}` usage of a
   changed def must become `f {D = D}`; if the body names the carrier, bind it on the LHS (`f {C} … =`).
3. **A monoidal product over parameterized carriers takes the PRODUCT carrier:** `_⊗ᴰ_ : DivStr C₁ →
   DivStr C₂ → DivStr (C₁ × C₂)`, unit `⊤-div : DivStr ⊤` — the honest Lawvere form; coherence
   (pentagon/triangle/hexagon/naturality) still closes.
The RESIDUAL Set₁ this does NOT remove: a MATERIALIZED heterogeneous collection (`Registry.Obj = Σ Set
DivStr`, `objects : List Obj`) — that needs generic-not-materialized (state over `{C}`, instances
concrete), the Lawvere follow-up, NOT another carrier-param. See [[reuse-search-before-feasibility-conclusions]].
