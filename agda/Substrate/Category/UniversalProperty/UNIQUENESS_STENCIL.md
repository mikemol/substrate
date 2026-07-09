# The Lawvere Fixed-Point Uniqueness Stencil

*Externalized invariant (⟡uniqueness-stencil). The μ⊣ν uniqueness picture (ADD 185/186/187)
is not a one-off — it is a **stencil**: a reusable structure that cuts the same shape over
every Lawvere fixed-point in the substrate. This file is the durable statement of the
stencil, grounded against the substrate, with its instances (proved and candidate) and the
four-gate audit of the stencil-as-claim.*

---

## The stencil (the invariant)

> **Three layers, two frames, one Lawvere fixed-point.**

A **Lawvere fixed-point** is a self-reference/diagonal structure that is simultaneously an
INITIAL ALGEBRA (μ, the fold, map-OUT) and a TERMINAL COALGEBRA (ν, the unfold, map-IN) —
the two hinged by **Lambek's lemma** (`out`/`into` invert: one direction `≡`, the other
`~`). The substrate's own claim (`Category.Lawvere`): *"One theorem, every diagonal — and
every self-reference"* — Cantor / Gödel / Tarski / wedge-residue are ONE structure, with a
POSITIVE reading (`lawvere-fixed-point`: a reflexive object forces a fixed point =
metacircularity / self-reference) and a CONTRAPOSITIVE reading (`diag-not-in-family`: a
fixed-point-free endo forces a missed map = diagonalization).

Its **solver-uniqueness** decomposes into exactly three layers across two frames:

| Layer | Object | Frame | Uniqueness | Bound (Adm) | Substrate |
|-------|--------|-------|------------|-------------|-----------|
| **μ-fold**   | the fold (initial algebra map-out) | `≡` (inductive)   | UNCONDITIONAL | `Adm = ⊤` (the ≡-Witness self-determines) | `trace-fold-unique`; `mu-solver-unique` (185) |
| **ν-step**   | one unfold step (the wedge)        | `≡` (inductive)   | BOUNDED       | `Adm = r < b` (the halting/smallness gauge) | `wedge-witness-unique`; `nu-solver-unique` (186) |
| **ν-whole**  | the whole coinductive unfold (stream) | `~` (coinductive) | UP-TO-BISIM | (none — the terminal-coalgebra UP)         | `ana-unique`; `nu-whole-bisim` (187) |

**Two frames** = `≡` (the finite / halting / inductive reading, layers 1–2) vs `~` (the
unbounded / non-halting / coinductive reading, layer 3). This is exactly the **Lambek-iso
split** (`Final.agda`: "one direction `≡`, the other `~`"). The either/or "≡-uniqueness vs
bisim-uniqueness" **dissolves into the level**: it is ONE universal property (the Lawvere
fixed-point) read at two halting-levels, not two rival notions. `Final.agda` says it
directly — *bounded/halting: `≡`; unbounded/non-halting: `ana-unique`*.

**One Lawvere fixed-point** = the μ⊣ν adjunction is one adjoint structure hinged by Lawvere
(`Final.agda`: μ/ν "are one adjoint structure hinged by Lawvere"); the fold and the unfold
are the two halves of the same diagonal.

---

## Why it is a STENCIL, not a description (the ≥2-instances audit)

A stencil must cut the same shape over ≥2 distinct fixed-points, or it is just a description
of one. Grounded against the substrate, the structure recurs over at least three genuine
Lawvere fixed-points:

1. **The trace/wedge fixed-point** — `Trace` (μ, initial Φ-algebra) ⊣ `RealTrace` (ν,
   terminal coalgebra). Uniqueness: fold `≡`-uncond (185) ⊣ wedge `≡`-bounded (186) ⊣
   stream `~`-bisim (187). *All three layers PROVEN.* This is the reference instance.

