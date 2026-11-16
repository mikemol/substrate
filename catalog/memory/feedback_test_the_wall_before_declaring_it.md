---
name: feedback_test_the_wall_before_declaring_it
description: "Before writing any 'revert / defer / impossible / it's a wall' conclusion, test that the obstruction is real AND enumerate ≥2 alternative witnesses/encodings — and re-read your own just-emitted notes, the path is often one you already flagged 'for later'."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c1329ff9-896f-4600-8952-67ec237e5bbc
---

When an obstruction appears, do NOT conclude "revert / defer / can't / universe wall"
on the FIRST escape's cost. The default loop scores "retreat to banked wins" as cheap
and "enumerate alternative witnesses" as expensive, with no step forcing the enumeration
— so the cheap retreat fires by default. That is the recurring **premature-wall reflex**
(sibling of the negative-findings overclaim, [[feedback_negative_findings_in_corpus]] /
[[feedback_negative_findings_corpus_bound]]; and of the stale-`.agdai` "pre-existing"
misfire this same session).

**Why:** the obstruction is usually real for the FIRST encoding tried (anchoring) but
sidestepped by a different witness. Concretely (2026-06-13, el-atlas IDC): I reached for
the ∀-probe `faithful-refines-verdict` (Set₁, incompatible with `Statement : Claim →
Set`), called it a "universe wall," and reverted — when the **Set-level codec instance**
(`faithful-refines-verdict` at the `recode` probe) graduated IDC in two small edits, no
universe bump. I had even WRITTEN DOWN the alternative two steps earlier ("`kernel-Quotient`
is a sibling of my `ker-Quotient` — for later") and not connected it.

**Recurrence (2026-06-17, jea_circuit Φ1′):** I built a wall INTO code — `nodal_solve` raised
`TypeError` for a subtraction-free carrier, with a docstring asserting "sub-free ⟹ cannot solve
irreducible graphs (Wheatstone)." Untested for the alt route; the user supplied it (logspace +
division + exp). The wall was a collapsed COORDINATE: subtraction is the Gaussian-elimination
chart, not the law — by Matrix-Tree, G_eff is a subtraction-free RATIO of spanning-tree polynomials,
and the sub-free wedge solves the irreducible graph exactly (`nodal_solve_subfree`). Note the shape:
a `raise TypeError("... cannot ...")` IS a premature wall in executable form — same reflex, harder
to spot because it reads as a guard. Also a recurrence of [[feedback_coordinate_to_geometry]].

**How to apply:** before any "revert/defer/impossible" line (or a guard/`raise` that encodes one) —
1. **Test** the asserted obstruction (run the typecheck/command); an untested wall is
   affect, not a finding. (When I finally tested `Statement : Claim → Set₁`, the failure
   was real — but the wall was around the wrong witness.)
2. **Enumerate ≥2 alternative witnesses/encodings**; the revert message must cite a tested
   failure of the BEST alternative, not the first.
3. **Re-read your own recent notes** — the "for later" aside is often the path now.

Firing layer: this class is NOT hook/gate-able (it is about reasoning, not a detectable
repo state), so it terminates here (a memory, the weak layer — declared as such) plus the
standing **retrospective-ritual** trigger, which forces G3/G4 on completed actions.
