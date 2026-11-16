# V4 — Substrate.Category.RuleAction.V4

A capstone is a **directory with a README**, not a module. It ATTESTS a
roster; it does not import one. The former `V4.agda` was a pure barrel —
prose and imports, no definitions of its own — so the attestation is prose
and the roster is a table. A consumer that wants one of these names binds
it at its OWNER, directly.

Substrate.Category.RuleAction.V4

The V₄ residue factor (Klein four group) — Coxeter group of order 4.

Ⓒ.v4 (2026-07-05): this WAS a local `data V₄ = e|α|β|γ` reinvention of the
Klein four-group carrier. It now RE-EXPORTS the substrate's canonical V₄
(Groups.V4) — so RuleAction's residues are the SAME group elements as
everywhere else (they no longer fail to interoperate across subsystems), and
V4Compose's composition is the canonical Groups.V4 operation (not a
hand-written table). Dependents (Record, V4Compose) open it unchanged
(constructor names e α β γ preserved).

## Roster

| name | owner |
|---|---|
| `V₄` | `Substrate.Groups.V4.Bijection` |
| `e` | `Substrate.Groups.V4.Bijection` |
| `α` | `Substrate.Groups.V4.Bijection` |
| `β` | `Substrate.Groups.V4.Bijection` |
| `γ` | `Substrate.Groups.V4.Bijection` |
