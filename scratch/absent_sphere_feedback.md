# Ⓒ.absent-sphere — feed-back for `bridge_absent_sphere` (the Agda→cotype orphan)

Companion to `scratch/cotype_pi_agda_contrast.md`. The cotype↔Agda Rosetta has TWO orphan arms
(symmetric coverage). The contrast doc detailed the **cotype→Agda** arm (cyclotomic/Φ_p/Weil).
This note closes the **Agda→cotype** arm: `warrants_bridge.bib`'s `bridge_absent_sphere` flags
that the **commuting-sphere / Cayley–Dickson campaign is *in* Agda but dropped from the cotype**.
Here is the content to re-note when the cotype is next regenerated.

The cotype `.bib` corpus is external (extracted from `cotype-rosetta.tgz`/`cotype-bridgefix.tgz`,
not committed) — so this is a repo-side mining note, not a homed artifact (the cotype's own rule).

## The Agda campaign the cotype is missing

- **`Algebra/CayleyDickson.agda`** — the Cayley–Dickson doubling as a **GENERATOR** (`Carrier : ℕ → Set`,
  total at every level; ℂ,ℍ,𝕆,𝕊,𝕋,… all constructible by structural recursion over ℚ-setoid `≈#`).
  Thesis (user, 2026-06-12): it does NOT "stop at the octonions" — the Hurwitz losses are tracked
  **residues**, not halts:
    ℝ→ℂ self-conjugacy · ℂ→ℍ commutativity · ℍ→𝕆 associativity · 𝕆→𝕊 alternativity (zero divisors).
  A zero divisor is a multiplicative MODULO where the state was collapsed to 0 instead of keeping the
  remainder (the cancelled value `acP−dbP=0` only because `acP≈dbP`; the kept remainder `acP=e₅ᴼ` is
  a nonzero unit octonion). "Stops at octonions" = a discarded-residue WALL; the generator keeps
  doubling unobstructed. Sub-modules: `CayleyDickson.Cocycle` (generic product law `prod`:
  `eᵢ·eⱼ ≈# ε(i,j)·e_{i⊕j}` ∀n), `CayleyDickson.Grade` (OR=XOR⊕AND, the two index-products),
  `CayleyDickson.Curve` (Morton/Z-order + crossover = tropical min).
- **`Algebra/Wedge/Sphere.agda`** — THE COMMUTING SPHERE: a LIVE in-code index of the wedge/shape arc
  (references proven cells by name → fails to typecheck if any is removed) + a CONJECTURE LEDGER kept
  next to the proofs. Proven cells incl.: `cell-wedge` (DivStr), `cell-square` (double-category 2-cell),
  `cell-twist` (companion/conjoint = trace/Bézout), `cell-cocycle`, `cell-grade`, `cell-hexagon`
  (symmetric-monoidal coherence), `cell-morton`/`cell-crossover`. KEYSTONE conjecture **PROVED**
  (`Wedge.Adjunction`): the r<b residue = the Free⊣Forgetful adjoint correction. Also `Wedge.Wedderburn`,
  `Semiring.Contraction`.
- **`Category/MultiscaleOctonionLoop.agda`** — the categorical loop layer.
- Durable: memories `project_cayley_dickson_generator`, `project_commuting_sphere`,
  `project_wedge_pentagon_sphere`.

## The key finding (same shape as the contrast doc's cyclotomic finding): it's an INSTANCE

The contrast doc's thesis for the cotype→Agda arm was "the gap is not a foreign tower — it's the same
wedge/gauge/projection/retraction structure, instantiated at the Φ_p/Frobenius region." The Agda→cotype
arm is the **mirror**: the commuting-sphere/Cayley–Dickson campaign is the **same generic
wedge / residue / Free⊣Forgetful / symmetric-monoidal structure**, instantiated at the
**division-algebra-doubling region**:

- the Hurwitz losses = the **wedge residue** (`never-discard-residue`; loss = kept remainder, not halt);
- the doubling = a **generator** (like `Free`/`unfold` — runs forever, the "wall" is a discarded residue);
- the KEYSTONE (residue = Free⊣Forgetful adjoint correction, `Wedge.Adjunction`) = the **same
  Free⊣Forgetful centre** as the cotype's gauge/retraction bridges AND as this session's Ⓤ arc
  (`FreeUP`, `eea-fold-unique`, `cofree-dual`).

So **both orphan arms are instances of one centre** (wedge/residue/Free⊣Forgetful). The cotype's bridge
checks already certify the cyclotomic instance; this campaign is the doubling instance. Re-noting it in
the cotype = recording that the Agda's division-algebra arc is the SAME structure its number-theory
region is — the Rosetta is bidirectional and the centre is shared.

## Contrast-doc update (the cotype→Agda arm is now substantially FILLED)

`cotype_pi_agda_contrast.md` listed the cotype→Agda gaps (cyclotomic Φ_p, the c=2 multiplicity, the
`WitnessTower`-fibered `mult`). The **Ⓕ.spectral arc has since built them**:
- `WitnessTower/PhiMultiplicity` — `mult2`/`nullity2`, `mult2-fibered` PROVEN (= the f090_2 family; the
  cotype even NAMED `WitnessTower` as its home).
- `Algebra/F2/Linear/{SpectralCycleDim, SpectralTower, SpectralCRT, SpectralCrossCoherent}` — the
  per-factor degΦ_p = dim ker Φ_p(σ_p), `nullity2 = mult2·degΦ`, composite order via CRT.
- `Algebra/Polynomial/Cyclotomic` (Φ via geomSum); the divisor-product `x^L−1 = ∏Φ_m` remains the one
  open primitive (Ⓕ.cyclotomic).
So the contrast's "B. NOT in Agda" column is now mostly the "already formalized" column. Both arms of
the symmetric coverage are now closeable: cotype→Agda (built), Agda→cotype (this note).
