# Agda comment hygiene: don't overclaim

_(Substrate governance policy. Migrated from `memory/discipline/feedback_comments_dont_overclaim.md`.)_

Comments in Agda modules must not state as fact anything stronger than what the slice's `--safe --without-K` proofs actually establish. Prose-level framings (intuitive descriptions, references to mathematical structure that isn't yet formalised) are fine, but they must be MARKED as prose, not asserted as theorems.

**Why:** in slice 15 (`Substrate.Cardinality`), an initial comment said "the bijection chooses one of n! valid orderings." This sounds like a theorem (the action of S_n on enumerations is transitive, with orbit of size n!), but the slice doesn't develop the permutation-action-on-enumerations needed to back it up. A future reader could mistake the prose for a machine-checked claim. The user flagged this as a sharpening point ("avoid accidentally making a stronger machine-checked claim than the slice proves").

**How to apply:**
- When writing prose in Agda comments, if the prose contains a quantifier ("for all", "n! valid", "any of the orderings") or asserts the existence of structure not formalised in the slice, REPHRASE to something that is observably true at this slice's level (e.g., "the bijection chooses one presentation among the possible finite enumerations").
- If the stronger framing is illuminating, keep it but mark it as prose: "(The 'differs by an inner automorphism' framing is prose-level; promoting it to a theorem would require X, not developed here.)"
- Cross-check after the file is written: read your own comments and ask "does the code prove this?" If not, soften.
- Sister rule to [[feedback-reject-lem-in-substrate]] and [[feedback-negative-findings-in-corpus]]: the substrate project's discipline is that LLM-authored claims must match what's actually proved.
