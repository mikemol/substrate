---
name: feedback_judgement_is_demechanization
description: all judgement is demechanization; every line of code is a judgement; keep a line only when the mechanization it ENABLES exceeds the mechanization it COSTS by freezing a choice — a cost-ledger on code itself
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c1329ff9-896f-4600-8952-67ec237e5bbc
---

All judgement is demechanization: a judgement is a point where the live computation STOPS and a frozen choice
takes over -- it removes a degree of mechanization by substituting a fixed decision for something that could be
computed. Every line of code is such a judgement (crystallized choice). So every line has a balance:
  COST    = the mechanization it FORECLOSES (the adaptivity / generality / live-solve it replaces with a constant
            or a fixed control path).
  BENEFIT = the mechanization it ENABLES downstream (the automation / re-solve / generality it makes possible).
Keep a line/judgement ONLY when BENEFIT > COST -- it must deliver more useful mechanization than it costs by
being a judgement. A hardcoded constant or a frozen "best config" is GUILTY until proven net-positive.

This is the cost-function under the whole structural-not-scalar / navigator family:
- NET-NEGATIVE judgements (delete them): magic constants that froze a solve into a hand-coded ladder and bought
  ~nothing -- e.g. live_dispatcher.decide()'s I=0.1 / 150e9 / 10906e9 / <0.5 ternary (the constants cancelled or
  never bound; pure demechanization cost). [[feedback_structural_not_scalar]]
- NET-POSITIVE judgements (the leverage): a SMALL frozen choice that ENABLES a large mechanization -- use a Schur
  complement (kron_reduction); read /sys (discover); micro-ablate (measure_edges); argmin over the surface
  (navigate). A few lines buy the whole adaptive space across any graph / box / evidence. [[feedback_navigator_not_answer]]

**How to apply:**
- Writing code = spending judgement. For each line ask: what mechanization does this freeze, and what does it
  enable? Commit it only if it enables more than it forecloses.
- PREFER mechanizing lines (discover / measure / parameterize / solve / read-evidence) over judging lines
  (hardcode a constant / pick a winner / freeze a config / branch on a threshold). The former are usually
  net-positive; the latter are usually net-negative unless they buy disproportionate mechanization.
- When a judgement is unavoidable but not yet earned, make it PLUGGABLE and FLAG it (e.g. the navigator's g-slope
  heuristic and corner-sampling of convex knobs) -- a marked judgement to replace with a measured surface when it
  pays, not a frozen winner. Don't fabricate the mechanization you can't yet measure; don't freeze it either.
- Fewer, higher-leverage judgements beat many low-leverage ones. The best line of code mechanizes a whole space;
  the worst freezes one number that could have been read. (Cost-accounting twin of recompute-from-residue /
  never-discard-residue.)