2. **The Kleene fixed-point** — `μΦ = ⋃ₙ Φⁿ⊥ ≅ Trace` (the colimit, 159; the `≅`/`≡`
   side) ⊣ `νΦ = limit` (162; the `~` side), Lambek-hinged (`TraceKleeneColimit`: "Trace
   is the INITIAL Φ-algebra = μΦ … the ν-half (RealTrace ≅ νΦ)"). Same two frames, same
   fixed-point; the layers are the colimit/limit readings. *Colimit ≅ Trace proven; a
   full three-layer uniqueness restatement is the candidate work (⟡kleene-stencil).*

3. **The combinator-Y fixed-point** — `ExtruderFix`: `HasFix = Σ fix. (f) → fix·f ≡
   f·(fix·f)`, `FixFromDiagonal`, `fixpoint-from-diagonals` — the SKI Y-combinator, via
   the SAME Lawvere diagonal (`lawvere-fixed-point` positive reading). This is the
   **X8a extruder's own fixed-point**. Its soundness is a universal property, so it is a
   stencil instance in waiting: **X8a-as-backedup** = the μ-fold layer (the extruder IS
   the fold to the fixpoint filter), with the reduction confluence (Newman/Bisim over the
   Trace) as the `~` layer. *This is exactly ⟡X8a-iter — the extruder is the THIRD
   registered solver, stencilled onto layer μ (existence + ≡-uniqueness) with a `~`
   confluence layer.*

So: **one proven instance (trace/wedge), one partially-proven (Kleene), one in waiting
(combinator-Y = the extruder).** The stencil cuts ≥2 shapes → it IS a stencil.

---

## The stencil as a claim — four gates

- **Constructible.** The reference instance is fully built and typechecks: `mu-solver-unique`
  (185), `nu-solver-unique` (186), `nu-whole-bisim` (187), all `--safe --without-K`
  (`--guardedness` for layer 3), zero postulate. The stencil is their common shape, read off
  grounded modules — not imposed.
- **Reachable.** Each layer is a named substrate universal property instantiated, not
  hand-rolled: `trace-fold-unique` / `wedge-witness-unique` / `ana-unique`, unified by
  `Category.Lawvere`'s one-diagonal claim + `Final.agda`'s Lambek split. The stencil is
  reached by reading the substrate's OWN organizing statements, not by external synthesis.
- **Observable.** The stencil fires: it correctly predicts the Adm of each layer (⊤ /
  smallness / none) and the frame of each (≡ / ≡ / ~) for the reference instance, AND it
  correctly classifies the Kleene and combinator-Y fixed-points as further instances with
  the same two-frame hinge (grounded above). The prediction "the extruder is layer-μ of the
  combinator-Y fixed-point" is the observable, falsifiable content that guides ⟡X8a-iter.
- **Coverable — boundary.** The stencil covers the uniqueness of any Lawvere fixed-point in
  the substrate that presents both a fold and an unfold. NOT covered (scoped, honest): a
  fully ABSTRACT Agda module quantifying over "any Lawvere fixed-point" and deriving the
  three layers generically — that needs the fixed-point presented as a formal
  (initial-algebra, terminal-coalgebra) pair with a Lambek iso, which the substrate has
  per-instance but not yet as one generic interface (⟡uniqueness-stencil-abstract). The
  stencil here is the SPECIFICATION + the instance-catalogue, not yet a generic functor.

---

## Residue (kept)

- **⟡uniqueness-stencil-abstract** — the generic Agda module (quantify over any
  Lawvere fixed-point presented as (μ, ν, Lambek) and derive the three layers). Needs a
  generic fixed-point interface the substrate has per-instance but not yet unified. The
  honest reason it is not done here: the substrate's fixed-points (trace, Kleene, Y) are
  presented in DIFFERENT concrete forms (Trace/RealTrace; Φ-colimit/limit; combinator ·),
  so the generic interface is a real abstraction task, not a wrap.
- **⟡kleene-stencil** — restate the Kleene fixed-point (159/162) as an explicit three-layer
  instance (colimit ≅ / limit / bisim), completing the second proven instance.
- The Lambek-iso `~`-direction is the coinductive half (Final.agda) — the `≡` and `~`
  frames are NOT symmetric (one direction of the iso is `≡`, the other `~`), which is WHY
  layer 3 is `~` not `≡`. This asymmetry is the stencil's load-bearing content, not a defect.

---

## The one-line stencil

> **Every Lawvere fixed-point's uniqueness = { fold `≡`-unconditional | step `≡`-bounded |
> whole `~`-bisim }, two frames (`≡` halting / `~` non-halting) hinged by Lambek, one
> diagonal.** The extruder (⟡X8a-iter) is the combinator-Y instance's μ-layer — the third
> registered solver, cut by the same stencil.

---

## Does the stencil form a groupoid? (⟡stencil-groupoid — machine-checked, StencilGroupoid.agda)

Not yes/no — **which structure**. The either/or dissolves into the LEVEL at which the
groupoid lives:

- **YES at the frame level.** Each of the two frames is a groupoid (a setoid-as-groupoid =
  an equivalence, every morphism/proof invertible by `sym`):
  - the **≡-frame**: `≡` is refl/sym/trans (`Foundation.Eq`) — the equality groupoid.
  - the **~-frame**: `~` is refl/sym/trans — the bisim groupoid. `Bisim` (169) had only
    `~-refl`; **`~-sym`/`~-trans` are supplied in `StencilGroupoid.agda` (coinductively),
    completing the ~-frame as a groupoid** (machine-checked, `--guardedness`).
  - the **wedge-iso layer** is the substrate's EXPLICIT funext-free groupoid
    (`Wedge.IsoGroupoid`: `iso-sym` + `≈ʷ-invˡ/invʳ`, "every morphism invertible").
- **The uniqueness IS a contractibility.** "Unique up to (unique) iso" (185/186/187) = each
  fixed-point's solution-groupoid is contractible: μ-fold up to `≡`, ν-step up to
  `≡`-bounded, ν-whole up to `~`. The stencil's uniqueness content is precisely the
  contractibility of the solution-object in its frame-groupoid.
