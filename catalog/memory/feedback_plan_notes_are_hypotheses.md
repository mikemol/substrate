---
name: feedback_plan_notes_are_hypotheses
description: "the saturated plan's OWN notes are hypotheses to probe, exactly like code comments; a typecheck confirms an outcome, never a mechanism"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
  modified: 2026-07-21T19:13:44.707Z
---

The plan file's saturation notes — detailed, file:line-cited, produced by prior sessions' research agents — READ
as verified and are not. Measured 2026-07-21: **5 inherited claims probed, 4 FALSIFIED.**
(i) `*ℤ-comm`'s home (the plan swapped `Mul`/`MulFull`); (ii) the `+-coherent` "two `mk-monoid` applications are
distinct terms" mechanism; (iii) "no Grothendieck pair exists in-tree; C's carrier is NEW ~15 lines"; (iv) "1831
files need the pragma". Only `coeff`'s `{0ℤ,+ℤ}` footprint survived.

**Why:** CLAUDE.md already says a deferral/TODO comment is "a hypothesis to verify, not a fact"
([[feedback_judgement_is_demechanization]] — comments are reified judgements, stale within ~3 commits). The plan's
own notes are the SAME CATEGORY — a prior session's reading — but their citation density makes them feel settled,
so the trigger does not fire. Two of the four survived into commit MESSAGES before being probed, requiring
retraction commits. (iii) is the sharpest: the agent searched by NAME (`Grothendieck|difference pair|_⊖_|posPart|
negPart`, which finds only fibrations) rather than by SHAPE — the structure was `GradedProductOver` all along.

**⚑ AND: a typecheck confirms an OUTCOME, never a MECHANISM.** `+-coherent = refl` typechecked, which I reported
as proof that sharing the monoid term was load-bearing. It was not — a fresh unshared `mk-monoid` typechecks too,
because `mk-monoid` is transparent and identical arguments normalize identically. The real boundary is LAW-PROOF
drift (a propositionally-equal but definitionally-different proof on one side DOES break it — measured). Same
shape at the global-`--guardedness` build: 1973/1973 PASS is consistent with the flag being IGNORED, so a separate
live-path check was needed. Green ≠ the reason you think it is green.

**How to apply:** before writing a plan-sourced claim into a module header, a commit message, or a conclusion, run
the probe that would falsify it — these cost ~2 minutes each and four of five paid off. Prefer a SHAPE search
(`jea_pysim --clusters`, or grep the type/structure) over a name search for any absence claim. When a check
passes, ask what it actually ruled out, and construct the counter-case if the claim is about a mechanism.

Relates to [[feedback_judgement_is_demechanization]], [[feedback_measure_instrument_before_theorize]],
[[feedback_reuse_search_before_feasibility_conclusions]], [[feedback_report_presence_never_absence]],
[[similarity-not-grep]].
