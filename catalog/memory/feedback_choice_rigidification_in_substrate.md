---
name: feedback-choice-rigidification-in-substrate
description: "LLMs working on this corpus tend to freeze provisional gauge-free choices into permanent structural commitments. Watch for choices that the math leaves free but the implementation treats as load-bearing; when you see one, check whether it has been content-addressed-against, verified-as-contract, or built-into-downstream-digests."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 92eaad2c-ead2-4c10-b788-1f971ff34b56
---

**Pattern: operational choice-rigidification.** A choice that the
mathematics permits as free (gauge freedom, canonical-within-orbit,
representation choice) is treated by an LLM as permanent and built
into the operational substrate — verified as a contract, content-
addressed against, depended on by downstream digests. When a later
move wants to make a different choice (the formally cleaner one), it
can't displace the frozen choice; instead a translation/bridge layer
is grafted on. The bridge is the residue of the rigidification.

This is structurally related to the negation-IS-overclaim pattern in
[[feedback-negative-findings-in-corpus]] — both are LLM moves that
commit operationally to more than the math requires. There, the
overclaim is "X fails universally"; here, the overclaim is "this
particular canonical is THE canonical."

**Why:** The lex-min canonical choice in M41 v16 is the corpus's
crisp case. The mathematics (M2's "topos's freedom" / M8 cocycle
gauge) permits any V_4 translate as canonical. **Nuance from drift
archaeology (T219→T220, 2026-05-15)**: the *framing* "canonical is
always left-choice" was supplied by the user at T219 as a
Cayley-Dickson direction; the LLM operationalised this framing as
lex-min specifically at T220 without surfacing that "left-choice"
admits multiple operationalisations. The user's structural framing
was not the rigidification — the LLM's specific operational
commitment (lex-min, encoded into the content-address chain, frozen
as a verifier contract) was. By M41 v19, when the formal V_4 ⋊ S_3
framing wanted Stab(D)-representative as canonical, the lex-min
couldn't be displaced; `verify_v17_v19_decomposition_agreement` +
`verify_canonical_offset_consistent_per_orbit` exist precisely to
bridge two frozen canonical conventions. The user at T229 actually
named this gap with precise vocabulary — "**canonical-choice
defect**" — but the rigidification was already in receipts.

**Lesson sharpened**: when operationalising a user's structural
framing, distinguish "what the framing forces" from "what we
picked" — the user supplying "left-choice" did NOT force lex-min
specifically. Surface the operational gauge choice as a gauge
choice in code, not as a verified contract.

**Instance (2026-06-22, jea_oneforest completeness audit).** Asked for tooling auditing Python↔Agda
structural mirroring, I built the fidelity gate's recall companion, then proposed "author a *manifest* of
INTENDED Python-op ↔ Agda-def correspondences" as the next step. User: "ain't nothing supposed to mirror
nothing; the key is structural correspondence and SYMMETRY." The manifest-of-intentions was textbook
rigidification — a *declared* canonical mapping with a verifier against it, for a relation the math leaves
to be DISCOVERED (two units correspond iff they share canonical structure under the interner's α/role
quotient = the gauge). Fix = `OneForest.correspondence()`: the SYMMETRIC mutual-best/reciprocal matching,
discovered from the shared forest, `symmetric`=total structural bijection up to the gauge — no manifest. The
manifest survived only DEMOTED to a regression pin ("assert a once-discovered symmetry still holds"). Tell:
**reaching for a "manifest / spec / intended-mapping" to describe a structural relation is the rigidification
flag — discover the symmetry, don't declare it.** Same shape as the lex-min case: a gauge-free relation (here
the cross-arm correspondence) about to be frozen as a declared contract.

**How to apply:**
- A "manifest/spec/table of intended correspondences" for a relation the structure already determines is a
  rigidification flag. Compute the symmetric (reciprocal/mutual-best, or canonical-structure-equal) matching
  and let orphans/asymmetry fall out; if you keep a declared list at all, demote it to a regression pin on a
  *discovered* symmetry, never the source of truth.
- When implementing a piece of the substrate that involves a
  canonical-within-orbit choice, an in-list-element-zero choice, or
  any other selection from gauge-equivalent options: **say
  explicitly that the choice is a gauge convention**, not a
  structural commitment. Add a `# CHOICE: lex-min (one of N
  gauge-equivalent options)` comment, not a `# REQUIRED: lex-min`
  one. Do not write verifiers that test the *specific* choice; if
  you must verify, verify the *abstract property* (e.g., "canonical
  is a deterministic function of orbit_key") rather than the
  specific representative.
- Be especially suspicious of content-addressing schemes that
  encode `delta-from-canonical`. The receipts' content is now
  parametrised by the canonical choice — that means a downstream
  choice swap requires re-encoding receipts. Either content-address
  by the gauge-invariant only (orbit_key alone, never v4_delta), or
  accept the rigidification with eyes open.
- If you find yourself writing a "translation layer" or "agreement
  theorem" between two canonical conventions, recognise that this
  is the residue of an earlier rigidification — neither convention
  is wrong, but neither could be substituted. Note it explicitly.
- The general lesson: **frozen choice masquerading as discovered
  structure** is the underlying drift mode. Distinguish "this is
  what the math forces" from "this is what we picked" in code and
  prose; never let the latter pass for the former.
