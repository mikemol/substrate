---
name: feedback_dedup_x_numpy_product_search
description: "To find whether a construction already exists, take the PRODUCT of the two search machineries: numpy enumeration gives the SHAPE the term must have; the SPPF/dedup structural search (jea_pysim over .agdai cores + reuse-index) finds the existing PIECES to assemble it. The SPPF is shallow, but the pieces almost always already exist."
metadata:
  node_type: memory
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

Caught 2026-07-11 (closing the ⟡rig-UP-cat-perm-UP Ⓐ witness). I had reported a `sign : Perm n →
ℤ/2` "doesn't yet exist in the tree" — a fresh ABSENCE claim (the recurring miss —
[[feedback_reuse_search_before_feasibility_conclusions]]). The user: *"That's the alternating sign
that walks up the witness tower already"* and *"Should probably take the product of the deduplication
machinery and the numpy searches; the SPPF in the database doesn't hold to a great deal of depth, but
pieces will generally already exist."*

**Why:** the two search tools answer DIFFERENT halves and compose. numpy (enumerate the concrete
instance) tells you the SHAPE the construction must have — e.g. "the witness needs a sign that is EVEN
on C₃ and ODD on the transposition." The SPPF/dedup structural search (`jea_pysim` over the interned
`.agdai` cores + `catalog/reuse-index.md` + targeted grep) tells you which PIECES of that shape already
exist. Neither alone suffices: numpy alone tempts the from-scratch rebuild (or a false absence call);
dedup alone doesn't know what shape to look for. Their PRODUCT is the reuse-before-build reflex made
mechanical. And the SPPF is shallow (it interns canonical node shapes, not deep proofs) — so you won't
find the whole assembled theorem, but you WILL find its pieces (here: `CycleType.cycle-type : {n} →
Perm n → Vec ℕ n` general; `SimplicialBoundary.osign` + `∂∂-opp-sign` = the sign-as-xor-hom pattern;
`M40Action.sgn-hom` = a sign hom for chirality). The construction is then an ASSEMBLY, not a build.

**How to apply:** when about to build OR to call something absent — run BOTH: (1) numpy-enumerate the
target to get its shape and the exact discriminating property; (2) structural-search the SPPF/dedup +
reuse-index for pieces of that shape (not just the exact name — the pieces are under other names:
`osign`, `cycle-type`, `sgn-hom`). Assemble from the pieces; only the un-found connective tissue is
new. This IS the ⟡pipeline-driver deliverable (numpy⊗typeholer/dedup) in manual form — worth
mechanizing. Sibling of [[similarity-not-grep]] (the dedup half) and
[[feedback_unsolved_constraints_use_numpy]] (the numpy half); the standing prevention layer is the
CLAUDE.md reuse-search rule, this is the "combine the two engines" refinement.
