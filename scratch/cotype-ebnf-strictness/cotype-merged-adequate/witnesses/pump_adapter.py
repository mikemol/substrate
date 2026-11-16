# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Shared pump()/parse() adapter for paperkit liveness (github.com/mikemol/paperkit driver.py).

A sweep-witness exposes two module-level names:
    CASES          : a list of opaque, JSON-able case descriptors (the enumeration)
    compute(case)  : runs ONE case, returns a JSON-able result (heavy objects built & discarded inside)
and optionally:
    GOLD           : dict {repr(case)->expected_result} so parse() can emit a PASS/FAIL verdict
    fmt(case,res)  : a one-line string for the cold __main__ printout

Then `from pump_adapter import make; initial,pump,parse,serialize,deserialize = make(globals())`
gives the five functions the paperkit driver calls. One pump() = one CASES item; state is a cursor +
accumulated results (no heavy object ever serialized). Cold fallback: call run_main(globals()).
"""
import json, sys

def make(ns):
    CASES = ns["CASES"]; compute = ns["compute"]; GOLD = ns.get("GOLD")
    def initial(): return {"cursor": 0, "results": []}
    def pump(state):
        i = state["cursor"]
        if i >= len(CASES): return state
        res = compute(CASES[i])                      # heavy work here; nothing heavy escapes
        return {"cursor": i+1, "results": state["results"] + [res]}
    def parse(state):
        done = state["cursor"] >= len(CASES)
        out = {"done": done, "results": state["results"],
               "progress": f'{state["cursor"]}/{len(CASES)}'}
        if GOLD is not None:
            bad = [(repr(CASES[k]), state["results"][k]) for k in range(len(state["results"]))
                   if GOLD.get(repr(CASES[k])) != state["results"][k]]
            if bad: out["verdict"]="FAIL"; out["counterexample"]=bad[0]
            elif done: out["verdict"]="PASS"
        return out
    def serialize(s): return json.dumps(s, sort_keys=True)
    def deserialize(b): return json.loads(b)
    return initial, pump, parse, serialize, deserialize

def run_main(ns):
    """Cold fallback: full sweep, print, exit 0/1 on PASS/FAIL (existing cmd: contract)."""
    initial,pump,parse,_,_ = make(ns)
    st = initial()
    while not parse(st)["done"]: st = pump(st)
    m = parse(st); fmt = ns.get("fmt")
    for case, res in zip(ns["CASES"], m["results"]):
        print(fmt(case,res) if fmt else f"{case} -> {res}")
    if "verdict" in m:
        print(f"verdict: {m['verdict']}")
        sys.exit(0 if m["verdict"]=="PASS" else 1)
    sys.exit(0)
