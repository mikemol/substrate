---
name: feedback_a_flag_is_an_either_or_to_dissolve
description: "a flag \"claim X does not hold\" is itself an either/or — recurse into the common structure before resting on \"wrong\""
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a96a1d8c-75ae-47e6-807c-c4988d800d8f
---

When verify-by-compile produces a FLAG ("the doc/handoff claims A, but A does not hold"), that flag is itself an either/or (their-A vs my-not-A) — do NOT rest at "they're wrong." Recurse: lift BOTH sides to their **common structure** (the right shared space), then one of two things resolves it:

1. **Basis/coordinate artifact** → they coincide in the common space; the flag dissolves, the claim HOLDS up to convention (you were comparing different coordinatizations). *Always check this first* — it's the sibling of [[feedback_dont_reconstruct_a_missing_source_and_conclude]] (your "doesn't hold" can be as premature as a by-read "holds").

2. **Collapsed wedge** → they genuinely differ in the common space, AND both are facets of one richer structure the claim **collapsed into one**. Reframe the flag as "X collapsed a wedge of two retained facets," not "X is false." This is [[feedback_duality_operator_is_either_or_trap]] / [[feedback_wedge_not_projection]] applied to the FLAG itself.

**The instance (Ⓟ.3′):** the doc identified "the static antisymmetric-form witness kernel" with "the dynamic V₂-reflection's −1 eigenline" as one line. I flagged ≠ (T·w=(−1,1,3)≠−w). Recursing into the common structure (edge space, lifting each by its own C-convention): B₃ kernel = `(0,0,0,1,−1,1)` (triangle {1,2,3}), T's −1 axis = `(0,1,−1,1,−1,0)` (τ-related cycle) — GENUINELY distinct. So it's case 2: there are TWO parity-distinguished lines (static kernel ⊕ dynamic reflection axis), a wedge the doc collapsed — not one line, not a coordinate artifact.

**Generalize: FRAMINGS, not just claims (2026-06-19).** A *framing* that doesn't hold is the same either/or — recurse to the common structure both framings are special cases of. **Instance (membudget shell-injection):** I framed "auto-wrap `agda`" as a bash **function**; that framing didn't hold for `make` (recipes run in non-interactive `/bin/sh`, never see functions). The common structure under "interactive `agda`" and "`make`'s `agda`" is **PATH resolution** — so the resolution is a PATH **shim** (an executable both paths hit), not a function. The broken framing pointed at the shared substrate. (Earlier in the same arc: "background compiles are free/independent tasks" was a framing that didn't hold — they share one RAM topology; the common structure is a shared budget → the whole `membudget` semaphore.)

**How to apply:** every "doesn't hold" — claim OR framing — → (a) lift both to the common space/substrate, (b) if same → dissolve (basis/convention), (c) if different → name the wedge (the two facets + the structure they're both of) or the shared substrate (e.g. PATH under function-vs-make). Only then is the flag final, and its resolution is a forward target, not a dead "wrong."
