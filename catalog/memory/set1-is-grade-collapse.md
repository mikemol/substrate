---
name: set1-is-grade-collapse
description: "Set₁ is not a separate problem — it is grade-collapse: forcing leveled/graded things into 'one carrier' is a level succession. Construct across the grade (Set₀ per step); never hold the whole family as one object."
metadata:
  node_type: memory
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

There is ONE Set₁ move, wearing different clothes. Whenever heterogeneously-graded
data (e.g. a wedge's four points: dividend at grade `suc n`, divisor at grade `n`,
quotient a number, remainder at grade `n`) is forced "over one carrier `C`", you have
QUOTIENTED AWAY the grade distinctions. That quotient is a **grade lift**; a grade lift
is a **level succession** (`Set → Set₁`); so "one carrier" for genuinely-leveled points
IS Set₁, dressed as a convenience. `record DivStr (C : Set)` packing a carrier,
`Σ Set DivStr`, a code universe `El : Code → Set`, `Fam : Set → Set₁`, `objects : List
(Σ Set …)` — all the same move: **hold the whole graded/leveled family as a single
object**. The predicativity floor IS grade-collapse.

**Why:** a `List` (or any single carrier) demands a HOMOGENEOUS element type, so listing
things at different grades must pack the grade/carrier as data — and a `Set`-as-data is
`Set₁`. `C : ℕ → Set` (a graded family) held whole is `Set₁`; used only via `(n : ℕ) → C n`
it is `Set₀` at each step.

**How to apply:** don't collapse the grade — CONSTRUCT ACROSS it, one step at a time. The
generative form (`recon n : C n → R n → C (suc n)`, a grade-raising MAP; the witness
tower; a simplicial (co)face operator) relates grade `n` to `n+1` by a map, each grade at
its own Set₀, never forming the whole family. That is the honest Set₀ resolution; the
capped/materialized form (hold every grade at once) is the Set₁. This is the deep reason
behind [[set1-carrier-always-parameterize]] (parameterize = keep the carrier a per-use
Set₀, don't field/pack it) and the generic-not-materialized Registry paydown. Corollary
(watch for it): "just map the same carrier to each point" is exactly this collapse —
reject it for graded points.
