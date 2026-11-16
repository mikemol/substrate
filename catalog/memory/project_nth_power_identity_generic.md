---
name: nth-power-identity-generic
description: Generic (suc n)-power identity proved once in Coxeter.Cyclic.NthPower; Z2/Z3/Z4/Z5/Z7 per-instance proofs collapse to one-liners
metadata: 
  node_type: memory
  type: project
  originSessionId: d49d2868-8ade-4add-9d72-b31958685ef0
---

`Substrate.Groups.Coxeter.Cyclic.NthPower (n : ℕ)` proves
`nth-power-identity : (w : Word Gen) → apply-power-suc w n ≈ ε`
once and for all cyclic Coxeter groups.

Submodule layering:
- `NthPower.Concat` — power-concat-eq + iter-power-mod + power-cyclic-normalize
  (`normalize (power k) ≡ power (k mod-suc n)`).
- `NthPower.Flat` — apply-power-suc / apply-power-suc-flat + flatten + flat-normalize.
- `NthPower` — flat-power-eq + mult-suc-n-mod + nth-power-canonical + nth-power-identity.

Re-exported from `Substrate.Groups.Coxeter.Cyclic` shim.

Per-Zₙ specializations are now one-liners (apply-power-suc reduces definitionally):
- Z2 `self-inverse = nth-power-identity` (n=1, `(w · w) ≈ []`).
- Z3 `cube-identity = nth-power-identity` (n=2).
- Z4 `fourth-power-identity = nth-power-identity` (n=3).
- Z5 `fifth-power-identity = nth-power-identity` (n=4).
- Z7 `seventh-power-identity = nth-power-identity` (n=6).

Why: was [[discipline/feedback_expose_generator_not_orbit_applies]] — five per-Zₙ
flatten-arith-canonical towers (~25 lines each) were exposing the same generator;
collapsing them gained ~100 net lines and centralized the arithmetic chain in one place.

How to apply: any new Z_(suc n) Coxeter instance gets the (suc n)-power identity
for free via `nth-power-identity`. New Coxeter groups with different relator patterns
(e.g., dihedral) still need their own arc.
