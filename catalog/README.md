# Catalog of the substrate project

A line-anchored, auditable index of what the [parent corpus](..) is doing
mathematically, what it claims to show, and how those claims relate to
each other. Produced under the `decomposable-by-entailment` skill: each
file is a shadow that survives session boundaries.

The complementary asset is [decomposition/](../decomposition/), which
mechanically parses the narrative into a SQLite of section/triple
records. This catalog adds editorial interpretation that the mechanical
pipeline cannot produce: which concepts are the same idea under
different names, which claims supersede which, where intent drifted
between LLM sessions.

## Files

- [concepts.md](concepts.md) — mathematical concepts ledger.
  Each entry: stable id, short name, precise statement, evidence
  anchors (file:line), introducing move, current status.
- [claims.md](claims.md) — claims-attempted-to-be-shown ledger.
  Each entry: stable id, claim statement, status
  (`shown` / `partial` / `open` / `superseded` / `drifted` /
  `abandoned` / `negative`), evidence, concepts used.
- [entailment.md](entailment.md) — typed edges between concepts and
  claims, with explicit drift annotations (Types A/B/C/D).
- [drift_archaeology.md](drift_archaeology.md) — conversation-anchored
  evidence for the drift instances entailment.md records. Each
  drift gets the turn-ordinal where it was authored, the verbatim
  quote, and a behavioural classification (summary-collapse,
  user-framing operational-drift, silent naturalisation,
  acknowledged-then-abandoned).

## Schema

### Concept record

```
### C-{slug}
- **Name**: ...
- **Statement**: one-sentence precise definition or the mathematical
  object's identity.
- **Introduced**: M{n} (line LL) or §{section} (line LL).
- **Evidence**: [file.md:LL-LL], [file.py:LL-LL], ...
- **Status**: live | superseded-by-{C-id} | renamed-to-{C-id} | dormant
- **Notes**: editorial — drift signals, alternate names, etc.
```

### Claim record

```
### K-{slug}
- **Statement**: the proposition that is/was being shown.
- **Introduced**: M{n} (line LL).
- **Evidence**: [file.md:LL-LL] plus any code witness.
- **Status**: shown | partial | open | superseded-by-{K-id} | drifted |
  abandoned | negative (claim refuted)
- **Concepts**: [C-id, C-id, ...]
- **Notes**: which version of a version-chain landed it.
```

### Edge record

```
- {src} →[relation]→ {dst}
  - **Relation**: motivates | depends_on | refines | generalizes |
    supersedes | drift_into | witnesses | refutes
  - **Evidence**: [file:LL-LL] (the place the relation is asserted or
    visible)
  - **Notes**: optional gloss.
```

## Epistemic discipline: LEM is rejected

This repository operates intuitionistically. The law of the excluded
middle is rejected: `P ∨ ¬P` is not automatic, and absence-of-
affirmation is not negation.

What this means for the catalog:

- **Asserting P** (status `shown` / `partial`): requires a
  constructive witness — a construction, proof, or verifier result.
- **Asserting ¬P** (status `negative`): requires a constructive
  `P ⊢ ⊥` — a counterexample, an explicit contradiction, an
  absurdity derived from P. Without one, do not use `negative`.
- **When an audit ran but found no inhabitant / no witness**:
  status is `open` or `disaffirmed-by-non-constructive-audit`, not
  `negative`. Describe what was checked, in existence-form, in the
  record's body. Do not collapse "not-found" to "not-exists."
- **`refutes` edges in [entailment.md](entailment.md)**: require
  constructive warrant. An audit that "failed to verify" is not
  a `refutes` edge.

This rule clarifies what the project's M1 realizability charter
(constructible → reachable → observable → coverable) already commits
to: every step is a positive predicate; none requires LEM.

## Auditability contract

Every record cites at least one line range in the corpus. To verify a
record, open the cited file at the cited lines. No record asserts
content not so anchored.

## How to extend

1. When reading a new section, add concept records for any new
   mathematical object named for the first time and claim records for
   any proposition the section tries to establish.
2. Prefer adding new records over editing existing ones; if an idea
   was renamed or superseded, point the old record at the new with the
   `Status` field.
3. Add edges to [entailment.md](entailment.md) only when they have a
   line-anchored basis. An edge without evidence is a guess and should
   be excluded.

## Scope of this first pass

Seeded breadth-first from the narrative's move structure (M1–M41 with
version chains) plus depth-first into the three committed Python files
([../applied_grammar.py](../applied_grammar.py),
[../s4_structure.py](../s4_structure.py),
[../verify_applied_grammar.py](../verify_applied_grammar.py)). Specifically
**not** an exhaustive enumeration of every footnote. Coverage gaps are
called out at the bottom of each ledger file.
