---
name: coxeter-word-is-combine-generators
description: "When a group's _·_ routes through a word/normal-form representation, that IS the free-monoid reflection path, not a blocker — define the action on generators, extend over words, and the homomorphism is FREE."
metadata:
  node_type: memory
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

If a group's `_·_` "routes through" a word/normal-form representation
(`x · y = from-c (to-c x · to-c y)`, as `Groups.V4-Coxeter` / `Coxeter.Word`), do NOT
treat that as friction that blocks a proof (I twice called it a "blocker" — wrong). It
IS the point: a Coxeter/word presentation is the **free monoid on the generators**, and
"permute/combine generators" is literally the word algebra.

**Why:** to build a group ACTION or homomorphism, define it on the GENERATORS
(`genAct A = rowSwap`, `genAct B = colSwap`) and EXTEND over words
(`wordAct (g ∷ w) = genAct g (wordAct w)`). Then the homomorphism `wordAct (w₁ ++ w₂) ≡
wordAct w₁ ∘ wordAct w₂` is FREE — a two-line induction (concatenation ↦ composition),
no group-multiplication table, no casing the enumerated `{e,α,β,γ}`. The relations
(`s²=ε`, `AB=BA`) are discharged by exactly the generator involution/commute facts
(`rowSwap-inv`, `row-col-commute`); normalize-invariance of the action follows from an
8-case `insert` lemma → `wordAct (normalize w) ≡ wordAct w`, giving `wordAct ⟷ Bφ` as an
iff through the normal form (`to-c`/`from-c`).

**How to apply:** enumerated-element casing is the shadow; the word-level reflection
representation is the real thing, and it is free precisely BECAUSE it goes through the
word algebra. Reach for `Coxeter.Word` + the generator map, not the group table. (Also:
`deloop`/`DeloopingGroup` turns the group into the one-object groupoid; `PresentedGroup`
is the group-by-generators.) See [[free-universal-property]], [[expose-generator-orbit]].
