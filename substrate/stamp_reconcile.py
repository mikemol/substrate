# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Delete every build stamp the STORE does not back — per tenant (⟡promote-path A, ⒯).

⚑⚑⚑ WHY THIS IS A NEW MODULE. `scripts/sppf_decode.reconcile_stamps` already switches tenant for
the STORE read (`sandbox_connect` vs `connect`), but its three helpers hard-code the LIVE stamp
names: `endswith(".ingested")`, then `sp[:-len(".ingested")]` to find the core. Sandbox stamps
are `X.ingested.sandbox` (`flat_emit` TSFX), so a sandbox pass skips every sandbox stamp and
judges every LIVE stamp against the SANDBOX store — deleting nearly all of them (measured t107;
confirmed by a read-only audit t108). `sppf_decode.py` carries 366 ruff findings and the per-file
gate refuses any edit, so the fix is this clean module, which `Flat.mk`'s `reconcile` calls
directly — `sppf_decode` and `sppf_db` are not touched.

⚑⚑ THE SUFFIX HAS ONE OWNER. `stamp_suffix(kind, tenant)` is the only spelling of a stamp name;
`flat_emit`'s TSFX (empty for live, `.<tenant>` otherwise) states the same rule in make syntax,
and a case pins the two together so the makefile and the reconciler cannot drift apart.

⚑ THE THREE TRUTH CONDITIONS ARE PORTED UNCHANGED from `sppf_decode` (`_reconcile_over`,
`_reconcile_promoted_over`, `_reconcile_drained_over`), where their rationale lives:
    .ingested   `core_fp` holds this core AT THE CORE'S CURRENT MTIME
    .promoted   `obs_node` holds rows for this core
    .drained    `obs_node` holds rows  ∧  `obs` holds NONE
Only WHICH FILES are walked changes; what makes a stamp true does not.

⚑ TWO NAMED VALUES, BECAUSE THE GATE'S ARITY LIMIT FOUND THEM. The first draft passed six
arguments; underneath, `stampdir`/`base`/`tenant` are one thing (WHICH stamps, `Walk`) and
`promoted_ids`/`ids_by_rel` are another (WHAT the store said, `Promotion`). This half is
STORE-FREE: every judgement takes the store's answer as a value, so cases drive it on a temp
directory.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

#: The per-module stamp kinds a tenant owns.
KINDS = ("ingested", "promoted", "drained")
#: The tenants the build chain accepts; `live` keeps the unsuffixed names.
TENANTS = ("live", "sandbox")
CORE = ".agdai"


class UnknownTenantError(ValueError):
    """A tenant outside `TENANTS` — refused rather than turned into a new stamp namespace."""


def stamp_suffix(kind: str, tenant: str) -> str:
    """Return the stamp suffix for `kind` under `tenant`: `.ingested` live, `.ingested.sandbox`."""
    if tenant not in TENANTS:
        msg = f"unknown tenant {tenant!r}; expected one of {TENANTS}"
        raise UnknownTenantError(msg)
    return f".{kind}" if tenant == "live" else f".{kind}.{tenant}"


@dataclass(frozen=True, slots=True)
class Walk:
    """WHICH stamps a pass judges: the tree, the base core paths are relative to, the tenant."""

    stampdir: Path
    base: Path
    tenant: str
    #: False judges without deleting — the CLI's dry run. The verdict is identical either way;
    #: only whether a false stamp is unlinked differs, so a dry run reports what --apply does.
    apply: bool = True

    def drop(self, stamp: Path) -> None:
        """Delete a stamp the store does not back — unless this is a dry run."""
        if self.apply:
            stamp.unlink()

    def stamps(self, kind: str) -> Iterator[tuple[Path, str]]:
        """Yield `(stamp, core_relpath)` for every file ending EXACTLY in this tenant's suffix.

        ⚑ `endswith` IS EXACT, WHICH IS WHAT SEPARATES THE TENANTS: `X.ingested.sandbox` does not
        end in `.ingested`, and `X.ingested` does not end in `.ingested.sandbox`, so a pass for
        one tenant never sees the other's stamps. A case pins both directions.
        """
        suffix = stamp_suffix(kind, self.tenant)
        for dirpath, _, names in os.walk(self.stampdir):
            for name in sorted(names):
                if name.endswith(suffix):
                    stamp = Path(dirpath) / name
                    core = str(stamp)[: -len(suffix)] + CORE
                    yield stamp, os.path.relpath(core, self.base)


@dataclass(frozen=True, slots=True)
class Promotion:
    """WHAT the store said about promotion: which core ids `obs_node` holds, and each path's id."""

    promoted_ids: frozenset[str]
    ids_by_rel: dict[str, str]

    def holds(self, rel: str) -> bool:
        """Report whether `obs_node` holds rows for the core at `rel`."""
        return self.ids_by_rel.get(rel) in self.promoted_ids


def ingested(backed: dict[str, int], walk: Walk) -> tuple[int, list[str]]:
    """Keep a `.ingested` stamp iff `core_fp` holds its core at the core's current mtime."""
    kept, dropped = 0, list[str]()
    for stamp, rel in walk.stamps("ingested"):
        try:
            now: int | None = (walk.base / rel).stat().st_mtime_ns
        except OSError:
            now = None
        if now is not None and backed.get(rel) == now:
            kept += 1
        else:
            walk.drop(stamp)
            dropped.append(rel)
    return kept, dropped


def promoted(promotion: Promotion, walk: Walk) -> tuple[int, list[str]]:
    """Keep a `.promoted` stamp iff `obs_node` holds rows for its core."""
    kept, dropped = 0, list[str]()
    for stamp, rel in walk.stamps("promoted"):
        if promotion.holds(rel):
            kept += 1
        else:
            walk.drop(stamp)
            dropped.append(rel)
    return kept, dropped


def drained(
    promotion: Promotion, walk: Walk, still_staged: Callable[[str], bool]
) -> tuple[int, list[str]]:
    """Keep a `.drained` stamp iff `obs_node` holds rows for its core AND `obs` holds none."""
    kept, dropped = 0, list[str]()
    for stamp, rel in walk.stamps("drained"):
        cid = promotion.ids_by_rel.get(rel)
        if cid is not None and cid in promotion.promoted_ids and not still_staged(cid):
            kept += 1
        else:
            walk.drop(stamp)
            dropped.append(rel)
    return kept, dropped
