# JEA Pi Cotype ↔ Agda substrate — contrast (formalities not yet in Agda)

Source: `cotype-rosetta.tgz` + `cotype-bridgefix.tgz` (extracted to scratch, NOT committed). The cotype is a
source to mine, not an artifact to home: decompose its **probe-verified** findings and contrast against the
Agda to surface formalities the cotype has established that Agda does not yet express.

## Audit (the prose↔probe Rosetta holds, on this machine)

39 checks green, all self-contained:
- **14/14** gold-bound finding checks (live recompute = committed gold).
- **21/21** content-sensitive `claim:` checks (numbers asserted in the *prose* reproduce on a live probe; corrupt the prose → the check flips).
- `refinement_map` (keyword spine refines onto T1/T2/T3); both `proofs/`.
- **4/4 bridge/wedge identities** (after `cotype-bridgefix`: `cotype.md` is now a real 535KB source, not a dangling /tmp symlink):
  - `gauge_identity`: **Σ Bézout gauge freedom = Φ_p multiplicity width** (Frobenius region).
  - `projection_identity`: Σ non-injectivity-in-projection = unsigned-P non-chain-map mismatch.
  - `retraction_identity`: Σ parse/quotient/exp retraction = C·P·Cᵖ⁻¹ frame-projection.
  - `frame_mismatch`: all three co-occur across the Σ/Frobenius regions.
- (External, not run: the `ratchet`/`closure` flow needs `~/github/paperkit` (WIP).)

## The contrast

The cotype has two regions; they land very differently against the 1563-module Agda substrate.

### A. Substrate-lowering (§18–29) — already formalized
| cotype theme | Agda |
|---|---|
| T2 EEA/Bézout residue, gauge, retention | `Algebra/Z/{Bezout,Coprime,Wedge}.agda`; `Category/.../QuotientProduct` |
| T3 g-calculus / Kirchhoff | `Logic/Evidence/ElAtlas*` (GValueAsQ, CenterWitness, StarIsGNot, OrbitCloud) |
| T3 torsor | `Cocycle.agda`, `Algebra/Torsor.agda` |
| T3 witness-tower | `WitnessTower/` |
| T1 grammar/SPPF | `ShadowArchitecture/Raven/Grammar.agda` (partial) |

### B. The domain object (§2–6) — NOT in Agda (the gap)
Keyword scan returns **(none)** for `cyclotomic`, `Φ_p`, `zeta`, `Ihara`, `Weil`, `face-action`, `p-cycle`.
The cotype's load-bearing, probe-verified findings are unexpressed:

1. **Cyclotomic Φ_m + the factorization x^L−1 = ∏_{m|L} Φ_m** (f072). The base object the whole domain needs; Agda has no cyclotomic polynomials. *Foundational gap.*
2. **Φ_p multiplicity on the cycle/edge lattice** (f089/f090): the (p,c)→mult table; c=1→0; for two p-cycles (c=2) **mult = (p−1)/2 = φ(p)/2**, nullity = (p−1)²/2. Verified p=3,5,7. *Cleanest formalization target — a lemma.*
3. **Face-action / arity climb** (f072/f085): the operator acts on the 1-face (edge) lattice, order = lcm(edge-orbit lengths); the unsuppressed prime **climbs with face-dimension** (edges→2, triangles→3).
4. **Graph-Weil / Ihara edge-zeta** det(I−Au+Du²), Bass functional equation u↦1/(qu), and where T (the cycle-space Frobenius) sits inside it (cotype §9, open).

## The key finding: it's an INSTANCE, not a foreign tower

The gap is **not** a foreign domain. The cotype's own bridge checks *prove* (probe-verified) that its
number-theory region is the **same wedge / gauge / projection / retraction structure** the Agda already
formalizes generically — just instantiated at the Φ_p/Frobenius region:

- Φ_p **multiplicity width** ≡ Bézout **gauge freedom** → the generic is the wedge gauge (`Algebra/Wedge`, the Bézout gauge in `Algebra/Z/Bezout`).
- face-projection **non-chain-map** ≡ non-injectivity-**in-the-projection** → the generic is the **split idempotent / wedge projection** (`project_split_idempotent_apex`, `Algebra/Quotient.split-Canonical`).
- Frobenius **frame-projection** C·P·Cᵖ⁻¹ ≡ the parse/quotient/exp **retraction** → the generic is the **retraction = split-Canonical** (same apex).

So **formalizing the gap = instantiating the existing Agda generics at the cyclotomic/graph-Weil region**, not
building number theory from scratch. This is the reuse-search discipline (name the generator the plan
instantiates) — and here the cotype's bridge *is the Rosetta* certifying the instance↔generic correspondence.

## Forward formalization targets (ranked)

