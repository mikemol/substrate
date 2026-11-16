# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Types for the one `paperkit.bib` entry point this repo calls.

⚑ THE ENGINE SHIPS NO `py.typed`, SO ITS RETURN IS `Any` AT EVERY CALL SITE. A stub types the
import independently of the distribution — the mechanism this repo already uses for the reachable
authority — and `scripts/check_stub_authority.py` runs `stubtest` against it, so a signature that
drifts from the real module fails a gate rather than rotting quietly.

⚑ ONLY WHAT IS CALLED IS DECLARED. A stub mirroring the whole module would be a second copy of
someone else's interface, drifting on every one of their edits; this one covers `parse`, which is
the only name `substrate.warrant_bib` reaches for.

⚑⚑⚑ AND THAT PARTIALITY WAS ARGUED IN PROSE FOR MONTHS WITHOUT BEING DECLARED, SO IT WAS NEVER
GRANTED. The paragraph above states the policy exactly; the `⟡declines:` marker below is what
`check_stub_authority` actually READS. Until 2026-09-02 the gap did not show, because
`paperkit.bib` imports `bibparse`, that package is absent from this machine, and the gate
correctly classified the unit as ABSENT-DEP — a passing state. The stub was passing on the
IMPORT FAILURE, not on its own correctness, and the moment the import resolved it reported
`dep_order` and `emit_anchors` as drift.

⚑⚑ WHICH IS `census-green-is-a-fact-about-the-census` IN THE STUB GATE'S OWN POPULATION. A
declaration written as prose is a declaration nothing enforces and nothing grants; the
distinction between "this stub declines a surface" and "this stub could not be checked" was
invisible while both printed as pass. Both findings here are pure ABSENCE — names the stub never
claimed — which is precisely and only what `--ignore-missing-stub` can silence, so the marker
cannot hide a contradiction it later acquires.

⟡declines: every `paperkit.bib` name beyond `parse` and the `_LIST` field roster — the engine's
own helpers (`dep_order`, `emit_anchors` and their siblings), which this repo does not call. A
stub mirroring the whole module would be a second copy of someone else's interface.
"""

from pathlib import Path

# ⚑⚑⚑ THE EDGE/TOKEN FIELD ROSTER, DECLARED BECAUSE A CONSUMER MUST READ IT RATHER THAN RESTATE
# IT. `_LIST` is the engine's authority on which fields parse as LISTS of keys; every other field
# is a scalar carried verbatim. A reader that hardcodes the roster reports a newly-accepted field
# as engine-dropped — a false finding pointing at correct work.
#
# ⚑⚑ MEASURED: the engine's own MODULE DOCSTRING names three (`from`, `rests-on`, `reads`) and the
# constant carries FOUR — `consumes` was added and the prose did not follow. **The prose about an
# authority is not the authority.** Declaring it here makes the read TYPED, so a consumer gets a
# `tuple[str, ...]` instead of the `Any` a `getattr` on an untyped module yields.
#
# ⚑ UNDERSCORE-PREFIXED AND DECLARED ANYWAY. A private name is not part of a promised interface,
# and `stubtest` will refuse this stub the moment the engine renames or removes it — which is the
# point: this repo depends on the name, so the dependency should be the thing that breaks loudly
# rather than a census that quietly reports zero.
_LIST: tuple[str, ...]

def parse(
    path: Path, consumer_fields: tuple[str, ...] = ...
) -> dict[str, dict[str, str]]: ...
