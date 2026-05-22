#!/usr/bin/env python3
"""
agda_types.py — cache elaborated type signatures for every definition
in the Substrate corpus.

Approach: write a wrapper .agda module that `open import`s every
Substrate.* module publicly, then feed `agda --interaction-json` a
batch of IOTCM commands (Cmd_load + Cmd_show_module_contents_toplevel
× {AsIs, Normalised} for each module) on stdin and parse the JSON
replies in order.

Result is written to scratch/.agda_types.json as

  { "<Module.Name>::<def-name>": {
      "module":     "<Module.Name>",
      "asis":       "...",
      "normalised": "..."
    },
    ...
  }

Cache is rebuilt whenever any .agda file is newer than the JSON, or
when --force is passed.

Why two levels:

  findings.py's parametric-helper detector scores candidates by a
  dot-product of multiple similarity dimensions. AsIs preserves the
  orbit's structural identity (Stab-C ≠ Stab-D, distinct tokens);
  Normalised catches definitional equalities (two defs that are
  definitionally equal share all normalised tokens). Intermediate
  Rewrite modes (Instantiated, HeadNormal, Simplified) collapse to
  AsIs in practice because the codebase uses synonyms, not metavars.
"""

import json
import re
import subprocess
import sys
import time
from pathlib import Path


SUBSTRATE_AGDA_ROOT = Path("/home/mikemol/github/substrate/agda")
SUBSTRATE_ROOT = SUBSTRATE_AGDA_ROOT / "Substrate"
CACHE_PATH = Path("/home/mikemol/github/substrate/scratch/.agda_types.json")
WRAPPER_PATH = Path("/tmp/AgdaQueryAll.agda")


def discover_modules():
    """Return sorted list of (module_name, file_path) for every Substrate.* module."""
    modules = []
    for path in sorted(SUBSTRATE_ROOT.rglob("*.agda")):
        rel = path.relative_to(SUBSTRATE_AGDA_ROOT)
        mod = ".".join(rel.with_suffix("").parts)
        modules.append((mod, path))
    return modules


def write_wrapper(modules):
    """Write a wrapper module that plain-imports every Substrate module.

    Plain `import M` (not `open import M public`) loads each module —
    type-checking it transitively — without bringing its names into
    the wrapper's top-level scope. This is critical because several
    Substrate modules define the same name (e.g. `Fiber` appears in
    multiple cocycle files); a public open would trigger
    "Multiple definitions" errors. Cmd_show_module_contents_toplevel
    still works on the fully-qualified module names.
    """
    lines = ["{-# OPTIONS --safe --without-K #-}", "module AgdaQueryAll where", ""]
    for mod, _ in modules:
        lines.append(f"import {mod}")
    WRAPPER_PATH.write_text("\n".join(lines) + "\n")


def cache_is_stale(modules):
    if not CACHE_PATH.exists():
        return True
    cache_mtime = CACHE_PATH.stat().st_mtime
    for _, p in modules:
        if p.stat().st_mtime > cache_mtime:
            return True
    return False


def clean_term(term):
    """Strip whitespace/newlines for compact storage."""
    return re.sub(r"\s+", " ", term).strip()


def parse_module_contents_in_order(output):
    """
    Parse agda's JSON-per-line stdout. Returns the list of
    `ModuleContents` payloads (each a list of {name, term} dicts)
    IN THE ORDER they appear in the output.

    Other JSON kinds (Status, ClearHighlighting, AllGoalsWarnings,
    InteractionPoints, Error) are returned in a side-channel so
    callers can detect failures.
    """
    payloads = []
    errors = []
    for line in output.splitlines():
        line = line.replace("JSON> ", "").strip()
        if not line or not line.startswith("{"):
            continue
        try:
            j = json.loads(line)
        except json.JSONDecodeError:
            continue
        info = j.get("info", {})
        if info.get("kind") == "ModuleContents":
            payloads.append(info.get("contents", []))
        elif info.get("kind") == "Error":
            errors.append(info.get("error", {}).get("message", ""))
    return payloads, errors


