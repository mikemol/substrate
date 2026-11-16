---
name: feedback_dedup_by_import_reexport_and_policy
description: "collapsing a duplicate lemma to an import — re-export if it had consumers; def/proof-separation bounds where it's legal"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a96a1d8c-75ae-47e6-807c-c4988d800d8f
---

When collapsing a DUPLICATE lemma to import-instead-of-reprove (the Ⓓ dedup family), two structural constraints govern — both caught by CI gates, NOT by per-file typecheck:

**Re-export discipline.** A lemma that was DEFINED (hence exported) in the dup module must be re-exported with `open import Canonical using (name) public` if anything consumed it FROM that module — including transitive whole-module `open`s. Plain `using (name)` brings it into local scope but does NOT re-export, so consumers break. The full-build gate caught this on `suc-injective` (16 ℚ/GCD/Z consumers via Cancel); per-file typecheck of the changed module passes and hides it. **Mechanical check before committing a dedup:** grep files importing the dup module for the name; if any, `public`. When unsure, `public` defensively — a missing one costs an aborted full build (~minutes), an extra one is harmless.

**Why:** the duplicate's name was part of the module's interface; removing the def silently narrows that interface.

**How to apply:** for each dedup — (1) confirm signature+body identity (word-boundary grep, the [[feedback_similarity_not_grep]] lesson), (2) confirm no import cycle (canonical must not reach the dup; the typecheck is the real cycle check), (3) grep external consumers → `public` if any, (4) prefer the lemma's CARRIER home (carrier-locality), often a lemma already exists there under another name (e.g. CRT/Residue `suc-mod-self` = `Nat.Mod.suc-mod-suc-self`).

**def/proof-separation bounds legality.** The pre-commit def/proof-separation gate forbids a definition-provider module from importing a proof module (`*.Properties`). So a def-provider that re-proves a lemma CANNOT dedup-by-import — it must keep a policy-mandated local copy (caught on `Realizability/Charter` ← `Foundation.Bool.Properties`). That is not sloppiness to chase; document it and move on. Dedup-by-import is only legal where the consumer isn't a def-provider.

Not every same-named pair is a mechanical dup: `rearrange` (medial law) is a commutative-monoid apex across carriers, built once in Algebra.Medial + instantiated at 5 sites (→ Ⓜ done).

**The import graph is the arbiter, not prose — distrust a negative finding AND its over-correction.** Ⓥ (`V4/Axioms/Lifted`): the audit said "orphan, retire"; I "corrected" it to "live consumer + unique content"; re-grounding the actual `import` statements showed the AUDIT was right (nothing imports it — I'd misread a `grep -l` name-collision on "Lifted") and MY correction was wrong. It was an orphan parallel-derivation of V₄ axioms that V4.Axioms supplies live; deleted in Ⓥ. Verdict on existence/orphan claims: `grep -nE "import .*ModuleName"` is the ONLY arbiter — neither the prose-audit nor a counter-claim counts. Refines [[feedback_negative_findings_in_corpus]] / [[feedback_test_the_wall_before_declaring_it]]. Full ledger: scratch/similar_opportunities_audit.md; anchor [[project_overclaim_witness_arc]].
