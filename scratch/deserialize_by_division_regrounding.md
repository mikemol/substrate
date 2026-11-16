# ⟡REGROUNDING (2026-07-23) — the deserialize-by-division arc. COMPACTION-SAFE, stands alone.

## STATE (one line)
The prior session's "grind the 10-module Trace split" was MEASURED-FUTILE and abandoned; a measurement-driven
diagnostic localized the real cap-128 floor and arrived at a better arc: **⟡deserialize-by-division** — apply the
repo's own graded-division wedge `a=recon q b r` to the substrate's deserialize (route AND seal). No code committed
this arc (diagnostic + plan). dcee071 (otlp-wire) still unpushed from before. Memory saved:
[[deserialize-the-way-you-divide]].

## THE MEASURED COST STRUCTURE (all deltas above the fixed 62 MB agda process baseline)
- Empty module = **62 MB** (GHC+agda+Prelude; fixed, stable across -M ceilings). → 128 cap = 62 + ~66 deserialize budget.
- Algebra-record tower (Magma→…→CommutativeRing) / F₂ / Vec = **+5** (CHEAP — level-poly record discipline, the architecture win).
- Graded-poly substrate (`Poly` via `Graded.Div`) = **+38**. Breakdown (catalog.db node counts, 18809 total):
  base `Graded` (multiplicative `*P`/convCoeff/nth-*P/basis-decomp) = 10250 nodes = **55%**; Mod 18%; ModZero/Quotient 17%;
  **Div (EEA itself) = only 6%** — division is LIGHT, built ON the heavy base.
- Distribution is FLAT: **gini 0.283**, top-1 def (recon-nth 243) = 1.3%, top-10 = 8.1% ⟹ **SPLIT by access path, NOT seal a monolith.**
- The AES floor was NEVER the GF S-box (import Inverse = 89, the LIGHTEST AES module). Every AES module pays the shared
  graded-poly substrate (~100). KAT deltas: Trace +42 (fits); KeyPins +71 (busts ~5); Full-after-fin +94 (busts ~28).
- Route-around diagnostic (REJECTED as a fix, kept as a localizer): AES S-box on raw `Vec F₂ 8` (no Poly) = ~71 (−29). User:
  "the AES proof is interesting BECAUSE it's algebraic — fix the infra, don't route around."

## ⟡dbd-probe-seal VERDICT (2026-07-23) — route-alone REFUTED; seal = interface-parameterization
Source-read of Graded.agda (catalog.db is BLIND to intra-`Over`-module deps — sibling refs are de Bruijn LOCALS,
not qname atoms; both `refs` and `node_atom.op` gave false "100% sheddable"): **`*P-comm` refs basis/linear-extensionality/
mono-assoc/convCoeff-basis-right; `*P-assoc` refs basis/linear-extensionality/mono-assoc.** So the multiplicative laws
that Mod/Quotient/Div NEED are proven VIA the basis-decomposition cluster ⟹ the cluster is UPSTREAM/load-bearing, NOT
off-path. **⟡dbd-basis-lift REFUTED** (would fail the typecheck). Vindicates user's "supersets" + "route AND seal — the
interesting part is both". Div's residue-route (what it names): {nth, snoc, vlast, ytime, vinit, convCoeff, reduce-mod-f, nth-*P}.

**THE SEAL MECHANISM (empirically proven by the repo's OWN architecture):** CommutativeRing tower (record of law-STATEMENTS,
consumers parameterize over it) = **+5**; graded-poly (COMPUTES laws as proofs, `open … public` bundles the tower) = **+38**.
Same algebraic content, 8× deserialize, purely interface-vs-computed. The fix = make graded-poly abstract over a
**`GradedPolyRing` interface** (laws `*P-comm`/`*P-assoc`/`nth-*P`/`convCoeff`/`recon` as record FIELDS), instantiated ONCE,
consumers parameterized over the record → deserialize the field TYPES (sealed `recon` boundary), not the proof tower. +38→~+5.
"Deserialize the way you divide" = "abstract over the graded-ring interface the way the tower abstracts over CommutativeRing."
⚠ the `refs`/`node_atom` catalog.db views are STRUCT/external-qname-only — intra-module access needs the SPPF term-walk (⟡dbd-query-lib).

