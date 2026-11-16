# V4 — Substrate.Category.ComposedReference.V4

A capstone is a **directory with a README**, not a module. It ATTESTS a
roster; it does not import one. The former `V4.agda` was a pure barrel —
prose and imports, no definitions of its own — so the attestation is prose
and the roster is a table. A consumer that wants one of these names binds
it at its OWNER, directly.

Substrate.Category.ComposedReference.V4

The V₄ residue carried by ComposedReference's action algebra.

Ⓒ.v4 (2026-07-05): this WAS a local `data V₄` — the comment claimed it was
"kept local to keep this primitive dependency-light (no group-axiom
infrastructure needed here)", but that residue is a genuine V₄ GROUP element
(the compensating σ) produced elsewhere by the group operation; a private
carrier meant those residues could not interoperate across subsystems. It now
RE-EXPORTS the canonical Groups.V4 carrier, so the residue IS the one V₄
(dependents open it unchanged — constructors e α β γ preserved).

## Roster

| name | owner |
|---|---|
| `V₄` | `Substrate.Groups.V4.Bijection` |
| `e` | `Substrate.Groups.V4.Bijection` |
| `α` | `Substrate.Groups.V4.Bijection` |
| `β` | `Substrate.Groups.V4.Bijection` |
| `γ` | `Substrate.Groups.V4.Bijection` |
