---
name: feedback_cross_carrier_tie_is_crossmix
description: "a cross-carrier tie is a CrossMix cospan (Wedge), NOT a hand-built bridge or an \"un-mechanical\" gap"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a96a1d8c-75ae-47e6-807c-c4988d800d8f
---

When two results live on DIFFERENT carriers and need tying together, do NOT frame it as "needs a hand-built bridge / isn't mechanical / open edge." The substrate already has the cross-carrier construction: **`Algebra.Wedge.CrossMul`** — the `CrossMix A B R` cospan `A → R ← B` (two carriers embed via `Bridge`s into a common multiplicative carrier R; `cross a b = mul R (embA a) (embB b)`), with **COHERENCE = the cross term being a nilpotent residue** (`Nilpotent R (cross …)`): degree ≤ 1 = orthogonal/clean correspondence; degree n > 1 = a GRADED obstruction whose degree IS the cost (not a binary wall). `Wedge.Cross` is the product/lockstep form; CRT (orthogonal idempotents `e₁·e₂≡0`) is the worked numeral instance.

**Why:** I keep defaulting to "design a bridge" or "this cross-carrier identity is the open conceptual edge" when the answer is to REACH FOR THE WEDGE. The user caught this on Ξ★.3 ("the cross-carrier tie isn't mechanical? Isn't that CrossMixer?"): center-is-★ ties the ℤ³ cycle-space witness to the ℚ G_NOT — and it is a CrossMix coherence (the Wheatstone bridge-null = the coupling cross term vanishing = the orthogonal correspondence = the loop kernel = the witness). Mechanical, not posited. Reinforces [[project_wedge_pentagon_sphere]] ("Wedge CONSTRUCTS bridges") and [[project_bridge_indexes_algebra_category]].

**How to apply:** on any "tie carrier A to carrier B" task — (1) reach for `Wedge.CrossMul.CrossMix` (cospan to a common R) BEFORE hand-building; (2) the "do they interfere?" question = the cross term's nilpotency DEGREE (0 = clean, n = graded cost), never a yes/no wall; (3) if a richer/numeral common carrier R is needed for graded coherence, that is a deferral (like CrossMul's own CRT deferral), not an impossibility. The "bridge-null / orthogonality / witness ⟂ representable / e₁·e₂≡0" are all the SAME coherence shape: the cross term → z.
