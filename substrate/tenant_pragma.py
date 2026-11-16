# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The tenant a suite declares, read by mtools' reader with THIS tree's admitted tenants bound.

⚑⚑ WHY THIS EXISTS AFTER `substrate/suite_pragmas` RETIRED (W46). That module was a twin of
`mikemol.corpus.suite_pragmas`; the one difference was that it hardcoded the two admitted tenant
names INSIDE ITS REGEX, where mtools takes them as `admitted=`. Retiring the twin moves that
fact out of a pattern and into a named set, and binds it here once — so every consumer asks the
same question with the same answer, and none types the set again.

⚑ THE AUTHORITY IS `jea.metalanguage.store.TENANT_FLAGS`, NOT THIS TUPLE. It is repeated rather
than imported because `store` is untyped and would carry `Any` into every clean module that reads
a pragma. The repetition is CHECKED, not trusted: `tenant_pragma_selftest` asserts the two agree,
so a third tenant added to the store fails that suite instead of silently reading as undeclared.
"""

from __future__ import annotations

from mikemol.corpus import suite_pragmas

# The tenants a suite may declare, without the `--`. Mirrors `store.TENANT_FLAGS`.
ADMITTED: tuple[str, ...] = ("sandbox", "live")


def tenant(path: str) -> str | None:
    """Return the tenant FLAG a suite declares (`--sandbox` / `--live`), or None."""
    return suite_pragmas.tenant(path, admitted=ADMITTED)
