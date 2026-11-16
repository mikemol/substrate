---
name: negative-findings-corpus-bound
description: "when reporting empirical absence (X doesn't beat Y), bound it as \"on tested corpora × tested modes\" — never generalise to \"Y is the optimum\""
metadata: 
  node_type: memory
  type: feedback
  originSessionId: bb094a39-05c5-494d-8b01-cc34809ccae9
---

When a sweep finds no improvement, the honest claim is
**"on the tested corpora with the tested modes, no mode
outperformed the baseline"** — bounded to what was actually
measured. Refrain from phrasings like:

  * "greedy IS the local optimum"
  * "X is structurally best"
  * "the factor doesn't earn bits"

These collapse "absence on tested set" into "structural property
of the codec." That collapse is a negation-overclaim — the same
pattern named in [[negative-findings-in-corpus]] and rejected by
[[reject-lem-in-substrate]] / intuitionistic discipline.

**Why:** in the U-arc capstone wording, "greedy IS the local
optimum on text/ELF/zeros" was corrected by the user to "on the
three standard corpora, none of the other modes outperformed
greedy." The first form forecloses what factor-biased corpora
might reveal; the second leaves the W-arc empirical question
open.

**How to apply:** when reporting (E3)-style sweep results,
default to the bounded form:

  * say "no tested mode beat baseline" not "baseline is best"
  * say "no benefit observed at sizes 256-1024" not "no benefit"
  * say "factor X did not activate" not "factor X never helps"

The active voice belongs to what was measured; the structural
verdict requires either proof or exhaustive coverage of the
relevant corpus space.

Related: [[negative-findings-in-corpus]] (the shape of negation
itself is the overclaim signal); [[reject-lem-in-substrate]]
(absence of evidence ≠ evidence of absence); [[choice-rigidification-in-substrate]]
(rigidifying "this is THE optimum" is the gauge-collapse pattern
this rule is meant to prevent at the empirical layer).
