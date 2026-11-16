#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Read an arm's OWN PROSE for whether it declares its claims joint.

⚑⚑⚑ WHY THIS EXISTS (gate-G44). Two syntactic readings of relation-vs-bundle were built and both
were refuted: keying on the probed FIELD fused arms that ask two questions, and keying on the CALL
broke arms that assert one law at two points. Both shapes occur in both meanings, so the syntax
does not carry the distinction. What does carry it is written down — every arm sampled states its
own status in prose, and no AST reading reaches that.

⚑⚑ THREE PROSE FORMS, ALL MEASURED, NOT GUESSED. Sampling four INDEPENDENT arms found one signal
in three spellings:

  * CONJUNCTION — "names what is covered AND what is not", "is exported to the child, and a miss
    changes nothing". The claims are stated as one sentence with two halves.
  * CONTRAST — "returns the seed it found, not merely True". The second guard exists because the
    first alone is insufficient, which is what a control IS.
  * DECLARED FUSION — "BOTH HALVES ARE ASSERTED", "one law at two points, deliberately left
    fused". The author says it outright, usually under a ⚑.

⚑⚑⚑ IT REPORTS A FLOOR AND NEVER A VERDICT, WHICH IS THE WHOLE DESIGN. Prose is weaker evidence
than structure: an arm may be joint and say nothing, and a word may appear for unrelated reasons.
So a hit is EVIDENCE FOR jointness and a miss is SILENCE — never evidence against. A reader that
returned "independent" from an absent word would be the third refuted discriminator, and it would
fail in the licensing direction, which is the expensive one.

⚑ SO ITS OUTPUT IS A SECOND OPINION, not a replacement. `relation_arm` reads structure and this
reads intent, and the useful reading is where they DISAGREE.

⚑⚑⚑ BUT A DISAGREEMENT DOES NOT MEAN THE PROSE WINS, AND THE FIRST FRAMING OF THIS IMPLIED IT DID
(gate-G47). `the_generator_is_not_debt` matches `contrast` and is NOT joint: one of its two guards
is a FIXTURE PRECONDITION — *was the parse seen at all* — which protects the fixture rather than
asserting half a law. The structural reader calls it independent on probes `_derivations` and
`any`, two different predicates, and structure is RIGHT there.

⚑⚑ SO EVERY SIGNAL CLASS HAS A MEASURED FALSE-POSITIVE MODE. `conjunction` fires on the design
paragraph (gate-G46) and `contrast` fires on a fixture guard (gate-G47). A disagreement between
the two readers FLAGS AN ARM FOR A HUMAN READ; it settles nothing on its own, and neither reader
is the tiebreak.

⚑ AND THE OBVIOUS PATCH — key on WHERE the match sits, summary line versus design paragraph — was
tried and refuted in the same tick: `omitting_the_builder_skips_the_build` matches deep in a
paragraph and IS joint. Location does not predict correctness, so no such narrowing is applied.
"""

from __future__ import annotations

import ast
import re
import sys
from dataclasses import dataclass

from substrate import corpus

# How many rows to spell out before summarising.
SAMPLE = 12

# ⚑ A CONJUNCTION JOINING TWO CLAIMS, not any "and". The word must sit between clauses, which the
# comma-or-uppercase forms below approximate — a bare `and` inside a noun phrase ("covered and
# uncovered names") is the common false hit, so the pattern wants a verb-ish neighbourhood.
_CONJUNCTION = re.compile(r"\b(?:AND|and)\s+(?:a|an|the|what|that|it|its|this)\b")

# ⚑ A CONTRAST SAYS THE FIRST HALF IS INSUFFICIENT, which is the definition of a control.
_CONTRAST = re.compile(
    r"\b(?:not merely|rather than|not just|not only|but not|and not|never merely)\b"
)

# ⚑ AND SOMETIMES THE AUTHOR SIMPLY SAYS SO, usually under a ⚑ block.
_DECLARED = re.compile(
    r"\b(?:both halves|one law|deliberately left fused|the pair|together|jointly|"
    r"each alone|alone (?:is|would)|the discriminator is the (?:pair|second))\b",
    re.IGNORECASE,
)

_KINDS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("declared", _DECLARED),
    ("contrast", _CONTRAST),
    ("conjunction", _CONJUNCTION),
)


@dataclass(frozen=True, slots=True)
class Prose:
    """What one arm's own docstring says about whether its claims are joint."""

    suite: str
    name: str
    signal: str
    quote: str

    @property
    def joint(self) -> bool:
        """Whether the prose declares the claims joint — evidence FOR, never against.

        ⚑⚑⚑ A CONJUNCTION DOES NOT COUNT, AND THAT IS MEASURED (gate-G46). Auditing five hits
        found both `conjunction` matches FALSE and all three `contrast`/`declared` matches real.
        The weak class fires on the DESIGN PARAGRAPH — *"and a table of such bindings looks
        complete"* — which explains why an arm exists rather than describing what its guards
        assert. `a_binding_runs` is a sequential pipeline and `a_stamp_path_cannot_collide` tests
        two independent properties; both matched an `and` that was never about their claims.

        ⚑ SO THE WEAK CLASS IS REPORTED AND NOT COUNTED. Dropping it entirely would lose the
        evidence that it fires; treating it as jointness would freeze splittable arms, which is
        the over-reach that cost two structural discriminators.
        """
        return self.signal in {"declared", "contrast"}

    @property
    def weak(self) -> bool:
        """Whether the only signal is a conjunction — reported, never counted as joint."""
        return self.signal == "conjunction"


