---
name: feedback_policy_is_a_ratchet_over_census
description: "a recurring gate/policy over accumulating DEBT (Set₁ count, carrier-locality exemptions, sum-type debt, decode-cost) is a RATCHET over a MATERIALIZED census — a baseline that pays down monotonically (refuses increases, auto-lowers on paydown), self-calibrating — NEVER a frozen ALLOW-list, a hardcoded scalar, or a one-off exempt-vs-fix pick; when a gate fires, PAY DOWN (home/fix), never --no-verify or add an exemption"
metadata:
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
  modified: 2026-07-27T17:48:17.140Z
---

When a gate guards ACCUMULATING DEBT (a count that should trend to 0 or hold), model it as a RATCHET
over a materialized census, exactly like `set1_ratchet_cores.py`: a baseline file, a census query, and a
compare that (1) REFUSES an increase, (2) AUTO-LOWERS + rewrites the baseline on a decrease, (3) freezes
at baseline otherwise. The debt is then monotone-paydown by construction — not a frozen list that only
grows, and not a scalar someone hand-picks.

**The failure this corrects (2026-07-19).** An ingested Agda module tripped the carrier-locality gate
(a local `_⊕_` over Bool×Bool). I recommended EXEMPT (add to the gate's ALLOW set) — the frozen-list
anti-pattern. The user chose IMPORT (home the operator, a paydown) and GENERALIZED: "that ALLOW list
needs to be subject to a ratchet-and-paydown policy the same way Set₁ was, and the same way sumtypes
should." A sanctioned exemption is STILL DEBT; the ALLOW list should ratchet DOWN (block new exemptions,
lower on paydown), not sit frozen.

**Why:** an exemption list / a hardcoded threshold is a stale proxy that only grows — it hides forks
(the thing check_carrier_locality's DEDICATION rule exists to prevent) and never forces the fix. A
ratchet over the live census makes the debt visible, monotone, and self-healing: the census IS the
truth (read it), the baseline IS the ratchet (pay it down). This is the same fixed point as
[[feedback_cost_is_structural_times_live]] (a cost is a live factored measure, not a hardcoded scalar)
one layer up — at GATE POLICY.

**THE CENSUS PREDICATE MUST MATCH THE POLICY, NOT THE GATE'S CONVENIENCE (2026-07-27, corrected TWICE).**
The `public`-re-export ratchet counted only WHOLESALE `open import … public`; NARROWED ones (`… public` +
a `using`/`renaming` on a continuation line) were invisible to its regex — so ~158 real conduits were not
"exempt", they were **NOT IN THE CENSUS AT ALL**. I read that gap as licensing a softer policy ("narrowed
re-exports should never have been stripped") — the same collapse this memory already forbids, one layer
up: **inferring the POLICY from what the INSTRUMENT can see.** The user's ruling both times: *"No. No
exemptions."* / *"I'm pushing for a policy-driven ban on **all** re-exports."* A narrowed re-export is
still a CONDUIT — the consumer reaches structure through a module that does not define it.

⟹ When the policy is wider than the predicate, **widen the predicate and REGENERATE the baseline UPWARD**,
then pay down. A census that grows on a predicate fix is the ratchet working, not a regression. Corollary:
**census-exemption is about what the GATE counts, never about what the PAYDOWN owes** — an instance the
instrument cannot see is invisible debt, and reasoning from its absence is a stale-proxy read of the
substrate. The tell = "the census doesn't count these, so they're fine", "the gate's definition of X is
narrower, so X is out of scope", "this class was never in the baseline".

**How to apply:** at a gate firing, PAY DOWN (home the operator / fix the def), never `--no-verify` and
never add an exemption to make it pass. When building a gate over accumulating debt, give it a ratcheting
baseline (mirror set1_ratchet_cores.py) — refuse increases, auto-lower on paydown. Three+ such ratchets
(Set₁, carrier-locality, sum-type) share ONE structure (baseline + census + monotone compare) → factor a
`ratchet.py` helper they instantiate (single-source). The tell = "just add it to the ALLOW list", "the
threshold is N", "exempt this one", "--no-verify". Relates to [[feedback_cost_is_structural_times_live]],
[[read-structure-dont-rebuild]], [[single-source-truth]], [[policy-load-bearing-discipline]].
