---
name: feedback_verify_the_recursive_form_not_just_the_closed_form
description: "When you numpy-verify a decomposition to hand a subagent, verify the RECURSIVE form you actually spec (e.g. bubble(suc q) = …), not only the closed-form top-level identity. A correct closed form can have an INCORRECT recursion you invented for it — the agent will hit it."
metadata:
  node_type: memory
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

Caught 2026-07-11 (⟡coxeter-completeness-general). I numpy-verified the TOP-LEVEL decomposition
`insert-at p σ = bubble(p) ∘ (id⊕σ)` over 872 perms (n≤5) — solid. But in the delegation spec I ALSO
handed the agent a RECURSIVE form for `bubble` (`bubble(suc q) = compose (sadj) (blockSum (id 1)
(bubble q))`, a structural descent) that I had NOT separately verified. The agent numpy-checked it,
found it FALSE, and reorganized to a fuel = `toℕ p` structural recursion (the true bubble descends on
`toℕ p`, and `inj1 q'` is not a structural subterm). It still proved the theorem — but only because it
re-verified my spec rather than trusting it.

**Why:** a closed-form identity being correct does NOT make an arbitrary recursion you write to compute
it correct. I verified the WHAT (the decomposition holds) but invented an unverified HOW (the recursive
shape) and shipped it as if verified. This is the same proxy-trust failure as
[[feedback_verify_commit_landed_not_exit_code]] (report state from a proxy) one level in: I let "the
closed form is numpy-checked" stand in for "everything in the spec is numpy-checked." A subagent given
a wrong recursion can burn a lot of effort (or fake it) before noticing.

**SECOND INSTANCE, same root (2026-07-11, ⟡sign-hom-perm):** I numpy-verified `sign(σ∘τ) = sign σ ⊕
sign τ` and the `flip-lemma` over ALL PERMUTATIONS n≤6 — solid — and wrote the spec WITHOUT `IsPerm σ`
on the left factor. The agent found that hypothesis is NECESSARY: for a non-injective `σ=[0,0]` the two
swapped entries coincide, the pair doesn't flip, and the lemma is FALSE (`τ=s₁`: sign(compose)=false
but sign σ ⊕ sign τ=true). My numpy ranged only over the WELL-BEHAVED SUBSET (permutations), so it
never exhibited the counterexample that reveals the hypothesis is load-bearing. Same root as the
recursion bug: an incomplete numpy sweep of the spec I ship, trusted as complete.

**How to apply:** when you numpy-verify a spec to hand off, sweep the WHOLE shape you actually ship —
(a) if it has a RECURSIVE form (base+step), compute BY the recursion and compare to the closed form;
(b) if it has HYPOTHESES, range over inputs that VIOLATE them (non-permutations, non-invertible, empty,
degenerate) to confirm each hypothesis is load-bearing / the statement fails without it — don't range
only over the well-behaved subset where everything holds. If you only verified a narrow slice, SAY SO
in the spec ("verified over perms only; check whether IsPerm is needed") so the agent re-derives. The
agent doing its own numpy re-verification is the sustain that saved both cases — reinforce that
instruction. Sibling of [[feedback_dedup_x_numpy_product_search]] (numpy gives the shape — verify the
WHOLE shape, including its boundary and hypotheses, before shipping).
