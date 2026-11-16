---
name: feedback_registry_as_pi_not_markdown
description: "status / coverage / claim registries belong as a typechecked dependent function (Π), never a generated markdown table — markdown is the sum-type FREEZE of a claim-function; the live artifact recomputes and the typechecker enforces every discharge."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c1329ff9-896f-4600-8952-67ec237e5bbc
---

Don't track proof-tier / coverage / claim status in **markdown**. A generated
doc (e.g. `el-atlas-structured.md`'s perspective-visibility tables) is the
SUM-TYPE FREEZE of a function — each claim is really `C : S → Verdict`, and the
markdown is one frozen printout. A hand-written "proved" cell is an ASSERTION a
grep can read but the machine cannot enforce. User (2026-06-12): "I don't want to
lean on the markdown for stuff like this. That's sum-type behavior when we need
pi-type dynamicism."

**Why:** the exact failure the UP-Registry rejects — conformance is a COMPILED
witness, not the absence of a ⊤-stub; cf. [[feedback_names_vacuous_shape_is_meaning]]
and the G8 standing rule "a verdict needs a mechanical predicate, not assertion."

**How to apply:** make it a Π. `Statement : Claim → Set` (each claim's spec as a
type) + `proof-tier : (c : Claim) → Statement c` (a TOTAL dependent function,
every case a real witness). No escape constructor ⟹ a claim cannot sit
undischarged; adding one FORCES a witness or the build breaks. Querying status =
EVALUATING the function (you can extract a claim's PROOF, which a markdown row
can't give you). Keep the honest open frontier as a separate witness-free enum.
Exemplar: `Substrate.Logic.Evidence.ElAtlas(.Proofs)` (7ab1afc); kin = the
typechecked `BackedUP` registry ([[project_bridge_indexes_algebra_category]]).