- **NO at the transport level.** The category of registered solvers (`BackedCategory`, 181)
  is NOT a groupoid — `count⇒eq` (182, σ = `count-solve`) has no inverse. These non-iso
  arrows ARE the **groupoid-distance** (IsoGroupoid's own invariant): how far the
  solver-transport sits from the underlying iso-groupoid.

**The Lambek iso is the invertible hinge BETWEEN the frames** (`≡` one way, `~` the other) —
an iso in the combined groupoid, invertible up to the frames' equalities, NOT strict `≡` on
the underlying functions. This is the SAME answer as the funext question (181): the
substrate's invertibility always lives up to the pointwise/bisim equality, never strict `≡`.

So the stencil's groupoid is the **Lambek-hinged pair of frame-groupoids (≡ and ~)**, in
which each fixed-point's solution is a contractible object; the transport of solvers across
fixed-points is a category with genuine non-iso arrows, not a groupoid.

---

## The third instance: the stencil as a fixed point of itself (⟡fixpoint-stencil, FixpointStencil.agda)

*Question (operator): the stencil relates two framings; we have two instances; what is the
stencil instance where those two instances are THEMSELVES the two framings?*

The two existing instances are two **characterizations of the same fixed-point**:

- **trace/wedge** (185/186/187) = the **algebraic** framing: `Trace` = initial Φ-algebra,
  `RealTrace` = terminal coalgebra (the universal-property / map framing).
- **Kleene** (159/162, `KleeneStencil` 188) = the **iterative** framing: `μΦ = ⋃ₙ Φⁿ⊥`
  (colimit, ascending from ⊥), `νΦ = ⋂ₙ Φⁿ⊤` (limit, descending from ⊤) — the
  chain/approximation framing.

**The third instance is the fixed-point-CONSTRUCTION's own characterization-independence**:
the object that is the same fixed-point *however you build it* (algebraic = Kleene). Its two
frames are the two instances, related **level-wise** by the meta-Lambek hinge (machine-checked
in `FixpointStencil.agda`):

| Frame | Level | Hinge | Status |
|-------|-------|-------|--------|
| **≡** | μ (finite/halting) | algebraic `Trace` ≅ Kleene `Colim` (`Colim ≅ Trace`, 159, BOTH directions) | EXACT, proven |
| **~** | ν (non-halting) | algebraic ν below Kleene `Limit` (`coalg-below-limit`, 162; greatest-fixed-point UP) | UP-TO, delivered; full `RealTrace ≅ Limit` scoped |

The **one Lawvere fixed-point**: the construction operator `Fix` itself, whose
self-application — *the fixed point is the fixed point however built* — is the diagonal.

**The tell that this is genuine, not forced**: the third instance reproduces the base
stencil's OWN ≡/~ asymmetry — **exact on the μ/≡ side, partial/up-to on the ν/~ side**. The
stencil applied to its own two instances *cuts the same shape again*. So **the stencil is a
FIXED POINT OF ITSELF**, self-similar under "frame the two framings as one framing" — which
is exactly what makes the meta-instance a genuine Lawvere fixed-point (the diagonal = the
construction naming itself). The either/or "is the third instance new, or just the stencil
again?" dissolves: it is the SAME stencil (self-similar), and that self-similarity IS the
fixed point.

So the answer to "which instance has the two instances as its framings" is: **the instance
whose fixed-point is Fix itself** — algebraic-μ ≅ Kleene-μ on the nose (the ≡ frame),
algebraic-ν below Kleene-ν up-to (the ~ frame), hinged by `Colim ≅ Trace`. The stencil
stencils itself.

---

## The generic stencil, cross-form (⟡uniqueness-stencil-abstract — StencilAbstract.agda)

The cross-form difficulty — the two framings' carriers differ (Trace/RealTrace coinductive
vs Kleene `Fam`), so a naive generic module must unify them — is **dissolved by the
arrow-category / HetQ cross pattern** (`Algebra.Q.HetBasis`, `Algebra.Wedge.CrossMul`),
grounded in the repo, not guessed:

- **`CrossMix A B R`** (`Wedge.CrossMul`) is a **cospan**: `A →(embA) R ←(embB) B` — two
  DIFFERENT carriers each `Bridge` into a common `R`, meeting via `cross a b = embA a · embB b`
  *in R*. The carriers are never identified.
- **`HetQ A B`** (`HetBasis`) holds `hnum : A`, `hden : B` in DIFFERENT carriers; `CrossEq`
  gives `p ≈H q = (hnum p ⊗ hden q) ≈R (hnum q ⊗ hden p)` — equality via cross-multiply into
  common `R`, **refl/sym generic, trans (the hinge) supplied per instance**.

`StencilAbstract` mirrors `HetBasis.CrossEq` exactly. `StencilAgreement` is parameterized
over two DISTINCT framing-carriers `A, B`, a cross `⊗ : A → B → R` into a common frame `R`,
and a frame-relation `≈R`. A `Framed` object is an A-framing + a B-framing of the same
fixed-point (`HetQ A B`); `p agrees q = (fA p ⊗ fB q) ≈R (fA q ⊗ fB p)` is the cross-equality;
`agrees-refl`/`agrees-sym` are GENERIC. So:

- **The two framings are two cospan legs, NOT one unified carrier.** This is why the repo is
  grounded in arrow categories + allegory: heterogeneous objects are related THROUGH a
  common frame, never forcibly identified.
- **The per-source layers (μ-fold, ν-step) are the ≡ legs**; the **ν-whole (map-level) layer
  is the cross relation itself** — abstracted polymorphically, exactly the operator's point:
  "abstract over the carriers polymorphically" rather than unify Trace vs RealTrace.
- The concrete `TwoFraming` record (`FixpointStencilRecord`, the Fam-form) is the `R = Fam`
  specialization; the coinductive Trace/RealTrace framing is another cospan leg into the same
  generic shape. The hinge (trans / the nontrivial cross-cancellation) is per-instance, as
  `HetBasis` does for ℚ.

Machine-checked: `StencilAgreement` instantiates with genuinely heterogeneous carriers, the
cross-equality computes concretely, and generic refl/sym fire — the abstraction is real, not
vacuous. The cross-form problem is dissolved by CrossMul/HetQ, the substrate's own pattern.

---

## The cospan's either/or is a commute in the allegory (⟡stencil-allegory, StencilAllegory.agda)

The cospan `A →(embA) R ←(embB) B` is itself an either/or — the two legs, the A-vs-B
direction — and it **commutes**. Grounded in `Category.Allegory` (the repo's real allegory:
`Rel A B = A → B → Set`, converse `_†` with `†-invol`/`†-comp`, meet `_∧_` as GLB,
composition `_⨾_`, and `graph f` = functions-as-maps, `isMap = entire × deterministic`):

- **The commute (machine-checked):** the stencil's cross-relation `agrees` is a genuine
  allegory `Rel`, and its symmetry (`agrees-sym`, 192) IS **self-converse** — `agree † ≈
  agree` (`agree-self-converse`). The A-vs-B / forward-vs-backward direction dissolves into
  ONE symmetric relation read both ways (the converse involution). This is the allegory
  statement of "the cospan commutes."