def _quote(text: str, found: re.Match[str]) -> str:
    """Return the sentence fragment around a hit, so a reader can audit the match."""
    start = max(0, found.start() - 40)
    end = min(len(text), found.end() + 40)
    return " ".join(text[start:end].split())


def read_doc(doc: str) -> tuple[str, str]:
    """Return `(signal, quote)` for one docstring, or `("silent", "")`.

    ⚑ THE KINDS ARE ORDERED STRONGEST FIRST. A declared fusion is the author saying it; a contrast
    is the author's reason; a conjunction is the weakest and the most likely to be incidental. The
    first hit wins so the reported signal is the best evidence present, not the last one scanned.
    """
    flat = " ".join(doc.split())
    for kind, pattern in _KINDS:
        found = pattern.search(flat)
        if found:
            return kind, _quote(flat, found)
    return "silent", ""


def read(path: str, names: frozenset[str]) -> tuple[Prose, ...]:
    """Return the prose reading for each named arm in one suite."""
    try:
        tree = ast.parse((corpus.ROOT / "substrate" / path).read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return ()
    out: list[Prose] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef) or node.name not in names:
            continue
        signal, quote = read_doc(ast.get_docstring(node) or "")
        out.append(Prose(path, node.name, signal, quote))
    return tuple(out)


def render(found: tuple[Prose, ...]) -> str:
    """Render the prose reading, as a floor.

    ⚑ THE SILENT COUNT IS NOT AN INDEPENDENT COUNT, and the wording says so. An arm whose prose
    says nothing about jointness has told this reader nothing at all — the same third-outcome
    discipline the structural reader keeps, arriving on the weaker instrument where it matters
    more.
    """
    if not found:
        return "joint-prose: no arms read — a fact about the WALK\n"

    joint = [p for p in found if p.joint]
    weak = [p for p in found if p.weak]
    out = [
        f"  {len(found)} arm(s) read",
        f"    prose DECLARES the claims joint      : {len(joint)}",
        # ⚑ THE WEAK CLASS IS ITS OWN ROW, because folding it into either side would hide a
        #   measured false-positive class — see `Prose.joint` and gate-G46.
        f"    a conjunction only (MEASURED WEAK)   : {len(weak)}",
        f"    prose says nothing (NOT independent) : {len(found) - len(joint) - len(weak)}",
    ]
    # ⚑⚑ THE SAMPLE NAMES ITS OWN CLASS, and this header is not decoration. The rows below are
    #   the JOINT arms, and they were previously appended directly beneath the SILENT count —
    #   so twelve `contrast` rows sat under a line reading "prose says nothing", where they read
    #   as its members. The counts were right and the layout inverted them, which is the
    #   over-read `render`'s docstring words the silent row to prevent, defeated one line later.
    if joint:
        out.append(f"    the {len(joint)} JOINT arm(s), with the quote that carries each match:")
    out.extend(
        f"      {p.signal:<11} {p.suite}::{p.name}\n        {p.quote}" for p in joint[:SAMPLE]
    )
    if len(joint) > SAMPLE:
        out.append(f"      … and {len(joint) - SAMPLE} more arm(s) declaring jointness")
    return "\n".join(out) + "\n"


def main(argv: list[str]) -> int:
    """Report what the structurally-INDEPENDENT arms say about themselves."""
    if argv:
        sys.stderr.write("usage: joint_prose.py\n")
        return 2
    from substrate import relation_arm  # noqa: PLC0415 — the population's owner

    by_suite: dict[str, set[str]] = {}
    for arm in relation_arm.splittable(relation_arm.census()):
        by_suite.setdefault(arm.suite, set()).add(arm.name)
    found: list[Prose] = []
    for suite in sorted(by_suite):
        found.extend(read(suite, frozenset(by_suite[suite])))
    sys.stdout.write(render(tuple(found)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
