#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Discover which files ARE selftest suites: a thin shim over the two modules that hold the work.

⚑ DRAINED 2026-10-10 (W336). The predicate lives in `substrate.suite_flag` (an entry point plus
CODE that names `--selftest`, never prose) and the walk in `substrate.suite_walk` (git's ignore
is the one authority for which directories to enter). This module keeps the names its callers
import, so `run_selftests` and the selftest are unchanged.
"""

from __future__ import annotations

from substrate.suite_flag import FLAG, HAS_BODY, HAS_ENTRY, is_suite
from substrate.suite_walk import SKIP_DIRS, discover, roots

__all__ = ["FLAG", "HAS_BODY", "HAS_ENTRY", "SKIP_DIRS", "discover", "is_suite", "roots"]