- **The map-vs-relation either/or also commutes:** a function becomes a relation via `graph`
  (`graph f a b = f a ≡ b`), an allegory MAP (`entire × deterministic`). "Function or
  relation?" dissolves — a function IS a relation (its graph), the degenerate coreflexive
  case. The comment in `Maps` names it: the map condition is "Φ landing on a singleton," the
  recursion's bottom.

**The allegory is the category-theoretic name for the whole pattern** — relations, functions,
spans, cospans, the refinement order `⊑ᶠ`, the cross `⊗`, the HetQ `≈H` — all as allegory
morphisms, and every either/or among them (relation vs function, A vs B, forward vs converse)
is a **commute** in it (via converse, meet, the modular law), never a choice. This is *why*
the repo is grounded in arrow categories + allegory: heterogeneous objects related through a
common frame, the either/ors dissolved into commutes, never forcibly identified. The stencil's
cross-relation is a symmetric allegory relation — a groupoid (189) = self-converse here — and
the commute IS the invariant.

---

## The modular law — where the either/or-dissolutions bottom out (⟡stencil-modular, StencilModular.agda)

The **modular law** (`Category.Allegory.modular`, "the gate that earns 'allegory'") is the
one identity making converse + meet + composition cohere:
`(R ⨾ S) ∧ T ⊆ (R ∧ (T ⨾ S†)) ⨾ S` — proven in the repo (a constructive Σ/×-rearrangement).

- **Instantiated at the stencil's cross-relation** (`stencil-modular = modular agree agree
  agree`): the stencil's `agree` participates in the FULL allegory coherence, not just the
  converse commute (193). Machine-checked on the concrete 192/193 agreement.
- **Self-contained under symmetry:** because `agree` is self-converse (193; witnessed both
  ways by `agree†→agree` / `agree→agree†`), the modular law's `S†` term collapses to `agree`
  — the coherence closes ENTIRELY within the symmetric cross-relation (a groupoid, 189).

**This is where the recursion of either/or-dissolutions bottoms out.** Every either/or the
stencil touched — relation vs function, A vs B, forward vs converse, root vs log — is a
commute (193), and ALL those commutes COHERE via the one modular identity. The substrate's
`residual-duality` (`(R ∖ T)† ≡ R†／T†`, "left and right division are not two choices but the
same residual seen through †") is the same dissolution made a theorem elsewhere: the
modular/residual structure IS the either/or-dissolution mechanism, named
category-theoretically. The stencil's `agree` is a symmetric relation satisfying the modular
law — an allegory-coherent equivalence, the invariant the recursion bottoms out at.

---

## The cross-relation is an idempotent equivalence (⟡stencil-modular-app, StencilModularApp.agda)

The stencil's `agree` is **idempotent** (`agree ⨾ agree ≈ agree`) — and the honest
decomposition (a scope-correction of the earlier "use the modular law to derive it"):

- **⊇** (`agree ⊆ agree ⨾ agree`, `agree-below-square`): GENERIC from **reflexivity**
  (`agrees-refl`, 192). Any related pair `(p, r)` factors through `q = p`. No hinge.
- **⊆** (`agree ⨾ agree ⊆ agree`, `square-below-agree`): IS **transitivity** — the
  per-instance hinge (192), supplied by the concrete stencil (as `HetBasis`'s trans is the
  cross-cancellation). Given it, `agree-idempotent` follows.

So **idempotence = refl (⊇) ⊕ trans (⊆)**, the same refl/sym-generic, trans-per-instance
split as `HetBasis.CrossEq`. The modular law (194) is the ambient allegory **coherence**
(where `⨾`/`∧`/`†` cohere), NOT the deriver — idempotence follows from refl+trans
specifically.

Combined across the arc: `agree` is refl+sym generic (192), self-converse commute (193),
modular-coherent (194), idempotent (here) — a symmetric reflexive transitive idempotent
relation, i.e. **a full allegory equivalence** (the groupoid of 189 at the relation level).
The either/or "idempotence generic vs per-instance" dissolves into WHICH DIRECTION: ⊇ generic
(refl), ⊆ per-instance (trans). The invariant the recursion settles on is: the stencil's
cross-relation is an equivalence in the modular allegory.

---

## The cross-relation is difunctional — and the modular law bottoms out (⟡stencil-modular-difunc, StencilModularDifunc.agda)

The stencil's `agree` is **difunctional** (`agree ⨾ agree† ⨾ agree ≈ agree`) — and, continuing
the honest correction (the fourth), this does NOT genuinely use the modular law:

- **⊇** (`agree ⊆ agree ⨾ agree† ⨾ agree`, `agree⊆difunc`): ALWAYS true (diagonal witnesses,
  reflexivity) — generic for any reflexive relation.
- **⊆** (`agree ⨾ agree† ⨾ agree ⊆ agree`, `difunc⊆agree`): from **symmetry** (`agree† ⊆
  agree`, 193) + **transitivity** (the hinge) — NOT the modular law.

So **both idempotence (195) and difunctionality (here) of `agree` follow from its being an
EQUIVALENCE** (refl/sym/trans), not from the modular law. The recursion "what fresh property
does the modular law give the stencil's `agree`?" **bottoms out**: nothing — `agree` is
already the strongest relational structure (an equivalence), self-sufficient from
refl/sym/trans. The modular law (194) is the ambient allegory **coherence** `agree` lives IN,
genuinely used only on NON-equivalence relations (maps — the cross `⊗` as a function in the
abstract allegory, `⟡stencil-modular-map`). The either/or "difunctionality via modular vs via
equivalence" dissolves: for an equivalence it is via the equivalence structure; the modular
law is where that structure coheres, not a source of new properties.

**`agree` is a difunctional idempotent symmetric reflexive transitive relation — a full
allegory equivalence, and every consequence flows from that.** That is the settling point of
the whole cross-relation arc (192→195).

---

## Where the modular law genuinely bites: maps preserve meets (⟡stencil-modular-map, StencilModularMap.agda)

After four findings that the modular law is the *backdrop* for `agree`'s equivalence
properties (195/196), HERE is its genuine bite — on a **map**, not an equivalence:

- **Maps preserve meets** (`map-preserves-meet`): for a deterministic `f`,
  `f ⨾ (S ∧ T) ≈ (f ⨾ S) ∧ (f ⨾ T)`. The `⊆` is monotonicity (all relations); the `⊇` is
  the genuine content — abstractly `(f ⨾ S) ∧ (f ⨾ T) ⊆ f ⨾ (S ∧ (f†⨾f⨾T))` [modular/Dedekind]
  then `f†⨾f ⊆ idR` [determinism] collapses to `f ⨾ (S ∧ T)`. Concretely, determinism forces
  the shared middle (`det a b b'`), doing the collapse directly; the modular route is the
  abstract equivalent.