def build_cache(force=False):
    modules = discover_modules()
    print(f"[agda_types] discovered {len(modules)} Substrate modules",
          file=sys.stderr)

    if not force and not cache_is_stale(modules):
        print(f"[agda_types] cache fresh ({CACHE_PATH})", file=sys.stderr)
        return json.loads(CACHE_PATH.read_text())

    write_wrapper(modules)
    print(f"[agda_types] wrapper written ({WRAPPER_PATH})", file=sys.stderr)

    # Build the batch script: one Cmd_load + 2N Cmd_show_module_contents.
    wp = str(WRAPPER_PATH)
    inc_args = f'["-i", "{SUBSTRATE_AGDA_ROOT}", "-i", "{WRAPPER_PATH.parent}"]'
    lines = []
    lines.append(f'IOTCM "{wp}" None Direct (Cmd_load "{wp}" {inc_args})')
    # Send AsIs for every module, then Normalised. Order matters: we
    # match ModuleContents payloads back to (mod, mode) by position.
    asis_order = []
    norm_order = []
    for mod, _ in modules:
        lines.append(
            f'IOTCM "{wp}" None Direct '
            f'(Cmd_show_module_contents_toplevel AsIs "{mod}")'
        )
        asis_order.append(mod)
    for mod, _ in modules:
        lines.append(
            f'IOTCM "{wp}" None Direct '
            f'(Cmd_show_module_contents_toplevel Normalised "{mod}")'
        )
        norm_order.append(mod)
    batch = "\n".join(lines) + "\n"

    print(f"[agda_types] running agda (1 load + {2 * len(modules)} queries)…",
          file=sys.stderr)
    t0 = time.time()
    proc = subprocess.run(
        ["agda", "--interaction-json",
         "-i", str(SUBSTRATE_AGDA_ROOT),
         "-i", str(WRAPPER_PATH.parent)],
        input=batch,
        capture_output=True,
        text=True,
        timeout=600,
    )
    elapsed = time.time() - t0
    print(f"[agda_types] agda done in {elapsed:.1f}s "
          f"(exit {proc.returncode})", file=sys.stderr)

    payloads, errors = parse_module_contents_in_order(proc.stdout)
    if errors:
        print(f"[agda_types] {len(errors)} error(s) reported by agda:",
              file=sys.stderr)
        for e in errors[:5]:
            print(f"  • {e[:200]}", file=sys.stderr)

    expected = 2 * len(modules)
    if len(payloads) != expected:
        print(f"[agda_types] WARNING: expected {expected} ModuleContents "
              f"payloads, got {len(payloads)}", file=sys.stderr)

    asis_payloads = payloads[: len(modules)]
    norm_payloads = payloads[len(modules) : 2 * len(modules)]

    cache = {}
    for i, mod in enumerate(asis_order):
        items = asis_payloads[i] if i < len(asis_payloads) else []
        for item in items:
            qname = f"{mod}::{item['name']}"
            cache.setdefault(qname, {"module": mod, "asis": "", "normalised": ""})
            cache[qname]["asis"] = clean_term(item["term"])
    for i, mod in enumerate(norm_order):
        items = norm_payloads[i] if i < len(norm_payloads) else []
        for item in items:
            qname = f"{mod}::{item['name']}"
            cache.setdefault(qname, {"module": mod, "asis": "", "normalised": ""})
            cache[qname]["normalised"] = clean_term(item["term"])

    CACHE_PATH.write_text(json.dumps(cache, indent=1, sort_keys=True))
    print(f"[agda_types] wrote {len(cache)} defs to {CACHE_PATH}",
          file=sys.stderr)
    return cache


def load_cache():
    """Read the cache without rebuilding. Returns {} if missing."""
    if not CACHE_PATH.exists():
        return {}
    return json.loads(CACHE_PATH.read_text())


if __name__ == "__main__":
    force = "--force" in sys.argv
    cache = build_cache(force=force)
    print(f"[agda_types] {len(cache)} entries cached", file=sys.stderr)
