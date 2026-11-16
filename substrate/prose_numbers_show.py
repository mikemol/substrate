#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Print the measured-numbers census — the CLI over `substrate.prose_numbers`.

⚑ THE CLI IS ITS OWN MODULE BECAUSE THE READER SHOULD NOT PRINT, the split the rest of this
toolkit uses: `prose_numbers` returns data, this decides how to render it.

    prose_numbers_show.py [ROOTS...]            # the holders, largest first
    prose_numbers_show.py --sites [ROOTS...]    # every finding with its location
    prose_numbers_show.py --exempt [ROOTS...]   # what the discriminator REFUSED, and why

⚑⚑ THE BOUNDARIES PRINT WITH EVERY RUN, INCLUDING A CLEAN ONE. A zero from this reader is a
fact about the DISCRIMINATOR — what it can match — and a reader who does not know its blind
spots reads a small number as a clean tree. That is the false-zero shape this repo keeps
catching, so the instrument states its own reach rather than leaving it to be inferred.

⚑ `--exempt` EXISTS SO THE REFUSALS ARE AUDITABLE. An over-eager exemption is invisible in the
census by construction: it makes the tree look clean. The only way to check a discriminator is
to read what it decided NOT to say, which means the refusals need a mode of their own.
"""

from __future__ import annotations

import sys

from substrate import prose_numbers

#: How many holders to name before the tail is summarised.
_TOP = 25

#: How many refusals `--exempt` prints before it stops.
_EXEMPT_SHOWN = 60


def render_holders(findings: list[prose_numbers.Finding]) -> list[str]:
    """Render the per-file counts, largest holder first."""
    rows = prose_numbers.by_holder(findings)
    out = [f"  {n:>6}  {path}" for path, n in rows[:_TOP]]
    if len(rows) > _TOP:
        out.append(f"  … and {len(rows) - _TOP} more file(s)")
    return out


def _site_key(f: prose_numbers.Finding) -> tuple[str, int, str]:
    """Order findings by file, then line, then the number — canonical across runs."""
    return (f.path, f.line, f.number)


def _exempt_key(e: prose_numbers.Exempt) -> tuple[str, int]:
    """Order refusals by file, then line."""
    return (e.path, e.line)


def _share_key(kv: tuple[str, int]) -> int:
    """Order the per-rule tally by descending share, so the widest rule reads first."""
    return -kv[1]


def render_sites(findings: list[prose_numbers.Finding]) -> list[str]:
    """Render every finding with its location, signal and the line it sits on."""
    out = []
    for f in sorted(findings, key=_site_key):
        out.append(f"{f.path}:{f.line}  [{f.signal}:{f.unit}]  {f.number}")
        out.append(f"      {f.text[:160]}")
    return out


def render_exempt(refused: list[prose_numbers.Exempt]) -> list[str]:
    """Render the refusals, grouped so an over-eager rule is visible by its share.

    ⚑ THE PER-RULE TALLY IS THE AUDIT, and the sites below it are the evidence. A rule whose
    share is far larger than the others is the one to read first — that is what an over-broad
    exemption looks like from outside, and it is invisible in the census by construction.
    """
    by_rule: dict[str, int] = {}
    for e in refused:
        by_rule[e.why] = by_rule.get(e.why, 0) + 1
    out = [f"  {n:>6}  {why}" for why, n in sorted(by_rule.items(), key=_share_key)]
    out.append("")
    for e in sorted(refused, key=_exempt_key)[:_EXEMPT_SHOWN]:
        out.append(f"{e.path}:{e.line}  {e.number:<10} refused: {e.why}")
        out.append(f"      {e.text[:160]}")
    if len(refused) > _EXEMPT_SHOWN:
        out.append(f"  … and {len(refused) - _EXEMPT_SHOWN} more refusal(s)")
    return out


def boundaries() -> list[str]:
    """Render what the reader cannot see — printed on every run, clean or not."""
    return [f"   ⚑ CANNOT SEE: {b}" for b in prose_numbers.BOUNDARIES]


def main(argv: list[str]) -> int:
    """Print the census over the named roots, defaulting to the whole corpus."""
    flags = {a for a in argv[1:] if a.startswith("-")}
    roots = [a for a in argv[1:] if not a.startswith("-")]

    findings, refused, nfiles = prose_numbers.census(*roots)

    if "--exempt" in flags:
        sys.stdout.write("\n".join(render_exempt(refused)) + "\n")
        sys.stdout.write(
            f"{len(refused)} number(s) exempt across "
            f"{len({e.path for e in refused})} file(s); {nfiles} file(s) read\n"
        )
        sys.stdout.write(
            "   ⚑ THESE ARE THE REFUSALS, shown so the discriminator can be AUDITED.\n"
            "     An over-eager exemption is invisible in the census and visible only here.\n"
        )
        return 0

    if "--sites" in flags:
        sys.stdout.write("\n".join(render_sites(findings)) + "\n")
    else:
        sys.stdout.write("\n".join(render_holders(findings)) + "\n")

    sys.stdout.write(
        f"{len(findings)} measured number(s) in prose across "
        f"{len({f.path for f in findings})} file(s); {nfiles} file(s) read; "
        f"{len(refused)} number(s) exempt\n"
    )
    # ⚑ A FLAGGED NUMBER IS NOT AUTOMATICALLY WRONG, and saying so is not hedging. A count in
    # prose is either already false or a falsehood waiting, and NOTHING HERE SEPARATES THOSE —
    # only re-running the tool that owns the figure can. Reporting the population as if it were
    # a defect list would invite a sweep that "fixes" numbers by retyping today's value, which
    # rebuilds the condition one edit later.
    sys.stdout.write(
        "   ⚑ A COUNT HERE IS NOT AUTOMATICALLY WRONG — it is a measurement written into a\n"
        "     medium nothing re-derives, so it is either already false or a falsehood\n"
        "     waiting. This reader cannot tell those apart; only re-running the owning\n"
        "     tool can. ⚑ AND RETYPING TODAY'S VALUE IS NOT A REPAIR — it rebuilds the\n"
        "     condition. The repair is to CITE the tool, never to quote a fresher number.\n"
    )
    sys.stdout.write("\n".join(boundaries()) + "\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS MODULE, and it DELEGATES rather than
# exiting 0 — a no-op guard reports nothing, which the outcome classifier calls `silent`.
if __name__ == "__main__":
    if "--selftest" in sys.argv:
        from substrate import prose_numbers_selftest

        sys.exit(prose_numbers_selftest.selftest())
    sys.exit(main(sys.argv))