- **The stencil's cross `⊗` is a map** (`cross-preserves-meet`): its graph is deterministic
  (`graph-det`), so meet-preservation applies to the cross — machine-checked at `⊗ = ℕ *`.

**The either/or "the modular law is idle vs essential" dissolves into WHICH RELATION**: idle
on equivalences (`agree` gets everything from refl/sym/trans, 195/196), essential on maps
(`⊗` preserves meets BECAUSE it is deterministic, the modular law the abstract route). This
completes the modular-law picture of the stencil: `agree` the equivalence (192–196, modular =
coherence backdrop) and `⊗` the map (here, modular = the deriver of meet-preservation) — the
two allegory roles (the `isMap` either/or: relation vs map) each with the modular law in its
proper place. Honest nuance: in concrete Rel the `⊇` is provable by witnesses (determinism);
the modular law's *irreducible* use is inherently abstract (axiomatic allegory, no witnesses).

---

## Meet-preservation is a chirality-opposed stencil instance (⟡stencil-dedekind, StencilDedekind.agda)

Meet-preservation (197) is *itself* a stencil instance — its two directions are two framings,
**chirality-opposed under the converse `†`**:

- **Framing 1 — monotonicity** (`meet-mono`, the free/generic side): `f ⨾ (S ∧ T) ⊆
  (f ⨾ S) ∧ (f ⨾ T)`, holds for ALL relations. The "≡-exact" hand.
- **Framing 2 — Dedekind** (`meet-dedekind`, the structured side): `(f ⨾ S) ∧ (f ⨾ T) ⊆
  f ⨾ (S ∧ (f†⨾f⨾T))`, the modular content, needing the map (determinism collapses `f†⨾f ⊆
  idR` to reach `f ⨾ (S ∧ T)`). The "~-partial" hand.

