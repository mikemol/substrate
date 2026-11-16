#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""A module that REFUSES AT IMPORT — the fixture for `gate_module`'s `BaseException` catch.

⚑⚑⚑ THIS EXISTS BECAUSE THE BEHAVIOUR IT PINS LOOKS LIKE A BUG. `gate_module` catches
`BaseException`, which is normally wrong; the justification is that several real gates in this
tree refuse at IMPORT time by exiting — an unstated tenant, an unknown flag — and `SystemExit`
does not derive from `Exception`. Catching only `Exception` would let a gate's own refusal kill
the census trying to report it.

⚑⚑ AND THE FIXTURE IS A REAL MODULE IN THE PACKAGE, NOT A TEMPFILE ON `sys.path`. Writing one
at test time would need a path insert, which is exactly the mechanism this repo forbids
(operator: *"NOO. No sys.path modification."*). A committed fixture is importable by its real
name, so the case exercises the same code path a live gate takes.

⚑ IT IS NOT A SUITE. `suite_discovery` keys on an entry point plus selftest evidence, and this
file has neither — it is data for another suite, and must never be run as one.
"""

from __future__ import annotations

import sys

# ⚑ THE EXIT IS AT MODULE SCOPE, which is the whole point: it fires during IMPORT, before any
# caller can guard it with anything but an exception handler around the import itself.
sys.exit(2)
