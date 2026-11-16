---
name: feedback_opacity_blowup_routearound_freeup
description: "Hitting a dense-materialization OOM or an `opaque`/won't-reduce wall (the cyclen/Cycle7 pattern)? The clean, principled route-around is the FreeUP β-interface — prove via the exposed basis-action lemma + lift-on-generators, NEVER materialize the dense form."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a96a1d8c-75ae-47e6-807c-c4988d800d8f
---

When a concrete instantiation OOMs (e.g. `Cycle7 = cyclic {6}` forcing a 7×7 dense map to the
7th power in normal form) **or** a definition flat refuses to reduce (`apply (linear-from-images …)
(basis k)` won't `refl` because `linear-from-images` is `opaque`), do NOT fight the seal or try to
normalize the dense form. **Reach for the universal-property β-interface.**

The move (uniform, every time):
1. Use the EXPOSED basis-action lemma — the `extend-on-basis` β-rule (e.g. `cyclic-Linear-basis :
   apply (cyclic-Linear) (basis k) ≡ basis (cyclic-suc k)`, proven once inside the `opaque` block).
2. Prove your goal ON GENERATORS and LIFT — `HasOrder-from-perm` (transport the cheap *permutation*
   order through the basis interface), `extend-unique`, `package-comm`. The dense form is never
   touched. Verified: the Cycle7 order proven this way typechecks in 0.83 s / 74 MB.

**Why:** opacity is BOTH an obstruction (it blocks naive `refl`/normalization — a dead-end for a
fresh attempt) AND the enforcement of the β-interface (it *channels* you into the only cheap path).
The two seals in play: `FromImages.linear-from-images` (the free-F₂-module `extend`, the irreducible
dense def) and the per-instance `Cyclic.cyclic-Linear`. `package-comm`/`FreeUP` is the CATEGORICAL
name for why the β-route is sound+complete: the operator is determined by its basis-action up to
unique iso, so the dense form is never logically needed. The opacity-fix and the FreeUP centre are
the **same structure** — operational vs categorical (see [[cyclen-opacity-fix]],
[[def-proof-separation-lever]], [[free-universal-property]], [[read-structure-dont-rebuild]]).

**How to apply:** the trigger is "OOM at a concrete cyclic/linear-map instance" or "an `apply`/dense
def won't reduce." Don't grind the dense normalization and don't reinvent a seal — find the exposed
β-lemma (or add one inside the `opaque` block) and prove-on-basis-then-lift. `package-comm` does NOT
delete the seal (the dense `extend` stays sealed); it gives you a complete cheap reasoning interface
*around* it, so you are never blocked. This route did NOT always exist for this case and is NOT
obvious to an agent new to the repo — that is exactly why it is written down.
