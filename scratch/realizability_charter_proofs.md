# §4–§5 proofs — *Grounding the Realizability Charter*

Prose to drop into the skeleton. Every result here is backed by a
machine-checked lemma in
[`Substrate.Realizability.Charter`](../agda/Substrate/Realizability/Charter.agda)
— **verified green** under Agda 2.8.0, `--safe --without-K`, **zero
postulates, zero open holes** (`agda --safe --without-K
Substrate/Realizability/Charter.agda`, exit 0). Per framing decision #2
the proofs *lead with the faithful core* (realizer = witness = explicit
construction); per #5 every statement is about **admissibility, not
truth**.

## The common substructure (read first — shapes §4 and §6)

The four gates are one structure — a **typed cons-list of flag-gates**,
`Chain` — instantiated as nested prefixes. This is the same cons-list
shape as the substrate's term-algebra (`UPTerm`): the chain is the
*syntax*, carrying two evaluations,

- `⟦_⟧? : Chain → D → Bool` — the cumulative **decidable test**, and
- `Wit : Chain → D → Set` — the cumulative **realizer**, an *inductive
  family*,

bridged by `sound : ⟦ c ⟧? d ≡ true → Wit c d`. Reading the design's
either/ors through their common substructure, recursively:

| either / or | common substructure |
|---|---|
| four gates | one `Chain`, four prefixes |
| Bool test *vs* Set witness | one chain, `⟦_⟧?` / `Wit`, bridged by `sound` |
| the chain *vs* a gate | the chain *is* a gate (decision + extractable realizer) |
| gate-chain *vs* audit pipeline (§4.2) | the same cons-list (free monoid ⊂ free category) |
| abstract carrier *vs* concrete `Distinction` (§5) | the **Boolean cube** `Cube n = Fin n → Bool`; `Distinction = Cube 4` |

Two payoffs. (a) `Wit` is an *inductive family*, so its index is
inferable and the proofs need almost no explicit instantiation. (b)
`⟦ c ▷ f ⟧?` reduces to a *syntactic* `_∧_`, so the `∧`-reflection
lemmas apply without hint. The single substructure is the honest located
home of §6's "the chain is elementary" concession: it is the free
word-algebra the substrate already uses everywhere.

The atomic engine is six one-line Bool-reflection lemmas (`∧-elimˡ/ʳ`,
`∧-intro`, `∧-false→⊎` for §4; `∨-elim`, `∨-trueʳ` for §5 — module §0).

---

## §4.1 Lemma 4.1 (the ordering is forced)

A realizer for a later gate *contains* the earlier one's:
`Coverable d → Observable d → Reachable d → Constructible d`. A longer
chain is a `_▷_`-extension, so its realizer `Wit (c ▷ f) d` is `w▷ w _`;
the entailment is one peel of the cons:

```
drop : Wit (c ▷ f) d → Wit c d        drop (w▷ w _) = w
```

(`forces-cov⇒obs/obs⇒rea/rea⇒con` are `drop`; `forces-cov⇒con` is
`drop³`.) ∎ This is **monotone narrowing** — the funnel `constructible ⊇
reachable ⊇ observable ⊇ coverable` is exactly the prefix order; the
"back-map" is §5.

## §4.1 Lemma 4.2 (witness composition)

The *same cons-list*, carrying audited steps with `ℕ` boundary tags — a
free category (the gate chain is its one-object specialisation). A
`Step s t` ships its realizer `Accepted carries`; composition is append,
which type-checks only when boundaries align, so the invariant is
preserved by construction (`_++ᵖ_`). Unit/associativity: `++ᵖ-idˡ` is
`refl`, `++ᵖ-idʳ`/`++ᵖ-assoc` are one-line inductions. ∎

## §4.1 Lemma 4.3 (determinism ⇒ replayability)

`run = decide ∘ canon`; replayability is its `cong`:
`replay : canon i ≡ canon j → run i ≡ run j` is `cong decide`,
`replay-self` is `refl`. ∎ (module `Replay`.)

## §4.2 Theorem 4.4 (soundness as a necessary-condition filter)

*Acceptance ⇒ realizers.* One induction extracts the realizer:
`sound ε p = wε`; `sound (c ▷ f) p = w▷ (sound c (∧-elimˡ p)) (∧-elimʳ p)`.
`audit-sound = sound charter`. (This *is* every per-gate soundness lemma
at once.)

*Accepted = intersection.* `intersection w = drop³ w , drop² w , drop w ,
w`; `intersection-conv (_,_,_,cov) = cov`.

*Rejection witnessed at a gate.* `reject` decomposes a failed test with
`∧-false→⊎`, emitting a typed `Rejected` (`here`/`there`);
`audit-reject = reject charter`, with `reject-at-{constructible…coverable}`.
∎