## ⟡dbd-beta-interface VERDICT (2026-07-23, MEASURED) — the seal is GENERIC-ONLY
Minimal real slice (record of statements + abstract consumer + concrete plug-in + opaque variant, all measured):
- record type (statements): +3 · **ABSTRACT consumer over the record param, USING the heavy law nth-*P: +5** (67580 KB) ⟸ generic seal WORKS.
- CONCRETE instance (packages Graded-at-F₂): +21 · PLUG (instance→consumer): +25 · OPAQUE instance: +23 · DIRECT import (today): +24.
⟹ CONCRETE consumers get NO win (+25 ≈ +24 direct); **`opaque` does NOT reduce deserialize** (standing uncertainty RESOLVED).
**REACH: generic/parameterized-over-the-ring consumers = +5 (kleinfour WIN); concrete-carrier consumers = fixed +38 substrate (NO seal).**
The AES KAT is IRREDUCIBLY CONCRETE (pins `round M S ≡ Sct` on concrete bytes) ⟹ the interface CANNOT clear cap-128 AES.
**The two goals separate cleanly: kleinfour ← ⟡dbd-gradedring-interface (generic seal); cap-128 AES ← round-composition staging (⟡cap128-mixcolumns + round-pin opaque-STAGING, substrate fixed).**
RE-SCOPE: ⟡dbd-gradedring-interface = a KLEINFOUR / EEA-over-abstract-ring win (build it for THAT). ⟡cap128-aes-via-dbd = RETIRED.

## THE COLLAPSE (user, load-bearing): route AND seal = the graded-division wedge
Every either/or collapsed to `a = recon q b r`: split-vs-seal → NEITHER (the wedge is BOTH: seal the quotient q·b, route
the residue r); route-around-vs-keep-algebra → the wedge (keep algebra AND cheap); type-only-vs-EEA consumers → both route
their residue over the sealed quotient. **Graded (not flat) division exists precisely so a consumer at grade k never
re-expands grades below k — the seal boundary IS the grade, recon is the cross-boundary hom.** The floor is the substrate
failing to apply its own wedge to its deserialize: `open … public` unfolds the whole quotient tower onto every consumer.

## ⟡dbd-gradedring-interface SATURATION — A1 (record + instance design, 2026-07-23, file:line-witnessed)
**KEY REUSE FINDING: build ONE record, not three.** The tower has three tiers; two are ALREADY homed:
- **Tier Q (quotient ring) → REUSE `CommutativeRing (Poly (suc d))` = `Quotient-CommRing` (Quotient.agda:160).** Every `_*Q_`/`+P` law is FIXED-carrier (Poly (suc d) in/out, NO grade index, NO subst — reduction lands everything at length suc d) ⟹ the quotient interface IS the existing CommutativeRing record (+5, the measured-cheap tower). A consumer over `(R : CommutativeRing (Poly (suc d)))` gets _*Q_/_+P_/oneC/𝟎C/-P + all laws as R's fields at +5. DO NOT build a QuotientPolyStructure.
- **Tier D (division/EEA recon) → REUSE `DivStr`/`GradedDivStr` + `Wedge`, ALREADY instantiated** as `Poly-div : DivStr QPolyR` (PolyDivWedge.agda:60) + `step-wedge` (:73) whose `wedge-eq` IS `recon-nth`. `DivStr (C : Set)` (Wedge.agda:53, carrier-param set1-paydown) + `GradedDivStr C R` (Wedge/Graded.agda:49). ⟹ **kleinfour EEA consumers can ALREADY parameterize over `DivStr QPolyR` at +5 — the division tier is already the interface.** DO NOT build a PolyDivStructure.
- **Tier G (raw graded `*P` before reduction) → the ONE genuine gap → NEW `GradedPolyStructure`.** No existing record captures length-additive `_*P_ : Poly n → Poly m → Poly (n ℕ+ m)` + its subst-laden `*P-comm`/`*P-assoc`. Needed by consumers working with graded mult before reduction (own reduce/quotient at a different modulus, or a kleinfour action on un-reduced graded syntax).

