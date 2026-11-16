#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Print the unwitnessed-example census — the CLI over `substrate.docstring_examples`.

⚑ THE CLI IS ITS OWN MODULE BECAUSE THE READER SHOULD NOT PRINT, the split the rest of this
toolkit uses: the reader returns data, this decides how to render it.

    docstring_examples_show.py [ROOTS...]            # the holders, largest first
    docstring_examples_show.py --sites [ROOTS...]    # every example with its location
    docstring_examples_show.py --skipped [ROOTS...]  # what the discriminator REFUSED, and why

⚑⚑ THE BOUNDARIES PRINT WITH EVERY RUN, INCLUDING A CLEAN ONE. A zero from this reader is a
fact about the MATCHER — an example exercised under another spelling, or one whose case was
deleted, reads exactly like one that never had a case. A reader who does not know that reads a
small number as a clean tree, which is the false-zero shape this repo keeps catching.

⚑ THE SKIPPED MODE EXISTS SO THE REFUSALS ARE AUDITABLE. An over-eager refusal rule is
invisible in the census by construction: it makes the tree look clean. The only way to check a
discriminator is to read what it decided NOT to say.
"""

from __future__ import annotations

import sys

from substrate import docstring_examples

#: How many holders to name before the tail is summarised.
_TOP = 25

#: How many refusals the skipped mode prints before it stops.
_SKIPPED_SHOWN = 60


def render_holders(found: list[docstring_examples.Example]) -> list[str]:
    """Render the per-file counts, largest holder first."""
    rows = docstring_examples.by_holder(found)
    out = [f"  {n:>6}  {path}" for path, n in rows[:_TOP]]
    if len(rows) > _TOP:
        out.append(f"  … and {len(rows) - _TOP} more file(s)")
    return out


def _site_key(e: docstring_examples.Example) -> tuple[str, int, str]:
    """Order examples by file, then line, then span — canonical across runs."""
    return (e.path, e.line, e.span)


def _skipped_key(s: docstring_examples.Skipped) -> tuple[str, int]:
    """Order refusals by file, then line."""
    return (s.path, s.line)


def _share_key(kv: tuple[str, int]) -> int:
    """Order the per-rule tally by descending share, so the widest rule reads first."""
    return -kv[1]


def render_sites(found: list[docstring_examples.Example]) -> list[str]:
    """Render every unwitnessed example with its location and the suite that lacks it."""
    out = []
    for e in sorted(found, key=_site_key):
        # ⚑ "NO SIBLING SUITE" IS NOT "NO CASES", and the first cut of this line said the wrong
        # one. A module carrying its cases inline — every vendored hook here — was rendered as
        # having no suite while its own arms were being read. The reader consults BOTH; the
        # render must not describe a narrower population than the one that was searched.
        where = e.suite or "its own inline cases (no sibling suite — see suite_gap)"
        out.append(f"{e.path}:{e.line}  [{e.signal}]  {e.span}")
        out.append(f"      no case in {where}")
    return out


def render_skipped(refused: list[docstring_examples.Skipped]) -> list[str]:
    """Render the refusals, grouped so an over-eager rule is visible by its share.

    ⚑ THE PER-RULE TALLY IS THE AUDIT, and the sites below it are the evidence. A rule whose
    share dwarfs the others is the one to read first — that is what an over-broad refusal looks
    like from outside, and it is invisible in the census by construction.
    """
    by_rule: dict[str, int] = {}
    for s in refused:
        by_rule[s.why] = by_rule.get(s.why, 0) + 1
    out = [f"  {n:>6}  {why}" for why, n in sorted(by_rule.items(), key=_share_key)]
    out.append("")
    out.extend(
        f"{s.path}:{s.line}  {s.span[:60]:<60} refused: {s.why}"
        for s in sorted(refused, key=_skipped_key)[:_SKIPPED_SHOWN]
    )
    if len(refused) > _SKIPPED_SHOWN:
        out.append(f"  … and {len(refused) - _SKIPPED_SHOWN} more refusal(s)")
    return out


def boundaries() -> list[str]:
    """Render what the reader cannot see — printed on every run, clean or not."""
    return [f"   ⚑ CANNOT SEE: {b}" for b in docstring_examples.BOUNDARIES]


def main(argv: list[str]) -> int:
    """Print the census over the named roots, defaulting to the whole corpus."""
    flags = {a for a in argv[1:] if a.startswith("-")}
    roots = [a for a in argv[1:] if not a.startswith("-")]

    found, refused, nfiles = docstring_examples.census(*roots)

    if "--skipped" in flags:
        sys.stdout.write("\n".join(render_skipped(refused)) + "\n")
        sys.stdout.write(
            f"{len(refused)} span(s) refused across "
            f"{len({s.path for s in refused})} file(s); {nfiles} file(s) read\n"
        )
        sys.stdout.write(
            "   ⚑ THESE ARE THE REFUSALS, shown so the discriminator can be AUDITED.\n"
            "     An over-eager rule is invisible in the census and visible only here.\n"
        )
        return 0

    if "--sites" in flags:
        sys.stdout.write("\n".join(render_sites(found)) + "\n")
    else:
        sys.stdout.write("\n".join(render_holders(found)) + "\n")

    sys.stdout.write(
        f"{len(found)} unwitnessed example(s) across "
        f"{len({e.path for e in found})} file(s); {nfiles} file(s) read; "
        f"{len(refused)} span(s) refused\n"
    )
    # ⚑ AN UNWITNESSED EXAMPLE IS NOT AUTOMATICALLY FALSE, and saying so is not hedging. It is a
    # capability claim nothing checks — which is how the wrapper-flag example shipped as a
    # worked case while being the broken one. Whether any given claim is TRUE needs the case to
    # be written, which is the work this census sizes rather than performs.
    sys.stdout.write(
        "   ⚑ AN EXAMPLE HERE IS NOT AUTOMATICALLY WRONG — it is a capability claim with no\n"
        "     witness. The docstring that motivated this reader named two forms; one worked\n"
        "     and one was precisely the broken case, and nothing in the text said which.\n"
        "   ⚑ AND THIS IS AN UPPER BOUND, NOT A DEFECT LIST: an illustrative example reads\n"
        "     exactly like a claim, and nothing structural separates showing from asserting.\n"
    )
    sys.stdout.write("\n".join(boundaries()) + "\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS MODULE, and it DELEGATES rather than
# exiting 0 — a no-op guard reports nothing, which the outcome classifier calls `silent`.
if __name__ == "__main__":
    if "--selftest" in sys.argv:
        from substrate import docstring_examples_selftest

        sys.exit(docstring_examples_selftest.selftest())
    sys.exit(main(sys.argv))