**Computed self-audit (§7.4).** `good = const true` ⟶ `good-accepted` by
`audit-sound refl`; `dedup-no-eqrel` (coordinate 0 = recipe false — "dedup
by semantic similarity, no declared equivalence relation") ⟶
`dedup-rejected` by `audit-reject refl`. Both fire by reduction.

### §4.3 What Theorem 4.4 does *not* give

Not truth (a true distinction with no finite recipe under the declared
vocabulary is correctly rejected — filter ≠ truth), not completeness, not
witness uniqueness. Gates are relative to *declared* resources.

---

## §5 The gate reflections — parametrized to the cube, variance-corrected

The earlier draft's `Conj-` obligations are **superseded** (they were
refutable, not open). The diagnosis: gates are *necessary conditions*, so
each passer-set is an **up-set**; the draft sought a **right adjoint /
interior operator** ("largest passing sub-distinction"), which fails — at
`⊥` (always interior-closed, passes nothing). The correct structure is the
dual **left adjoint / closure operator** ("smallest passing
super-distinction" = declare the missing resources), which is the
charter's own `conditionally-accept(remediation)`.

**Parametrization.** §4 is already carrier-generic and needs nothing.
§5 needs the structure the closure uses, so the carrier becomes the
**Boolean cube** `Cube n = Fin n → Bool`, generic in arity `n`, with
`Distinction = Cube 4` (coordinates recipe/manifest/measure/bounded =
projections at 0/1/2/3). A gate is a coordinate **mask**; it passes `d`
iff `mask ⊑ d` (pointwise `_⊑_`). The reflection is **join with the
mask**:

```
rmask mask d j = d j ∨ mask j
```

**The closure laws + the fix, generic over the mask** (`mkReflection :
(mask : C) → GateReflection mask`):

```
rmask-ext            : d ⊑ rmask mask d                       -- extensive
rmask-mono           : d ⊑ e → rmask mask d ⊑ rmask mask e
rmask-idem           : rmask mask (rmask mask d) ⊑ rmask mask d
rmask-closed→passes  : rmask mask d ⊑ d → mask ⊑ d            -- closed ⇒ passes
rmask-passes→closed  : mask ⊑ d → rmask mask d ⊑ d            -- passes ⇒ closed
```

`closed ⟺ passes` holds in **both** directions, for **every** mask — the
`⊥` defect is gone (extensivity means `⊥` is no longer fixed). The proofs
use only `∨-elim` and `∨-trueʳ` — **no `Fin` decidable-equality**.

**The four gates, closed** (`refl-{con,rea,obs,cov} = mkReflection
{con,rea,obs,cov}Mask`), each `GateReflection`. The masks are coordinate
patterns (`conMask` = coord 0, …, `covMask = const true`). And the masks
*are* the gates: `·⇒mask`/`mask⇒·` prove `mask ⊑ d ⟺ gate? d ≡ true`
(`con`/`rea` directly; `obs`/`cov` route through `sound` + `Wit`
pattern-match to dodge nested-`∧-elim` inference).

**Headline.** The old refuted `Conj-closed⇒observable` is now the *proved*
`obs-closed⇒passes : rmask obsMask d ⊑ d → observable? d ≡ true` (with its
converse `obs-passes⇒closed`): the closure's fixed objects are *exactly*
the observable passers.

### The one residue — an asymmetry, not a hole

`covMask ⊑ d ⟺ d ≡ const true`, so **coverable has a left adjoint** (the
closure `rmask covMask`, `refl-cov`) but **no right adjoint** (the only
coverable point is `⊤`, and `⊤ ⊑ d` forces `d ≡ ⊤`, so for `d ≠ ⊤` there
is no coverable sub-distinction `⊑ d`). Per the no-negation-overclaim
discipline this is stated in prose (module §10), **not** proved as a
universal non-existence. §5.3 obligation 6's instinct was right about the
*handedness*, mis-stated as "no adjoint."

---

## Mapping to the Agda artifact (for the reader's replay)

| Paper result | Agda name | discharged by |
|---|---|---|
| common substructure | `Chain`, `⟦_⟧?`, `Wit` | inductive family |
| Lemma 4.1 | `drop` (+ `forces-*`) | cons peel |
| Lemma 4.2 | `_++ᵖ_`, `++ᵖ-idˡ/idʳ/assoc` | structural induction |
| Lemma 4.3 | `Replay.replay`, `replay-self` | `cong` / `refl` |
| Theorem 4.4 (sound) | `sound`, `audit-sound` | induction + `∧-elimˡ/ʳ` |
| Theorem 4.4 (= ∩) | `intersection`, `intersection-conv` | `drop` |
| Theorem 4.4 (reject) | `reject`, `audit-reject`, `reject-at-*` | `∧-false→⊎` |
| self-audit | `good-accepted`, `dedup-rejected` | reduction (`refl`) |
| §5 carrier | `Cube n`, `Distinction = Cube 4` | parametric module |
| §5 reflection (generic) | `rmask`, `rmask-ext/mono/idem`, `mkReflection` | `∨-elim`, `∨-trueʳ` |
| §5 closed ⟺ passes | `rmask-closed→passes`, `rmask-passes→closed` | ∨-core |
| §5 four gates closed | `refl-{con,rea,obs,cov}` | `mkReflection` |
| §5 mask = gate | `·⇒mask`, `mask⇒·`, `obs-closed⇒passes` | `sound` / ∧-core |
| §5 coverable asymmetry | module §10 (prose) | noted, not proved |

**Verification.** `agda --safe --without-K
Substrate/Realizability/Charter.agda` from `agda/` (exit 0, zero
postulates, zero holes). The module is intentionally *not* yet in
`Substrate.All` until you wire it in, so the project build cannot be
reddened meanwhile.