**THE RECORD (`Substrate/Algebra/Polynomial/Graded/Structure.agda`, --safe --without-K, the ONLY new module):**
`record GradedPolyStructure {A : Set}(Poly : ℕ → Set)(_+_ _*_ : A→A→A)(𝟘 𝟙 : A) : Set` — carrier `Poly` is a PARAMETER
(Set₁ paydown; only `_+_/_*_/𝟘/𝟙` appear in field types, the 10 coeff LAWS live only in proof bodies → thin interface, Set₀).
FIELDS (Tier G, exact types in A1 report): ops `_+P_ _·c_ _*P_ nth convCoeff`; bridges `nth-+P nth-·c nth-*P nth-ext`;
laws `*P-distribˡ/ʳ *P-scalarˡ/ʳ *P-comm *P-assoc convCoeff-comm subst-+P subst-·c`. ⚠ `*P-comm`/`*P-assoc` have
`subst Poly (+ℕ-comm/+ℕ-assoc …)` IN THE TYPE — authorable because Poly is a param AND you import the SAME `+ℕ-comm`/`+ℕ-assoc`
(Foundation.Nat.Properties) + `subst` that Graded.agda uses (do NOT re-derive a local +-comm — breaks the subst-motive defeq).
Order `_*P_` BEFORE the laws (field-type deps). EXCLUDED (the ~80 proof-helper cluster, stays in instance, never fields):
basis-collapse/basis-pair/linear-extensionality/anti-diag-sum/convCoeff-basis-xpower/mono-assoc + the Linear records (Lq/Mq/Li/Mi/Lp/Rp/…) + with-*/lhs*/rhs* helpers + hsum/ytime/vinit/vlast/xpow/basis + KEY/P1/P2.
**BUILDER:** `gradedPolyStructure : (CR : CommutativeRing A) → GradedPolyStructure (Vec A) (…CR ops…)` = pure PROJECTION of
the already-proven `FromCommRing.Over CR` fields (record { _*P_ = F.Over._*P_ CR ; *P-comm = F.Over.*P-comm CR ; … }) — NO
re-proof. The builder module pays +38 ONCE; every consumer over the record param pays +5. `Poly = Vec A` (needs only CR, not d/f-lo).
NODE-COUNT VALIDATION (catalog.db): the top ~50 heaviest units are ALL proof bodies / Linear records (recon-nth 243, nth-*P 159,
basis-collapse 158, …) = exactly the excluded cluster; the public statements carry near-zero marginal nodes. Confirms +5-vs-+38.

## ⟡dbd-gradedring-interface SATURATION — A2 (consumer census, 2026-07-23, file:line-witnessed)
**DECISIVE: no external consumer parameterizes over the ring today — all hardcode F₂-CommRing/GF256-CommRing.** So the axis is
USAGE not signature: a module proving facts FROM the poly/ring LAWS has a generic CORE extractable to `(GPS) → …` (+5), with
the concrete carrier deferred to a thin bottom-of-file cap (still +38, but ISOLATED). A module that FORCES normalization of
concrete Poly values (KAT/tables/S-box/is-zero8) or leans on char-2 constructor facts (-P=id, +-self, 𝟙≢𝟘, F₂.𝟘/𝟙 matching)
has no extractable core.
- **Class A — GENERIC CORE (extract → WINS; = the kleinfour/EEA consumers):** `DLogHom` (gpow-hom = the ℤ-action on the
  cyclic mult group R[x]/f, proven structurally from *Q laws — THE group-action-into-syntax bridge, generic; GF16 instance +
  `order15=refl` is the concrete cap), `DLogPow` (gx₄/GF16 cap), `EEATrace` (pure Div projections; QPoly carrier = the only F₂),
  `FuelEEA` (fuel-bezout builder; char-2 dep only via ComputeTrace), `PolyDiv §1-4` (F₂[x] division IS a generic DivStr/Trace
  wedge; §5 recover-flo/-P-id is char-2 residue, stays concrete).
