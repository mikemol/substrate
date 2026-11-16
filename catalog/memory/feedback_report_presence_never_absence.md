---
name: feedback_report_presence_never_absence
description: "report what is FOUND with witnesses; never report what is not there — an empty search is a fact about the method, and the substrate SATISFIES what axioms would declare"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
  modified: 2026-07-21T02:23:34.761Z
---

Report only what is **found**, with a witness (term + `file:line`). **Never report what is not there.**
An empty search yields exactly one honest sentence: *"I searched X by method M and did not find it"* — a
statement about the method, never a property of the repository. Do not promote it to a gap/hole/wall/residue,
do not build a plan step on it, and do NOT over-correct into "therefore it exists" (the mirror error). The
honest state is agnostic.

**Why (the asymmetry).** A presence claim needs ONE witness — cheap, checkable. An absence claim is a
universal quantifier over ~2000 Agda modules plus a large Python corpus, and to be genuine it needs
exhaustive coverage AND the right NAME AND the right CATEGORY AND the ability to recognize the thing in
whatever FORM it is realized. Demonstrated failures on all four axes in one session: NAME (`Subring`),
CATEGORY (hunting `Ring` in a SEMIRING substrate whose carriers have no additive inverses), FORM
(declared-as-a-record-field vs SATISFIED-by-construction), REGISTER (Agda term vs Python/SQL realization vs
proven under another name).

**The deeper law: the substrate SATISFIES what axioms would DECLARE.** Absence-of-declaration ≠
absence-of-structure. A vacuous record (`UPTopos` with zero fields) is not evidence of an absent topos — it
is evidence the record was never where the topos lives. Before writing "absent", ask **what construction
would satisfy this** — the substrate almost always names its centers (`split-Canonical`, the SPPF interner,
`prove-or-correct`, `QuotientUP`, `sign-sadj`). Five times in one arc a "gap" was a construction realized
under a name I had not searched.

**⚑ IN THIS REPO, CONSTRUCTION IS THE ARBITER.** The substrate is `--safe --without-K`, rejects
sum types, rejects LEM — so **if you can construct the type under those constraints, it cannot be
wrong**. That makes "build the term" the settlement procedure and "assert the negative" always the
weaker move. Concretely: do not write *"the spec's claim is WRONG"*, *"X is not load-bearing"*,
*"that cannot be done"* — try to CONSTRUCT the thing the claim would forbid. Usually the
construction dissolves the disagreement rather than adjudicating it (both sides turn out to be
claims about a chosen ROUTE, and the constructed term is the invariant underneath). Live instance:
"only three of `Canonical`'s four fields are load-bearing" was a fact about my proof reported as a
fact about the record — constructing `canonical-idempotent` from `canonical-respects-≈ ∘
≈-canonical` showed the record is merely OVER-COMPLETE, so the question was not well-posed.

**How to apply:**
- "grep-confirmed" is NOT a rigor qualifier — it NAMES an insufficient method (`CLAUDE.md`: the reuse-search
  must be **structural, not grep**). Attaching it to an absence claim implies rigor that was not performed.
- ⚑ The trigger fires on **your own agents' ledgers too.** A read-only agent asked "is X declared?" will
  faithfully report absence; reading that as a substrate property is the same error, laundered as
  independent evidence. Fan-out does not manufacture independence when you wrote the prompt.
- Correcting an absence claim sharpens a PREDICATE, it does not widen a SCOPE. Quarantine the
  *justification*; the CONSTRUCTION it motivated keeps its value independently (a named, discoverable apex
  helps a future reader whether or not the reason for reaching for it was sound).

Related: [[read-structure-dont-rebuild]], [[no-set1-floor-fifth-layer]], [[declaring-wall-rebuild-reflex]],
[[reuse-search-structural-questions]], [[collapse-keeps-the-orientation-residue]].
