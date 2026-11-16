---
name: feedback_wedge_not_projection
description: "a \"scalar\"/single-channel view of a richer carrier is a NON-LOSSY wedge (rotation; residue in hidden structure), not a lossy projection — the substrate never discards; only the partial LOOK truncates. Don't frame no-collapse/quotient results as \"loss.\""
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c1329ff9-896f-4600-8952-67ec237e5bbc
---

The user's principle (2026-06-12, developing the Nedge ↔ substrate bridge):
"we never discard anything. But when we LOOK, we might not always be looking
where the residue went — *that* is the truncation that's lossy."

So converting an implicit single-channel carrier to an explicit multi-channel
one is **not** a lossy projection. If the single channel is multi-channel
under the hood, the map is a NON-LOSSY **wedge** — a basis change / rotation
that moves the residue into the carrier's HIDDEN structure (think two reals →
one complex carrier, residue in the phase; or a=qb+r keeping r). Nothing is
discarded by the *encoding*. The only lossy act is **truncation-on-looking**:
reading one channel when the residue went into the other.

**Why:** I repeatedly framed projections / quotients / no-collapse results as
"loss" — "Nedge = the collapse the dual-rail corrects," "the single rail can't
carry the verdict (lossy)." That is too adversarial AND wrong: the upgrade
PRESERVES the original (it's a faithful reading/projection of the richer form),
and the richer carrier conserves everything. The "can't carry" theorem is the
LOOK failing, not the structure losing.

**How to apply:** when a `no-collapse` / `no-single-rail` / quotient result
shows "X cannot carry Y," state it as *"the LOOK at X is partial; Y's residue
is conserved in the hidden channel,"* never "X loses Y." Build the non-lossy
iso (the wedge) ALONGSIDE the can't-carry theorem — cf.
`Logic/Evidence/Verdict/NedgeShadow.agda`: `bias-cannot-carry-verdict` (the look
fails) sits next to `recode`/`unrecode` round-trips (Evidence ≅ Bool×Bool,
non-lossy) and `verdict-survives-recode` (the full re-encoding keeps it).
Substrate constructs this is: the Wedge (keeps the remainder a=qb+r),
Cayley-Dickson doubling ℝ²→ℂ, the exp⊣log atlas (two non-lossy charts of one
value), §11.5 Z=R+jX. Corollary: WHERE YOU LOOK is the gauge/chart choice — so
this is the same discipline as [[feedback_choice_rigidification_in_substrate]]
(don't mistake your look for the whole) and [[feedback_negative_findings_in_corpus]]
(don't overclaim loss). Related: [[project_wedge_pentagon_sphere]].
