#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Print the counts-in-data census — the CLI over `substrate.data_numbers`.

⚑ THE CLI IS ITS OWN MODULE BECAUSE THE READER SHOULD NOT PRINT, the split the rest of this
toolkit uses: the reader returns data, this decides how to render it.

    data_numbers_show.py --root DIR [ROOTS...]            # the holders, largest first
    data_numbers_show.py --root DIR --sites [ROOTS...]    # every finding with its location
    data_numbers_show.py --root DIR --claims [ROOTS...]   # only the CLAIMS
    data_numbers_show.py --root DIR --skipped [ROOTS...]  # what the discriminator REFUSED

⚑⚑ THE CLAIMS MODE IS THE ONE THIS READER CAN OFFER AND ITS SIBLING CANNOT. `prose_numbers`
reports an upper bound throughout, because a quoted specimen and an assertion are both just a
number beside a noun. A named explanatory FIELD is different in kind — it is addressed to a
reader and asserts — so the claims are separable here, and separating them is more useful than
hedging the whole census uniformly.

⚑ THE BOUNDARIES PRINT WITH EVERY RUN, INCLUDING A CLEAN ONE. A zero here is a fact about the
POSITIONS this reader knows and about the measurement judgement it inherits, not about the tree.

⚑ THE TREE IS CHOSEN HERE (2026-09-24, operator: "We should not have things [like] corpus.ROOT"):
`--root` is required, read through `mikemol.corpus.tree_root.from_argv`, which refuses rather than
falling back; `data_numbers.census` takes it as an argument.
"""

from __future__ import annotations

import sys

from mikemol.corpus import tree_root

from substrate import data_numbers

#: How many holders to name before the tail is summarised.
_TOP = 25

#: How many refusals the skipped mode prints before it stops.
_SKIPPED_SHOWN = 60


def render_holders(found: list[data_numbers.Finding]) -> list[str]:
    """Render the per-file counts, largest holder first."""
    rows = data_numbers.by_holder(found)
    out = [f"  {n:>6}  {path}" for path, n in rows[:_TOP]]
    if len(rows) > _TOP:
        out.append(f"  … and {len(rows) - _TOP} more file(s)")
    return out


def _site_key(f: data_numbers.Finding) -> tuple[str, int, str]:
    """Order findings by file, then line, then number — canonical across runs."""
    return (f.path, f.line, f.number)


def _skipped_key(s: data_numbers.Skipped) -> tuple[str, int]:
    """Order refusals by file, then line."""
    return (s.path, s.line)


def _share_key(kv: tuple[str, int]) -> int:
    """Order the per-rule tally by descending share, so the widest rule reads first."""
    return -kv[1]


def render_sites(found: list[data_numbers.Finding]) -> list[str]:
    """Render every finding with its location, position and whether it is a claim."""
    out = []
    for f in sorted(found, key=_site_key):
        kind = "CLAIM" if f.claim else "mention"
        out.append(f"{f.path}:{f.line}  [{f.position}:{f.unit}:{kind}]  {f.number}")
        out.append(f"      {f.text[:160]}")
    return out


def render_skipped(refused: list[data_numbers.Skipped]) -> list[str]:
    """Render the refusals, grouped so an over-eager rule is visible by its share.

    ⚑ THE PER-RULE TALLY IS THE AUDIT, and this reader's rules OVERLAP — a braced repetition is
    both regex-shaped and format-shaped — so first-match-wins attribution is what keeps the
    shares from summing past the population. A case pins that order.
    """
    by_rule: dict[str, int] = {}
    for s in refused:
        by_rule[s.why] = by_rule.get(s.why, 0) + 1
    out = [f"  {n:>6}  {why}" for why, n in sorted(by_rule.items(), key=_share_key)]
    out.append("")
    out.extend(
        f"{s.path}:{s.line}  refused: {s.why}\n      {s.text[:120]}"
        for s in sorted(refused, key=_skipped_key)[:_SKIPPED_SHOWN]
    )
    if len(refused) > _SKIPPED_SHOWN:
        out.append(f"  … and {len(refused) - _SKIPPED_SHOWN} more refusal(s)")
    return out


def boundaries() -> list[str]:
    """Render what the reader cannot see — printed on every run, clean or not."""
    return [f"   ⚑ CANNOT SEE: {b}" for b in data_numbers.BOUNDARIES]


def main(argv: list[str]) -> int:
    """Read `--root <dir>`, then print the census over the named roots, or the whole tree."""
    try:
        tree, args = tree_root.from_argv(argv[1:])
    except tree_root.RootError as exc:
        sys.stderr.write(f"data_numbers: {exc}\n")
        return 2
    flags = {a for a in args if a.startswith("-")}
    roots = [a for a in args if not a.startswith("-")]

    found, refused, nfiles = data_numbers.census(*roots, root=tree.path)

    if "--skipped" in flags:
        sys.stdout.write("\n".join(render_skipped(refused)) + "\n")
        sys.stdout.write(
            f"{len(refused)} string(s) refused across "
            f"{len({s.path for s in refused})} file(s); {nfiles} file(s) read\n"
        )
        sys.stdout.write(
            "   ⚑ THESE ARE THE REFUSALS, shown so the discriminator can be AUDITED.\n"
            "     An over-eager rule is invisible in the census and visible only here.\n"
        )
        return 0

    shown = [f for f in found if f.claim] if "--claims" in flags else found

    if "--sites" in flags or "--claims" in flags:
        sys.stdout.write("\n".join(render_sites(shown)) + "\n")
    else:
        sys.stdout.write("\n".join(render_holders(shown)) + "\n")

    claims = [f for f in found if f.claim]
    sys.stdout.write(
        f"{len(found)} measured number(s) in prose-bearing string literal(s) across "
        f"{len({f.path for f in found})} file(s); {nfiles} file(s) read; "
        f"{len(refused)} string(s) refused; {len(claims)} of them CLAIMS\n"
    )
    # ⚑ A FLAGGED NUMBER IS NOT AUTOMATICALLY WRONG. A count in a data position is a measurement
    # written into a medium nothing re-derives, so it is either already false or a falsehood
    # waiting — and nothing here separates those. Retyping today's value is not a repair; it
    # rebuilds the condition one edit later. The repair is to CITE the tool that owns the figure.
    sys.stdout.write(
        "   ⚑ A COUNT HERE IS NOT AUTOMATICALLY WRONG — it is a measurement in a medium\n"
        "     nothing re-derives. Only re-running the owning tool can say whether it has\n"
        "     drifted, and RETYPING TODAY'S VALUE IS NOT A REPAIR — citing the tool is.\n"
        "   ⚑ THE CLAIMS ARE THE SHARPENED HALF: a named explanatory field asserts, where a\n"
        "     bare explanatory string may only be quoting. Outside those, this is an UPPER\n"
        "     BOUND, exactly as `prose_numbers` reports for prose.\n"
    )
    sys.stdout.write("\n".join(boundaries()) + "\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS MODULE, and it DELEGATES rather than
# exiting 0 — a no-op guard reports nothing, which the outcome classifier calls `silent`.
if __name__ == "__main__":
    if "--selftest" in sys.argv:
        from substrate import data_numbers_selftest

        sys.exit(data_numbers_selftest.selftest())
    sys.exit(main(sys.argv))
