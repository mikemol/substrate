---
name: feedback-dbe-failure-rule-and-inline-format
description: "Hard rule: every SECOND failure on the same problem triggers DBE — stop patching errors, name the substructure. Default DBE externalisation is a separate file (good for cross-session reuse); the in-file comment/metadata form is the intervention specifically WHEN the second-failure rule fires (keeps the recovery local, doesn't disrupt flow with a new module)."
metadata:
  node_type: memory
  type: feedback
  originSessionId: 28a7490c-cf4a-4933-8773-215362d96f13
---

**Rule 1 (hard): every second failure on the same problem, trigger DBE.**

If the first attempt failed (type error, unification block, wrong proof shape, etc.) AND the second attempt also failed, STOP. Do not try a third local patch. Instead, apply the DBE protocol:
1. Halt and name what the goal of this stuck sub-problem is (one sentence).
2. Search for the repeatable form across the failing attempts (what shared shape is each iteration trying to produce?).
3. Name the costructure explicitly.
4. Name the composition operation.
5. Name the entailment.
6. ONLY then resume implementation, against the named structure.

**Why:** Patching errors locally without naming the substructure is exactly the thrash pattern DBE exists to prevent. The first failure can be an honest mistake; the second is a signal the framing is wrong.

**How to apply:** Concretely, after the second failure I should write a DBE block — either as a comment in the current file, a new helper lemma, or (in pathological cases) a separate file — that names what I'm trying to achieve before writing more proof. Diagnostic moves (e.g., "stub out parts to isolate the failing component") are valid DBE Step 6 multi-angle attacks.

**Rule 2: DBE externalisation form depends on context.**

- **Default = separate file** (for shadows likely to be reused across sessions, or to onboard future readers).
- **In-file comment/metadata** is the intervention WHEN the second-failure rule fires. Keeps the cognitive checkpoint local; doesn't disrupt flow with a new module; readable as a docstring describing what just got named.

The DBE skill already permits inline form: "the costructure name and its stated properties land in commentary at the top of whatever file the session produces."

Suggested in-file DBE format (Agda; adapt for other languages):

```agda
------------------------------------------------------------------------
-- DBE: <target sentence>
--
-- Shadows:
--   <name-1> : <type/signature> — <one-line role>
--   <name-2> : <type/signature> — <one-line role>
-- Compose: <how shadows assemble>
-- Entail:  <what the composition licenses>
------------------------------------------------------------------------
```

**Don't apply to:** Single-error fixes that genuinely are honest local typos. The rule fires on PATTERNED failure (the second failure looks like the first failed for the same kind of reason).

**Empirical anchor (2026-05-17):** The rule first fired in this session on `Substrate.Groups.S3`. First failure: unsolved constraints with bare `φ.act-cong`. Second failure: still unsolved with simple eta-expansion. Per the rule, I DBE'd via a diagnostic stub (Step 6 multi-angle attack) which pointed at the actual issue: Agda's unifier can't invert `Z₂.normalize` in the SP module-application context. Fix: explicit `{h₁} {h₂} {n₁} {n₂}` binding on the lambda makes the implicits rigid. The DBE move shortened what would otherwise have been an extended local-patching crawl.

**Connection to existing memories:**
- [[feedback-composable-primitives-over-flat-enumeration]] — DBE is the discipline that PRODUCES composable primitives; the failure-rule is its trigger.
- [[feedback-v4-typeclass-architecture]] — applying DBE successfully produced the Coxeter framework; the failure-rule would have shortened the path.