- **Class B — CHAR-2/DECEQ RESIDUE (partial/no win):** `BezoutFold` (+-self char-2), `ComputeTrace` (-P-id), `Trim` (matches
  vlast r | F₂.𝟙 | F₂.𝟘 — needs DecEq). Re-param costs a DecEq/neg arg for no deserialize win; leave concrete.
- **Class C — CONCRETE (keep the +38 substrate):** the AES/GF(2ⁿ) EVALUATION layer — SBoxFaces/SBox/SBoxTable/AsField,
  GF256/{Bridge,HornerSeam,MulLaws,Poly,XtimeTable}, GF16/GF4 *, GUnit, Inverse, the nilpotent R/Trace DLog caps
  (ExtruderNfCrossDlog*, NilpotentFaithfulLogChart, NilpotentLogExpBridge). All force computation. (No ℤ/ℚ carrier feeds these
  four modules — the whole downstream is F₂/GF(2ⁿ); Cyclotomic/JacobianResidue/Medial/Semiring.Instances are comment-only, NOT importers.)
**KLEINFOUR PAYOFF = Class A exactly:** the interface makes the group-action/EEA machinery ring-agnostic — one +5 core
instantiates at GF(2⁴), GF(2⁸), AND the nilpotent R/Trace regime (3 carriers today) from ONE core; the concrete caps localize +38.
**⚠ RECONCILES + EXTENDS A1:** the generic cores use, beyond the ring laws, the REDUCE-BRIDGE names ytime/xpow/reduce-*P-expand/
reduce-idempotent/hsum/*Q-{assoc,comm,identityˡ} + Div's b-poly/r-div/q-div/recon-nth. So a Class-A core parameterizes over
A1's `CommutativeRing (Poly (suc d))` (=`Quotient-CommRing`, for _*Q_/+P) + `DivStr`/`Wedge` (for divmod/recon-nth) PLUS a small
reduce-bridge interface (ytime/xpow/reduce-* as statement-fields — if any is a DEFINITION not a law it becomes a `(name:type)`
field + coherence law). NOT just the raw-*P `GradedPolyStructure` (that's for pre-reduction consumers).
**MIGRATION ORDER (bottom-up):** 1. EEATrace (leaf) → 2. DLogHom then DLogPow → 3. PolyDiv §1-4 → 4. FuelEEA. **MEASURE +5-vs-+38
on EEATrace+DLogHom FIRST** (confirm the modeled win before the harder PolyDiv/FuelEEA splits). Leave Class B/C concrete.

## ⟡cap128-mixcolumns SATURATION — B1 (round-composition staging, 2026-07-23, MEASURED, file:line)
**REFRAME: MixColumns is NOT the lever — extraction of the in-module CHAIN TERMS is.** `mix-fast` (MixColumns/Fast.agda:41-46)
is table-lookup+XOR, zero generic gmul (guaranteed by `gmul c02≡xtime`/`gmul c03≡xtime⊕id`, Scale.agda:15,25) — so a round
`refl` never fires a const×const normalization. MixColumns/Proof (208MB re-typecheck, +146) is a ONE-TIME BUILD cost (abstract
over the 8 products+4 collapses; circulant-factored: rt-head at coord 0 + rotation-equivariance f-rot/f-rot²/f-rot³ ⟹ 12 of 16
collapses evaporate), deserialized CHEAPLY by Round. **The round-composition delta is not MixColumns re-normalizing.**
Per-ROUND cut is already done + cheap (Round1 = `round M0 S0 ≡ S1` refl = only +10 over the Trace floor) ⟹ per-LAYER splitting
(SubBytes/ShiftRows/MixColumns/addKey) is the WRONG cut. `opaque` is NOT the lever (zero opaque blocks in AES tree; the
Assemble parameterized-module + `open`-no-reconversion, Full.agda:15-17,51,105-110, already prevents re-normalization). **Extraction is.**

**Full's +56 in-module delta = two large proof-TERM chains Assemble builds** (same class RoundFin removed, 228→156):
key-schedule chain `ck1..ck10 → rkmid-eq/rk10-eq` (Full.agda:70-85) + round fold-chain `fc : fold round ms s0 ≡ s9` (Full.agda:88-97).
**THE PLAN (generalizes RoundFin from a refl to the two chains):**
- (a) **Split KeyPins per-key** → KeyPin1..KeyPin10, each a single `nextRoundKey` refl like Round1..9 (fixes the KeyPins buster, 137→~Round1).
- (b) **Extract KAT.SchedChain** (rkmid-eq/rk10-eq — the ck-chain built ONCE, imports KeyPin handles + Trace).
- (c) **Extract KAT.FoldChain** (fc — the 9-trans fold built ONCE, imports RoundN handles + Trace).
  ⟹ Full imports rkmid-eq/rk10-eq/fc/pre/fin as pre-checked HANDLES; its `kat` becomes ~3 trans/cong → in-module elaboration
  drops well below the +28 headroom (a single round pin is only +10 over the floor).
- (d) **Deepest lever — split Trace.** The irreducible ~+59 floor under EVERY KAT pin is Trace's 20 State + 11 key literals
  (Trace.agda:41-52,71-82). A per-round/per-key pin needs only 2-3 (Round1 uses M0,S0,S1). Split TraceStates/TraceKeys (or per-item)
  → each pin deserializes a SLICE → drops Round1..9/RoundFin/KeyPin1..10 toward ~70-80. (Does NOT help Full — needs all states; a-c fix Full.)
PRECEDENTS: opaque-TYPE seal `Q/JacobianEncodingLiteral.agda:38-53` (Identify₁/₂/₃ sealed, heavy reduction once behind the boundary,
consumed as handle at JacobianCounterexample.agda:87-99); incremental normalize-staging `Z/JacobianDetNative.agda:53-54` (98 vs 317MB);
`AES/KAT/RoundFin.agda:9-14` (the fin-extraction to generalize).
⚑ **INCIDENTAL BUG (uncommitted working-tree, blocks Full's fresh build): `AES/KAT/RoundFin.agda:1` has `--safe --without-K`
while all KAT siblings are `--safe` (with-K) → `[CoInfectiveImport]` at RoundFin.agda:23. FIX: drop `--without-K` from RoundFin.agda:1.**
(Separately: full-tree `make` blocked by a Flat.mk sync-check vs untracked files e.g. Algebra/Z/CommRing.agda — unrelated.)
→ ⟡cap128-mixcolumns RENAMED **⟡cap128-round-staging** (MixColumns isn't it; the chain-extraction + KeyPins-split + Trace-split are).

## ⟡cap128-round-staging SATURATION — B2 (KAT clearance, 2026-07-23, MEASURED w/ REAL agda 2.8.0 @-M256m) — STAGING REFUTED
⚠ REFUTES two premises (measured, real binary /home/mikemol/.local/bin/agda, .agdai rm'd, foreground):
- **Full = 227, NOT 156.** The fin-extraction (RoundFin) bought ~nothing — the prior "228→156" is FALSIFIED ([[feedback_plan_notes_are_hypotheses]]).
- **The floor is ~110-112 MB AES graded-poly MACHINERY import, not 62+38+states.** Zero-state `AES/Round.agda`=111; Trace's 26
  states add only +5-8. (My earlier 62-floor/+38 numbers were the shimmed `agda`; B2's real-binary peaks are ~13MB higher and authoritative.)
MEASURED: Trace 117-118 (clears), Pre 115, RoundFin 111, Round4 119, Round5 121 (clear); Round1/2/3/6/7/8/9 129-132 (BUST by 1-4);
KeyPins 134 (BUST 6); **Full 227 (BUST 99)**.
**Full's +115 — DOMINANT is the abstract KEY-SCHEDULE cong-chain +88** (ck1..ck10→rkmid-eq/rk10-eq, Full.agda:70-85), NOT rounds/fin
(that's why fin/round extraction never moved Full — different summand). Cumulative over the 112 floor: imports 112 → +ck1-5 = 160
(**+48 fixed to host ANY nextRoundKey cong-chain**) → +ck1-10 = 175 → +rkmid/rk10-eq = 200 → +fc fold = 224 → +kat 226 → +open 231.
"Neutral ≠ cheap": each `cong (nextRoundKey rcᵢ)` symbolically unfolds the S-box word-recursion (~+10MB apiece).
**EXTRACTION MOVES THE BUST, DOESN'T DISSOLVE IT** (refutes B1's plan a-d): extracting SchedChain+FoldChain makes Full thin
(~119) but the extracted schedule module = ~200, fold = ~136; a depth-5 sub-chain ALONE = 160. **NO decomposition hosts the schedule
glue in ANY module under 128** (confirms + strengthens RoundComposite-busted-151). **Trace split CONFIRMED FUTILE** (states +5-8, machinery is the floor).
KeyPins: 4/6 split (KP1-4/KP5-10) ~118/126 = safe; 5/5 = 128/121 (KP1 forces key-C1 state). Marginal floor-band, not a headroom win.
**HONEST BOTTOM LINE: the 128 target sits BELOW the substrate floor (~110) + one AES op — UNREACHABLE for Full/most-rounds by staging.**
- Clear 128 as-is: Trace, Pre, RoundFin, Round4, Round5.
- Irreducibly over by 1-6 (floor + single `refl`, nothing to extract): Round1/2/3/6/7/8/9, KeyPins (splittable to the 121-128 band, not comfortably under).
- Irreducibly over, unsplittable: Full (227).
**⚑⚑ B2's "accept 384 / floor irreducible" is RETRACTED — WALL-REFLEX (user 2026-07-23: "128 is a deliberate forcing
function; the floor is not the floor; you forgot our strategies for digging deeper").** B2 measured the ~110 import as a
black box and declared it irreducible WITHOUT the reuse-search. The floor is UNDIAGNOSED. B2 CONFLATED two cost types:
- **~110 DESERIALIZE floor = LOAD-BOUND → the lever is `def/proof separation`** ([[feedback_def_proof_separation_lever]]):
  loading deserializes the whole transitive closure incl proof TERMS; `opaque`/`abstract` do NOT help (B2's true "opaque
  doesn't help" — but the lever is SPLIT, not opaque). A KAT pin `round M S ≡ S'` USES sbox/mix-fast as DEFS but never the
  LAWS sbox-is-aes/mixcolumns-round-trip/*P-comm/nth-*P — yet deserializes their whole proof closure incl the ~89MB GF-inversion
  (Inverse) behind sbox-is-aes. **SPLIT graded-poly + S-box + MixColumns into `defs` vs `.Properties` → KAT deserializes the
  DEF closure only.** Corroborated: S-box table-def-alone ≈71 vs SBoxTable-with-proof ≈102 (+31 = the sbox-is-aes/Inverse
  closure never unfolded). **KEEPS the algebra (proof still in .Properties) — fix-infra, NOT the raw-Vec route-around (retracted).**
  MEASURED precedent: DefPart-only +1 vs Combined +23; split removes the +23.
- **Full's +88 TYPECHECK glue = NORMALIZATION-BOUND → `opaque-seal the super-linear neutral + FreeUP β-interface`**
  ([[opacity-tracks-blowup-layer]], [[opacity-blowup-routearound-freeup]], [[cyclen-opacity-fix]]): each `cong (nextRoundKey rcᵢ)`
  unfolds the S-box word-recursion (super-linear). Seal `nextRoundKey`/the key-schedule fold `opaque` (typechecks once at abstract
  args; consumer references a black box) + discharge rkmid's nesting via a fold-combinator on generators (prove-on-generators-then-lift).
  B2 flagged this "the escape" then WRONGLY hedged "floor-bound" = the wall-reflex; it's the exact Cyclen `iterate 7` fix (0.83s/74MB).
**⟹ 128 IS REACHABLE. ⟡cap128-round-staging is SUPERSEDED by ⟡cap128-defproof-split (the ~110 deserialize floor) + ⟡cap128-schedule-seal
(Full's +88 typecheck glue). opacity tracks the BLOWUP not the layer; the def/proof SPLIT (not opaque) is the load-bound lever.**
⚑ B2's measured facts STAND (Full 227, floor ~110, states cheap, extraction-moves-the-bust for the CHAIN approach); only its
"irreducible/accept-384" CONCLUSION is refuted — the untried levers are def/proof-split (load) + opaque-seal-super-linear (typecheck).

## LABELED ⟡ ROSTER (specify by symbol)
### THE ARC — ⟡deserialize-by-division (route AND seal the graded-poly substrate via the wedge)
- **⟡dbd-probe-seal** — γ₁ VERIFY-FIRST (operator=self, runnable now): measure that MOVING the off-EEA basis-decomp cluster
  out of the Graded→Mod→Quotient→Div chain actually DROPS Div's deserialize. Decides whether a module-boundary seal reduces
  transitive deserialize in Agda's model BEFORE any refactor. Do FIRST — the whole arc rests on this being true.
- **⟡dbd-basis-lift** — lift the basis-decomposition tower into a separate module EEA/Div doesn't import (Mod imports only
  basis/basis-decomp roots). Cleanest first seal-and-route; gated on ⟡dbd-probe-seal.
- **⟡dbd-mult-seal** — the core: express base Graded's multiplicative quotient (*P/convCoeff/nth-*P) as a sealed graded
  neutral behind `recon` — statement-handle in the interface, opaque proof-tower in a proof-consumer module. Drops the +38→routed.
- **⟡dbd-openpublic-audit** — audit the `open … public` chain (Graded→FromCommRing→Mod→Quotient→Div): selective re-export
  (route) instead of proof-unfolding (bundle). The mechanism behind the floor.
- **⟡dbd-query-lib** — the python SPPF query library: fetch the FUNCTION-level reference graph (term-node walk, not the
  struct-only `refs` view) sqlite→numpy, so access-path splits are computed mechanically. Reusable instrument (also unblocks
  ⟡cap128-largemodule-profile). The user's "build a python library" nudge.
### AES / cap128 (reframed by the finding)
- **⟡cap128-aes-via-dbd** — the KAT clears once ⟡deserialize-by-division drops the shared substrate. Full's residual bust
  (+94) is round-COMPOSITION on top — reassess after the substrate drops. RETIRES the Trace-split + opaque-pipeline framings (measured-futile).
- **⟡cap128-mixcolumns** — MixColumns genuinely uses ring-mult on the round-forcing path (the residual after the substrate
  seal). Same wedge: seal the GF-mult quotient, route the byte residue (or xtime/table runtime form, ring-mult proof offline).
- **⟡cap128-largemodule-profile** — apply the proven diagnostic (catalog.db distribution + access-path via ⟡dbd-query-lib)
  to the other offenders (ExtrudeCoEmitGraded / Polynomial-Graded / Q.Properties.Decidable).
- **⟡cap128-decide** — GATED endgame: after all offenders clear, drop MEM_CAP 256→128 + AGDA_FBC_MEM=128 + doc sweep.
### STANDING / RETIRED
- **⟡push** — dcee071 (otlp-wire) unpushed, marker ✓. USER pushes.
- **⟡aes-lehmer-extruder** — DEFERRED (user: "we'll get around to it"); the ⟡deserialize-by-division arc is adjacent (both
  the substrate-representation question) and may inform it.
- **RETIRED**: ⟡cap128-aes-pipeline (opaque pipeline stages), the Trace-split, ⟡cap128-mixcolumns-freeup-as-separate —
  subsumed by ⟡deserialize-by-division / ⟡cap128-mixcolumns.
- **⟡flat-parallel-validate** — confirm flat `make -j` full gate on next STRUCTURAL commit. operator=other.

## THE RECURRING MISS (G3/G9): inheriting a saturated plan and building on its cost-premise before measuring it.
The Trace-split (from the compaction summary) rested on a wrong cost model; measure-disproves-the-plan (half-Trace =
full-Trace) killed it before I built it. Standing memories cover this ([[feedback_plan_notes_are_hypotheses]],
[[measure-instrument-before]]) — fire them BEFORE building on an inherited plan. Decorrelation came from the USER's redirects
(streaming, fix-infra, catalog.db, python-lib, route-and-seal) + measurement, not self-subtraction — the recurring pattern.
