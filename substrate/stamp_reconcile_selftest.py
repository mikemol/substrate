# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.stamp_reconcile` — the ported truths, then the TENANT separation.

⚑⚑⚑ THE TENANT CASES ARE THE REASON THIS MODULE EXISTS. The origin's helpers match `.ingested`
alone, so a sandbox pass judged LIVE stamps against the SANDBOX store and deleted them. The
mixed-population cases put both tenants' stamps in ONE tree and assert that a pass for either
tenant leaves the other's stamps present — in both directions, because a guard checked in one
direction is half a guard.

⚑ THE PORTED CASES MIRROR `sppf_decode.reconcile_stamp_cases` (ingested 4, promoted 3, drained
the four corners of its conjunction), run for the live tenant so they state the origin's
behaviour, and for the sandbox tenant so the port carries it across the suffix unchanged.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import stamp_reconcile as sr

_ALIVE_ID = "id-staged"


def _touch(path: Path) -> None:
    """Create an empty file, and its parent directory."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("", encoding="utf-8")


def _staged(cid: str) -> bool:
    """Stand in for the `obs` probe: one id still has staged rows."""
    return cid == _ALIVE_ID


def _ingested_cases(root: Path, tenant: str) -> list[tuple[str, bool]]:
    """Return the four `.ingested` verdicts, for one tenant."""
    sfx = sr.stamp_suffix("ingested", tenant)
    for name in ("Fresh", "NoRow", "Stale"):
        _touch(root / f"{name}.agdai")
        _touch(root / f"{name}{sfx}")
    _touch(root / f"Orphan{sfx}")
    now = (root / "Fresh.agdai").stat().st_mtime_ns
    backed = {"Fresh.agdai": now, "Stale.agdai": now - 1, "Orphan.agdai": now}
    kept, dropped = sr.ingested(backed, sr.Walk(root, root, tenant))
    return [
        (f"[{tenant}] .ingested kept at the current mtime", (root / f"Fresh{sfx}").exists()),
        (f"[{tenant}] .ingested dropped with no core_fp row", "NoRow.agdai" in dropped),
        (f"[{tenant}] .ingested dropped at a stale mtime", "Stale.agdai" in dropped),
        (f"[{tenant}] .ingested dropped when the core is gone", "Orphan.agdai" in dropped),
        (f"[{tenant}] the ingested pass counts one kept", kept == 1),
    ]


def _promotion_cases(root: Path, tenant: str) -> list[tuple[str, bool]]:
    """Return the three `.promoted` verdicts and the four `.drained` corners, for one tenant."""
    psfx = sr.stamp_suffix("promoted", tenant)
    dsfx = sr.stamp_suffix("drained", tenant)
    for name in ("Held", "Dropped", "NoId"):
        _touch(root / f"{name}{psfx}")
    for name in ("Done", "Staged", "Unpromoted", "Unknown"):
        _touch(root / f"{name}{dsfx}")
    promo = sr.Promotion(
        promoted_ids=frozenset({"id-held", "id-done", _ALIVE_ID}),
        ids_by_rel={
            "Held.agdai": "id-held",
            "Dropped.agdai": "id-gone",
            "Done.agdai": "id-done",
            "Staged.agdai": _ALIVE_ID,
            "Unpromoted.agdai": "id-gone",
        },
    )
    walk = sr.Walk(root, root, tenant)
    _, pdrop = sr.promoted(promo, walk)
    _, ddrop = sr.drained(promo, walk, _staged)
    return [
        (f"[{tenant}] .promoted kept when obs_node holds it", (root / f"Held{psfx}").exists()),
        (f"[{tenant}] .promoted dropped when obs_node lost it", "Dropped.agdai" in pdrop),
        (f"[{tenant}] .promoted dropped for a never-ingested core", "NoId.agdai" in pdrop),
        (f"[{tenant}] .drained kept: promoted, nothing staged", (root / f"Done{dsfx}").exists()),
        (f"[{tenant}] .drained dropped: rows still staged", "Staged.agdai" in ddrop),
        (f"[{tenant}] .drained dropped: not promoted", "Unpromoted.agdai" in ddrop),
        (f"[{tenant}] .drained dropped: no id at all", "Unknown.agdai" in ddrop),
    ]


def _separation_cases(root: Path) -> list[tuple[str, bool]]:
    """Put both tenants' stamps in ONE tree; a pass for either must leave the other's alone.

    ⚑ THE STORE ANSWER IS EMPTY, which is the harshest input: it would drop EVERY stamp the pass
    can see. So any stamp that survives survived because the pass could not see it.
    """
    stamps = {t: [root / f"M{sr.stamp_suffix(k, t)}" for k in sr.KINDS] for t in sr.TENANTS}
    empty = sr.Promotion(promoted_ids=frozenset(), ids_by_rel={})
    out: list[tuple[str, bool]] = []
    for tenant, other in (("sandbox", "live"), ("live", "sandbox")):
        # ⚑ BOTH tenants' stamps are (re)created before EACH pass: a pass deletes its own, so a
        # setup that restored only one side would test the second pass against a tree already
        # missing the stamps it must not touch — which is how this case first failed.
        for paths in stamps.values():
            for p in paths:
                _touch(p)
        walk = sr.Walk(root, root, tenant)
        sr.ingested({}, walk)
        sr.promoted(empty, walk)
        sr.drained(empty, walk, _staged)
        out.append(
            (
                f"a {tenant} pass leaves every {other} stamp in place",
                all(p.exists() for p in stamps[other]),
            )
        )
        out.append(
            (
                f"and it DOES drop its own {tenant} stamps (the pass ran)",
                not any(p.exists() for p in stamps[tenant]),
            )
        )
    return out


def _suffix_cases() -> list[tuple[str, bool]]:
    """Return the cases on the suffix rule itself."""
    refused = False
    try:
        sr.stamp_suffix("ingested", "bogus")
    except sr.UnknownTenantError:
        refused = True
    live = sr.stamp_suffix("drained", "live")
    return [
        ("live keeps the unsuffixed name", sr.stamp_suffix("ingested", "live") == ".ingested"),
        (
            "sandbox appends the tenant",
            sr.stamp_suffix("promoted", "sandbox") == ".promoted.sandbox",
        ),
        ("an unknown tenant is refused, not turned into a namespace", refused),
        # ⚑ THE MAKEFILE AND THE RECONCILER SPELL ONE RULE: flat_emit's TSFX is `.$(TENANT)`
        # off-live and empty on live, which is exactly this function.
        (
            "the suffix rule matches flat_emit's TSFX shape",
            sr.stamp_suffix("drained", "sandbox") == live + ".sandbox" and live == ".drained",
        ),
    ]


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []
    with tempfile.TemporaryDirectory() as where:
        base = Path(where)
        for tenant in sr.TENANTS:
            (base / tenant / "i").mkdir(parents=True)
            (base / tenant / "p").mkdir(parents=True)
            out.extend(_ingested_cases(base / tenant / "i", tenant))
            out.extend(_promotion_cases(base / tenant / "p", tenant))
        (base / "mixed").mkdir()
        out.extend(_separation_cases(base / "mixed"))
    out.extend(_suffix_cases())
    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"stamp-reconcile selftest: {ok}/{len(cases)}\n")
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(0 if ("--selftest" in sys.argv or len(sys.argv) == 1) and selftest() else 1)
