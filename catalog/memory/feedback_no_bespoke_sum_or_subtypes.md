---
name: feedback_no_bespoke_sum_or_subtypes
description: "In substrate Agda, don't model a task's data with bespoke sum types / subtypes / Σ-packaging — use the grounded constructions; consumer supplies meaning via a valuation"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

Building the pyast rewrite rig, the user rejected, in quick succession: a bespoke `data PyPrim`
(sum type / enumeration), a `Σ (Perm n) (λ σ → act σ t ≡ t′)` "same-orbit" relation (subtype /
proposition-packaging), and my calling SPPF's missing additive unit a "gap" (it's a **rig**, no
zero ctor; ring comes via the **log/antilog** move, not a `zero`). Three instances of ONE
discipline.

**Why:** the substrate models everything as a grounded CONSTRUCTION over the canonical carriers —
`Fin` (finite alphabets/positions), `SPPF` (the free rig / free-functor terms), `Perm`/`SnGroup`
(symmetry), `LehmerPath` (the factoradic orbit coordinate). A fresh `data`/coproduct, a
`Σ`-carved subset, or an `∃`/`∃!` proposition is the collapse the mission fights: it invents
ungrounded structure instead of specialising the existing generator. `∃!`/Σ is a construction to
EXPOSE (a fold), not to package ([[feedback_exists-unique_is_a_construction_not_a_sigma]]).

**How to apply:** before writing `data X`/`record`/`Σ …`/`∃ …` for a task's model, ask what
grounded construction it specialises. A finite alphabet is `Fin k`, not an enumeration. An orbit
coordinate is a total map from `LehmerPath n` (the point IS its residue), not a Σ of connecting
perms. The MEANING of a position is a CONSUMER valuation `Fin n → A` (the actions the category
builds are generic; the consumer supplies meaning), not a baked-in label type. Consuming the
LIBRARY's inductive types (mapping/folding over `SPPF`'s ctors) is fine — the prohibition is on
introducing your OWN sum/subtype as the data model. Ties to [[coxeter-word-is-combine-generators]]
and the reuse-search-before-building discipline.