The chirality is the **`†` involution**: the Dedekind form (`dedekind`, modular-2) is the
substrate's base modular law (modular-1) seen through the converse — witnessed by the two
chirality lemmas `†-∧` (converse over meet, newly derived — the substrate lacked it) and
`†-comp` (converse over `⨾`). So the mirror relating the two framings is the same `†` that
gives self-converse (193) and residual-duality (194, "left/right division = one residual
through `†`").

**The either/or "monotonicity vs Dedekind" dissolves into the two chiral hands of one
meet-preservation, related by `†`**: monotonicity the free hand (any relation), Dedekind the
structured hand (the map). This is the stencil again, self-similar (190): a fixed point (the
`≈`), two framings (free/structured), one mirror (`†`) — the ≡-exact/~-partial asymmetry
realized as free-vs-structured, the Lambek/converse hinge realized as the chirality. The
stencil stencils even its own modular proof.

---

## The point-free collapse — closing the seam (⟡dedekind-collapse, StencilDedekindCollapse.agda)

The fully **point-free** meet-preservation ⊇ closes the seam between 197 (which proved it
*concretely*, determinism forcing the shared middle) and 198 (which exposed the Dedekind
*landing* `f⨾(S ∧ (f†⨾f⨾T))` abstractly):

- **`residual-collapse`**: `f† ⨾ (f ⨾ T) ⊆ T` — via `⨾-assoc` → `f†⨾f ⊆ idR` (determinism,
  `det→incl`) → `idR⨾T ≈ T`. The residual term collapses *because* `f` is a map.
- **`map-meet-⊇-pointfree`**: `(f⨾S)∧(f⨾T) ⊆ f⨾(S∧T)` = `meet-dedekind` (198) then
  `⨾-mono-r (∧-mono-r residual-collapse)` — no witness-casing.

The derived glue (`⨾-mono-l`/`⨾-mono-r`/`∧-mono-r`/`det→incl`) is the monotonicity the
substrate did not name, now assembled. So **197 and 199 prove the *same* ⊇** — one by
witness-casing, one point-free — and they meet in the middle. The point-free one is the
genuine irreducibly-abstract modular use: the modular law (via the Dedekind form) + the map's
determinism, assembled without unfolding. **The either/or "concrete determinism vs abstract
modular" dissolves**: they are the two proofs of one ⊇, the chirality (198) resolved at the
proof level. The modular-law picture is now complete *and* its abstract assembly is
machine-checked — `agree` the equivalence (192–196), `⊗` the map (197 concrete, 198 chiral,
199 point-free abstract).

---

## The full point-free ≈ (⟡dedekind-full-pointfree, StencilDedekindFull.agda)

Maps preserve meets, proven **entirely point-free**, both hands (`map-preserves-meet-pointfree`):

- **⊆** (`map-meet-⊆-pointfree`): monotonicity via the meet GLB — `f⨾(S∧T)` lands below each
  of `f⨾S`, `f⨾T` (`⨾-mono-r` on the projections), so below their meet (`∧-greatest`). No split.
- **⊇** (`map-meet-⊇-pointfree`, 199): the Dedekind form + determinism collapse.

No witness-casing on either side. This completes the chirality picture at the proof level:
the two directions are the two chiral hands, both now proven point-free through the allegory's
own operations — monotonicity the free hand (GLB), Dedekind the structured hand (modular + the
map). The concrete version (197) and this prove the same `≈`; the either/or "concrete vs
point-free" dissolves into two proofs of one fact, both machine-checked. The modular-law
picture is complete and fully assembled: `agree` the equivalence (192–196), `⊗` the map
(197 concrete, 198 chiral, 199 ⊇-pointfree, here ≈-pointfree).

---

## The chirality as †-functoriality (⟡dedekind-via-dagger, StencilDedekindDagger.agda)

The Dedekind form (modular-2) is derived **mechanically** from the substrate's `modular`
(modular-1) by transport through the converse `†` — making 198's observation ("modular-2 is
modular-1's `†`-mirror") a theorem:

- **`dedekind-via-†`**: instantiate modular-1 at `(Q†, P†, U†)`, apply `†-mono` (the converse
  is order-preserving), and align the LHS/RHS by the `†` laws (`lhs≈`/`rhs≈`, built from `†-∧`,
  `†-comp`, `†-invol`). No witness-casing — pure `†`-functoriality.

Both 198's direct `dedekind` and this transported `dedekind-via-†` inhabit the *identical*
modular-2 signature (machine-checked). So **the chirality-opposition (198) is now a theorem**
(the `†` image), not just an observation. The either/or "modular-1 vs modular-2" dissolves:
they are one law seen through `†`, exactly as residual-duality (194, "left/right division =
one residual through `†`") and self-converse (193). **The `†` involution is *the* mirror; the
two modular forms its two hands; the transport the mechanical proof of the chirality.** The
derived `†`-functor glue (`†-mono`, `⨾-cong`, `∧-cong`, `≈-trans`/`sym`) is upstreamable
(`⟡allegory-mono-upstream`). The stencil's chirality bottoms out at `†`-functoriality.

---

## The allegory glue upstreamed (⟡allegory-mono-upstream, Category/Allegory/Mono.agda)

The `†`-functor / monotonicity / congruence lemmas — assembled ad hoc across the Dedekind
sub-arc (198–201) — are consolidated into a **canonical home**, `Category.Allegory.Mono`, a
sibling of `Allegory.Maps`/`Division`/`Power`/`Refinement`/`Trace`. Genuine additions the core
`Category.Allegory` lacked as named lemmas:

- **`≈` is an equivalence** (`≈-refl`/`≈-sym`/`≈-trans`).
- **`†` is an order-preserving functor over meet** (`†-mono`, `†-cong`, `†-∧`).
- **`⨾` monotone/congruent** (`⨾-mono-l`/`r`/`⨾-mono`/`⨾-cong`).
- **`∧` monotone/congruent** (`∧-mono-l`/`r`/`∧-mono`/`∧-cong`, via the core GLB lemmas).
- **determinism as inclusion** (`det→incl`: `f†⨾f ⊆ idR`).

All `--safe --without-K`, zero postulates — one-line Σ/×-manipulations or reductions to the
core GLB. Verified the upstream **serves its consumer**: `StencilDedekindDagger` was deduped to
import the glue from `Allegory.Mono` (local defs removed) and still proves `dedekind-via-†`
(the same modular-2). The remaining downstream modules (`StencilDedekind`, `StencilDedekindCollapse`)
can be deduped likewise (`⟡allegory-downstream-dedup`), deferred to keep them working here.

---

## Downstream deduplicated (⟡allegory-downstream-dedup, all four Dedekind modules)

The consolidation from 202 is completed: all four Dedekind-sub-arc modules now import the glue
from `Category.Allegory.Mono` — **zero local glue definitions remain**. The coordinated dedup
followed the dependency graph:

- `StencilDedekind` — removed local `†-∧` (used only downstream).
- `StencilDedekindCollapse` — removed local `⨾-mono-l`/`r`/`∧-mono-r`/`det→incl`, imports from `Mono`.
- `StencilDedekindDagger` — imports `†-∧` from `Mono` (dropped the `StencilDedekind` import).
- `StencilDedekindFull` — imports `⨾-mono-r` from `Mono` (kept `map-meet-⊇-pointfree` from `Collapse`).

Verified: all four compile, and the theorems (`dedekind`, `dedekind-via-†`,
`map-preserves-meet-pointfree`) still prove. The glue lives in exactly one place. The
shadow-engineer residue (per-module glue) is now fully resolved into `Category.Allegory.Mono`
— a single canonical home, no duplication.

---

## Registry merge: a scope-correction, not a merge (⟡canonical-registry-merge → ⟡registry-cons-idiom-is-canonical)

`⟡canonical-registry-merge` proposed merging the arc's downstream registry conses
(`shape-registry`, `nu-registry`, …) into the base `Category.UniversalProperty.Registry`'s
`registry` list. **Grounding the actual state shows this is mis-scoped** — the honest
resolution is a scope-correction, not a merge:

- The base `registry = eq-backed ∷ Z3-backed ∷ Z5-backed ∷ crt-backed ∷ []` is **tracked and
  self-contained** (imports only tracked modules).
- The `X ∷ registry` cons is the substrate's **documented, deliberate idiom** — the base
  `Registry.agda` header itself prescribes it (`verdict-registry = bias-coeq-backed ∷
  registry`), and **8 modules** use it (`count`/`deferred`/`f2mod`/`freeMonoid`/`limit`/`mu`/
  `nu`/`shape`). Consing where each `BackedUP` is *defined* keeps its non-vacuity proof local
  — which is the registry's stated invariant ("REALLY backed... AND TYPECHECKS").
- **Merging would break self-containment**: the base `Registry.agda` would have to import the
  arc's untracked backing modules (`FoldRegistry`, `MuBacked`, `NuBacked`, …) — the opposite
  of the clean, tracked-only `Category.Allegory.Mono` upstream.

So the either/or "merge into base vs leave scattered" dissolves into the invariant the repo
already encodes: **the base list is the canonical seed; per-solver conses are the intended
extension mechanism**, not debt. The correct upstream (if any) is the *reverse* of a merge:
promote individual backing modules to tracked homes first, each keeping its own cons — the
list is never centralized. `⟡canonical-registry-merge` is retired; the standing item is
`⟡registry-cons-idiom-is-canonical` (the finding: the cons idiom is the architecture).

---

## The extruder registered (⟡x8a-backed, X8aBacked.agda + X8aRegistry.agda) — THE CAPSTONE

The extruder — the reduction-to-fixpoint run (`S5Fixpoint.Machine.run`, the python x7
`_reduce_step` formalized) — is now a **`BackedUP`**, the **third solver** joining μ
(`MuBacked`, the initial-algebra fold) and ν (`NuBacked`, the terminal-coalgebra unfold):

- **`x8a-UP`** — Source = `(fuel , start)`; Target = ℕ; Witness `s v = v ≡ run fuel start`
  ("the value IS the fixpoint/normal-form the reduction reaches").
- **`x8a-solve = run`** — step via `next` until a fixpoint. **`x8a-solves = refl`** (the run
  computes it). **`x8a-contentful`** — `(1,1) ↦ 1 ≠ run 1 1 = 0`, so the UP is non-vacuous.
- **`x8a-backed : BackedUP`** — the common bridge (arrow/solve/solves/content), identical in
  shape to μ/ν, differing only in that its solver is the **fixpoint run**.
- **`x8a-registry = x8a-backed ∷ registry`** — the canonical cons idiom (the registry's own
  documented extension mechanism, not a central merge), certifying the extruder by TYPING as
  a real, non-vacuous solver.

So the μ⊣ν pair gains its third member: **fold** (initial algebra), **unfold** (terminal
coalgebra), and **run** (the fixpoint machine) — all three backed by the common solve-bridge,
all non-vacuous by typing. Existence is registered unconditionally (as μ/ν register
fold/unfold existence); the ≡-uniqueness is FUSep's SKI Church-Rosser upstream. The extruder's
whole foundation was grounded upstream across ADD 208/210/211 (combinator infra + FUSep SKI-CR
+ ObsBisim ~-frame + S5 fixpoint-machine); `x8a-backed` is the one BackedUP that assembles it.

---

## The extruder's ≡-uniqueness (⟡x8a-uniqueness, X8aUnique.agda) — two honest layers

The extruder BackedUP (x8a-backed, ADD 212) registered EXISTENCE unconditionally. Its
≡-uniqueness is placed HONESTLY in two layers, mirroring NuBacked's existence/uniqueness split:

- **① run-value `WitnessUnique` (Adm = ⊤, the μ-mirror)** — x8a's Witness `v ≡ run fuel start`
  self-determines v (run is a function), so two witnesses coincide unconditionally:
  `x8a-witness-unique s t₁ t₂ _ _ w₁ w₂ = trans w₁ (sym w₂)` — exactly `mu-witness-unique`.
  `x8a-solver-unique` then gives: any admissible t witnessing s IS the run's output.
- **② confluence-uniqueness (`cr-nf-unique`, the deeper half)** — a normal form is unique BY
  Church-Rosser. Abstract over the CR frame (`⇒*`, `Converge`, `CR` — exactly FUSepQCR.Newman's
  telescope): if `a ⇒* b`, `a ⇒* c`, and b, c are Normal, then `b ≡ c`, via
  `trans (sym (nb d …)) (nc d …)` on the common reduct. So the run's fixpoint is
  path-INDEPENDENT: `solve` computes THE canonical normal form.

Layer ② is the genuine content FUSep's SKI-CR (`FUSepQCR.newman : WCR + SN ⟹ CR`) supplies.
It is kept ABSTRACT (parameterized over the CR frame) because `FUSepQCR` compiles with
`--guardedness` while X8aUnique is `--safe --without-K` — so the concrete FUSep instantiation
happens at the `⟡x8a-ski-instance` seam (verified: `CRUnique` instantiates at the exact
Newman telescope). The ℕ demonstrator's `next` is deterministic, so ITS confluence is trivial;
the CONTENT lives at the branching SKI reduction. Existence (212) ⊕ uniqueness (here) ⟹ the
extruder is "THE" solver, joining μ/ν in the full honest frame.

---

## The confluence-uniqueness landed at real SKI (⟡x8a-ski-instance, X8aSkiInstance.agda)

Layer ② of the extruder's uniqueness (the abstract CR ⟹ unique-NF principle, X8aUnique.CRUnique,
ADD 213) is now instantiated at FUSep's **concrete SKI Church-Rosser** — at the `--guardedness`
seam 213 identified:

- **`SkiCR.ski-CR`** — FUSep's `sn-confluent` (`FUSepQCR.newman` at the SN term's `Acc` over the
  shedding step `↦`): given local confluence `WCR↦` and `SN t`, multi-step peaks converge.
