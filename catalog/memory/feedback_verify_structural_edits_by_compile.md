---
name: feedback_verify_structural_edits_by_compile
description: "Verifying a mechanical structural edit (sed re-point, rm, import migration) by GREP is unsound — grep filters/boundaries have blind spots that mask exactly the error the edit introduces. The sound verifier is the typechecker/build. Compile, don't (only) grep."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a96a1d8c-75ae-47e6-807c-c4988d800d8f
---

**When you verify a mechanical multi-file structural edit — a `sed` import re-point, a `rm` of a module, an
import migration — GREP VERIFICATION IS UNSOUND. Confirm with the COMPILER (targeted typecheck / the
pre-commit build), not only grep.** Grep's own filters and boundaries have blind spots that mask precisely
the class of error the edit introduces. Caught twice in one session (2026-07-05):

- **`-v <path-prefix>` false-excludes siblings.** Enumerating `Cycle3` importers with
  `grep -rl ... | grep -v 'Permutation/Cycle3'` silently dropped `Permutation/Cycle3-FreeLinearization.agda`
  (its path *contains* the excluded prefix) — a real consumer, hidden. (Ⓖ.cyclen-collapse-registry.)
- **`\b` masks prefix-corruption of a longer sibling.** An anchored `sed 's|…Permutation\.Iterate|…Foundation.Fin.Iterate|'`
  also rewrote the PREFIX of `…Permutation.IterateLift` → `…Foundation.Fin.IterateLift` (a nonexistent
  module). The verification grep `…Permutation\.Iterate\b` reported "clean" because `\b` finds no boundary
  between `Iterate` and `Lift` — so it neither saw the surviving-wrong string nor the corruption. The
  **pre-commit targeted typecheck** caught it (`FileNotFound`); grep never would. (Ⓖ.tower-basis-phase3.)

**Why:** grep verifies a STRING predicate; a structural edit's correctness is a TYPING/RESOLUTION predicate.
They diverge exactly at siblings sharing a prefix (`Iterate`/`IterateLift`, `Cycle3`/`Cycle3-FreeLinearization`)
and at whatever the filter excludes. The compiler resolves every import against the real module graph — it
cannot be fooled by a boundary or a filter.

**How to apply:**
- For any `sed`/batch import re-point: anchor the pattern with a TRAILING boundary that excludes longer
  siblings (`Permutation\.Iterate([^A-Za-z]|$)`, not `Permutation\.Iterate` or `…\b`), AND typecheck the
  touched files before trusting it. Prefer per-file `Edit` (needs a Read, but can't prefix-corrupt) when the
  set is small; reserve `sed` for genuinely-uniform large sets and then COMPILE to verify.
- For `rm`/deletion: the syntactic grep for importers is necessary but not sufficient — the build is the
  gate (this is the same lesson as [[feedback_ground_in_tower_build]]'s bare-import deletions and the
  Cycle2/5/7 leaf collapse, where a bare unused import was missed by the semantic qname graph).
- The commit's pre-commit full build is the backstop, but catch it EARLIER with a targeted `membudget run …
  agda …` on the edited modules + their key consumers, so you iterate in seconds not minutes.

Related: the substrate discipline "structural search, not grep" ([[similarity-not-grep]]) is the SEARCH-side
twin of this VERIFY-side lesson.
