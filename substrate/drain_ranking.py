# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Rank the dirty files blocking the `sys.path` drain, by what cleaning each one releases.

⚑⚑⚑ CLEANLINESS IS THE ONLY LEVER LEFT, AND THAT WAS MEASURED RATHER THAN ASSUMED. Crossing
scope with editability left three of 492 sites reachable; the other 325 mechanical sites sit
behind 257 files the per-file gate refuses to edit. So no packaging decision moves this drain —
the files must become editable first, and the question is which file to clean.

⚑⚑ THE WEIGHT IS SITES RELEASED, NOT FINDINGS CARRIED. Ranking by finding count would put the
biggest monoliths first, which is the work least likely to finish; ranking by what a file
RELEASES puts the reader in front of the file whose paydown converts directly into drained
sites. A file with three hundred findings and one site is worth less than a clean-ish file with
four sites, and only the release count says so.

⚑ AND THE COST IS CARRIED BESIDE THE WEIGHT, NEVER FOLDED INTO IT. A single score mixing
release and effort would need a weighting nobody can justify, and would hide which half moved
when the ranking changed. Both numbers are reported; the operator does the trade.

⚑ THIS RANKS, IT DOES NOT SCHEDULE. A file's findings may be one import away from clean or may
be a decomposition; nothing here can tell, and a ranking that implied otherwise would be a plan
resting on a count. `drain_blockers` is the sibling shape for a different unit — that one ranks
what a paydown unblocks for OTHER files' drains, this one for the file's OWN sites.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from substrate import editable


@dataclass(frozen=True, slots=True)
class Blocked:
    """One dirty file, the sites it holds, and what its paydown would cost."""

    path: str
    sites: int
    findings: int

    @property
    def release_per_finding(self) -> float:
        """Sites released per finding paid down — the trade, stated as a ratio.

        ⚑ REPORTED, NEVER SORTED ON. A ratio makes two incomparable quantities look
        comparable, and a file with one finding and one site would outrank a file with ten
        findings and eight sites on it. It is here because an operator comparing two
        similarly-ranked rows wants it, not because the ordering uses it.
        """
        return self.sites / self.findings if self.findings else float(self.sites)


def _weight(blocked: Blocked) -> tuple[int, int, str]:
    """Return the sort key: most sites first, then cheapest, then path.

    ⚑ TIES BREAK ON FEWER FINDINGS, THEN ON PATH. Two files releasing the same number of
    sites are not equally good targets — the cheaper one is — and a path tiebreak after that
    keeps the ranking stable across runs, so a diff of two reports shows real movement.
    """
    return (-blocked.sites, blocked.findings, blocked.path)


def rank(sites_by_file: dict[str, int], verdicts: dict[str, editable.Verdict]) -> list[Blocked]:
    """Return the blocked files, most sites released first.

    ⚑⚑ A FILE WITH NO VERDICT IS OMITTED, NOT DEFAULTED. Assuming it clean would place an
    unmeasured file at the head of a work queue; assuming it dirty would invent a finding
    count. The caller measured what it measured, and the ranking covers exactly that.
    """
    out = [
        Blocked(path, n, verdicts[path].findings)
        for path, n in sites_by_file.items()
        if path in verdicts and not verdicts[path].is_editable
    ]
    return sorted(out, key=_weight)


def released_by(blocked: list[Blocked], limit: int) -> int:
    """Return how many sites cleaning the top `limit` files would release."""
    return sum(b.sites for b in blocked[:limit])


def render(blocked: list[Blocked], show: int = 20) -> str:
    """Render the ranking, most-released first."""
    total = sum(b.sites for b in blocked)
    out = [f"{len(blocked)} dirty file(s) hold {total} mechanical site(s)", ""]
    out.append(f"  {'sites':>5}  {'findings':>8}  file")
    out.extend(f"  {b.sites:>5}  {b.findings:>8}  {b.path}" for b in blocked[:show])
    if len(blocked) > show:
        out.append(f"  … {len(blocked) - show} more")
    # ⚑ THE HEAD'S SHARE IS THE PLANNING NUMBER. A long tail of one-site files means the
    # ranking cannot concentrate the work, and an operator should know that before starting.
    out.append("")
    for cut in (1, 5, 10, 25):
        if cut <= len(blocked):
            got = released_by(blocked, cut)
            share = got * 100 // total if total else 0
            out.append(f"   top {cut:>3}: {got:>4} site(s) ({share}%)")
    return "\n".join(out) + "\n"