- **`SkiNfUnique.ski-nf-unique`** — `SN ⇒ t → t ⇒* b → t ⇒* c → Normal b → Normal c → b ≡ c`:
  a real SKI term's shedding-normal-form is **unique** (path-independent), proved directly from
  `sn-confluent` at the SN root (`trans (sym (nb d …)) (nc d …)` on the common reduct).

**A grounding finding (an overclaim caught):** `CRUnique`'s `CR` is quantified over *all* roots,
but FUSep's `sn-confluent` gives CR only when the root is `SN`. So the honest instantiation
threads the `SN t` hypothesis explicitly — `ski-nf-unique` takes `SN ⇒ t`, not an unconditional
CR. The extruder's layer-② uniqueness is thus **SN-relative** at SKI (the wedge-projected
confluent fragment — exactly FUSep's ℚ/rational side), mirroring how ν's uniqueness is
smallness-relative. The ℕ demonstrator's deterministic `next` made its confluence trivial; here
the branching SKI reduction's confluence is the genuine content, supplied by FUSep's `newman`
(WCR from the braided diamond ⊕ SN from the shedding-halts). `solve` computes THE canonical
normal form of a real SKI term.

---

## The existence half landed at real SKI (⟡x8a-ski-existence, X8aSkiExistence.agda)

