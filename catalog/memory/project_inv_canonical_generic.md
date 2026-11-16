---
name: inv-canonical-generic
description: Generic inv-left/right/inv-canonical proved arithmetically in Coxeter.Cyclic.InvCanonical via inv-pos-add-mod + ∸ identities
metadata: 
  node_type: memory
  type: project
  originSessionId: d49d2868-8ade-4add-9d72-b31958685ef0
---

`Substrate.Groups.Coxeter.Cyclic.InvCanonical (n : ℕ)` proves the three
inverse-canonical properties generically over `Canonical-ex` inputs,
decomposed file-per-lemma:

- `InvPosAddMod` — arithmetic core `(toℕ (inv-pos k) + toℕ k) mod-suc n ≡ 0`
  via case-split on Fin k + `∸-+-id` + `suc-mod-suc-self`.
- `Left` — `normalize (inv w ++ w) ≡ []` via `inv-power-eq` + `power-concat-eq`
  + `power-cyclic-normalize` + `InvPosAddMod`.
- `Right` — `normalize (w ++ inv w) ≡ []` via the same chain with `+-comm`.
- `InvInv` — `inv (inv w) ≡ w` via two `inv-power-eq` applications +
  `toℕ-inv-pos-inv-pos` (the Fin-level involution, proved by `∸-suc-l`
  + `∸-∸-cancel`).

Foundation additions to support the arc:
- `Order.agda`: `<→≤`, `≤-trans`, `≤-<-trans`.
- `Sub.agda`: `∸-+-id`, `∸-≤-self`, `m∸m≡0`, `∸-suc-l`, `∸-∸-cancel`.
- `Cyclic.Inverse`: `inv-power-eq` exposed (was private).

Per-Zₙ-Coxeter (Z2/Z3/Z4/Z5/Z7) drop the local cover-by-refl inv-* proofs
(-86 lines / +20 renaming lines) and alias the generic ex-variants via
the existing `renaming` clause:
  `inv-left-canonical-ex  to inv-left-canonical`
  `inv-right-canonical-ex to inv-right-canonical`
  `inv-inv-canonical-ex   to inv-inv-canonical`

What stays per-Zₙ: the named `canonical-cover` (n-arity) and variadic
pattern synonyms (`c-aa`, `c-aaa`, …), because downstream consumers
(S3-on-V4 etc.) still pattern-match on the named synonyms. The generic
`c-pos k` pattern (added in [[s3-on-v4-file-per-lemma]] aftermath) is
available as an alternative entry point.

How to apply: when a new cyclic Coxeter instance is added (Z6, Z8, …),
the renaming clause + nth-power-identity + InvCanonical re-export
deliver the entire inverse-property package "for free"; no per-instance
arithmetic needed.

Deferred: lifting `gen-≟` + `same-canonical` to Cyclic (still per-Zₙ),
and the full c-pos migration to drop named patterns entirely (would
require Z{n}-Coxeter-Group re-export cleanup + downstream migration).
