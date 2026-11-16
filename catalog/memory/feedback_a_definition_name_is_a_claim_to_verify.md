---
name: feedback_a_definition_name_is_a_claim_to_verify
description: "A module/def NAME is itself a load-bearing claim — verify the OBJECT matches its name (its carrier/Hom-set/shape), not just that it compiles. Naming from INTENT ('this should be the symmetric group') without checking the DEFINITION lets a mischaracterization propagate through many commits."
metadata:
  node_type: memory
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

Caught 2026-07-11, closing the cat-perm arc. I named the category `orientationRigCatPerm` "THE GENUINE
SYMMETRIC (Sₙ-morphism) RIG CATEGORY" and carried that framing through ~6 commits (cat-perm, cat-perm-
UP, bifunctor, coxeter, adjclosure) — but its morphisms are `Homₚ = Σ(i≡j)(Perm j)` with `Perm j = Vec
(Fin j) j` UNRESTRICTED: the full TRANSFORMATION MONOID Tₙ (jʲ functions), NOT Sₙ (n! bijections). The
mischaracterization surfaced only when I went to ASSEMBLE the free UP and realized `coxeter-complete`
needs `IsPerm` — it generates only the Sₙ ⊂ Tₙ sub-part, so "the category is free on the braidings" is
FALSE for Tₙ. The genuine free UP needed a NEW IsPerm-restricted category (`orientationRigCatSym`).

**Why:** I named from INTENT ("the morphisms are meant to be permutations / the braidings are genuine
symmetries") and verified the wrong things — that it COMPILES and that the braidings are non-trivial —
but never checked the actual Hom-SET was Sₙ vs Tₙ. A name is a claim; I asserted the claim and audited
everything except the claim. Same root as [[feedback_verify_the_recursive_form_not_just_the_closed_form]]
(verify the whole shape/hypotheses you ship) and the absence-claim misses
([[feedback_reuse_search_before_feasibility_conclusions]]): assert a characterization, verify around it.
The compile being green is orthogonal — Tₙ is a perfectly good category, just not the one the name
claimed.

**How to apply:** when you NAME a construction after a known object (a group, a category, "the free X",
"the symmetric/…"), verify the OBJECT realizes that name — check its carrier / Hom-set / generators /
cardinality against the named thing (here: is Hom really the n! bijections, or all jʲ vectors? numpy-
count it — |Hom n n| = n! vs nⁿ settles it in one line). Do this AT NAMING time, not when a downstream
proof forces it. And when you find a mischaracterization, the git-history commit MESSAGES that used the
wrong name are an immutable residue — correct the live headers and note the correction, but the record
carries the error. Sibling of [[overclaim-witness-arc]]: the name is the first overclaim.