Mirroring the uniqueness half (214), the extruder's EXISTENCE (x8a-solve/solves, 212) is now
instantiated at the real SKI reduction — `S5Fixpoint.Machine.run` over FUSep's SKI `Tm` with
`next` = the residue-shedding step:

- **`SkiRun.next`** — `step→next t (⇒ t)`: step to the shed target, or stay at a stop (nf).
- **`SkiRun.fix?`** — decides `next t ≡ t` via the stop/shed TAG (no `Tm ≟`): `stop → yes refl`;
  `shed t' → no (fpf …)`, using the classifier's fixed-point-free invariant `fpf` threaded as a
  parameter (⇒'s own documented invariant, not assumed).
- **`SkiExistence.x8a-ski-UP`** — Source = `(fuel , term)`; Target = `Tm`; Witness `= v ≡ run fuel term`.
  **`x8a-ski-solve = run`** (run the shedding to nf); **`x8a-ski-solves = refl`** (the same
  self-determining ≡-Witness as 212/μ).

So **both halves** of the extruder's BackedUP frame now hold at real SKI: EXISTENCE (here,
`run` over the SKI shedding) + UNIQUENESS (214, SN-relative confluence via FUSep's `sn-confluent`).
Same machine (`S5Fixpoint.run`) at the SKI carrier, the stop/shed tag as the decidable fixpoint
probe. Carries `--guardedness` (the FUSep seam). The either/or "ℕ demonstrator vs real SKI"
dissolves: the identical Witness/solve/solves shape (212) at a real reduction — x8a's frame
instantiated, not a new construction.

---

## The SKI extruder registered (⟡x8a-ski-backed, X8aSkiBacked.agda)

The SKI existence UP (215) is wrapped into a full BackedUP at the real SKI carrier and registered:

- **`SkiBacked ⇒ fpf` (schema)** — for ANY SKI classifier `⇒` (+ its fixed-point-free invariant),
  a full `BackedUP`. The non-vacuity is CLASSIFIER-INDEPENDENT: `run 0 t = t` (fuel-0
  short-circuit), so term `atom`, candidate `app atom atom` gives `app atom atom ≢ atom`
  (constructor disjointness) = `¬ Witness` — `ski-contentful`. Every SKI classifier yields a
  non-vacuous backed solver.
- **`x8a-ski-backed`** — the schema at the all-stop classifier `⇒₀ t = stop` (every term its own
  nf; `fpf₀` vacuous — no `shed` cases), since FUSep exposes `Reduce` only abstractly. A genuine,
  concrete, non-vacuous SKI `BackedUP`.
- **`x8a-ski-registry = x8a-ski-backed ∷ registry`** — the canonical cons idiom (205),
  certifying the SKI extruder by TYPING as a real, non-vacuous solver.

So the extruder now has BOTH a ℕ-demonstrator BackedUP (212, `X8aRegistry`) AND a real-SKI
BackedUP (here) — the same frame at two carriers. Wiring `⇒₀` → a concrete branching FUSep
classifier (`⟡x8a-wcr-discharge`) registers the full SKI reduction. Carries `--guardedness`.

---

## The confluent-classifier obligation (⟡x8a-wcr-discharge → an interface, X8aConfluentClassifier.agda)

`⟡x8a-wcr-discharge` as framed ("discharge WCR↦ from FUSepQConfluence's braided diamond") rests
on a **shape mismatch** — the honest resolution is an obligation interface, not a discharge:

- FUSepQConfluence's `diamond` is **equational** over a `Span` (`rBack ≡ app viaP pBack`), NOT a
  **relational** `WCR↦` (`a↦b → a↦c → Converge b c`) — different objects; **no bridge exists**.
- `WCR↦` is **nowhere discharged** in the whole tree — `sn-confluent` takes it as a parameter,
  open **by design**.
- **No concrete branching `Reduce` classifier is exported** (216: `Reduce` abstract-only).

So a genuine discharge needs a concrete branching classifier + a `diamond → WCR↦` bridge — a
CONSTRUCTION, not a wiring. The honest deliverable (like ADD 205) is to NAME the obligation:

- **`ConfluentClassifier`** — a record bundling the two open hypotheses: `⇒ : Reduce`,
  `fpf` (shed fixed-point-free), `wcr` (local confluence of `↦`, relational). One record = the
  whole obligation.
- **`classifier-CR`** — given a `ConfluentClassifier`, `sn-confluent` fires for every SN term
  (the `wcr` field feeds it). So the discharge becomes "supply a `ConfluentClassifier`."

Verified: the all-stop `⇒₀` (216) inhabits it trivially (both fields vacuous — no `↦` steps). A
**branching** classifier (the `diamond → WCR↦` bridge + a real shed-branching `Reduce`) is the
genuine open construction — `⟡x8a-branching-classifier` — now with a precise target type, kept
as residue rather than faked.