1. **`Algebra/Polynomial/Cyclotomic.agda`** — Φ_m over ℤ + `x^L−1 = ∏_{m|L} Φ_m` (f072). Prerequisite for the rest; `Algebra/Polynomial/Graded` exists to build on.
2. **The c=2 multiplicity lemma** `mult(two p-cycles) = (p−1)/2 = φ(p)/2` (f090_2) — small, verified, and lands as a wedge-gauge-width instance. Needs Euler φ (likely already near `Algebra/Z`).
3. **Face-action operator order = lcm(edge-orbit lengths)** (f072) — a `GroupAction`/cycle-lattice statement; `Algebra/GroupAction.agda` is the home.
4. (Deeper, cotype-open) Ihara edge-zeta + Bass — only after 1–3.

## Bib study — the formal-claim corpus (5 .bib files)

The `.bib` files ARE the claim-DAG. Structure:
- `warrants.bib` (868): `section/claim/check/from`. Check-types: **841 `file`** (existence-note, backed by a process note — the ratchet's "840 honest existence-notes"), **21 `claim:`** (content-sensitive prose↔probe), **6 `cmd:`** (command-verified). So the *strongly formal* corpus is **27 claims**; the rest are existence.
- `warrants_sigma.bib` (157, all `file`): the Σ-arc lowering, sectioned **T1-forest 86 / T2-residue 43 / T3-navigator 28**.
- `warrants_kw.bib` (157, all `file`): keyword readings — **sppf-grammar 58 / metalanguage 35 / torsor-witness 22 / bezout-gauge 20 / interning 12 / kirchhoff 5 / obligation-spine 3 / foundations 2**.
- `warrants_bridge.bib` (5): the cross-arc thesis + 3 wedge identities + `bridge_absent_sphere`.
- `warrants_refinement.bib` (3): the keyword-spine ↔ T1/T2/T3 refinement map.

### The 27 probe-backed formalities (the actual formal claims)
Almost all sit in the **`inversion`/`object`/`arity`** sections — i.e. the **cyclotomic/face-action domain that is NOT in Agda**. Centerpiece is the `f090_2` family (the Φ_p multiplicity), which is a *closed-form theorem*, not a lone number:
- `f090_2_pinned` — c=2: `nullity=(p−1)²/2`, `mult=(p−1)/2=φ(p)/2` (p=3,5,7).
- `f090_2_generalized` — **`nullity(p,c)=(c−1)(p−1)(cp−p−1)/2`**, held-out-validated p=11,13, c≤7.
- `f090_2_grounded` — **`mult = p·C(c,2) − [(p−1)/2+1]·(c−1)`**, each term structural.
- `f090_2_strata` — crossing-basis: `mult = (p+1)/2 − (p+1)/2·c + p·C(c,2)`.
- `f090_2_argument` — the inference surfaced as a 5-step machine-checked lemma chain (not result-recompute).
- **`f090_2_tower` — "a FIBERED COUNT over the WitnessTower's rung-(c−1) simplex; the c p-cycles form a witness-tower"** → names `agda/Substrate/WitnessTower` as its Agda home.
- `f090_2_rosetta` — `mult(p,c)` has **four equivalent renderings**, "the cross-language comparison IS the content" (the theorem-level Rosetta).
- plus `f072_1/2` (face-action, cyclotomic factorization), `f085_4` (arity climb), `f089_*` (the data), `f093/f094` (frame-dependence), `f091_2` (cmd-verified, honestly un-bindable).

The 4 `cmd:` bridge claims + `refine_thesis` are the other strongly-formal entries.

### What the bib study changes about the contrast
1. **The forward target is sharper than "build cyclotomic from scratch":** `f090_2` is a *verified closed-form theorem family* whose Agda home the cotype **already names — `WitnessTower`** (the c p-cycles = a witness-tower; `mult` = a fibered count over rung-(c−1)). So target #2 lands as a `WitnessTower` instance, with cyclotomic Φ_p (target #1) as the one missing primitive.
2. **Bidirectional orphans** (the symmetric coverage, both arms): cotype→Agda gap = the cyclotomic/Φ_p/Weil domain; Agda→cotype gap = `bridge_absent_sphere` (the commuting-sphere/Cayley-Dickson campaign, *in* Agda, dropped from the cotype). The cotype's own bib flags the second.
3. **The 314 sigma/kw claims are the lowering map, not new math** — they assert correspondences to substrate themes already in Agda, organized by `refine_crossings` (sppf-grammar spans all three traces = the SPPF fusion point JEA interns through). They are the "already formalized" column, refined.
4. **The Rosetta is recursive:** `f090_2_rosetta` (4 renderings of one multiplicity) is the same prose↔probe↔proof correspondence we built `jea_oneforest` for, one level up — a theorem with four equivalent language-renderings, which is exactly a quotient-ladder of the *same* object.

## Note: graph-side partial overlap
`Logic/Evidence/ElAtlas/*` (OrbitCloud, CenterIsStar) IS graph-structural Agda, but it is the g-calculus /
Kirchhoff (nedge/Wheatstone) graph — NOT the cyclotomic spectral object. It anchors the T3 lowering, not the
graph-Weil findings; the spectral/zeta layer is genuinely new.
