# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Decide whether each exemption in a markdownlint config is EARNED or decoration nobody re-checks.

⚑⚑⚑ A DISABLED RULE IS A CLAIM, AND NOTHING CHECKED IT. The first config written for this project
turned off FOUR rules. Measured: two of them fire ZERO times on the documents they govern — pure
decoration, and the kind that rots into *we have always had that off*. The other two were different
in kind: one wanted a WIDTH the documents already had, which is configurable rather than
disableable, and only the last was a genuine mismatch. **One exemption of four was real.**

⚑⚑ THE VERDICTS ARE THE POINT AND THERE ARE FIVE, because collapsing them to on-or-off is what let
the decoration survive:

  `earned`      the rule fires enough that the exemption is load-bearing
  `unearned`    disabled and fires ZERO times — delete it, the rule costs nothing
  `paydown`     disabled and fires FEW times — the findings are fixable CONTENT, and fixing them
                RETIRES the exemption rather than justifying it
  `configured`  not disabled, given a value that makes it AGREE with the writer — an agreement,
                never a suppression
  `live`        not mentioned in the config at all and firing — real debt, and reporting it is
                what stops the audit reading as a clean bill for a document full of findings

⚑ AND `paydown` IS WHY THIS IS AN AUDIT AND NOT A GENERATOR. A tool that WROTE the config from the
findings would emit a disable for two missing blank lines — encoding a document's defects as
permanent policy. The audit reports what an exemption COSTS so a person decides, and for a small
population the fix is almost always the document.

⚑⚑ IT TAKES THE CONFIG AND THE COUNTS, NOT A PATH. The origin read the JSON, listed the directory
beside it, and ran the linter itself — so the verdict rules could only be exercised by building a
directory of markdown that produces the right findings. Here the caller counts (with `md_lint`) and
this classifies, which is what makes each of the five statable as a case.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

#: At or below this many findings, a disabled rule is PAYDOWN — the document can absorb the fix.
#: Above it, the exemption is load-bearing. ⚑ A THRESHOLD, NOT A LAW: it is exposed so a caller
#: with a different tolerance can say so rather than disagree silently.
PAYDOWN_MAX = 3

#: Config keys that are schema metadata rather than rules.
META_PREFIX = "$"

#: The verdict classes, in the order a reader should scan them — actionable first.
CLASSES = ("unearned", "paydown", "earned", "configured", "live")


class Verdict(NamedTuple):
    """One config entry or live rule, with the account that decided it.

    ⚑ THE DETAIL CARRIES THE COUNT AND THE DENOMINATOR. `disabled but fires 0 times` says nothing
    without *over how many documents*, because zero findings from a corpus of zero documents is a
    fact about the run rather than about the rule.
    """

    verdict: str
    rule: str
    detail: str

    def why(self) -> str:
        """Return a one-line account naming the rule, its verdict and the reason."""
        return f"{self.rule}: {self.verdict} — {self.detail}"


def _disabled_verdict(rule: str, hits: int, documents: int, paydown_max: int) -> Verdict:
    """Return the verdict for a rule the config turns OFF.

    ⚑⚑ THE ZERO CASE IS THE ONE THAT MATTERS. A disabled rule that never fires is an exemption
    nobody is paying for, and it survives precisely because nothing asks — the audit exists for
    this row.
    """
    if hits == 0:
        return Verdict(
            "unearned",
            rule,
            f"disabled but fires 0 times over {documents} document(s) — "
            f"delete it, the rule costs nothing",
        )
    if hits <= paydown_max:
        return Verdict(
            "paydown",
            rule,
            f"disabled, fires {hits}x over {documents} document(s) — few enough to "
            f"FIX in the document and retire the exemption",
        )
    return Verdict(
        "earned", rule, f"disabled, fires {hits}x over {documents} document(s) — load-bearing"
    )


def _declared(
    config: Mapping[str, object], counts: Mapping[str, int], documents: int, paydown_max: int
) -> list[Verdict]:
    """Return one verdict per rule the config mentions."""
    out: list[Verdict] = []
    for rule in sorted(config):
        if rule.startswith(META_PREFIX):
            continue
        hits = counts.get(rule, 0)
        if config[rule] is False:
            out.append(_disabled_verdict(rule, hits, documents, paydown_max))
        else:
            out.append(
                Verdict(
                    "configured",
                    rule,
                    f"given a value rather than disabled, {hits} finding(s) remain",
                )
            )
    return out


def _live(config: Mapping[str, object], counts: Mapping[str, int]) -> list[Verdict]:
    """Return a row per firing rule the config does not mention.

    ⚑ THESE ARE NOT OPTIONAL. Without them the audit answers only *are my exemptions justified* and
    reads as a clean bill for a corpus with real debt — the question a reader actually has is what
    the linter would say, and an unmentioned firing rule is part of that.
    """
    return [
        Verdict("live", rule, f"ON and firing {counts[rule]}x — real debt, not exempt")
        for rule in sorted(counts)
        if rule not in config
    ]


def audit(
    config: Mapping[str, object],
    counts: Mapping[str, int],
    documents: int,
    paydown_max: int = PAYDOWN_MAX,
) -> list[Verdict]:
    """Return one verdict per config entry, plus a `live` row per firing rule the config omits.

    ⚑ `documents` IS THE CALLER'S TO SUPPLY BECAUSE ONLY THE CALLER WALKED. A denominator this
    module inferred would be a second authority on which documents the config governs.
    """
    return _declared(config, counts, documents, paydown_max) + _live(config, counts)


def by_verdict(rows: Sequence[Verdict], verdict: str) -> list[Verdict]:
    """Return only the rows carrying `verdict`."""
    return [row for row in rows if row.verdict == verdict]


def summarise(rows: Sequence[Verdict], documents: int) -> str:
    """Return one line naming each non-empty verdict class, with the denominator.

    ⚑ THE DENOMINATOR IS THE DOCUMENT COUNT, NOT THE ROW COUNT. `0 unearned` from a config with no
    entries and `0 unearned` from a config whose every exemption is load-bearing are different
    claims, and only the corpus size separates a real audit from one that read nothing.
    """
    seen = [f"{len(by_verdict(rows, name))} {name}" for name in CLASSES if by_verdict(rows, name)]
    body = ", ".join(seen) if seen else "no rules audited"
    return f"lint-config: {body}, over {documents} document(s)"
