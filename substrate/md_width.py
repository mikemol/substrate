# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Find the narrowest writer width that keeps a corpus both convergent and all-pipe.

⚑⚑⚑ IT IS A CONJUNCTION, AND THE OPERATOR NAMED IT AS ONE (2026-08-01: *"now you have a supremum
bound; binary search for this AND this other condition"*):

  1. **converges** — `normalize(normalize(x)) == normalize(x)`, so a write is stable;
  2. **all tables stay PIPE** — no multiline fallback, which is what trades MD060 for
     MD035/MD003/MD023. MEASURED: at 120 columns all fifty of the plan's tables went multiline.

⚑⚑ AND BISECTION IS SOUND ON (2) IN A WAY IT IS NOT ON (1) ALONE. *Every table fits the budget* is
monotone BY CONSTRUCTION — widening can only keep a table inside it — whereas the earlier claim
that CONVERGENCE is non-monotone in width was an artifact of a termination bug, not a property of
the problem. So (2) supplies the genuine boundary and (1) is checked AT the answer rather than
searched on. That is the difference between a search whose monotonicity is asserted and one whose
monotonicity is structural, and asserting it is how the first attempt went wrong.

⚑ THE SUPREMUM MUST BE VERIFIED, NEVER ASSUMED. The search checks its upper bracket first and
REFUSES when it does not hold: without that it would be hunting a boundary that may not exist,
which is exactly the state the first attempt was in. A `None` width with the tried sequence
attached says *no width in this range satisfies both*, which is a finding rather than a failure.

⚑⚑⚑ THIS TAKES A PREDICATE, NOT PATHS, AND THAT IS THE WHOLE TESTABILITY GAIN. The origin opened
every document, shelled to pandoc, wrote to a temp directory and read the result back — so the
BISECTION itself could only be exercised by having a corpus and a converter, and a search bug and a
pandoc bug were indistinguishable. Here the caller supplies `holds(width)`; `corpus_predicate`
builds the real one, and a case builds a synthetic one whose boundary it knows.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

from substrate import md_fixpoint, table_syntax

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

#: The default bracket. `LO` is narrower than any width the corpus has needed; `HI` is the width at
#: which the corpus was MEASURED all-pipe and convergent, which is what makes a bracket valid.
LO = 60
HI = 2000

#: The writer flags the width is searched within. Kept here because the answer is only meaningful
#: for the writer it was measured against.
BASE = "markdown-smart+pipe_tables"


class Try(NamedTuple):
    """One width and what each half of the conjunction said about it."""

    width: int
    converges: bool
    all_pipe: bool

    @property
    def holds(self) -> bool:
        """Report whether this width satisfies BOTH conditions."""
        return self.converges and self.all_pipe

    def why(self) -> str:
        """Return a one-line account naming which half failed."""
        if self.holds:
            return f"{self.width}: converges and all-pipe"
        failed = [
            name
            for name, ok in (
                ("does not converge", self.converges),
                ("falls back off pipe", self.all_pipe),
            )
            if not ok
        ]
        return f"{self.width}: " + " and ".join(failed)


class Search(NamedTuple):
    """The narrowest satisfying width, or None, with every width tried.

    ⚑ THE TRIED SEQUENCE IS RETURNED BECAUSE A `None` IS NOT SELF-EXPLANATORY. A bare None cannot
    distinguish *the bracket was invalid* from *the boundary is outside this range*, and the
    origin's own history is a sequence of verdicts that were wrong in ways only the sequence
    revealed.
    """

    width: int | None
    tried: tuple[Try, ...]
    why: str


def options(width: int, base: str = BASE) -> str:
    """Return the pandoc writer options for one candidate width."""
    return f"{base} --columns={width} --wrap=preserve"


def corpus_predicate(
    sources: Sequence[str],
    convert: Callable[[str, str], str],
) -> Callable[[int], Try]:
    """Return the real `holds(width)` over `sources`, using `convert` as the writer.

    ⚑ THE CONVERTER IS INJECTED so this module never shells out. `md_pandoc.convert` is the
    production one; a case supplies its own and gets a boundary it controls.

    ⚑⚑ A CONVERTER FAILURE IS A FAILING WIDTH, NOT A CRASH — but it is recorded as failing BOTH
    halves rather than silently as one, because a width that cannot be rendered tells us nothing
    about convergence and claiming otherwise would put a guess in the tried sequence.
    """

    def holds(width: int) -> Try:
        opts = options(width)
        converges = all_pipe = True
        for src in sources:

            def normalize(text: str, o: str = opts) -> str:
                return convert(text, o)

            try:
                emitted = normalize(src)
            except (OSError, RuntimeError, ValueError):
                return Try(width, converges=False, all_pipe=False)
            if not md_fixpoint.run(src, normalize).converged:
                converges = False
            shape = table_syntax.forms(emitted.split("\n"))
            if shape.multiline or shape.grid:
                all_pipe = False
        return Try(width, converges, all_pipe)

    return holds


def narrowest(holds: Callable[[int], Try], lo: int = LO, hi: int = HI) -> Search:
    """Return the narrowest width in `[lo, hi]` for which `holds` is true.

    ⚑⚑⚑ THE UPPER BRACKET IS CHECKED FIRST AND ITS FAILURE IS A REFUSAL. A bisection over a
    predicate that never holds returns whichever endpoint the loop happens to land on, which reads
    as an answer. Verifying the supremum is what makes the returned width a boundary rather than
    an artifact of the loop.
    """
    tried: list[Try] = []

    def probe(width: int) -> bool:
        got = holds(width)
        tried.append(got)
        return got.holds

    if not probe(hi):
        return Search(None, tuple(tried), f"no width holds: the upper bracket {hi} fails")
    if probe(lo):
        return Search(lo, tuple(tried), f"the lower bracket {lo} already holds")

    # ⚑ THE INVARIANT IS `lo` FAILS AND `hi` HOLDS, so the boundary lies strictly between them and
    # the loop narrows it by one each round — a well-founded descent on `hi - lo`.
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if probe(mid):
            hi = mid
        else:
            lo = mid
    return Search(hi, tuple(tried), f"narrowest holding width is {hi}, and {lo} fails")
