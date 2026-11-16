---
name: project_simplicity_recognizer
description: "Simplicity-as-recognizer over ConjugationCoalgebra; group simplicity is a coalgebraic observation over the conjugation trace, dual to term-algebra construction."
metadata: 
  node_type: memory
  type: project
  originSessionId: 1ec5ce03-bc06-4fe2-ad82-d065809b8da4
---

`agda/Substrate/Category/ConjugationCoalgebra/Simplicity.agda` — generic
simplicity recognizer over any `ConjugationCoalgebra {0ℓ}` + an `_≈_`.
Green standalone under `--safe --without-K`, zero holes/postulates. NOT
in All.agda (per [[feedback_never_build_all_agda]]).

Contents: `Recognizer` module with `NormalSubgroup` (trace-closed
element predicate), `IsTrivial`/`IsWhole`/`IsSimple` (lattice form),
`whole-NS`, `refute-simple` (PROVEN reject-certificate: one proper
nontrivial normal subgroup ⇒ ¬simple), `NonSimplicityWitness` (the
"attempt by default" type — inhabited iff not simple; `witness→¬simple`
+ `simple→¬witness` PROVEN), `Decidable`/`Classical` (the scoped
classical converse `¬witness→simple`), `WithOrbits.saturated`
(PROVEN: normal subgroups are class-saturated given the orbit axiom →
the recognizer reads the rep-class trace), and `WithOrbits.Finite`
(Shadow 5, PROVEN: finite rep-class trace `Class ↔ Fin k` + decidable
membership/≈ε + cover discharges the three Decidable params
CONSTRUCTIVELY — `¬witness→simple` with NO LEM; properness decided by
sweeping the finite trace via local `Fin-∃?`).

**Promoted helpers:** `Fin-∃?` (+ dual `Fin-∀?`) now live in
`Foundation/Fin/Exists.agda`; `dec-¬` + `from-¬¬` (decidable props are
¬¬-stable) added to `Foundation/Negation.agda`. Simplicity imports
these (no longer local).

**First instance:** `ConjugationCoalgebra/Examples/V4.agda` (green) —
V₄ wrapped (reused from Substrate.Groups.V4, NOT rebuilt) as a
ConjugationCoalgebra; `V4-not-simple : IsSimple → ⊥` PROVEN via
NonSimplicityWitness ⟨α⟩={e,α} (proper: β∉; nontrivial: α∈,α≢e). The
REJECT leg. ACCEPT leg (proving a group simple) deferred: `IsSimple`
quantifies over ALL normal subgroups → needs normal-subgroup
ENUMERATION, which Finite does NOT provide (it only discharges the
per-N decision). Separate arc.

**Scoped-LEM decision (anti-LEM seam):** the converse `¬NonSimplicity-
Witness → IsSimple` is NOT constructive (IsSimple is ⊎-valued). Handled
as a SCOPED HYPOTHESIS not a postulate (stays --safe; classical dep
visible in the type) — reconciles with [[feedback_reject_lem_in_substrate]]
because a conditional theorem ≠ assuming LEM. Weakest sufficient
principle ([[feedback_negative_findings_corpus_bound]]): `Dec (proper N)`
(to CHOOSE the ⊎ branch — stability alone can't) + ¬¬-stability of
`_≈ ε` and `member` (to finish each branch). Full LEM (`Classical`
module, `(P:Set)→Dec P`) is a thin DERIVED instance, over-assumption
made explicit. Finite-trace discharge (Shadow 5, `WithOrbits.Finite`)
is BUILT — fully constructive on finite groups. Policy doc:
docs/governance/scoped-classical-hypotheses.md (this module is its
reference model); discipline pointer [[feedback_scoped_classical_hypotheses]].

**Why:** crystallises the algebra/coalgebra duality ([[project_homology_cohomology_recursion]],
[[discipline/feedback_coalgebraic_not_consumer_driven]]): term algebra
CONSTRUCTS a group, simplicity OBSERVES it by unfolding conjugation;
`GaloisAdjunction` (T4) is the bridge. Came from the groupprops
"prove all particular groups generically" thread — the recursive move
that dissolves 643 groups → ~5 constructors → the term algebra's own
free/quotient/colimit operations, with simplicity living on the
coalgebra side.

**How to apply:** per-group simplicity (Aₙ n≥5, PSL, sporadics) is an
INSTANTIATION of `IsSimple`, not a bespoke theorem — uniform statement,
shared lattice machinery. GAUGE-HONEST: recognizer compresses the
STATEMENT, not the WITNESS (Aₙ-simple witness is still real math).
`IsSimple` is `Set`-valued: a decidable Bool recognizer ONLY when
Class is finite + membership/≈ decidable (normal-closure sweep over
rep-classes); for infinite carriers (braids, Baumslag–Solitar) it
stays an Ω-valued observation. Next shadow = the finite/decidable
specialization.
