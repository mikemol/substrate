---
name: feedback_module_boundary_dissolves_blowup
description: "a 'deep composition won't normalize / Agda OOMs' wall is usually a FRAMING artifact — abstract the expensive part behind a parameterized module (neutral, unforced) and instantiate by `open`"
metadata:
  node_type: memory
  type: feedback
  originSessionId: a96a1d8c-75ae-47e6-807c-c4988d800d8f
---

When an Agda term **blows up the normaliser** (OOM / minutes-to-hours on a `refl` over a deep composition), do NOT conclude "infeasible / evaluator-bound." That is a FRAMING that doesn't hold — the wrong question ("how do I make Agda normalise this?") in place of the right one: **"what does the type-checker actually force across a module boundary?"** Recurse to that common structure.

**The escape (the parameterized-module pattern, cf. `Algebra.F2.MixColumns.Proof.G`):**
1. Assemble the proof INSIDE a module **abstract over the expensive arguments** (the keys, states, inputs). There the operations that pattern-match (`round`, `fold`, `nextRoundKey`, …) are **stuck/neutral** on the abstract vars, so NO composition is ever normalised — the proof type-checks once, cheaply, by `trans`/`cong` over supplied pins.
2. Supply the heavy facts as **concrete one-step pins** (each `refl` on a concrete checkpoint — one round, one key step), proven in their own modules.
3. **Instantiate by `open Mod <concrete> … renaming (kat to foo)`** — NOT a type-annotated re-declaration `foo : <type> = Mod.kat …`. The `open` substitutes params into the type and it crosses the boundary with NO conversion check; the typed re-declaration re-runs conversion and WHNFs the composition (the wall, back). This one line is the difference between 8 GB OOM and 3 s.

**The instance (Ⓚ, AES full-encrypt KAT, 2026-06-19):** `encrypt-key key-C1 pt-C1 ≡ ct-C1` blew up as a monolith (30 min / 5.6 GB). TWO deep chains: the 10-round composition AND the key schedule (`nextRoundKey`'s word recursion, **exponential** to force — 9s/46s/241s for rk1/rk2/rk3, no term sharing). Both dissolved by the above; chain ~27 s. The SAME structure dissolved THREE instances (rounds, key schedule, AND the `Section8Claims` citation — where I re-hit the typed-re-declaration trap and fixed it by build-pinning) — one symmetry, an orbit of three.

**I declared the wall TWICE before the escape** (monolith "infeasible"; then per-round *cumulative* `Xₙ = round Mₙ₋₁ Xₙ₋₁` which literally re-carries the residue Agda forces) — and even BANKED the wrong verdict. Strong sibling of [[feedback_test_the_wall_before_declaring_it]] / [[feedback_a_flag_is_an_either_or_to_dissolve]]: a "won't normalise" framing is an either/or; the common structure is module-boundary opacity. Also: a cumulative chain that names the composition (`Xₙ`) re-introduces the wall; INDEPENDENT pins (concrete in → concrete out) + a recomposer that stays abstract is the residue-free form.