# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Whether an extraction is COMPLETE — the drain's actual unit of work, checked.

⚑⚑⚑ DRAINING IS NOT EDITING A MONOLITH, IT IS MIGRATING CODE OUT OF ONE. Operator: *"Draining
is not editing in place, it is migrating code OUT, making it clean wherever it's been migrated
to, and then repointing consumers at the new code."* The origin's findings are never fixed —
they LEAVE with the code, and the husk shrinks until it can be deleted. That reframing matters
because the arithmetic differs by orders of magnitude: paying down the head blocker in place is
twelve thousand findings, while extracting one capability from it is a new clean module plus a
repoint.

⚑⚑ AND A HALF-DONE EXTRACTION IS WORSE THAN NONE, WHICH IS WHY THIS EXISTS AS A CHECK. Code
copied out but not repointed leaves TWO implementations of one capability — the shape this repo
retires everywhere else, arrived at by the very act meant to remove debt. Measured in this
session: a private finder was duplicated into `scratch_module` and `sibling_finder` and sat that
way until someone noticed. The check is therefore not "does the new module exist" but "does the
OLD one still define it".

⚑ THE THREE CONDITIONS ARE INDEPENDENT AND ALL THREE ARE NECESSARY. The new home must exist and
be CLEAN (an extraction into a dirty file moves debt rather than draining it); the origin must
no longer define the capability (or it is a copy); and the consumers must reach the new home (or
the extraction is unreachable and the old path is still live). Any two without the third is a
recognisable failure mode rather than partial progress.

⚑ THIS CHECKS AN EXTRACTION, IT DOES NOT PERFORM ONE. What to extract is a judgement about
coherence — which names belong together — and no reader can make it. What CAN be checked is
whether the act finished.
"""

from __future__ import annotations

from dataclasses import dataclass

from substrate import editable


@dataclass(frozen=True, slots=True)
class Extraction:
    """One capability moved out of a monolith, and whether the move finished."""

    name: str
    origin: str
    home: str
    home_clean: bool
    origin_still_defines: bool
    consumers_repointed: tuple[str, ...] = ()
    consumers_stale: tuple[str, ...] = ()

    @property
    def complete(self) -> bool:
        """Whether every condition of a finished extraction holds.

        ⚑ ALL THREE, NOT A MAJORITY. A clean new home whose origin still defines the same
        capability is a DUPLICATE; a repointed consumer set with a dirty home has moved debt
        rather than drained it. Neither is partial progress toward the third.
        """
        return self.home_clean and not self.origin_still_defines and not self.consumers_stale

    @property
    def failure(self) -> str:
        """Name the condition that fails first, or empty when the extraction is complete.

        ⚑ ONE NAMED FAILURE BEATS THREE BOOLEANS, because the three have different repairs:
        a dirty home is more extraction, a defining origin is a deletion, a stale consumer is
        a repoint. A caller shown a triple has to decide which matters; this says.
        """
        if not self.home_clean:
            return f"the new home {self.home} is not clean — debt moved, not drained"
        if self.origin_still_defines:
            return (
                f"{self.origin} still defines {self.name} — this is a COPY, "
                f"and two implementations of one capability is the shape being retired"
            )
        if self.consumers_stale:
            return (
                f"{len(self.consumers_stale)} consumer(s) still reach the origin — "
                f"the new home is unreachable and the old path is live"
            )
        return ""


def defines(source: str, name: str) -> bool:
    """Report whether `source` still defines `name` at top level.

    ⚑ A DEFINITION, NOT A MENTION. The origin will keep MENTIONING the extracted name — in a
    comment recording where it went, or in an import of the new home — and reading a mention
    as a definition would report every correctly-finished extraction as incomplete.

    ⚑⚑ AND TOP-LEVEL MEANS COLUMN ZERO, WHICH A FAILING CASE ESTABLISHED. A first cut matched
    on the `lstrip`ed line, so an INDENTED `def helper` — a method on a class the origin still
    legitimately owns — read as a top-level definition and reported a finished extraction as
    incomplete. The check must ask WHERE the definition sits, not merely that one exists.
    """
    for line in source.splitlines():
        if line.startswith((f"def {name}(", f"class {name}(", f"class {name}:", f"{name} = ")):
            return True
    return False


def check(name: str, origin: str, home: str, consumers: dict[str, str]) -> Extraction:
    """Return whether the extraction of `name` from `origin` into `home` finished.

    `consumers` maps a consumer path to its source text.

    ⚑ A CONSUMER IS REPOINTED WHEN IT NAMES THE NEW HOME'S MODULE. That is a weaker test than
    resolving its imports, and deliberately: a consumer may reach the home through a facade or
    a re-export, and demanding a direct import would report a working repoint as stale.
    """
    from pathlib import Path  # noqa: PLC0415 — one function's need, not the module's

    from substrate import corpus  # noqa: PLC0415

    origin_text = Path(corpus.ROOT / origin).read_text(encoding="utf-8", errors="replace")
    home_module = home.removesuffix(".py").replace("/", ".").removeprefix("substrate.")

    repointed: list[str] = []
    stale: list[str] = []
    for path, text in sorted(consumers.items()):
        if home_module in text:
            repointed.append(path)
        elif defines(text, name) or name in text:
            stale.append(path)

    return Extraction(
        name=name,
        origin=origin,
        home=home,
        home_clean=editable.verdict_for(home).is_editable,
        origin_still_defines=defines(origin_text, name),
        consumers_repointed=tuple(repointed),
        consumers_stale=tuple(stale),
    )


def render(found: Extraction) -> str:
    """Render one extraction's verdict."""
    verdict = "COMPLETE" if found.complete else "INCOMPLETE"
    out = [
        f"{found.name}: {found.origin} -> {found.home}  [{verdict}]",
        f"  new home clean:          {found.home_clean}",
        f"  origin still defines it: {found.origin_still_defines}",
        f"  consumers repointed:     {len(found.consumers_repointed)}",
        f"  consumers stale:         {len(found.consumers_stale)}",
    ]
    if not found.complete:
        out.append(f"  ⚑ {found.failure}")
    return "\n".join(out) + "\n"
