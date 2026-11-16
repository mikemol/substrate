---
name: feedback_scoped_classical_hypotheses
description: "Classical logic (LEM) may enter the substrate only as a scoped explicit hypothesis (module parameter), never a postulate; policy lives at docs/governance/scoped-classical-hypotheses.md."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 1ec5ce03-bc06-4fe2-ad82-d065809b8da4
---

Policy lives at `docs/governance/scoped-classical-hypotheses.md` (single
source of truth). This is the short pointer.

When a result needs a non-constructive step: admit the principle as a
**module parameter**, never `postulate`, never weaken `--safe`. The
theorem proved is the constructive implication `principle → P` — a
conditional, which is intuitionistically honest, unlike an assumed
axiom. Reconciles with [[feedback_reject_lem_in_substrate]] rather than
contradicting it.

**Why:** a conditional theorem ≠ assuming LEM; the classical dependency
stays visible in the type and every user must supply it explicitly.

**How to apply:** (1) parameter not postulate; (2) weakest sufficient
principle — `Dec` to choose a ⊎ branch, ¬¬-stability to finish, NOT full
LEM ([[feedback_negative_findings_corpus_bound]]); (3) full LEM only as a
thin derived instance, labelled as over-assumption; (4) provide a
constructive discharge where one exists (finite/decidable case); (5)
record it as a tracked tension, not silent. Reference model:
[[project_simplicity_recognizer]] (Shadows 3c Decidable/Classical + 5
Finite).
